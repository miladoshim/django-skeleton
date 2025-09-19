from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.text import slugify


def get_ckeditor_filename(filename, request):
    return filename.upper()


def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def create_unique_slug(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title, allow_unicode=True)

    instanceClass = instance.__class__
    qs = instanceClass.objects.filter(slug=slug)

    if qs.exists():
        new_slug = f"{slug}-{qs.first().id}"
        return create_unique_slug(instance, new_slug)

    return slug

class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()
