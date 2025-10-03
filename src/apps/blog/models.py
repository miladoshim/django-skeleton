from io import BytesIO
from PIL import Image
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.core.files import File
from django.db.models.functions import Length
from hitcount.models import HitCountMixin
from hitcount.settings import MODEL_HITCOUNT
from meta.models import ModelMeta
from taggit.managers import TaggableManager
from taggit.models import Tag
from treebeard.mp_tree import MP_Node
from apps.accounts.models import User
from apps.core.models import BaseModel
from apps.core.managers import PublishedManager
from apps.core.models import PublishStatusChoice, BaseModel
from jalali_date import datetime2jalali
from filebrowser.fields import FileBrowseField
from auditlog.registry import auditlog
from tinymce.models import HTMLField
from django_extensions.db.fields import AutoSlugField

class Category(MP_Node):
    parent = models.ForeignKey(
        "self",
        verbose_name=_("دسته بندی والد"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=255, unique=True, db_index=True, verbose_name=_("عنوان")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name=_("اسلاگ"),
        allow_unicode=True,
        help_text="به صورت خودکار ایجاد می شود!",
    )
    description = models.TextField(
        blank=True, null=True, max_length=2048, verbose_name=_("توضیحات")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("دسته بندی فعال باشد?")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = _("دسته بندی")
        verbose_name_plural = _("دسته بندی ها")

    def __str__(self) -> str:
        return self.name

    # def get_absolute_url(self):
    #     return reverse("blog:category-detail", args=[str(self.slug)])


class Post(BaseModel, HitCountMixin):
    objects = models.Manager()
    published = PublishedManager()

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"is_staff": True},
        related_name="posts",
        verbose_name=_("نویسنده"),
        blank=True,
        null=True,
    )
    title = models.CharField(_("عنوان"), max_length=255, db_index=True)
    slug = models.SlugField(
        unique=True, verbose_name=_("اسلاگ"), allow_unicode=True, default=None
    )
    body = HTMLField(_("متن مقاله"), null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to="posts/%Y/%m/%d", null=True, blank=True, verbose_name=_("تصویر شاخص")
    )
    # thumbnail = FileBrowseField(
    #     "Image", max_length=200, directory="images/", extensions=[".jpg"], blank=True
    # )

    published_status = models.CharField(
        max_length=1,
        choices=PublishStatusChoice.choices,
        default="d",
        verbose_name=_("وضعیت انتشار"),
    )

    category = models.ForeignKey(
        "Category",
        verbose_name=_("دسته بندی"),
        on_delete=models.CASCADE,
    )

    tags = TaggableManager(verbose_name=_("برچسب ها"), related_name="posts")

    # likes = models.PositiveBigIntegerField(default=0)
    # dislikes = models.PositiveBigIntegerField(default=0)
    # likes = models.ManyToManyField(User, related_name='likes', blank=True)

    # body_character_count = models.GeneratedField(
    #     expression=Length('body'),
    #     output_field=models.IntegerField(),
    #     db_persist=True
    # )

    hit_count_generic = GenericRelation(
        MODEL_HITCOUNT,
        object_id_field="object_pk",
        related_query_name="hit_count_generic_relation",
    )

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]
        verbose_name = _("مقاله")
        verbose_name_plural = _("مقاله ها")
        indexes = [
            models.Index(fields=['title'])
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[str(self.slug)])

    def posts_was_published_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    def get_jalali_date(self):
        return datetime2jalali(self.created_at)

    def thumbnail_tag(self):
        return format_html("<img width=100 src='{}' />".format(self.thumbnail.url))

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "JPEG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def delete(self):
        self.thumbnail.delete()
        return super().delete()


class Comment(BaseModel):
    user = models.ForeignKey(
        User, related_name="comments", on_delete=models.CASCADE, verbose_name=_("کاربر")
    )
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    comment = models.TextField(verbose_name=_("نظر"))
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    # parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        verbose_name = _("نظر")
        verbose_name_plural = _("نظرات")

    def __str__(self) -> str:
        return self.comment


# class CommentReply(BaseModel):
#     comment = models.ForeignKey(
#         Comment, on_delete=models.CASCADE, related_name='replies')
# user = models.ForeignKey(
#         User, related_name="comments", on_delete=models.CASCADE, verbose_name=_("کاربر")
#     )
#     body = models.TextField(verbose_name=_('نظر'))


class RecyclePost(Post):
    deleted = models.Manager()
    class Meta:
        proxy = True


auditlog.register(Post, serialize_data=True)
