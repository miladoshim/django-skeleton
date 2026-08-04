from django.db import transaction
from django.utils import timezone
from celery import shared_task
from .models import CoachIncome, CoachIncomeStatus


@shared_task
def check_available_pending_incomes():
    today = timezone.now().date()

    to_available_incomes = CoachIncome.objects.filter(
        status=CoachIncomeStatus.PENDING,
        available_date__lte=today,
    )

    if not to_available_incomes.exists():
        return f"No incomes due for payment on {today}."

    with transaction.atomic():
        to_available_incomes.update(status=CoachIncomeStatus.AVAILABLE)

        return f"{to_available_incomes.count()} درآمد جدید به حالت 'قابل برداشت' درآمد."


@shared_task
def send_new_income_to_coach_notification(coach, course, amount: int):
    print(
        f"new income for coach {coach.get_full_name} - course {course.title} - amount {amount}"
    )


# @shared_task
# def cleanup_rejected_payouts():
#     """
#     اختیاری: حذف یا علامت‌گذاری درخواست‌های رد شده یا منقضی شده (اگر نیاز به سیاست زمان‌دار دارید)
#     """
#     pass


# @shared_task
# def process_payout_queue():
#     """
#     این وظیفه تسویه‌ها را به صورت خودکار یا دستی (بر اساس CRON) پردازش می‌کند.
#     """
#     pending_payouts = Payout.objects.filter(
#         status=PayoutStatus.PENDING
#     )  # یا PROCESSING

#     for payout in pending_payouts[:10]:  # پردازش گره به گره برای جلوگیری از بار سنگین
#         try:
#             # 1. بررسی اعتبار درخواست
#             if not payout.can_be_paid:
#                 payout.status = PayoutStatus.CANCELLED
#                 payout.error_message = "شرایط پرداخت برقرار نیست."
#                 payout.save()
#                 continue

#             # 2. شبیه‌سازی یا انجام تراکنش بانکی (به API شاپرک درخواست بفرستید)
#             # result = banking_api.transfer(payout.bank_account, payout.amount)

#             # فرض کنید تراکنش موفق بود:
#             # if result.success:
#             #    payout.status = PayoutStatus.PAID
#             #    payout.bank_transaction_ref = result.ref_id
#             # else:
#             #    payout.status = PayoutStatus.FAILED
#             #    payout.error_message = result.message

#             # اینجا برای تست فرض می‌کنیم موفق است:
#             payout.status = PayoutStatus.PAID
#             payout.bank_transaction_ref = (
#                 f"TRX-{payout.id}-{timezone.now().timestamp()}"
#             )
#             payout.processed_at = timezone.now()
#             payout.save()

#             # 3. آزاد کردن درآمدهای قفل شده
#             from .models import CoachIncome

#             # پیدا کردن درآمدهایی که مربوط به این تسویه هستند و تغییر وضعیتشون
#             # این بخش پیچیده است و باید دقیقاً نگه دارید که کدام incomed قفل شده‌اند.
#             # برای سادگی اینجا فرض می‌کنیم همه با وضعیت LOCKED آزاد و با وضعیت بازنشسته (WITHDRAWN) شوند.
#             # در واقعیت باید Mapping دقیق داشته باشید.

#         except Exception as e:
#             payout.status = PayoutStatus.FAILED
#             payout.error_message = str(e)
#             payout.save()
#             continue


# @shared_task
# def handle_bank_webhook(payout_id, success=True, bank_ref=None, error_msg=None):
#     """
#     این تاسک توسط وب‌هوک بانک یا سیستم بررسی روزانه فراخوانی می‌شود.
#     """
#     try:
#         if success:
#             # اگر پرداخت موفق بود
#             PayoutService.process_payout_success(payout_id, bank_ref)
#             return f"Payout #{payout_id} processed successfully."
#         else:
#             # اگر پرداخت شکست خورد
#             PayoutService.process_payout_failure(payout_id, error_msg)
#             return f"Payout #{payout_id} failed: {error_msg}"

#     except Exception as e:
#         # اگر خود سرویس خطا داد، بهتر است لاگ کنیم تا تاسک تکرار نشود یا تکرار شود
#         return f"Error processing payout {payout_id}: {str(e)}"
