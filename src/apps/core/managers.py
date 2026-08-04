from django.db.models import Manager, QuerySet
from django.utils import timezone
from utils.enums import PublishStatusChoice


class PublishedManager(Manager):
    def get_queryset(self) -> QuerySet:
        return (
            super(PublishedManager, self)
            .get_queryset()
            .filter(published_status=PublishStatusChoice.PUBLISHED)
        )


class CommentQuerySet(QuerySet):
    def filter_approved(self):
        return self.filter(is_approved=True)

    def filter_not_approved(self):
        return self.filter(is_approved=False)

    def filter_parents(self):
        return self.filter(parent__isnull=True)

    def order_newest(self):
        return self.order_by("-created_at")

    def order_oldest(self):
        return self.order_by("created_at")


class CommentManager(Manager):
    def get_queryset(self) -> QuerySet:
        return CommentQuerySet(self.model, self._db)


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(Manager):
    def get_queryset(self) -> QuerySet:
        return SoftDeleteQuerySet(self.model, self._db).alive()

    def all_objects(self) -> QuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_objects(self):
        return self.all_objects().dead()
