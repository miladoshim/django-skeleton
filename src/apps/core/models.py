from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jalali_date import date2jalali
from persiantools.jdatetime import JalaliDate
from apps.core.managers import CommentManager
from utils.helpers import generate_unique_uuid

User = settings.AUTH_USER_MODEL


class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ["-created_at"]

    uuid = models.UUIDField(
        default=generate_unique_uuid,
        editable=False,
        db_index=True,
        unique=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت",
    )

    def get_jalali_date(self):
        return date2jalali(self.created_at)

    def get_jalali_date2(self):
        return JalaliDate(self.created_at, locale=("fa")).strftime("%c")


class Comment(BaseModel):
    user = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="کاربر",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    comment = models.TextField(
        verbose_name="نظر",
        max_length=1024,
    )
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = CommentManager()

    class Meta:
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"

    def __str__(self) -> str:
        if not self.parent:
            return f"{self.comment[:20]}"
        else:
            return f"[RE] ({self.parent.comment[:10]}) : {self.comment[:15]}"

    @property
    def is_parent(self):
        return self.parent is None


class Like(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ["user", "content_type", "object_id"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ❤️ {self.content_object}"


class Bookmark(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookmarks",
        verbose_name="کاربر",
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="نوع محتوا",
    )
    object_id = models.PositiveIntegerField(verbose_name="آی‌دی محتوا")
    content_object = GenericForeignKey("content_type", "object_id")
    note = models.TextField(
        blank=True,
        null=True,
        verbose_name="یادداشت",
    )

    class Meta:
        verbose_name = "علاقه مندی"
        verbose_name_plural = "علاقه مندی ها"
        unique_together = ("user", "content_type", "object_id")
        indexes = [
            models.Index(fields=["user", "content_type"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user_id} → {self.content_type.app_label}.{self.content_type.model}({self.object_id})"


# class BannerSection(models.IntegerChoices):
#     MAIN_HOME = 1, "بنر اصلی صفحه اصلی"
#     SUB_SLIDER_HOME = 2, "بنر اسلایدر فرعی صفحه اصلی"
#     SHOP_SLIDER = 3, "بنر اسلایدر صفحه فروشگاه"


# class Banner(BaseModel):

#     title = models.CharField(
#         max_length=255,
#         unique=True,
#         verbose_name="عنوان بنر",
#         help_text="عنوان بنر برای سئو",
#     )
#     slug = models.SlugField(
#         unique=True,
#         verbose_name="نامک",
#         allow_unicode=True,
#         default=None,
#     )
#     image = models.ImageField(
#         upload_to="banners/",
#         verbose_name="تصویر بنر",
#         help_text="تصویر بنر برای نمایش",
#     )
#     link = models.URLField(
#         verbose_name="لینک بنر",
#         help_text="لینک مرتبط با بنر",
#     )
#     section = models.PositiveSmallIntegerField(
#         verbose_name="بخش",
#         help_text="مکان نمایش بنر در سایت",
#         choices=BannerSection.choices,
#         default=BannerSection.MAIN_HOME,
#     )

#     def __str__(self):
#         return "%s" % self.title

#     class Meta:
#         verbose_name = "بنر"
#         verbose_name_plural = "بنر ها"

#     class Media:
#         js = ("admin/js/upload_progress.js",)
#         css = {"all": ("admin/css/upload_progress.css",)}
