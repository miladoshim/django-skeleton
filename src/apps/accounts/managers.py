import random
from typing import Any
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    def _create_user(self, mobile, password, **extra_fields):
        if not mobile:
            raise ValueError("The mobile must be set")

        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(str(password))
        user.save(using=self._db)

        return user

    def create_user(
        self, mobile: str, password: str | None = ..., **extra_fields: Any
    ) -> Any:
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(mobile, password, **extra_fields)

    def create_superuser(
        self, mobile: str, password: str | None = ..., **extra_fields: Any
    ) -> Any:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(mobile, password, **extra_fields)


class OtpRequestQuerySet(models.QuerySet):

    def can_generate(self, receiver) -> bool:
        return not self.filter(receiver=receiver).exists()

    def is_valid(self, receiver, request_id, password):
        current_time = timezone.now()

        return self.filter(
            receiver=receiver,
            request_id=request_id,
            password=password,
            # expired_at__lt=current_time,
            # expired_at__gt=current_time - datetime.timedelta(seconds=360),
        ).exists()


class OTPManager(models.Manager):

    def generate_otp(self, data):
        otp = self.model(channel=data["channel"], receiver=data["receiver"])
        otp.password = random.randint(000000, 999999)
        otp.expired_at = timezone.now() + timezone.timedelta(seconds=120)
        otp.save(using=self._db)
        return otp

    def get_queryset(self):
        return OtpRequestQuerySet(self.model, self._db)

    def is_valid(self, receiver, request_id, password):
        return self.get_queryset().is_valid(receiver, request_id, password)

    def can_generate(self, receiver):
        return self.get_queryset().can_generate(receiver=receiver)
