import os
import json
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.coaching.models import CoachingPlan
from apps.financial.models import IrBank
from apps.pages.models import ContactSubject
from apps.shop.models import (
    ProductAttribute,
    ProductAttributeGroup,
    ProductUnit,
    Shipping,
)


class Command(BaseCommand):
    help = "Seed initial data into the database"

    def handle(self, *args, **kwargs):
        banks_path = os.path.dirname(os.path.abspath(__file__)) + "/banks.json"
        # brands_path = os.path.dirname(os.path.abspath(__file__)) + "/brands.json"
        coaching_plans_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/coaching_plans.json"
        )
        contact_subjects_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/contact_subjects.json"
        )

        product_attribute_group_path = (
            os.path.dirname(os.path.abspath(__file__))
            + "/product_attribute_groups.json"
        )
        product_attributes_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/product_attributes.json"
        )
        product_unit_path = (
            os.path.dirname(os.path.abspath(__file__)) + "/product_unit.json"
        )
        shippings_path = os.path.dirname(os.path.abspath(__file__)) + "/shippings.json"

        with open(banks_path, encoding="utf-8", errors="ignore") as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(self.style.SUCCESS("Bank seeding file Loaded....."))

            for item in data:
                obj, created = IrBank.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "title": item["title"],
                        "logo": item["logo"],
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created irbank: {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated irbank: {obj.title}")
                    )

            self.stdout.write(self.style.SUCCESS("Bank seeding completed."))

            with open(
                product_attribute_group_path, encoding="utf-8", errors="ignore"
            ) as json_data:
                data = json.load(json_data, strict=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Product Attribute Group seeding file Loaded....."
                    )
                )

                for item in data:
                    obj, created = ProductAttributeGroup.objects.update_or_create(
                        title=item["title"],
                        defaults={
                            "id": item["id"],
                            "title": item["title"],
                            "slug": slugify(item["title"], allow_unicode=True),
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created Product Attribute Group: {obj.title}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Updated Product Attribute Group: {obj.title}"
                            )
                        )

                self.stdout.write(
                    self.style.SUCCESS("Product Attribute Group seeding completed.")
                )

        with open(
            contact_subjects_path, encoding="utf-8", errors="ignore"
        ) as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(
                self.style.SUCCESS("Contact us Subject seeding file Loaded.....")
            )

            for item in data:
                obj, created = ContactSubject.objects.update_or_create(
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

        with open(
            product_attributes_path, encoding="utf-8", errors="ignore"
        ) as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(
                self.style.SUCCESS("Product Attribute  seeding file Loaded.....")
            )

            for item in data:
                obj, created = ProductAttribute.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "group_id": ProductAttributeGroup.objects.first().id,
                        "title": item["title"],
                        "slug": slugify(item["title"], allow_unicode=True),
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Product Attribute : {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated Product Attribute : {obj.title}")
                    )

            self.stdout.write(
                self.style.SUCCESS("Product Attribute  seeding completed.")
            )

        with open(product_unit_path, encoding="utf-8", errors="ignore") as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(
                self.style.SUCCESS("ProductUnit seeding file Loaded.....")
            )

            for item in data:
                obj, created = ProductUnit.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "title": item["title"],
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Product Unit: {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated Product Unit: {obj.title}")
                    )

            self.stdout.write(self.style.SUCCESS("Product Unit seeding completed."))

        with open(shippings_path, encoding="utf-8", errors="ignore") as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(self.style.SUCCESS("Shipping seeding file Loaded....."))

            for item in data:
                obj, created = Shipping.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "title": item["title"],
                        "price": item["price"],
                        "description": item["description"],
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Shipping: {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated Shipping: {obj.title}")
                    )

            self.stdout.write(self.style.SUCCESS("Shipping seeding completed."))

        with open(coaching_plans_path, encoding="utf-8", errors="ignore") as json_data:
            data = json.load(json_data, strict=False)
            self.stdout.write(
                self.style.SUCCESS("Coaching plan seeding file Loaded.....")
            )

            for item in data:
                obj, created = CoachingPlan.objects.update_or_create(
                    title=item["title"],
                    defaults={
                        "title": item["title"],
                        "original_price": item["original_price"],
                        "discount_price": item["discount_price"],
                        "short_description": item["short_description"],
                        "is_preferred": item["is_preferred"],
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Created Coaching plan: {obj.title}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Updated Coaching plan: {obj.title}")
                    )

            self.stdout.write(self.style.SUCCESS("Coaching plan seeding completed."))
