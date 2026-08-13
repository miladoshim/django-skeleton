# apps/accounts/services/github.py
from .oauth_service_base import BaseSocialService


class GitHubService(BaseSocialService):
    """سرویس گیت هاب"""

    provider = "github"
    authorize_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    user_api_url = "https://api.github.com/user"
    emails_api_url = "https://api.github.com/user/emails"

    client_id_key = "GITHUB_CLIENT_ID"
    client_secret_key = "GITHUB_CLIENT_SECRET"
    redirect_uri_key = "GITHUB_REDIRECT_URI"

    def _update_authorize_params(self, params):
        params["scope"] = "user:email"

    def _update_token_data(self, data):
        pass  # گیت هاب از grant_type پشتیبانی نمیکند

    def _get_user_headers(self, access_token):
        return {"Authorization": f"token {access_token}"}

    def _parse_user_data(self, data):
        # دریافت ایمیل اگر نبود
        email = data.get("email")
        if not email:
            headers = {"Authorization": f"token {self._last_access_token}"}
            emails_data = self._make_request(
                "GET", self.emails_api_url, headers=headers
            )
            email = self._extract_primary_email(emails_data)

        name = data.get("name") or ""
        name_parts = name.split()

        return {
            "provider_id": str(data.get("id")),
            "username": data.get("login"),
            "email": email or f"{data.get('login')}@github.com",
            "first_name": name_parts[0] if name_parts else "",
            "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
            "avatar_url": data.get("avatar_url"),
        }

    def _extract_primary_email(self, emails_data):
        """دریافت ایمیل اصلی"""
        if isinstance(emails_data, list):
            for email_data in emails_data:
                if email_data.get("primary"):
                    return email_data.get("email")
            if emails_data:
                return emails_data[0].get("email")
        return ""
