import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.managers import SoftDeleteManager
# from apps.accounts.models import User


class PublishStatusChoice(models.TextChoices):
    published = "p", _("منتشر شده")
    draft = "d", _("پیش نویس")

class GenderChoices(models.TextChoices):
    male = 'male'
    female = 'female'
    unknown = 'unknown'
    __empty__ = '(Unknown)'

class BaseModel(models.Model):
    class Meta:
        abstract = True

    objects = SoftDeleteManager()

    uuid = models.UUIDField(unique=True, default=str(uuid.uuid4()), editable=False)
    is_deleted = models.BooleanField(
        default=False, null=True, blank=True, editable=False
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, editable=False, verbose_name=_("تاریخ حذف")
    )
    # deleted_by = models.ForeignKey(User, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ثبت"))

    def delete(self, user_id=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        # self.deleted_by = user_id
        self.save()

    def hard_delete(self):
        pass

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
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
    
# class ActivityHistory(LogEntry):
#     class Meta:
#         proxy = True



# class NewsletterSubscriber(BaseModel):
#     email = models.EmailField(max_length=255)
#     date_added = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return '%s' % self.email
