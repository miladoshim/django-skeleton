# apps/accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailMobileUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if not username or not password:
            return None
     
        identifier = str(username).strip().lower()

        user = self._find_user(identifier)

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
    
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

        print(user.email, password)
        if user and user.check_password(password):
            # user.register_login_attempt(success=True)
            return user
        return None

    def user_can_authenticate(self, user):
        is_active = getattr(user, "is_active", True)
        is_blocked = getattr(user, "is_blocked", False)
        return is_active and not is_blocked
    
    
    def _find_user(self, identifier):
        
        if '@' in identifier:
            return User.objects.filter(email__iexact=identifier).first()

        mobile = identifier
        if mobile and len(mobile) == 11:
            user = User.objects.filter(mobile=mobile).first()
            if user:
                return user

        return User.objects.filter(username__iexact=identifier).first()
