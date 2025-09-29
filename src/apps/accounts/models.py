import datetime
import random
import string
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint
from django.core.validators import FileExtensionValidator
from apps.core.models import BaseModel, GenderChoices


class User(AbstractUser):
    """
    Custom User model that have extra fields
    """


    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربر ها")

    # mobile = models.CharField(null=True, blank=True,
    #                           unique=True, max_length=11)
    # mobile_verified = models.BooleanField(default=False)
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['mobile']

    # objects = UserManager()

    # def __str__(self):
    #     return self.username



image_ext_validator = FileExtensionValidator(['png', 'jpg', 'jpeg']) 

class UserProfile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, default="default_avatar.jpg",
    )
    gender = models.CharField(
        max_length=8, choices=GenderChoices.choices, default=GenderChoices.unknown
    )
    bio = models.CharField(max_length=255, null=True, blank=True)
    birthday = models.DateField(verbose_name=_("تاریخ تولد"), null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username + " profile"

    def get_avatar_image_path(self, filename):
        return f"accounts/avatars/{self.pk}/profile_image.jpg"

    def get_default_avatar_image():
        return "accounts/avatars/default_avatar.jpg"

    class Meta:
        verbose_name = "پروفایل"


class UserMeta(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_logout_at = models.DateTimeField(null=True, blank=True)
    last_login_agent = models.TextField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    email_changed_at = models.DateTimeField(null=True, blank=True)
    mobile_changed_at = models.DateTimeField(null=True, blank=True)
    mobile_verified_at = models.DateTimeField(null=True, blank=True)
    username_changed_at = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    unbanned_at = models.DateTimeField(null=True, blank=True)


class ActivationCode(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    expired_at = models.DateTimeField(default=datetime.timedelta(minutes=3))


class OtpRequestQuerySet(models.QuerySet):
    def is_valid(self, receiver, request, password):
        current_time = timezone.now()

        return self.filter(
            receiver=receiver,
            request_id=request,
            password=password,
            created__lt=current_time,
            created__gt=current_time - datetime.timedelta(seconds=120),
        ).exists()


class OTPManager(models.Manager):
    def generate(self, data):
        otp = self.model(channel=data["channel"], receiver=data["receiver"])
        otp.save(using=self._db)
        return otp

    def get_queryset(self):
        return OtpRequestQuerySet(self.model, self._db)

    def is_valid(self, receiver, request, password):
        return self.get_queryset().is_valid(receiver, request, password)


class OtpRequest(models.Model):
    class OtpChannel(models.TextChoices):
        PHONE = "p", _("Phone")
        EMAIL = "e", _("Email")

    objects = OTPManager()

    request_id = models.UUIDField(default=uuid.uuid4, editable=False)
    channel = models.CharField(
        _("channel"),
        max_length=20,
        choices=OtpChannel.choices,
        default=OtpChannel.PHONE,
    )
    receiver = models.CharField(max_length=12)  # mobile or email
    password = models.CharField(max_length=4, null=True)
    valid_until = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(seconds=120)
    )
    receipt_id = models.CharField(max_length=255, null=True)

    def generate_otp(self):
        self.password = self._random_password()
        self.valid_until = timezone.now() + timezone.timedelta(seconds=120)

    def _random_password(self):
        rand = random.SystemRandom()
        digits = rand.choice(string.digits, k=4)
        return "".join(digits)

    class Meta:
        verbose_name = _("Otp Request")
        verbose_name_plural = _("Otp Requests")


class AccountDeleteRequest(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("کاربر"))
    approved_at = models.DateTimeField(null=True, blank=True)
    complete_at = models.DateTimeField(null=True, blank=True)
