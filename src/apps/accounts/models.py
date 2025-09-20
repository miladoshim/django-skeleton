from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel, GenderChoices
from django.db.models import UniqueConstraint


class User(AbstractUser):
    """
    Custom User model that have extra fields
    """

    pass
    # mobile = models.CharField(null=True, blank=True,
    #                           unique=True, max_length=11)
    # mobile_verified = models.BooleanField(default=False)
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['mobile']

    # objects = UserManager()

    # def __str__(self):
    #     return self.username


class UserProfile(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, default="default_avatar.jpg"
    )
    gender = models.CharField(
        max_length=8, choices=GenderChoices.choices, default=GenderChoices.unknown
    )
    # bio = models.CharField(max_length=255, null=True, blank=True)
    # birthday = models.DateField(verbose_name=_("تاریخ تولد"), null=True, blank=True)

    def __str__(self) -> str:
        return self.user.username + " profile"


#     def get_avatar_image_path(self, filename):
#         return f'accounts/avatars/{self.pk}/profile_image.jpg'

#     def get_default_avatar_image():
#         return 'accounts/avatars/default_avatar.jpg'


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
