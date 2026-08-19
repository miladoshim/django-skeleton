from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class PublicNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_display_links = ["id"]
    empty_value_display = "---"
