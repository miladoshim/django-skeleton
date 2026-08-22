import os
import json
from django.core.management.base import BaseCommand

from apps.pages.models import ContactUsSubject


class Command(BaseCommand):
    help = "Seed initial data into the database"

    def handle(self, *args, **kwargs):
        contact_subjects_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/contact_subjects.json"
        )

        with open(
            contact_subjects_path, encoding="utf-8", errors="ignore"
        ) as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(
                self.style.SUCCESS("Contact us Subject seeding file Loaded.....")
            )

            for item in data:
                obj, created = ContactUsSubject.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "title": item["title"],
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Contact us Subject: {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated Contact us Subject: {obj.title}")
                    )

            self.stdout.write(
                self.style.SUCCESS("Contact us Subject seeding completed.")
            )
