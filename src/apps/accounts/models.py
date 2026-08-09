from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from jalali_date import date2jalali
from django.core.exceptions import PermissionDenied
from apps.core.models import BaseModel
from utils.enums import GenderChoices, UserRole
from utils.helpers import generate_unique_uuid
from .managers import OTPManager, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that have extra fields
    """

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربر ها"
        swappable = "AUTH_USER_MODEL"

    uuid = models.UUIDField(
        default=generate_unique_uuid,
        editable=False,
        db_index=True,
        unique=True,
    )
    first_name = models.CharField(
        "نام",
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        "نام خانوادگی",
        max_length=150,
        blank=True,
        null=True,
    )
    username = models.CharField(
        "نام کاربری",
        blank=True,
        null=True,
        editable=False,
        unique=True,
        max_length=9,
    )
    email = models.EmailField(
        verbose_name="ایمیل",
        blank=True,
        null=True,
        unique=True,
    )
    mobile = models.CharField(
        "موبایل",
        unique=True,
        blank=True,
        null=True,
        max_length=11,
    )
    password = models.CharField(
        "رمز عبور",
        max_length=128,
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(
        verbose_name="کاربر مدیر باشد؟",
        default=False,
        help_text="با این کزینه کاربر توانایی ورود به پنل مدیریت را دارا می باشد.",
    )
    is_active = models.BooleanField(
        verbose_name="فعال باشد؟",
        default=False,
        help_text="Unselect this instead of deleting accounts.",
    )
    role = models.PositiveSmallIntegerField(
        verbose_name="نقش کاربر",
        choices=UserRole.choices,
        default=UserRole.USER,
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

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return reverse("accounts:profile_view", kwargs={"uuid": self.uuid})

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def is_banned(self) -> bool:
        return self.meta.is_banned

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            if obj is not None and obj.id != request.user.id:
                return False
        return True

    # Staff can only change their own account info
    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser:
            if obj is not None and obj.id != request.user.id:
                return False
        return True

    # Staff can't add new account
    def has_add_permission(self, request):
        if not request.user.is_superuser:
            return False
        return True

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return "is_superuser", "is_staff", "is_active"
        return super(User, self).get_readonly_fields(request)

    def is_registered(self):
        return self.meta.mobile_verified_at

    def check_login_allowed(self):
        """بررسی مجاز بودن ورود"""
        if self.is_blocked:
            raise PermissionDenied("Your account is blocked.")
        if not self.is_active:
            raise PermissionDenied("Your account is inactive.")
        return True


class UserProfile(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/%Y/%m/%d/",
        blank=True,
        null=True,
        default="images/default_man_avatar.jpg",
        verbose_name="تصویر پروفایل",
    )
    banner = models.ImageField(
        upload_to="users/banners/%Y/%m/%d/",
        blank=True,
        null=True,
        default="images/default_banner.jpg",
        verbose_name="بنر پروفایل",
    )
    gender = models.CharField(
        max_length=8,
        choices=GenderChoices.choices,
        default=GenderChoices.__empty__,
        verbose_name="جنسیت",
    )
    bio = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="بیوگرافی",
    )

    def __str__(self):
        return self.user.get_full_name() + " profile"

    def get_default_avatar_image(self):
        return "images/default_man_avatar.jpg"

    def get_default_banner_image(self):
        return "images/default_banner.jpg"

    class Meta:
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل ها"


class UserMeta(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="meta",
        verbose_name="کاربر",
    )
    last_login_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ آخرین لاگین",
    )
    # last_login_failed_at = models.DateTimeField(
    #     "last failed login",
    #     null=True,
    #     blank=True,
    # )

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="ip آخرین لاگین",
    )
    last_logout_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ آخرین خروج",
    )
    last_login_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="مرورگر آخرین ورود",
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تایید ایمیل",
    )
    email_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تغییر ایمیل",
    )
    mobile_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تغییر موبایل",
    )
    mobile_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تایید موبایل",
    )
    username_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تغییر نام کاربری",
    )
    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ تغییر رمز عبور",
    )
    is_banned = models.BooleanField(
        default=False,
        verbose_name="کاربر مسدود می باشد؟",
    )
    banned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ مسدود شدن کاربر",
    )
    unbanned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ رفع مسدودی ",
    )
    # two_factor_enabled = models.BooleanField("2FA enabled", default=False)


# class LoginHistory(models.Model):
#     """تاریخچه ورود کاربران"""

#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="login_history"
#     )
#     login_time = models.DateTimeField("login time", auto_now_add=True)
#     logout_time = models.DateTimeField("logout time", null=True, blank=True)
#     ip_address = models.GenericIPAddressField("IP address", null=True)
#     user_agent = models.TextField("user agent", blank=True)
#     device = models.CharField("device", max_length=100, blank=True)
#     browser = models.CharField("browser", max_length=100, blank=True)
#     os = models.CharField("operating system", max_length=100, blank=True)
#     location = models.CharField("location", max_length=100, blank=True)
#     is_successful = models.BooleanField("successful login", default=True)
#     auth_method = models.CharField("auth method", max_length=50, blank=True)

#     class Meta:
#         verbose_name = "login history"
#         verbose_name_plural = "login histories"
#         ordering = ["-login_time"]

#     def __str__(self):
#         return f"{self.user.email} - {self.login_time}"


class OtpChannel(models.TextChoices):
    PHONE = "p", "Phone"
    EMAIL = "e", "Email"


class OtpRequest(BaseModel):
    objects = OTPManager()
    request_id = models.UUIDField(
        default=generate_unique_uuid,
        editable=False,
        unique=True,
        db_index=True,
    )
    channel = models.CharField(
        "channel",
        max_length=1,
        choices=OtpChannel.choices,
        default=OtpChannel.PHONE,
    )
    receiver = models.CharField(max_length=256)  # mobile or email
    password = models.CharField(
        max_length=6,
        null=True,
        blank=True,
    )
    expired_at = models.DateTimeField(
        default=timezone.now() + timezone.timedelta(seconds=120),
        db_index=True,
    )

    class Meta:
        verbose_name = "درخواست رمز یکبار مصرف"
        verbose_name_plural = "درخواست رمز یکبار مصرف ها"

    def __str__(self):
        return "{}-{}-{}".format(self.channel, self.receiver, self.password)

    @property
    def is_expired(self):
        """آیا منقضی شده؟"""
        return timezone.now() > self.expired_at

    @classmethod
    def delete_expired(cls):
        """حذف همه رکوردهای منقضی شده"""
        expired_count = cls.objects.filter(expires_at__lt=timezone.now()).delete()[0]
        return expired_count

    # @property
    # def is_valid(self):
    #     return not self.is_used and self.expires_at > timezone.now()
