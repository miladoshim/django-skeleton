from django.conf import settings
from django.db import models
from django.utils import timezone
from .managers import SoftDeleteManager

User = settings.AUTH_USER_MODEL


class SoftDeleteModelMixin:
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    restored_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        related_name="deleted_%(class)s_objects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="حذف شده توسط",
    )

    objects = SoftDeleteManager()

    def delete(self, using=None, keep_parents=False, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user and user.is_authenticated:
            self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.is_deleted = False
        self.restored_at = timezone.now()
        self.deleted_at = None
        self.deleted_by = None
        self.save(
            update_fields=[
                "is_deleted",
                "restored_at",
                "deleted_at",
                "deleted_by",
            ]
        )
