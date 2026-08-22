from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone

from apps.core.models import Bookmark, Comment, Like
from .managers import SoftDeleteManager

User = settings.AUTH_USER_MODEL


class LikeableMixin(models.Model):
    likes = GenericRelation(Like)

    class Meta:
        abstract = True

    @property
    def likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class BookmarkableMixin(models.Model):
    bookmarks = GenericRelation(Bookmark)

    class Meta:
        abstract = True

    @property
    def bookmarks_count(self):
        return self.bookmarks.count()

    def is_bookmarked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.bookmarks.filter(user=user).exists()


class CommentableMixin(models.Model):
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True
