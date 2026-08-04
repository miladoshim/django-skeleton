from django.contrib import admin
from django import forms
from django.db import models
from django.utils import timezone
from image_uploader_widget.widgets import ImageUploaderWidget
from import_export.admin import ImportExportModelAdmin
from .models import Banner, Bookmark, NewsletterSubscriber, Skill, TopBarTimerMessage


class BaseAdminMixin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    empty_value_display = "---"
    search_fields = ["title"]
    list_display_links = ["id", "title"]
    list_filter = ["created_at", "is_deleted"]
    formfield_overrides = {
        models.ImageField: {"widget": ImageUploaderWidget},
    }

    def save_model(self, request, obj, form, change):
        if hasattr("obj", "author"):
            obj.author = request.user
        return super().save_model(request, obj, form, change)


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


@admin.register(Skill)
class SkillAdmin(ImportExportModelAdmin):
    list_display = ["id", "title", "created_at"]
    date_hierarchy = "created_at"
    search_fields = ["title"]
    list_display_links = ["id", "title"]
    prepopulated_fields = {"slug": ["title"]}
    empty_value_display = "---"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ImportExportModelAdmin):
    list_display = ["id", "email", "created_at"]
    date_hierarchy = "created_at"
    search_fields = ("email",)
    list_display_links = ["id", "email"]
    empty_value_display = "---"


class BannerAdminForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = "__all__"
        widgets = {
            "image": forms.FileInput(
                attrs={
                    "class": "upload-field",
                    "accept": "image/*",
                }
            ),
        }


@admin.register(Banner)
class BannerAdmin(ImportExportModelAdmin):
    list_display = ["id", "title", "section", "link", "created_at"]
    date_hierarchy = "created_at"
    search_fields = ["title"]
    list_display_links = ["id", "title", "link"]
    prepopulated_fields = {"slug": ["title"]}
    empty_value_display = "---"
    form = BannerAdminForm

    class Media:
        css = {"all": ("admin/css/upload_progress.css",)}
        js = ("admin/js/upload_progress.js",)


@admin.register(TopBarTimerMessage)
class TopBarTimerMessageAdmin(ImportExportModelAdmin):
    list_display = ["id", "message", "link_text", "link", "created_at"]
    date_hierarchy = "created_at"
    search_fields = ("message",)
    list_display_links = ["id", "message"]
    empty_value_display = "---"


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "content_type", "object_id", "created_at"]
    list_filter = ["content_type", "created_at"]
    search_fields = ["user__mobile"]
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "content_type")
