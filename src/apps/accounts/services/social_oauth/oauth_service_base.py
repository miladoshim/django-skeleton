# apps/accounts/services/base.py
import secrets
import requests
from abc import ABC, abstractmethod
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()


class BaseSocialService(ABC):
    provider = None
    authorize_url = None
    token_url = None
    user_api_url = None

    client_id_key = None
    client_secret_key = None
    redirect_uri_key = None

    def __init__(self):
        self.client_id = getattr(settings, self.client_id_key, "")
        self.client_secret = getattr(settings, self.client_secret_key, "")
        self.redirect_uri = getattr(settings, self.redirect_uri_key, "")

    def get_authorize_url(self, state=None):
        state = state or self._generate_state()

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
        }
        self._update_authorize_params(params)

        from urllib.parse import urlencode

        return f"{self.authorize_url}?{urlencode(params)}", state

    def exchange_code_for_token(self, code):
        """تبدیل code به token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        self._update_token_data(data)

        response = self._make_request(
            "POST",
            self.token_url,
            data=data,
            headers={"Accept": "application/json"},
        )

        return self._parse_token_response(response)

    def get_user_info(self, access_token):
        """دریافت اطلاعات کاربر"""
        headers = self._get_user_headers(access_token)

        response = self._make_request(
            "GET",
            self.user_api_url,
            headers=headers,
        )

        return self._parse_user_data(response)

    @transaction.atomic
    def login_with_provider(self, code, state=None):
        """
        متد اصلی - ورود کامل با سرویس سوشیال
        """
        # 1. تبادل code با token
        token_data = self.exchange_code_for_token(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise ValueError("Invalid access token")

        # 2. دریافت اطلاعات کاربر
        user_info = self.get_user_info(access_token)

        # 3. پیدا کردن یا ساخت کاربر
        user, is_new = self._get_or_create_user(user_info)

        # 4. ذخیره اطلاعات سوشیال
        self._save_social_account(user, user_info, token_data)

        return user, is_new

    # ---------- متدهای کمکی ----------

    @abstractmethod
    def _parse_user_data(self, data):
        """
        تبدیل داده خام سرویس به فرمت استاندارد
        {
            'provider_id': '123456789',
            'username': 'johndoe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'avatar_url': 'https://...',
        }
        """
        pass

    @abstractmethod
    def _update_authorize_params(self, params):
        """افزودن پارامترهای خاص سرویس"""
        pass

    @abstractmethod
    def _update_token_data(self, data):
        """افزودن دادههای خاص سرویس"""
        pass

    def _parse_token_response(self, token_data):
        return token_data

    def _get_user_headers(self, access_token):
        return {"Authorization": f"Bearer {access_token}"}

    def _make_request(self, method, url, **kwargs):
        """درخواست HTTP امن"""
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            data = response.json()

            if not response.ok:
                error_message = (
                    data.get("error_description")
                    or data.get("message")
                    or "خطا در ارتباط با سرویس"
                )
                raise ValueError(error_message)

            return data
        except requests.RequestException as e:
            raise ConnectionError(f"خطا در ارتباط با سرویس: {str(e)}")

    def _generate_state(self):
        return secrets.token_urlsafe(32)

    def _get_or_create_user(self, user_info):
        """پیدا کردن یا ساخت کاربر"""
        from ...models import SocialAccount

        # 1. پیدا کردن با حساب سوشیال
        social_account = (
            SocialAccount.objects.filter(
                provider=self.provider,
                provider_id=user_info["provider_id"],
            )
            .select_related("user")
            .first()
        )

        if social_account:
            return social_account.user, False

        # 2. پیدا کردن با ایمیل
        user = None
        if user_info.get("email"):
            user = User.objects.filter(email=user_info["email"]).first()

        # 3. ساخت کاربر جدید
        if not user:
            username = self._generate_unique_username(user_info.get("username", ""))

            user = User.objects.create_user(
                username=username,
                email=user_info.get("email", f"{username}@{self.provider}.com"),
                password=None,
                first_name=user_info.get("first_name", ""),
                last_name=user_info.get("last_name", ""),
                is_email_verified=True,
            )

        return user, True

    def _generate_unique_username(self, base_username):
        """تولید نام کاربری یکتا"""
        username = base_username or f"user_{self.provider}"
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    def _save_social_account(self, user, user_info, token_data):
        """ذخیره اطلاعات حساب سوشیال"""
        from ...models import SocialAccount

        SocialAccount.objects.update_or_create(
            user=user,
            provider=self.provider,
            defaults={
                "provider_id": str(user_info["provider_id"]),
                "provider_username": user_info.get("username", ""),
                "email": user_info.get("email", ""),
                "avatar_url": user_info.get("avatar_url", ""),
                "access_token": token_data.get("access_token", ""),
                "refresh_token": token_data.get("refresh_token", ""),
                "extra_data": user_info,
            },
        )
