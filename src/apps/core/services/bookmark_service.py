# apps/common/services/bookmark_service.py
from django.contrib.contenttypes.models import ContentType

from apps.core.models import Bookmark


class BookmarkService:
    def __init__(self, user):
        self.user = user

    def toggle(self, obj, note=""):
        ct = ContentType.objects.get_for_model(obj)
        bm, created = Bookmark.objects.get_or_create(
            user=self.user,
            content_type=ct,
            object_id=obj.id,
            defaults={"note": note},
        )
        if not created:
            bm.delete()
        return {
            "bookmarked": created,
            "message": "ذخیره شد" if created else "حذف شد",
        }

    def is_bookmarked(self, obj):
        if not self.user.is_authenticated:
            return False

        return self.user.bookmarks.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).exists()

    def get_bookmarked_ids(self, model_class):
        ct = ContentType.objects.get_for_model(model_class)
        return self.user.bookmarks.filter(content_type=ct).values_list(
            "object_id", flat=True
        )

    def get_all(self, model_class):
        ct = ContentType.objects.get_for_model(model_class)
        return self.user.bookmarks.filter(content_type=ct).select_related(
            "content_object"
        )

    @staticmethod
    def get_user_bookmarks(user, model_class=None):
        """دریافت بوکمارک‌های کاربر"""
        bookmarks = Bookmark.objects.filter(user=user)

        if model_class:
            content_type = ContentType.objects.get_for_model(model_class)
            bookmarks = bookmarks.filter(content_type=content_type)

        return bookmarks.select_related("content_type")

    def update_note(self, obj, note):
        ct = ContentType.objects.get_for_model(obj)
        updated = Bookmark.objects.filter(
            user=self.user,
            content_type=ct,
            object_id=obj.id,
        ).update(note=note)
        return updated > 0
