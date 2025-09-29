from django.db.models import QuerySet, Manager, Q
from django.utils import timezone

class PublishedManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super(PublishedManager, self).get_queryset().filter(published_status='p')

class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

class SoftDeleteManager(Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, self._db).filter(Q(is_deleted=False) | Q(is_deleted__isnull=True))
