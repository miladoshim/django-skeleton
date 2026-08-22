import uuid
from django.utils import timezone


def thumbnail_path(instance, filename, prefix="posts"):
    ext = filename.split(".")[-1]
    new_filename = f"{uuid.uuid4().hex[:16]}.{ext}"
    new_filename = f"{uuid.uuid4().hex[:16]}_{timezone.now().strftime('%Y%m%d')}.{ext}"

    return f"{prefix}/{instance.id}/thumbnails/{new_filename}"


def user_avatar_path(instance, filename):
    return f"users/user_{instance.user.id}/avatars/{filename}"


def user_banner_path(instance, filename):
    return f"users/user_{instance.user.id}/banners/{filename}"


def category_icon_path(instance, filename):
    return f"categories/icons/{filename}"
