from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.core.exceptions import ValidationError
from .models import (
    CoachIncomeStatus,
    Payout,
    PayoutStatus,
    UserGiftCodeUsed,
    Wallet,
    CoachIncome,
)


def create_coach_income(course, payment):
    available_date = timezone.now().date().__add__(timezone.timedelta(minutes=5))
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
        )
        .select_for_update(skip_locked=True)
        .order_by("created_at")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )


def get_available_coach_income_ids(coach):
    return list(
        CoachIncome.objects.filter(
            coach=coach,
            status=CoachIncomeStatus.AVAILABLE,
            available_date__lte=timezone.now().date(),
        ).values_list("id", flat=True)
    )


def create_coach_payout_request(user, bank, available_balance, income_for_payout_ids):
    with transaction.atomic():
        CoachIncome.objects.filter(id__in=income_for_payout_ids).update(
            status=CoachIncomeStatus.LOCKED,
            locked_at=timezone.now(),
        )

        return Payout.objects.create(
            user=user,
            bank=bank,
            amount=available_balance,
            income_ids=income_for_payout_ids,
        )


def get_paid_payouts(coach) -> int:
    return (
        Payout.objects.filter(
            user=coach,
            status=PayoutStatus.PAID,
        )
        .select_for_update(skip_locked=True)
        .order_by("created_at")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )


def get_pending_payouts(coach) -> int:
    filters = (
        Q(user=coach)
        and Q(status=PayoutStatus.PENDING)
        or Q(status=PayoutStatus.PROCESSING)
    )
    return (
        Payout.objects.filter(filters)
        .select_for_update(skip_locked=True)
        .order_by("created_at")
        .aggregate(total=Sum("amount"))["total"]
        or 0
    )


def giftcode_check_can_use(giftcode) -> bool:
    if giftcode.infinity:
        return True

    if giftcode.count_use == 0:
        return False
    else:
        return True


def giftcode_create_user_used(giftcode, user):
    return UserGiftCodeUsed.objects.create(user=user, gift_code=giftcode)


def giftcode_check_user_used(giftcode, user) -> bool:
    if UserGiftCodeUsed.objects.filter(user=user, gift_code=giftcode).exists():
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
            CoachIncome.objects.filter(
                coach=coach,
                status=CoachIncomeStatus.AVAILABLE,
            )
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
            status=CoachIncomeStatus.LOCKED,
            locked_at=timezone.now(),
        )

        # 3. ایجاد رکورد تسویه
        payout = Payout.objects.create(
            coach=coach,
            amount=amount,
            bank=bank,
            income_ids=income_ids,
            status=PayoutStatus.PROCESSING,
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
                status=CoachIncomeStatus.LOCKED,  # فقط اگر هنوز قفل هستند تغییر دهند (برای ایمنی بیشتر)
            ).update(
                status=CoachIncomeStatus.WITHDRAWN,
                withdrawn_at=timezone.now(),
            )

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
                id__in=payout.income_ids,
                status=CoachIncomeStatus.LOCKED,
            ).update(
                status="ready",
                locked_at=None,
            )

        return payout
