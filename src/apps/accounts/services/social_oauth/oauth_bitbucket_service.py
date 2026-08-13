# 1. سرویس جدید بسازید
class BitbucketService(BaseSocialService):
    provider = "bitbucket"
    authorize_url = "https://bitbucket.org/site/oauth2/authorize"
    token_url = "https://bitbucket.org/site/oauth2/access_token"
    user_api_url = "https://api.bitbucket.org/2.0/user"

    client_id_key = "BITBUCKET_CLIENT_ID"
    client_secret_key = "BITBUCKET_CLIENT_SECRET"
    redirect_uri_key = "BITBUCKET_REDIRECT_URI"

    def _parse_user_data(self, data):
        return {
            "provider_id": str(data.get("uuid")),
            "username": data.get("username"),
            "email": data.get("email"),
            "first_name": data.get("display_name", "").split()[0],
            "last_name": "",
            "avatar_url": data.get("links", {}).get("avatar", {}).get("href", ""),
        }

    def _update_authorize_params(self, params):
        params["scope"] = "account email"


# 2. در settings.py تنظیمات را اضافه کنید
BITBUCKET_CLIENT_ID = "..."
BITBUCKET_CLIENT_SECRET = "..."
BITBUCKET_REDIRECT_URI = "..."

# 3. سرویس را ثبت کنید
ServiceRegistry.register("bitbucket", BitbucketService)
