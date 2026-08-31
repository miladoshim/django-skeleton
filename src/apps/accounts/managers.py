import random
from typing import Any
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("ایمیل باید وارد شود")

        email = self.normalize_email(email)

        mobile = extra_fields.pop('mobile', None)

        user = self.model(email=email, **extra_fields)

        if mobile:
            user.mobile = self._clean_mobile(mobile)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


    def create_user_with_mobile(self, mobile, password=None, **extra_fields):
        if self.filter(mobile=mobile).exists():
            raise ValueError("این شماره موبایل قبلاً ثبت شده است")

        temp_email = f"{mobile.replace('+', '')}@temp.com"

        extra_fields['mobile'] = mobile
        extra_fields['is_mobile_verified'] = True

        return self.create_user(temp_email, password, **extra_fields)

    def create_user_with_email_or_mobile(self, identifier, password=None, **extra_fields):
        """ثبت‌نام خودکار - ایمیل یا موبایل"""
        if '@' in identifier:
            return self.create_user(identifier, password, **extra_fields)
        else:
            return self.create_user_with_mobile(identifier, password, **extra_fields)

    def get_by_identifier(self, identifier):
        """جستجوی کاربر با ایمیل یا موبایل"""
        if '@' in identifier:
            return self.get(email__iexact=identifier)
        else:
            mobile = self._clean_mobile(identifier)
            return self.get(mobile=mobile)

    def get_or_create_by_identifier(self, identifier, defaults=None):
        """دریافت یا ایجاد کاربر با ایمیل یا موبایل"""
        if '@' in identifier:
            return self.get_or_create(email__iexact=identifier, defaults=defaults or {})
        else:
            mobile = self._clean_mobile(identifier)
            return self.get_or_create(mobile=mobile, defaults=defaults or {})

    def authenticate_by_identifier(self, identifier, password):
        """احراز هویت با ایمیل یا موبایل"""
        from django.contrib.auth import authenticate

        try:
            user = self.get_by_identifier(identifier)
            if user.check_password(password):
                return user
        except self.model.DoesNotExist:
            pass

        return None


    def _validate_email(self, email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False


    def active_users(self):
        """کاربران فعال"""
        return self.filter(is_active=True)

    def verified_users(self):
        """کاربران با ایمیل تایید شده"""
        return self.filter(is_email_verified=True)

    def mobile_users(self):
        """کاربران با موبایل"""
        return self.exclude(mobile__isnull=True).exclude(mobile='')

    def email_users(self):
        """کاربران با ایمیل"""
        return self.exclude(email__isnull=True).exclude(email='')


class UserManager(BaseUserManager):

    use_in_migrations = True

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
