# apps/accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import MultipleObjectsReturned

User = get_user_model()


class EmailPhoneUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = str(username).strip().lower()

        try:
            user = User.objects.filter(
                Q(email__iexact=identifier)
                | Q(mobile__iexact=identifier)
                | Q(username__iexact=identifier)
            ).first()
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None

        if user and user.check_password(password) and self.user_can_authenticate(user):
            # user.register_login_attempt(success=True)

            return user
        return None

    def user_can_authenticate(self, user):
        """بررسی اینکه کاربر میتواند وارد شود"""
        is_active = getattr(user, "is_active", True)
        is_blocked = getattr(user, "is_blocked", False)
        return is_active and not is_blocked
