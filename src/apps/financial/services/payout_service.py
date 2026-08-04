# finance/services.py
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum
from apps.financial.models import (
    CoachIncome,
    CoachIncomeStatus,
    Payout,
    UserGiftCodeUsed,
    Wallet,
)


def create_coach_income(course, payment):
    available_date = timezone.now().date().__add__(timezone.timedelta(days=7))
    course_final_price = course.get_final_price

    with transaction.atomic():
        CoachIncome.objects.create(
            coach=course.coach,
            payment=payment,
            course=course,
            course_amount=course_final_price,
            percent=course.coach.coach_percent,
            amount=(course_final_price * course.coach.coach_percent) / 100,
            available_date=available_date,
        )


def get_available_coach_income_balance(coach) -> int:
    return (
        CoachIncome.objects.filter(
            coach=coach,
            status=CoachIncomeStatus.AVAILABLE,
            available_date__lte=timezone.now().date(),
        ).aggregate(total=Sum("amount"))["total"]
        or 0
    )


def get_available_coach_income_ids(coach):
    return CoachIncome.objects.filter(
        coach=coach,
        status=CoachIncomeStatus.AVAILABLE,
        available_date__lte=timezone.now().date(),
    ).values_list("id")


def create_coach_payout_request(user, amount, bank):
    with transaction.atomic():
        payout = Payout.objects.create(
            user=user,
            bank=bank,
            amount=amount,
        )


def giftcode_check_can_use(giftcode) -> bool:
    if giftcode.infinity:
        return True

    if giftcode.count_use == 0:
        return False
    else:
        return True


def giftcode_create_user_used(giftcode, user):
    return UserGiftCodeUsed.objects.create(
        user=user,
        gift_code=giftcode,
    )


def giftcode_check_user_used(giftcode, user) -> bool:
    if UserGiftCodeUsed.objects.filter(
        user=user,
        gift_code=giftcode,
    ).exists():
        return False
    return True


def gift_code_apply_to_wallet(giftcode, user):
    try:
        with transaction.atomic():
            user.wallet.charge(giftcode.value)

            giftcode.used_counter()

            giftcode.create_user_used(user)
            return True
    except:
        return False


def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


# def wallet_gift_charge(request):
#     if request.method == "POST":
#         user = request.user
#         code = request.POST.get("code")

#         gift = GiftCode.objects.filter(code=code).first()
#         if not gift:
#             messages.error(request, "کد هدیه موجود نمی باشد")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if not gift.user_can_use(user):
#             messages.error(request, "شما قبلا از این کد هدیه استفاده کرده اید.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if not gift.can_use:
#             messages.error(request, "کد هدیه قابل استفاده نمی باشد")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         if gift.apply(user):
#             messages.success(request, "کیف پول شما شارژ شد.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))
#         else:
#             messages.error(request, "خطا در اعمال کد هدیه.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))


# def wallet_charge(request):
#     if request.method == "POST":
#         user = request.user
#         amount = int(request.POST.get("amount"))
#         if amount < 100000:
#             messages.error(request, "مبلغ کم تر از صد هزار تومان می باشد.")
#             return HttpResponseRedirect(reverse("apps.accounts:dashboard_financial"))

#         callback_url = "apps.accounts:dashboard_financial_wallet_charge_callback"
#         pay = PaymentService(
#             request=request,
#             amount=amount,
#             payment_for="a",
#             callback_url=callback_url,
#         )
#         return pay.go_to_gateway()


# def wallet_charge_callback(request):
#     tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
#     if not tracking_code:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404

#     try:
#         bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
#     except bank_models.Bank.DoesNotExist:
#         logging.debug("این لینک معتبر نیست.")
#         raise Http404

#     if bank_record.is_success:
#         user = request.user

#         user.wallet.charge(bank_record.amount)

#         context = {
#             "success": True,
#             "message": "کیف شما به مبلغ شارژ شد",
#             "tc": tracking_code,
#             "btn_url": "apps.accounts:dashboard_financial",
#             "btn_title": "رفتن به کیف پول",
#         }
#         return render(request, "financial/payment_result.html", context=context)

#     context = {
#         "success": False,
#         "message": "پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.",
#         "tc": tracking_code,
#         "btn_url": "apps.accounts:dashboard_financial",
#         "btn_title": "رفتن به کیف پول",
#     }
#     return render(request, "financial/payment_result.html", context=context)


