from django.core.management.base import BaseCommand
from apps.accounts.tasks import cleanup_inactive_users


class Command(BaseCommand):
    help = "Deleting inactive users"

    def handle(self, *args, **options):
        result = cleanup_inactive_users()
        self.stdout.write(self.style.SUCCESS(f"inactive users cleared."))
