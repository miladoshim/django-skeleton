import uuid
from typing import Optional, Dict, Any
from django.core.cache import cache
from datetime import datetime
from django.contrib.auth.tokens import (
    PasswordResetTokenGenerator,
    default_token_generator,
)
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from apps.accounts.admin import User
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.contrib.sites.models import Site
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.api.serializers import UserSerializer
from apps.accounts.backends import EmailMobileUsernameBackend
from apps.accounts.tasks import send_activation_email
from apps.core.services.base_service import BaseService
from utils import logger

User = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()


class AuthService(BaseService):
    model = User

    def __init__(self, request=None):
        super().__init__(request=request)
        
    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        need_token: bool = False,
        **extra_data,
    ) -> Dict[str, Any]:

        try:
            with transaction.atomic():
                email = email.lower().strip()
                user = User.objects.filter(email=email).first()

                if user and user.is_active:
                    return {"success": False, "message": "این ایمیل قبلاً ثبت شده است"}

                if user and not user.is_active:
                    user = self._update_existing_user(user, first_name, last_name, password)
                    message = "لینک فعال‌سازی مجدد ارسال شد."
                else:
                    user = self._create_user(first_name, last_name, email, password)
                    message = "لینک فعال‌سازی ارسال شد."

                email_ok = self._send_activation_email(user) 
                if email_ok is not True:
                    return {"success": False, "message": "خطا در ارسال ایمیل"}

                return {"success": True, "email": user.email, "message": message}


        except ValueError as e:
            return {"success": False, "message": str(e)} 
        except Exception as e:
            print('-----------------------')
            print(str(e))
            return {
                "success": False,
                "message": "خطا در ثبت‌نام. لطفا دوباره تلاش کنید.",
                }  
    def login(
        self,
        identifier: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        try:
            user = authenticate(
                request=self.request,
                username=identifier,
                password=password,
            )

            if not user:
                return {"success": False, "error": "اطلاعات ورود اشتباه است"}

            if user.is_banned:
                return {"success": False, "error":"حساب کاربری شما مسدود است"}


            if self.request:
                login(self.request, user)

            user.meta.last_login_at = timezone.now()
            user.meta.save()

            tokens = self._get_tokens(user)
            response = {
                "success": True,
                "user": UserSerializer(user).data,
                "message": "ورود با موفقیت انجام شد",
                **tokens,
            }

            return response
        except Exception as e:
            logger.error(f"Register error: {str(e)}")
            return {"success": False, "error": "خطا در ثبت‌نام"}

    def logout(self):
        try:
            if self.request and self.request.user.is_authenticated:
                logout(self.request)
                return {"success": True, "message": "خروج با موفقیت انجام شد"}
        except Exception as e:
            return {"success": False, "message": f"خطا در خروج {str(e)}"}

    @transaction.atomic
    def activate_email(self, uidb64, token):
        """فعال‌سازی حساب با ایمیل"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.get(uid)  # استفاده از متد BaseService
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return {"success": False, "error": "لینک نامعتبر است"}

        if not default_token_generator.check_token(user, token):
            return {"success": False, "error": "لینک منقضی شده است"}

        # استفاده از متد update از BaseService
        self.update(user, is_active=True, is_email_verified=True)

        return {"success": True, "message": "حساب شما فعال شد"}

    # ============================
    #     CHANGE PASSWORD
    # ============================
    @transaction.atomic
    def change_password(self, user, old_password, new_password):
        """تغییر رمز عبور"""
        if not user.check_password(old_password):
            return {"success": False, "error": "رمز فعلی اشتباه است"}

        user.set_password(new_password)
        self.update(user)  # استفاده از متد BaseService

        return {"success": True, "message": "رمز عبور تغییر کرد"}

    # ============================
    #    FORGOT PASSWORD
    # ============================
    def forgot_password(self, identifier):
        """فراموشی رمز عبور"""
        user = None

        if "@" in identifier:
            user = self.get_queryset().filter(email__iexact=identifier).first()
        else:
            mobile = self._clean_mobile(identifier)
            user = self.get_queryset().filter(mobile=mobile).first()

        if not user:
            return {
                "success": True,
                "message": "اگر حساب موجود باشد، لینک ارسال می‌شود",
            }

        if user.email and "@" in identifier:
            self._send_password_reset_email(user)
        elif user.mobile:
            self._send_password_reset_sms(user)

        return {"success": True, "message": "لینک بازنشانی رمز ارسال شد"}

    # ============================
    #  RESET PASSWORD CONFIRM
    # ============================
    @transaction.atomic
    def reset_password_confirm(self, uidb64, token, new_password):
        """تایید بازنشانی رمز"""
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = self.get(uid)
        except:
            return {"success": False, "error": "لینک نامعتبر است"}

        if not default_token_generator.check_token(user, token):
            return {"success": False, "error": "لینک منقضی شده است"}

        user.set_password(new_password)
        user.save()

        # غیرفعال کردن توکن
        self._invalidate_token(user)

        return {"success": True, "message": "رمز عبور با موفقیت تغییر کرد"}

    # ============================
    #      VERIFY OTP (MOBILE)
    # ============================
    def verify_otp(self, mobile, otp_code):
        """تایید کد یکبار مصرف موبایل"""
        mobile = self._clean_mobile(mobile)
        cache_key = f"otp_{mobile}"
        saved_otp = cache.get(cache_key)

        if saved_otp == otp_code:
            cache.delete(cache_key)
            return {"success": True, "message": "کد تایید شد"}

        return {"success": False, "error": "کد اشتباه است"}

    @transaction.atomic
    def _create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
    ):
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.set_password(password)
        user.save()
        return user

    
    def _update_existing_user(self, user, first_name, last_name, password) -> User:
        user.first_name = first_name.strip()
        user.last_name = last_name.strip()
        user.set_password(password)
        user.save()
        return user
    
    @transaction.atomic
    def _send_activation_email(self, user):
        print(f"🔍 _send_activation_email called for {user.email}") 

        try:
            token = str(uuid.uuid4())
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            cache.set(f"verify_email_{token}", user.id, timeout=86400)

            activation_url = self._build_url(
                "apps.accounts:email_activation", uid, token
            )

            send_mail(
                subject="فعالسازی ایمیل",
                message=f"""
                به سایت ما خوش آمدید!
                برای فعال‌سازی ایمیل حساب خود روی لینک زیر کلیک کنید:
                    {activation_url}
                    """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return True
        except Exception as e:
            print(f"❌ Error in sending email: {str(e)}")  # ← این خط را اضافه کن

            return False

    def _send_password_reset_email(self, user):
        """ارسال ایمیل بازنشانی رمز"""
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = self._build_url("apps.accounts:password_reset_confirm", uid, token)

        send_mail(
            subject="بازنشانی رمز عبور",
            message=f"برای تغییر رمز روی لینک کلیک کنید: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def _send_password_reset_sms(self, user):
        """ارسال SMS بازنشانی رمز"""
        otp = str(random.randint(100000, 999999))
        cache.set(f"otp_{user.mobile}", otp, timeout=300)

        # اینجا سرویس SMS خود را فراخوانی کنید
        # Kavenegar.send_otp(receptor=user.mobile, otp=otp)

    def _invalidate_token(self, user):
        """غیرفعال کردن توکن‌های قبلی"""
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

    def _get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def _build_url(self, view_name, uid, token):
        domain = Site.objects.get_current().domain
        protocol = "https" if not settings.DEBUG else "http"
        path = reverse(view_name, args=[uid, token])

        return f"{protocol}://{domain}{path}"

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
            return True

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

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


    def _get_tokens(self, user):

        refresh = RefreshToken.for_user(user)
        return {
    "refresh": str(refresh),
    "access": str(refresh.access_token),
    }

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

    @transaction.atomic
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

        def _get_tokens_for_user(self, user) -> Dict[str, str]:
            refresh = RefreshToken.for_user(user)
            return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        }

    @transaction.atomic
    def verify_email(self, uid: str, token: str) -> bool:
        user_id = cache.get(f"verify_email_{token}")

        if not user_id:
            return False

        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))

            if str(user.id) == str(user_id):
                user.is_active = True
                user.save()
                user.meta.email_verified_at = datetime.now()
                user.meta.save()

                cache.delete(f"verify_email_{token}")
                return True

        except User.DoesNotExist:
            return False
        except Exception as e:
            print(str(e))
            return False
        
        def _send_welcome_email(self, user: User):
            """ارسال ایمیل خوشآمد"""
            send_mail(
                subject="خوش آمدید!",
                message=f"سلام {user.username}، به سایت ما خوش آمدید!",
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


            