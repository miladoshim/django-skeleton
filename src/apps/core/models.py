import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# from django.contrib.auth import get_user_model
from apps.core.managers import SoftDeleteManager


# User = get_user_model()


class PublishStatusChoice(models.TextChoices):
    published = "p", _("منتشر شده")
    draft = "d", _("پیش نویس")


class GenderChoices(models.TextChoices):
    male = "m", _("مرد")
    female = "f", _("زن")
    unknown = "u", _("نامشخص")
    __empty__ = "(Unknown)"


class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ["-created_at"]

    objects = SoftDeleteManager()

    uuid = models.UUIDField(unique=True, default=str(uuid.uuid4()), editable=False)
    is_deleted = models.BooleanField(
        db_default=False,
        default=False,
        null=True,
        blank=True,
        editable=False,
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("تاریخ حذف")
    )
    # restored_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ثبت"))

    @property
    def is_deleted(self) -> bool:
        return self.is_deleted

    @property
    def is_restored(self) -> bool:
        return self.restored_at is not None

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.restored_at = None
        self.save()

    def hard_delete(self, *args, **kwargs):
        super.delete(self, *args, **kwargs)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.restored_at = timezone.now()
        self.save()


# class IPAddress(BaseModel):
#     ip_address = models.GenericIPAddressField()
#     hit_count = models.PositiveBigIntegerField(default=0)

#     class Meta:
#         db_table = 'ip_addresses'
#         verbose_name = _("آدرس IP")
#         verbose_name_plural = _("آدرس IP ها")

#     def __str__(self) -> str:
#         return self.ip_address + ' : ' + self.hit_count

# class Notification(BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE,
#                              null=True,blank=True, related_name='notifications')
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     read_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.message


class NewsletterSubscriber(BaseModel):
    email = models.EmailField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.email


class FaqGroup(BaseModel):
    title = models.TextField(max_length=255)

    def __str__(self):
        return self.title


class Faq(BaseModel):
    question = models.TextField(max_length=1024)
    answer = models.TextField(max_length=1024)
    group = models.OneToOneField(
        FaqGroup, on_delete=models.CASCADE, related_name="group"
    )

    def __str__(self):
        return self.question
