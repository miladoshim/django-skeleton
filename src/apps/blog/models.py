import datetime
import readtime
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.functional import cached_property
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from hitcount.models import HitCountMixin
from hitcount.settings import MODEL_HITCOUNT
from star_ratings.models import Rating
from taggit_selectize.managers import TaggableManager
from treebeard.mp_tree import MP_Node
from apps.core.managers import PublishedManager
from apps.core.models import BaseModel, Bookmarkable, Commentable
from utils.enums import PublishStatusChoice, PostTypeChoice

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
        upload_to="blog/categories/",
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


class Post(BaseModel, Commentable, Bookmarkable, HitCountMixin):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": True},
        related_name="authored_posts",
        verbose_name="نویسنده",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="دسته بندی",
        on_delete=models.PROTECT,
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
        upload_to="posts/thumbnails/%Y/%m/%d",
        verbose_name="تصویر شاخص",
    )
    published_status = models.PositiveSmallIntegerField(
        choices=PublishStatusChoice.choices,
        default=PublishStatusChoice.DRAFT,
        verbose_name="وضعیت انتشار",
    )
    post_type = models.PositiveSmallIntegerField(
        choices=PostTypeChoice.choices,
        default=PostTypeChoice.POST.value,
        verbose_name="نوع پست",
    )
    attachment_link = models.CharField(
        "لینک پادکست یا سینما",
        null=True,
        blank=True,
        help_text="لینک فایل پادکست یا سینما",
        max_length=250,
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
    # ratings = GenericRelation(Rating, related_query_name="posts")

    objects = models.Manager()
    published = PublishedManager()

    def get_meta_thumbnail(self):
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
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    def thumbnail_tag(self):
        return format_html("<img width=50 src='{}' />".format(self.thumbnail.url))

    @cached_property
    def read_time(self):
        return readtime.of_text(self.body).minutes

    # def get_similar_posts(self):
    #     post_tags_ids = self.tags.values_list("id", flat=True)
    #     similar_posts = (
    #         Post.published.filter(tags__in=post_tags_ids)
    #         .exclude(id=self.id)
    #         .annotate(same_tags=Count("tags"))
    #         .order_by("-same_tags", "-created_at")[:4]
    #     )
    #     return similar_posts

    # def get_similar_courses(self):
    #     post_tags_ids = self.tags.values_list("id", flat=True)
    #     similar_courses = (
    #         Course.published.filter(tags__in=post_tags_ids)
    #         .exclude(id=self.id)
    #         .annotate(same_tags=Count("tags"))
    #         .order_by("-same_tags", "-created_at")[:8]
    #     )
    #     return similar_courses

    def get_type(self) -> str:
        if self.post_type == PostTypeChoice.POST.value:
            return "مقاله"
        elif self.post_type == PostTypeChoice.PODCAST.value:
            return "پادکست"
        else:
            return "سینما"
