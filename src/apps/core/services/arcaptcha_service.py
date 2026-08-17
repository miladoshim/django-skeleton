# apps/common/services.py
import requests
import json
from django.conf import settings


class ARCaptchaService:
    @staticmethod
    def verify(token):
        if not token:
            return False

        try:
            response = requests.post(
                settings.ARCAPTCHA_VERIFY_URL,
                data=json.dumps(
                    {
                        "site_key": settings.ARCAPTCHA_SITE_KEY,
                        "secret_key": settings.ARCAPTCHA_SECRET_KEY,
                        "challenge_id": token,
                    }
                ),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            return response.json().get("success", False)
        except Exception:
            return False
