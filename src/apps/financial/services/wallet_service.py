import logging
from decimal import Decimal
from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.db.models import Sum, F, Q
from azbankgateways import (
    default_settings as settings,
)
from azbankgateways import (
    models as bank_models,
)
from apps.financial.models import Wallet, WalletTransaction

logger = logging.getLogger(__name__)


def wallet_gift_charge(request):
    user = request.user
    code = request.POST.get("code")

    gift = GiftCode.objects.filter(code=code).first()
    if not gift:
        messages.error(request, "کد هدیه موجود نمی باشد")
        return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

    if not gift.user_can_use(user):
        messages.error(request, "شما قبلا از این کد هدیه استفاده کرده اید.")
        return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

    if not gift.can_use:
        messages.error(request, "کد هدیه قابل استفاده نمی باشد")
        return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

    if gift.apply(user):
        messages.success(request, "کیف پول شما شارژ شد.")
        return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))
    else:
        messages.error(request, "خطا در اعمال کد هدیه.")
        return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))


def wallet_charge_callback(request):
    tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
    if not tracking_code:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    try:
        bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
    except bank_models.Bank.DoesNotExist:
        logging.debug("این لینک معتبر نیست.")
        raise Http404

    if bank_record.is_success:
        user = request.user

        user.wallet.charge(bank_record.amount)

        context = {
            "success": True,
            "message": "کیف شما به مبلغ شارژ شد",
            "tc": tracking_code,
            "btn_url": "apps.accounts:dashboard_financial",
            "btn_title": "رفتن به کیف پول",
        }
        return render(request, "financial/payment_result.html", context=context)

    context = {
        "success": False,
        "message": "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.",
        "tc": tracking_code,
        "btn_url": "apps.accounts:dashboard_financial",
        "btn_title": "رفتن به کیف پول",
    }
    return render(request, "financial/payment_result.html", context=context)


class WalletService:
    MIN_CHARGE_AMOUNT = 100000  # حداقل شارژ
    MAX_CHARGE_AMOUNT = 20000000  # حداکثر شارژ
    MIN_WITHDRAW_AMOUNT = 500000  # حداقل برداشت

    def __init__(self, user):
        self.user = user
        self.wallet = self._get_wallet()

    def validate_for_charge(self, amount):
        try:
            if amount < self.MIN_CHARGE_AMOUNT:
                return {
                    "success": False,
                    "message": f"حداقل مبلغ شارژ {self.MIN_CHARGE_AMOUNT:,} تومان است",
                }

            if amount > self.MAX_CHARGE_AMOUNT:
                return {
                    "success": False,
                    "message": f"حداکثر مبلغ شارژ {self.MAX_CHARGE_AMOUNT:,} تومان است",
                }

            return {
                "success": True,
            }
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "مبلغ معتبر نیست",
            }
        except Exception as e:
            logger.error(f"Wallet charge error: {str(e)}")
            return {
                "success": False,
                "message": "خطا در شارژ کیف پول",
            }

    def process_callback(self, tracking_code):

        try:
            if not tracking_code:
                logger.warning(f"Invalid tracking code from {self.user}")
                raise Http404("کد پیگیری یافت نشد")

            bank_record = self._get_bank_record(tracking_code)

            with transaction.atomic():
                wallet_transaction = self._get_or_create_transaction(
                    self.user,
                    tracking_code,
                    bank_record.amount,
                )

                if wallet_transaction.is_processed:
                    return {
                        "success": False,
                        "message": "این تراکنش قبلا پردازش شده است.",
                        "tracking_code": tracking_code,
                    }

                if bank_record.is_success:
                    self.wallet.charge(bank_record.amount)

                    wallet_transaction.is_processed = True
                    wallet_transaction.processed_at = timezone.now()
                    wallet_transaction.save()

                    logger.info(
                        f"Callback processed for {self.user.username}: {bank_record.amount}"
                    )

                    return {
                        "success": True,
                        "message": f"کیف پول به مبلغ {bank_record.amount:,} تومان شارژ شد",
                        "tracking_code": tracking_code,
                        "balance": self.wallet.balance,
                    }

                return {
                    "success": False,
                    "message": "پرداخت با شکست مواجه شد",
                    "tracking_code": tracking_code,
                }

        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return {"success": False, "message": "خطا در پردازش پرداخت"}

    def get_transactions(self, page=1, limit=10):
        queryset = WalletTransaction.objects.filter(user=self.user)
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        transactions = queryset.select_related("user").order_by("-created_at")[
            start:end
        ]

        return {
            "items": transactions,
            "total": total,
            "page": page,
            "limit": limit,
            "has_next": end < total,
            "balance": self.wallet.balance,
        }

    def get_balance(self):
        return self.wallet.balance

    def _get_wallet(self):
        return Wallet.objects.get(user=self.user)

    def _get_bank_record(self, tracking_code):
        try:
            return bank_models.Bank.objects.filter(tracking_code=tracking_code).first()
        except Exception as e:
            logger.error(f"Bank record error for {tracking_code}: {str(e)}")
            raise Http404("لینک معتبر نیست")

    def _get_or_create_transaction(self, user, tracking_code, amount):
        transaction, _ = WalletTransaction.objects.select_for_update().get_or_create(
            tracking_code=tracking_code,
            defaults={
                "user": user,
                "amount": amount,
                "is_processed": False,
            },
        )
        return transaction
