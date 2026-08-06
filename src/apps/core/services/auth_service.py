from datetime import datetime
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMessage
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.accounts.admin import User


def send_activation_email(request, user):
    current_site = get_current_site(request)
    token = default_token_generator.make_token(user)
    encoded_uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_path = reverse("apps:accounts:activation", args=[encoded_uid, token])
    activation_url = f"{request.scheme}://{current_site}{activation_path}"
    print("----------------------Email Activation Url---------------------------")
    print(activation_url)
    message = render_to_string(
        "activation_email.html", {"user": user, "activation_url": activation_url}
    )
    email = EmailMessage("ایمیل خود را تایید کنید", message, to=[user.email])
    email.send()


def verify_activation_email(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.meta.update({"email_verified_at": datetime.now()})
        return True
    return False


def send_otp_sms(request, user):
    pass


def verify_otp_sms(request, user):
    pass


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()


from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.services.base_service import BaseService

User = get_user_model()


class AuthService(BaseService):
    """سرویس احراز هویت - استفاده مشترک بین Web/API/GraphQL"""

    model = User

    def register(self, email: str, password: str, **extra_data) -> Dict[str, Any]:
        """
        ثبت‌نام کاربر جدید و برگرداندن توکن‌ها
        استفاده در: Web ثبت‌نام، API Register، GraphQL register
        """
        with transaction.atomic():
            # بررسی وجود کاربر
            if User.objects.filter(email=email).exists():
                raise ValueError("این ایمیل قبلاً ثبت شده است")

            # ایجاد کاربر
            user = User.objects.create_user(
                email=email, password=password, **extra_data
            )

            # ارسال ایمیل فعال‌سازی
            self._send_activation_email(user)

            # ساخت توکن‌ها
            tokens = self._get_tokens_for_user(user)

            return {
                "user": user,
                "tokens": tokens,
                "message": "ثبت‌نام با موفقیت انجام شد",
            }

    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        ورود کاربر و برگرداندن توکن‌ها
        استفاده در: Web login، API Login، GraphQL login
        """
        user = authenticate(username=email, password=password)

        if not user:
            raise ValueError("ایمیل یا رمز عبور اشتباه است")

        if not user.is_active:
            raise ValueError("حساب کاربری شما غیرفعال است")

        tokens = self._get_tokens_for_user(user)

        return {"user": user, "tokens": tokens, "message": "ورود با موفقیت انجام شد"}

    def logout(self, user: User) -> bool:
        """
        خروج کاربر
        برای Web: session logout
        برای API: blacklist token
        """
        try:
            # غیرفعال کردن توکن‌ها (برای JWT)
            RefreshToken.for_user(user).blacklist()
            return True
        except Exception:
            return False

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """
        دریافت توکن جدید
        فقط برای API و GraphQL
        """
        try:
            refresh = RefreshToken(refresh_token)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        except Exception as e:
            raise ValueError("توکن نامعتبر است")

    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """
        تغییر رمز عبور
        استفاده در: Web change_password، API change_password، GraphQL changePassword
        """
        if not user.check_password(old_password):
            raise ValueError("رمز عبور فعلی اشتباه است")

        user.set_password(new_password)
        user.save(update_fields=["password"])

        # ارسال ایمیل اطلاع‌رسانی
        self._send_password_change_notification(user)

        return True

    def forgot_password(self, email: str) -> bool:
        """
        فراموشی رمز عبور - ارسال ایمیل بازیابی
        استفاده در: Web forgot_password، API forgot-password، GraphQL forgotPassword
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # برای امنیت، همین پیام را برمی‌گردانیم
            return True

        # ساخت توکن بازیابی
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # ساخت لینک بازیابی
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

        # ارسال ایمیل
        send_mail(
            subject="بازیابی رمز عبور",
            message=f"""
            برای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:
            {reset_url}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return True

    def reset_password(self, uid: str, token: str, new_password: str) -> bool:
        """
        بازیابی رمز عبور با توکن
        استفاده در: Web reset_password، API reset-password، GraphQL resetPassword
        """
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValueError("لینک بازیابی نامعتبر است")

        if not default_token_generator.check_token(user, token):
            raise ValueError("لینک بازیابی منقضی شده است")

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return True

    def verify_email(self, uid: str, token: str) -> bool:
        """
        تایید ایمیل
        استفاده در: Web verify_email، API verify-email، GraphQL verifyEmail
        """
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValueError("لینک تایید نامعتبر است")

        if not default_token_generator.check_token(user, token):
            raise ValueError("لینک تایید منقضی شده است")

        user.email_verified = True
        user.save(update_fields=["email_verified"])

        return True

    def get_user_by_token(self, token: str) -> Optional[User]:
        """
        دریافت کاربر از روی توکن
        فقط برای API و GraphQL
        """
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            user = User.objects.get(id=access_token["user_id"])
            return user
        except Exception:
            return None

    def social_login(self, provider: str, token: str) -> Dict[str, Any]:
        """
        ورود با شبکه‌های اجتماعی
        پشتیبانی از: google, github, linkedin
        """
        # اینجا باید از کتابخانه‌های مربوطه استفاده کنید
        # مثال: google-auth، social-auth-app-django
        pass

    # ------------------ متدهای خصوصی ------------------

    def _get_tokens_for_user(self, user: User) -> Dict[str, str]:
        """ساخت توکن‌های JWT"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def _send_activation_email(self, user: User):
        """ارسال ایمیل فعال‌سازی"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"

        send_mail(
            subject="فعال‌سازی حساب کاربری",
            message=f"""
            به سایت ما خوش آمدید!
            برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:
            {activation_url}
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def _send_password_change_notification(self, user: User):
        """ارسال ایمیل تغییر رمز"""
        send_mail(
            subject="تغییر رمز عبور",
            message="رمز عبور شما با موفقیت تغییر کرد. اگر این تغییر توسط شما نبوده، سریعاً پشتیبانی را مطلع کنید.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
