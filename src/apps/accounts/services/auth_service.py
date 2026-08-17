from typing import Optional, Dict, Any
from datetime import datetime
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMessage
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.accounts.admin import User
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from apps.core.services.base_service import BaseService

User = get_user_model()


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


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()


class AuthService(BaseService):
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

    def login(
        self, username: str, password: str, need_token=False
    ) -> Optional[Dict[str, Any]]:
        user = authenticate(username=username, password=password)

        if not user:
            raise ValueError("نام کاربری یا رمز عبور اشتباه است")

        if not user.is_block:
            raise ValueError("حساب کاربری شما مسدود است")

        response = {"user": user, "message": "ورود با موفقیت انجام شد"}

        if need_token:
            tokens = self._get_tokens_for_user(user)
            response = {
                "user": user,
                "tokens": tokens,
                "message": "ورود با موفقیت انجام شد",
            }

        return response

    def logout(self, user: User) -> bool:
        try:
            RefreshToken.for_user(user).blacklist()
            return True
        except Exception:
            return False

    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        try:
            refresh = RefreshToken(refresh_token)
            return {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        except Exception as e:
            raise ValueError("توکن نامعتبر است")

    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        if not user.check_password(old_password):
            raise ValueError("رمز عبور فعلی اشتباه است")

        user.set_password(new_password)
        user.save(update_fields=["password"])

        self._send_password_change_notification(user)

        return True

    def forgot_password(self, identifier: str) -> bool:
        identifier = identifier.strip().lower()

        #     if "@" in identifier:
        #         return self._handle_email(request, identifier)
        #     else:
        #         return self._handle_mobile(request, identifier)

        try:
            user = User.objects.get(email=identifier)
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

    # transaction.atomic

    # def _handle_email(self, request, email):
    #     user = User.objects.filter(email__iexact=email).first()

    #     if not user:
    #         messages.error(request, "کاربری با این ایمیل یافت نشد")
    #         return redirect("apps.accounts:password_forgot_view")

    #     token = default_token_generator.make_token(user)
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     domain = get_current_site(request).domain
    #     reset_link = f"http://{domain}{reverse('apps.accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"
    # reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

    #     try:
    #         send_mail(
    #             subject="بازیابی رمز عبور",
    #             message=f"""
    #             سلام {user.username}،

    #             برای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:
    #             {reset_link}

    #             این لینک ۲۴ ساعت اعتبار دارد.
    #             اگر شما درخواست نداده‌اید، این ایمیل را نادیده بگیرید.
    #             """,
    #             from_email=settings.DEFAULT_FROM_EMAIL,
    #             recipient_list=[user.email],
    #         )
    #         messages.success(request, "لینک بازیابی به ایمیل شما ارسال شد")
    #         return redirect("apps.accounts:password_forgot_done_view")

    #     except Exception:
    #         messages.error(request, "خطا در ارسال ایمیل. لطفا بعدا تلاش کنید")
    #         return redirect("apps.accounts:password_forgot_view")

    # @transaction.atomic
    # def _handle_mobile(self, request, mobile):
    #     mobile = self._normalize_mobile(mobile)

    #     user = User.objects.filter(mobile=mobile, is_active=True).first()

    #     if not user:
    #         messages.error(request, "کاربری با این شماره یافت نشد")
    #         return redirect("apps.accounts:password_forgot_view")

    #     otp = OtpRequest.objects.generate_otp(
    #         {
    #             "channel": OtpChannel.MOBILE,
    #             "receiver": mobile,
    #         }
    #     )

    #     cache.set(f"otp_{mobile}", otp.password, timeout=300)

    #     try:
    #         task = send_otp_password.apply_async(
    #             kwargs={"receiver": mobile, "otp": otp.password}
    #         )

    #         if task.status in ["PENDING", "SUCCESS"]:
    #             messages.success(request, "کد یکبار مصرف برای شما ارسال شد.")
    #             return redirect(
    #                 "apps.accounts:forgot_mobile_verify",
    #                 mobile=mobile,
    #                 reqid=otp.request_id,
    #             )
    #         else:
    #             messages.error(
    #                 request, "خطا در ارسال کد یکبار مصرف. لطفا دوباره تلاش کنید."
    #             )

    #     except Exception as e:
    #         messages.error(request, f"خطا در ارسال کد: {str(e)}")

    #         return redirect("apps.accounts:password_forgot_view")

    # def _normalize_mobile(self, mobile):
    #     mobile = re.sub(r"[^\d]", "", mobile)

    #     return mobile

    def reset_password(self, uid: str, token: str, new_password: str) -> bool:

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
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token)
            user = User.objects.get(id=access_token["user_id"])
            return user
        except Exception:
            return None

    def social_login(self, provider: str, token: str) -> Dict[str, Any]:
        pass

    def _get_tokens_for_user(self, user: User) -> Dict[str, str]:
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

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

    def _send_activation_email(self, user: User):

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_path = reverse("apps:accounts:activation", args=[encoded_uid, token])
        activation_url = f"{request.scheme}://{current_site}{activation_path}"

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
        send_mail(
            subject="تغییر رمز عبور",
            message="رمز عبور شما با موفقیت تغییر کرد. اگر این تغییر توسط شما نبوده، سریعاً پشتیبانی را مطلع کنید.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
