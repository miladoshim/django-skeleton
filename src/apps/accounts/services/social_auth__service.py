import datetime
import uuid
import logging
from django.db import transaction
import requests
from django.contrib.auth import get_user_model
from django.conf import settings

from apps.accounts.models import SocialAccount

User = get_user_model()
logger = logging.getLogger(__name__)


class SocialAuthService:

    def __init__(self, provider, code=None, token=None):
        self.provider = provider
        self.code = code
        self.token = token

        self.config = {
            "github": {
                "name": "GitHub",
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "user_url": "https://api.github.com/user",
                "emails_url": "https://api.github.com/user/emails",
                "scope": "user:email",
                "auth_header": "token",
                "client_id": settings.GITHUB_CLIENT_ID,
                "secret": settings.GITHUB_CLIENT_SECRET,
                "redirect": settings.GITHUB_REDIRECT_URI,
            },
            "google": {
                "name": "Google",
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "user_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "scope": "openid email profile",
                "auth_header": "Bearer",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect": settings.GOOGLE_REDIRECT_URI,
            },
            "gitlab": {
                "name": "GitLab",
                "authorize_url": "https://gitlab.com/oauth/authorize",
                "token_url": "https://gitlab.com/oauth/token",
                "user_url": "https://gitlab.com/api/v4/user",
                "scope": "read_user openid email",
                "auth_header": "Bearer",
                "client_id": settings.GITLAB_CLIENT_ID,
                "secret": settings.GITLAB_CLIENT_SECRET,
                "redirect": settings.GITLAB_REDIRECT_URI,
            },
        }

        if provider not in self.config:
            raise ValueError(f"Provider '{provider}' not supported")

        self.cfg = self.config[provider]

    def get_authorize_url(self, state):
        params = f"client_id={self.cfg['client_id']}&redirect_uri={self.cfg['redirect']}&scope={self.cfg['scope']}&state={state}"

        if self.provider == "google":
            params += "&response_type=code&prompt=select_account"
        elif self.provider == "github":
            params += "&response_type=code"
        elif self.provider == "gitlab":
            params += "&response_type=code"

        return f"{self.cfg['authorize_url']}?{params}"

    def login(self):

        if self.token:
            token = self.token
        else:
            token = self._exchange_code_for_token()

        user_data = self._get_user_info(token)

        user = self._get_or_create_user(user_data)

        self._save_social_account(user, token, user_data)

        return user, user_data

    def disconnect(self, user):

        SocialAccount.objects.filter(user=user, provider=self.provider).delete()

        return True

    def _exchange_code_for_token(self):

        data = {
            "client_id": self.cfg["client_id"],
            "client_secret": self.cfg["secret"],
            "code": self.code,
            "redirect_uri": self.cfg["redirect"],
        }

        if self.provider in ["google", "gitlab"]:
            data["grant_type"] = "authorization_code"

        try:
            response = requests.post(
                self.cfg["token_url"],
                data=data,
                headers={"Accept": "application/json"},
                timeout=30,
            )

            result = response.json()

            if "error" in result:
                error_msg = result.get(
                    "error_description", result.get("error", "error")
                )
                logger.error(f"Token error for {self.provider}: {error_msg}")
                raise ValueError(error_msg)

            logger.info(f"Token obtained for {self.provider}")
            return result["access_token"]

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise ConnectionError("خطا در اتصال به سرویس")

    def _get_user_info(self, token):

        headers = {"Authorization": f"{self.cfg['auth_header']} {token}"}

        try:
            response = requests.get(self.cfg["user_url"], headers=headers, timeout=30)

            data = response.json()

            if "message" in data and response.status_code != 200:
                raise ValueError(data["message"])

            return self._parse_user_data(data, token)

        except requests.RequestException as e:
            logger.error(f"User info error: {str(e)}")
            raise ConnectionError("خطا در دریافت اطلاعات کاربر")

    def _parse_user_data(self, data, token=None):
        """پردازش اطلاعات کاربر برای هر سرویس"""

        if self.provider == "github":
            email = data.get("email")

            if not email and token:
                email = self._get_github_email(token)

            name_parts = (data.get("name") or "").split()

            return {
                "provider_id": str(data.get("id")),
                "email": email,
                "username": data.get("login"),
                "first_name": name_parts[0] if name_parts else "",
                "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                "avatar": data.get("avatar_url", ""),
            }

        elif self.provider == "google":
            email = data.get("email", "")
            return {
                "provider_id": str(data.get("id")),
                "email": email,
                "username": email.split("@")[0] if email else "",
                "first_name": data.get("given_name", ""),
                "last_name": data.get("family_name", ""),
                "avatar": data.get("picture", ""),
            }

        elif self.provider == "gitlab":
            name_parts = (data.get("name") or "").split()
            return {
                "provider_id": str(data.get("id")),
                "email": data.get("email", ""),
                "username": data.get("username", ""),
                "first_name": name_parts[0] if name_parts else "",
                "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                "avatar": data.get("avatar_url", ""),
            }

    def _get_github_email(self, token):
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get(self.cfg["emails_url"], headers=headers, timeout=10)

            emails = response.json()

            if isinstance(emails, list):
                for email in emails:
                    if email.get("primary"):
                        return email.get("email")
                if emails:
                    return emails[0].get("email")

            return ""
        except Exception:
            return ""

    @transaction.atomic
    def _get_or_create_user(self, info):

        social = (
            SocialAccount.objects.filter(
                provider=self.provider,
                provider_id=info["provider_id"],
            )
            .select_related("user")
            .first()
        )

        if social:
            return social.user

        user = None
        if info.get("email"):
            user = User.objects.filter(email=info["email"]).first()

        if not user:
            # username = self._generate_username(info.get("username"))

            user = User.objects.create(
                # username=username,
                email=info.get("email", ""),
                first_name=info.get("first_name", ""),
                last_name=info.get("last_name", ""),
                password=None,
                is_active=True,
            )
            user.meta.last_login_at = datetime.datetime.now()
            user.meta.email_verified_at = datetime.datetime.now()
            user.meta.save()

            logger.info(f"New user created: {user.username}")

        return user

    def _generate_username(self, base):

        username = base or f"user_{self.provider}_{uuid.uuid4().hex[:6]}"

        if len(username) > 30:
            username = username[:30]

        original = username
        counter = 1

        while User.objects.filter(username=username).exists():
            suffix = f"_{counter}"
            username = f"{original[:30-len(suffix)]}{suffix}"
            counter += 1

        return username

    @transaction.atomic
    def _save_social_account(self, user, token, info):

        account, created = SocialAccount.objects.update_or_create(
            user=user,
            provider=self.provider,
            defaults={
                "provider_id": str(info["provider_id"]),
                "provider_username": info.get("username", ""),
                "provider_email": info.get("email", ""),
                "provider_avatar_url": info.get("avatar", ""),
                "access_token": token,
                "extra_data": info,
            },
        )

        logger.info(
            f"Social account {'created' if created else 'updated'}: {self.provider}"
        )
        return account
