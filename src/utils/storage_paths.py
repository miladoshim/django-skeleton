import uuid
from django.utils import timezone


def thumbnail_path(instance, filename, prefix="courses"):
    ext = filename.split(".")[-1]
    new_filename = f"{uuid.uuid4().hex[:16]}.{ext}"
    return f"{prefix}/{instance.id}/thumbnails/{new_filename}"


def upload_to_course_video(instance, filename):
    ext = filename.split(".")[-1]
    new_filename = f"{uuid.uuid4().hex[:16]}_{timezone.now().strftime('%Y%m%d')}.{ext}"
    return f"courses/{instance.course.id}/videos/{new_filename}"


def user_directory_path(instance, filename):
    """
    Generate upload path based on user ID.
    Files will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    """
    return f"user_{instance.user.id}/{filename}"
