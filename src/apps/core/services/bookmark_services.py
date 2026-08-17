# # apps/bookmarks/services.py
# from django.contrib.contenttypes.models import ContentType
# # from apps.core.models import Bookmark


from apps.core.services.base_service import BaseService


class BookmarkService(BaseService):
    pass


#     @staticmethod
#     def toggle(user, obj):
#         """تغییر وضعیت بوکمارک (افزودن/حذف)"""
#         content_type = ContentType.objects.get_for_model(obj)
#         bookmark, created = Bookmark.objects.get_or_create(
#             user=user, content_type=content_type, object_id=obj.id
#         )

#         if not created:
#             bookmark.delete()
#             return False  # حذف شد
#         return True  # اضافه شد

#     @staticmethod
#     def is_bookmarked(user, obj):
#         """بررسی بوکمارک شده بودن"""
#         if not user.is_authenticated:
#             return False
#         content_type = ContentType.objects.get_for_model(obj)
#         return Bookmark.objects.filter(
#             user=user, content_type=content_type, object_id=obj.id
#         ).exists()

#     @staticmethod
#     def get_user_bookmarks(user, model_class=None):
#         """دریافت بوکمارک‌های کاربر"""
#         bookmarks = Bookmark.objects.filter(user=user)

#         if model_class:
#             content_type = ContentType.objects.get_for_model(model_class)
#             bookmarks = bookmarks.filter(content_type=content_type)

#         return bookmarks.select_related("content_type")


# def _get_ct(model_or_instance):
#     if not model_or_instance:
#         raise ValueError("model_or_instance is required")
#     if isinstance(model_or_instance, type):
#         return ContentType.objects.get_for_model(model_or_instance)
#     return ContentType.objects.get_for_model(model_or_instance.__class__)


# def toggle_bookmark(user, obj):
#     """
#     اگر وجود داشته باشد حذف می‌کند، اگر نباشد ایجاد می‌کند.
#     خروجی: (bookmark_instance or None, created: bool)
#     """
#     ct = _get_ct(obj)
#     bookmark, created = Bookmark.objects.get_or_create(
#         user=user,
#         content_type=ct,
#         object_id=obj.pk,
#     )
#     if not created:
#         bookmark.delete()
#         return None, False
#     return bookmark, True


# def is_bookmarked(user, obj) -> bool:
#     if not user.is_authenticated:
#         return False
#     ct = _get_ct(obj)
#     return Bookmark.objects.filter(
#         user=user,
#         content_type=ct,
#         object_id=obj.pk,
#     ).exists()


# def list_bookmarks_for_model(user, model):
#     """
#     لیست بوکمارک‌های یک مدل خاص (مثلاً Course) برای یک کاربر
#     """
#     ct = _get_ct(model)
#     return Bookmark.objects.filter(user=user, content_type=ct).select_related(
#         "content_type"
#     )
