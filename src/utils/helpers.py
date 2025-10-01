import uuid
import os
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import exception_handler


class Helpers:
    @staticmethod
    def get_ckeditor_filename(filename, request):
        return filename.upper()

    @staticmethod
    def send_activation_account_mail():
        pass
    
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    @staticmethod
    def generate_filename(instance, filename):
        ext = filename.split(".")[-1]
        random_filename = f"{uuid.uuid4()}.{ext}"
        return os.path.join('avatars/',random_filename)

    @staticmethod
    def get_ip_address(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @staticmethod
    def generate_number(*args, **kwargs):
        return str(uuid.uuid4()).split('-')[0].upper()

    @staticmethod
    def create_unique_slug(instance, new_slug=None):
        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(instance.title, allow_unicode=True)

        instanceClass = instance.__class__
        qs = instanceClass.objects.filter(slug=slug)

        if qs.exists():
            new_slug = f"{slug}-{qs.first().id}"
            return Helpers.create_unique_slug(instance, new_slug)

        return slug

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first, 
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response

class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()
