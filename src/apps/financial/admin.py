from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Payment,
)


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    list_display = [
        "id",
        "user",
        "tracking_code",
        "final_amount",
        "payment_method",
        "payment_for",
        "result__status",
    ]
    list_display_links = (
        "id",
        "user",
    )
    empty_value_display = "---"
    date_hierarchy = "created_at"
    search_fields = (
        "user",
        "tracking_code",
    )
