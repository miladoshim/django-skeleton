# apps/common/services/like_service.py
from django.contrib.contenttypes.models import ContentType

from apps.core.models import Like


class LikeService:

    def __init__(self, user):
        self.user = user

    def toggle(self, obj):
        ct = ContentType.objects.get_for_model(obj)
        like, created = Like.objects.get_or_create(
            user=self.user,
            content_type=ct,
            object_id=obj.id,
        )
        if not created:
            like.delete()
        return {
            "liked": created,
            "count": self._count(obj),
        }

    def is_liked(self, obj):
        return self.user.likes.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).exists()

    def get_liked_ids(self, model_class):
        ct = ContentType.objects.get_for_model(model_class)
        return self.user.likes.filter(content_type=ct).values_list(
            "object_id", flat=True
        )

    def _count(self, obj):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).count()
