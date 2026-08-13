# apps/accounts/services.py
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
import random


class ForgotPasswordService:

    @staticmethod
    def send_email_reset_link(request, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        protocol = "https" if request.is_secure() else "http"
        reset_link = f"{protocol}://{domain}{reverse('apps.accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

        subject = "بازیابی رمز عبور"
        message = f"""
        سلام {user.username}،
        
        برای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:
        {reset_link}
        
        اگر شما این درخواست را نداده‌اید، این ایمیل را نادیده بگیرید.
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return True

    @staticmethod
    def send_mobile_otp(user):

        otp_code = str(random.randint(100000, 999999))

        # ذخیره در کش (5 دقیقه اعتبار)
        from django.core.cache import cache

        cache_key = f"otp_{user.mobile}"
        cache.set(cache_key, otp_code, timeout=300)  # 5 دقیقه

        # ارسال SMS (اینجا سرویس شما)
        # Kavenegar.send_otp(receptor=user.mobile, otp=otp_code)
        result = True  # جایگزین کنید با سرویس واقعی

        return result, otp_code

    @staticmethod
    def verify_mobile_otp(mobile, otp_code):
        """بررسی کد یکبار مصرف"""
        from django.core.cache import cache

        cache_key = f"otp_{mobile}"
        saved_otp = cache.get(cache_key)

        return saved_otp == otp_code
