import datetime
import readtime
from django.db.models.aggregates import Count
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.functional import cached_property
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from hitcount.models import HitCountMixin
from hitcount.settings import MODEL_HITCOUNT
from taggit_selectize.managers import TaggableManager
from treebeard.mp_tree import MP_Node
from apps.core.managers import PublishedManager
from apps.core.mixins import BookmarkableMixin, CommentableMixin, LikeableMixin
from apps.core.models import BaseModel
from utils.enums import PublishStatusChoice
from utils.storage_paths import category_icon_path, thumbnail_path

User = get_user_model()


class Category(MP_Node):
    parent = models.ForeignKey(
        "self",
        verbose_name="دسته بندی والد",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="نامک",
        allow_unicode=True,
        help_text="به صورت خودکار ایجاد می شود!",
    )
    description = models.TextField(
        blank=True,
        null=True,
        max_length=2048,
        verbose_name="توضیحات",
    )
    icon = models.ImageField(
        verbose_name="آیکون",
        null=True,
        blank=True,
        upload_to=category_icon_path,
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="دسته بندی فعال باشد?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "دسته بندی"
        verbose_name_plural = "دسته بندی ها"

    def __str__(self) -> str:
        return self.name

    def icon_tag(self):
        return format_html("<img width=30 src='{}' />".format(self.icon.url))

    def get_absolute_url(self):
        return reverse("apps.blog:category_detail", args=[str(self.slug)])


class Post(
    BaseModel,
    HitCountMixin,
    LikeableMixin,
    BookmarkableMixin,
    CommentableMixin,
):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="نویسنده",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="دسته بندی",
        on_delete=models.PROTECT,
        related_name="posts",
    )
    title = models.CharField(
        "عنوان مقاله",
        max_length=255,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="نامک",
        allow_unicode=True,
        default=None,
    )
    short_description = models.TextField(
        "توضیحات کوتاه",
        max_length=255,
    )
    body = models.TextField("متن مقاله")
    thumbnail = models.ImageField(
        upload_to=thumbnail_path,
        verbose_name="تصویر شاخص",
    )
    published_status = models.PositiveSmallIntegerField(
        choices=PublishStatusChoice.choices,
        default=PublishStatusChoice.DRAFT,
        verbose_name="وضعیت انتشار",
    )
    published_at = models.DateTimeField(
        verbose_name="تاریخ انتشار",
        blank=True,
        null=True,
    )
    tags = TaggableManager(
        verbose_name="برچسب ها",
        related_name="tags",
    )
    hit_count_generic = GenericRelation(
        MODEL_HITCOUNT,
        object_id_field="object_pk",
        related_query_name="hit_count_generic_relation",
    )

    objects = models.Manager()
    published = PublishedManager()

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url

    class Meta:
        verbose_name = "پست"
        verbose_name_plural = "پست ها"
        indexes = [models.Index(fields=["title", "body"])]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("apps.blog:post_detail", args=[str(self.slug)])

    def posts_was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=3)

    def thumbnail_tag(self):
        return format_html("<img width=50 src='{}' />".format(self.get_thumbnail_url))

    @property
    def view_count(self):
        return self.hit_count.hits

    @cached_property
    def read_time(self):
        return readtime.of_text(self.body).minutes

    def get_similar_posts(self):
        post_tags_ids = self.tags.values_list("id", flat=True)
        similar_posts = (
            Post.published.filter(tags__in=post_tags_ids)
            .exclude(id=self.id)
            .annotate(same_tags=Count("tags"))
            .order_by("-same_tags", "-created_at")[:4]
        )
        return similar_posts
