from .oauth_service_base import BaseSocialService
import requests


class GoogleService(BaseSocialService):
    """سرویس گوگل"""

    provider = "google"
    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    user_api_url = "https://www.googleapis.com/oauth2/v2/userinfo"

    client_id_key = "GOOGLE_CLIENT_ID"
    client_secret_key = "GOOGLE_CLIENT_SECRET"
    redirect_uri_key = "GOOGLE_REDIRECT_URI"

    def _update_authorize_params(self, params):
        params["scope"] = "openid email profile"
        params["prompt"] = "select_account"

    def _parse_user_data(self, data):
        return {
            "provider_id": str(data.get("id")),
            "username": data.get("email", "").split("@")[0],
            "email": data.get("email"),
            "first_name": data.get("given_name", ""),
            "last_name": data.get("family_name", ""),
            "avatar_url": data.get("picture", ""),
        }
