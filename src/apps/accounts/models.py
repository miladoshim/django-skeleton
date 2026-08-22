from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from jalali_date import date2jalali
from apps.accounts.mixins import FollowMixin
from apps.core.models import BaseModel
from utils.enums import GenderChoices, UserRole
from utils.helpers import generate_unique_uuid
from utils.storage_paths import user_avatar_path, user_banner_path
from .managers import OTPManager, UserManager


class User(AbstractBaseUser, FollowMixin, PermissionsMixin):
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
        max_length=35,
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
        help_text="با این گزینه کاربر فعال می باشد.",
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

    def get_profile_url(self):
        return reverse("apps.accounts:user_profile", kwargs={"username": self.username})

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_account_role_title(self):
        return "مدیر کل" if self.is_staff else "کاربر"

    def get_wallet_balance(self):
        return self.wallet.balance

    @property
    def is_banned(self) -> bool:
        return self.meta.is_banned

    @property
    def is_mobile_verified(self) -> bool:
        return self.meta.mobile_verified_at

    @property
    def is_email_verified(self) -> bool:
        return self.meta.email_verified_at

    @property
    def has_avatar(self) -> bool:
        return self.profile.avatar

    def get_avatar_url(self):
        if self.profile.avatar != '"images/default_man_avatar.jpg"':
            return self.profile.avatar.url
        else:
            return self.profile.get_default_avatar_image()

    def check_login_allowed(self):
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
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        verbose_name="تصویر پروفایل",
    )
    banner = models.ImageField(
        upload_to=user_banner_path,
        blank=True,
        null=True,
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
    birthday_day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="روز تولد",
        help_text="00",
    )
    birthday_month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="ماه تولد",
        help_text="00",
    )
    birthday_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="سال تولد",
        help_text="0000",
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
    last_logout_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ آخرین خروج",
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


class UserSession(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_key = models.CharField(
        max_length=40,
        unique=True,
    )
    ip = models.GenericIPAddressField(null=True)
    device = models.CharField(max_length=20, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ آخرین ورود",
    )

    class Meta:
        ordering = ["-last_login_at"]

    def __str__(self):
        return f"{self.user.username} - {self.browser} ({self.device})"

    def terminate(self):
        self.is_active = False
        self.is_current = False
        self.save()
        Session.objects.filter(session_key=self.session_key).delete()


class SocialAccountProvider(models.TextChoices):
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    GOOGLE = "google"


class SocialAccount(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )
    provider = models.CharField(
        verbose_name="provider",
        choices=SocialAccountProvider.choices,
    )
    provider_id = models.CharField(
        max_length=255,
        db_index=True,
    )
    provider_username = models.CharField(
        max_length=255,
        blank=True,
    )
    provider_email = models.EmailField(blank=True)
    provider_avatar_url = models.URLField(blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    extra_data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "حساب سوشیال"
        verbose_name_plural = "حسابهای سوشیال"
        unique_together = [["user", "provider"]]
        indexes = [
            models.Index(fields=["provider", "provider_id"]),
            models.Index(fields=["user", "provider"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.provider}"

    @property
    def is_token_valid(self):
        if self.token_expires_at:
            return self.token_expires_at > timezone.now()
        return True


class OtpChannel(models.TextChoices):
    MOBILE = "m", "Mobile"
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
        default=OtpChannel.MOBILE,
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
        return timezone.now() > self.expired_at

    @classmethod
    def delete_expired(cls):
        expired_count = cls.objects.filter(expires_at__lt=timezone.now()).delete()[0]
        return expired_count


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",  # افرادی که من دنبال می‌کنم
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",  # افرادی که من را دنبال می‌کنند
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["follower", "following"]  # جلوگیری از تکرار
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower} → {self.following}"