# # views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils import timezone
# from .models import PayoutRequest, CoachIncome, RefundRequest
# from .services import get_instructor_financials, create_payout_request, process_refund

# # --- پنل مربی ---


# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def instructor_dashboard(request):
#     financials = get_instructor_financials(request.user)

#     # دریافت تاریخچه نزدیک‌ترین ۵ درخواست
#     payouts = PayoutRequest.objects.filter(instructor=request.user).order_by(
#         "-created_at"
#     )[:5]

#     context = {
#         "financials": financials,
#         "payouts": payouts,
#         "refunds": RefundRequest.objects.filter(user=request.user).order_by(
#             "-created_at"
#         ),  # اگر مربی درخواستی می‌کند (اگر مربی دانشجو هم هست)
#     }
#     return render(request, "instructors/dashboard.html", context)


# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def request_payout(request):
#     if request.method == "POST":
#         try:
#             amount = float(request.POST.get("amount"))
#             bank_account = request.POST.get("bank_account")

#             result = create_payout_request(request.user, amount, bank_account)

#             if result.get("success"):
#                 messages.success(request, "درخواست تسویه با موفقیت ثبت شد.")
#                 return redirect("instructor_dashboard")
#             else:
#                 messages.error(request, result["error"])
#                 return redirect("instructor_dashboard")

#         except ValueError:
#             messages.error(request, "مبلغ وارد شده صحیح نیست.")

#     return redirect("instructor_dashboard")


# # --- پنل مدیریت (Admin) ---


# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def admin_financial_report(request):
#     # 1. داشبورد کلی
#     total_cleared = (
#         CoachIncome.objects.filter(status="cleared").aggregate(Sum("share_amount"))[
#             "share_amount__sum"
#         ]
#         or 0
#     )
#     total_paid = (
#         PayoutRequest.objects.filter(status="paid").aggregate(Sum("amount"))[
#             "amount__sum"
#         ]
#         or 0
#     )

#     # محاسبه بدهی به مربیان (موجودی تسویه نشده)
#     # فرمول: همه درآمدهای Cleared - (همه درآمدهای Refunded + همه درخواست‌های پرداخت شده)
#     # اما برای دقت بالا:
#     # بدهی = مجموع موجودی قابل برداشت برای تمام مربیان (که در ویوهای بالا محاسبه می‌شود)
#     # اینجا برای سادگی تقریبی:
#     pending_payouts = (
#         PayoutRequest.objects.filter(status__in=["pending", "approved"]).aggregate(
#             Sum("amount")
#         )["amount__sum"]
#         or 0
#     )

#     # گزارش ماهانه
#     monthly_data = (
#         CoachIncome.objects.filter(status="cleared")
#         .values("created_at__year", "created_at__month")
#         .annotate(total=Sum("share_amount"))
#         .order_by("-created_at__year", "-created_at__month")[:12]
#     )

#     # گزارش مربیان برتر
#     top_instructors = (
#         CoachIncome.objects.values("instructor__username")
#         .annotate(total=Sum("share_amount"))
#         .order_by("-total")[:10]
#     )

#     # درخواست‌های بازگشت وجه در انتظار
#     pending_refunds = RefundRequest.objects.filter(status="pending")

#     context = {
#         "total_cleared": total_cleared,
#         "total_paid": total_paid,
#         "pending_payouts": pending_payouts,
#         "monthly_data": monthly_data,
#         "top_instructors": top_instructors,
#         "pending_refunds": pending_refunds,
#     }
#     return render(request, "admin/financial_report.html", context)


# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def admin_payout_list(request):
#     payouts = PayoutRequest.objects.all().order_by("-created_at")
#     return render(request, "admin/payout_list.html", {"payouts": payouts})


# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def approve_payout(request, pk):
#     if request.method == "POST":
#         payout = get_object_or_404(PayoutRequest, pk=pk)
#         payout.status = "approved"
#         payout.save()
#         messages.success(request, f"درخواست {payout.id} تایید شد.")
#         return redirect("admin_payout_list")
#     return redirect("admin_payout_list")


# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def mark_payout_paid(request, pk):
#     if request.method == "POST":
#         payout = get_object_or_404(PayoutRequest, pk=pk)
#         payout.status = "paid"
#         payout.transaction_id = request.POST.get("tx_id")
#         payout.payment_date = timezone.now()
#         payout.save()
#         messages.success(request, "پرداخت ثبت شد.")
#         return redirect("admin_payout_list")
#     return redirect("admin_payout_list")


# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def process_refund(request, pk):
#     if request.method == "POST":
#         try:
#             process_refund(pk)
#             messages.success(request, "بازگشت وجه با موفقیت انجام شد.")
#         except Exception as e:
#             messages.error(request, f"خطا در پردازش بازگشت وجه: {str(e)}")
#         return redirect("admin_financial_report")
#     return redirect("admin_financial_report")


class PayoutService:
    @staticmethod
    @transaction.atomic
    def create_payout(coach, amount, bank_details):
        """
        ایجاد درخواست تسویه حساب:
        1. بررسی موجودی کافی.
        2. انتخاب درآمدهای 'ready' (به ترتیب قدیمی‌ترین اولویت - FIFO یا LIFO).
        3. قفل کردن این درآمدها (change status to 'locked').
        4. ایجاد رکورد Payout و ذخیره IDهای مربوطه.
        """
        # 1. انتخاب و قفل کردن درآمدها
        # با select_for_update(skip_locked=True) از همزمانی جلوگیری می‌کنیم
        available_incomes = (
            CoachIncome.objects.filter(coach=coach, status="b")
            .select_for_update(skip_locked=True)
            .order_by("created_at")
        )

        selected_incomes = []
        total_amount = 0
        income_ids = []

        # پیمایش و انتخاب تا رسیدن به مبلغ درخواستی
        for income in available_incomes:
            selected_incomes.append(income)
            income_ids.append(income.id)
            total_amount += income.amount

            if total_amount >= amount:
                break

        # اعتبارسنجی: اگر موجودی کافی نبود
        if total_amount < amount - 0.01:  # با کمی دقت اعشاری
            raise ValidationError(
                f"موجودی کافی نیست. موجودی فعلی: {total_amount}, درخواست: {amount}"
            )

        # 2. قفل کردن وضعیت درآمدها در دیتابیس
        CoachIncome.objects.filter(id__in=income_ids).update(
            status="b", locked_at=timezone.now()
        )

        # 3. ایجاد رکورد تسویه
        payout = Payout.objects.create(
            coach=coach,
            amount=amount,
            bank=bank,
            income_ids=income_ids,
            status="b",
        )

        # بازگشت اطلاعات برای استفاده در UI یا تسک‌ها
        return {
            "payout": payout,
            "total_amount": total_amount,
            "income_count": len(income_ids),
        }

    @staticmethod
    @transaction.atomic
    def process_payout_success(payout_id, bank_ref):
        """
        وقتی پرداخت بانکی موفقیت‌آمیز بود:
        1. تغییر وضعیت Payout به 'paid'.
        2. تغییر وضعیت درآمدهای مرتبط به 'withdrawn'.
        """
        payout = Payout.objects.select_for_update().get(
            id=payout_id, status__in=["pending", "processing"]
        )

        if payout.status == "paid":
            return  # قبلا پرداخت شده

        # ثبت موفقیت تراکنش بانکی
        payout.status = "paid"
        payout.bank_transaction_ref = bank_ref
        payout.processed_at = timezone.now()
        payout.save()

        # تغییر وضعیت درآمدها
        if payout.income_ids:
            CoachIncome.objects.filter(
                id__in=payout.income_ids,
                status="locked",  # فقط اگر هنوز قفل هستند تغییر دهند (برای ایمنی بیشتر)
            ).update(status="withdrawn", withdrawn_at=timezone.now())

        return payout

    @staticmethod
    @transaction.atomic
    def process_payout_failure(payout_id, error_msg):
        """
        وقتی پرداخت ناموفق بود:
        1. تغییر وضعیت Payout به 'failed'.
        2. بازگرداندن وضعیت درآمدها به 'ready' (تا کاربر دوباره درخواست دهد).
        """
        payout = Payout.objects.select_for_update().get(id=payout_id)

        payout.status = "failed"
        payout.error_message = error_msg
        payout.save()

        if payout.income_ids:
            CoachIncome.objects.filter(
                id__in=payout.income_ids, status="locked"
            ).update(status="ready", locked_at=None)

        return payout
