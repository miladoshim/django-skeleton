from django.contrib import admin
from django import forms
from django.db import models
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from jalali_date import datetime2jalali


class BaseAdminMixin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    empty_value_display = "---"
    search_fields = ["title"]
    list_display_links = ["id", "title"]
    list_filter = ["created_at", "is_deleted"]

    def save_model(self, request, obj, form, change):
        if hasattr("obj", "author"):
            obj.author = request.user
        return super().save_model(request, obj, form, change)

    @admin.display(description="تاریخ ایجاد", ordering="created_at")
    def get_created_at(self, obj):
        return datetime2jalali(obj.created_at).strftime("%Y/%m/%d _ %H:%M:%S")

    @admin.display(description="تاریخ بروزرسانی", ordering="updated_at")
    def get_updated_at(self, obj):
        return datetime2jalali(obj.updated_at).strftime("%Y/%m/%d _ %H:%M:%S")


class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ("is_deleted",)
    actions = ["soft_delete", "restore", "hard_delete"]

    def get_queryset(self, request):
        return self.model.objects.all_objects()

    @admin.action(description="Soft delete selected items")
    def soft_delete(self, request, queryset):
        queryset.update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=request.user if request.user.is_authenticated else None,
        )

    @admin.action(description="Restore selected items")
    def restore(self, request, queryset):
        queryset.update(is_deleted=False, deleted_at=None, deleted_by=None)

    @admin.action(description="Hard delete selected items (permanent)")
    def hard_delete(self, request, queryset):
        queryset.hard_delete()


# @admin.register(NewsletterSubscriber)
# class NewsletterSubscriberAdmin(ImportExportModelAdmin):
#     list_display = ["id", "email", "created_at"]
#     date_hierarchy = "created_at"
#     search_fields = ("email",)
#     list_display_links = ["id", "email"]
#     empty_value_display = "---"


# class BannerAdminForm(forms.ModelForm):
#     class Meta:
#         model = Banner
#         fields = "__all__"
#         widgets = {
#             "image": forms.FileInput(
#                 attrs={
#                     "class": "upload-field",
#                     "accept": "image/*",
#                 }
#             ),
#         }


# @admin.register(Banner)
# class BannerAdmin(ImportExportModelAdmin):
#     list_display = ["id", "title", "section", "link", "created_at"]
#     date_hierarchy = "created_at"
#     search_fields = ["title"]
#     list_display_links = ["id", "title", "link"]
#     prepopulated_fields = {"slug": ["title"]}
#     empty_value_display = "---"
#     form = BannerAdminForm

#     class Media:
#         css = {"all": ("admin/css/upload_progress.css",)}
#         js = ("admin/js/upload_progress.js",)


# @admin.register(Bookmark)
# class BookmarkAdmin(admin.ModelAdmin):
#     list_display = ["user", "content_type", "object_id", "created_at"]
#     list_filter = ["content_type", "created_at"]
#     search_fields = ["user__mobile"]
#     date_hierarchy = "created_at"

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related("user", "content_type")
