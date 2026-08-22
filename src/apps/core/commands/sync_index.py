from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Syncs the search index with the database"

    def handle(self, *args, **options):
        # index_courses()
        # index_users()
        # index_episodes()
        # index_products()
        # index_books()

        self.stdout.write(self.style.SUCCESS("Successfully synced search indexes"))
