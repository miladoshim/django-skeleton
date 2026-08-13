# apps/accounts/services/gitlab.py
from .oauth_service_base import BaseSocialService


class GitLabService(BaseSocialService):
    """سرویس گیت لب"""

    provider = "gitlab"
    authorize_url = "https://gitlab.com/oauth/authorize"
    token_url = "https://gitlab.com/oauth/token"
    user_api_url = "https://gitlab.com/api/v4/user"

    client_id_key = "GITLAB_CLIENT_ID"
    client_secret_key = "GITLAB_CLIENT_SECRET"
    redirect_uri_key = "GITLAB_REDIRECT_URI"

    def _update_authorize_params(self, params):
        params["scope"] = "read_user openid email profile"

    def _parse_user_data(self, data):
        name = data.get("name") or ""
        name_parts = name.split()

        return {
            "provider_id": str(data.get("id")),
            "username": data.get("username"),
            "email": data.get("email"),
            "first_name": name_parts[0] if name_parts else "",
            "last_name": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
            "avatar_url": data.get("avatar_url"),
        }
