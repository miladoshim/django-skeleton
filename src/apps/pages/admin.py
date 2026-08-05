from django.contrib import admin
from apps.pages.models import (
    ContactUsSubject,
    ContactUs,
    Faq,
    FaqGroup,
)


@admin.register(ContactUs)
class ContactModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "name",
        "mobile",
        "message",
        "created_at",
    )
    list_display_links = (
        "id",
        "name",
        "mobile",
    )
    search_fields = (
        "name",
        "mobile",
    )
    empty_value_display = "---"
    list_select_related = ("subject",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=...):
        return False


@admin.register(ContactUsSubject)
class ContactSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "created_at",
    )
    list_display_links = (
        "id",
        "title",
    )
    search_fields = ("title",)
    empty_value_display = "---"


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ["id", "question", "group", "created_at"]
    list_display_links = ["id", "question"]
    search_fields = ["question", "group"]
    autocomplete_fields = ("group",)
    list_filter = ("group",)
    list_select_related = ("group",)
    empty_value_display = "---"


@admin.register(FaqGroup)
class FaqGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "created_at"]
    list_display_links = (
        "id",
        "title",
    )
    search_fields = ("title",)
    empty_value_display = "---"
