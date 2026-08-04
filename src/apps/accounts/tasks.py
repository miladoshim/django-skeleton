from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from celery import shared_task
from apps.core.services.sms_service import Kavenegar
from .models import OtpRequest, User


@shared_task
def users_count():
    count = User.objects.count()
    return f"Count of Users: {count}"


@shared_task(bind=True, max_retries=3)
def send_welcome_message(receiver: str):
    new_user = User.objects.filter("username" == receiver)
    pass


@shared_task(bind=True, max_retries=3)
def send_login_message(receiver: str):
    User.objects.get(mobile=receiver)


@shared_task
def send_password_changed_message(receiver: str):
    pass


@shared_task
def delete_user_account():
    try:
        pass
    except Exception as e:
        pass


@shared_task(bind=True)
def send_otp_password(self, receiver: str, otp: str):
    try:
        Kavenegar.send_otp(receptor=receiver, otp=otp)
    except Exception as exc:
        print(f"Exception : {str(exc)}")
        raise self.retry(exc, countdown=5)


@shared_task
def cleanup_expired_otp_requests():
    now = timezone.now()

    query = Q(expired_at__lt=now) | Q(created_at__lt=now - timedelta(days=7))

    deleted_count = OtpRequest.objects.filter(query).delete()[0]

    if deleted_count:
        print(f"🧹 {deleted_count} OTP قدیمی پاکسازی شد")

    return deleted_count


@shared_task
def cleanup_inactive_users():
    now = timezone.now()

    query = Q(is_active=False | Q(created_at__lt=now - timedelta(days=1)))

    deleted_count = User.objects.filter(query).delete()[0]

    if deleted_count:
        print(f"🧹 deleted inactive and not registered users.")

    return deleted_count
