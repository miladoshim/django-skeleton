from django.core.management.base import BaseCommand
from apps.accounts.tasks import cleanup_expired_otp_requests


class Command(BaseCommand):
    help = "Cleanup OTP"

    def handle(self, *args, **options):
        result = cleanup_expired_otp_requests()
        self.stdout.write(self.style.SUCCESS(f"{result} otp request delete."))
