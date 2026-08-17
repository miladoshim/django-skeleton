import hashlib
import os
import pathlib
import uuid
from uuid import uuid4
import functools
from django.core.cache import cache
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_redis import get_redis_connection
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from persian_tools import digits, separator
from PIL import Image, ImageDraw, ImageFont
from rest_framework.views import exception_handler
from rest_framework_simplejwt.tokens import RefreshToken


def image_folder(instance, filename):
    return "photos/{}.webp".format(uuid.uuid4().hex)


def write_watermark(input_path, output_path, text="Cocooned"):
    photo = Image.open(input_path)
    w, h = photo.size
    drawing = ImageDraw.Draw(photo)
    text = f"{text}"
    font = ImageFont.truetype("TlwgTypo-Bold.ttf", 68)
    text_w, text_h = drawing.text(text, font)
    pos = w - text_w, (h - text_h) - 50
    c_text = Image.new("RGB", (text_w, text_h), color="#000")
    drawing.text((0, 0), text, fill="#fff", font=font)

    c_text.putalpha(100)
    photo.paste(c_text, pos, c_text)
    photo.save(f"images/{output_path}.png")
    return


def number_to_fa(number):
    return digits.convert_to_fa(number)


def number_to_word(number):
    return digits.convert_to_word(number)


def number_to_separator(number):
    return separator.add(number)


def card_number_bank_data(card_number):
    return card_number.bank_data(card_number)


def phone_number_normalize(phone_number):
    return phone_number.normalize(phone_number)


def generate_upload_filename(instance, filename):
    ext = filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/", random_filename)


def unique_avatar_path(instance, filename):
    ext = filename.split(".")[-1]  # Get file extension (e.g., 'jpg')
    filename = f"{uuid.uuid4()}.{ext}"  # e.g., 'a1b2c3... .jpg'
    return f"avatars/{filename}"  # Stored in MEDIA_ROOT/avatars/<uuid>.jpg


def generate_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    random_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/", random_filename)


def file_generate_name(original_file_name):
    extension = pathlib.Path(original_file_name).suffix

    return f"{uuid4().hex}{extension}"


def invalidate_pattern(pattern, connection="default"):
    conn = get_redis_connection("default")
    keys = conn.keys(f"*{pattern}*")
    if keys:
        conn.delete(*keys)


def get_user_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def cache_view(timeout=60 * 15, vary_on_user=True):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # تولید کلید کش
            key = f"view_{request.path}_{request.GET.urlencode()}"
            if vary_on_user and request.user.is_authenticated:
                key = f"{key}_user_{request.user.id}"

            result = cache.get(key)
            if result is not None:
                return result

            result = view_func(request, *args, **kwargs)
            cache.set(key, result, timeout)
            return result

        return wrapper

    return decorator


# def print_sql(queryset: QuerySet):
#     formatted = format(str(queryset.query), reindent=True)
#     print(highlight(formatted, PostgresLexer(), TerminalFormatter()))


# def get_current_users():
#     active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
#     user_id_list = []
#     for session in active_sessions:
#         data = session.get_decoded()
#         user_id_list.append(data.get('_auth_user_id', None))
#     # Query all logged in users based on id list
#     return User.objects.filter(id__in=user_id_list)


class Helpers:
    @staticmethod
    def get_ckeditor_filename(filename, request):
        return filename.upper()

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @staticmethod
    def generate_filename(instance, filename):
        ext = filename.split(".")[-1]
        random_filename = f"{uuid.uuid4()}.{ext}"
        return os.path.join("avatars/", random_filename)

    @staticmethod
    def generate_number(*args, **kwargs):
        return str(uuid.uuid4()).split("-")[0].upper()

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

    @staticmethod
    def hash_filename(instance, filename):
        hash_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
        file_extension = filename[filename.rfind(".") :]
        return f"{hash_name}{file_extension}"

    @staticmethod
    def get_user_ip(request):
        ip_address = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip_address:
            ip_address = ip_address.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

    @staticmethod
    def image_ext_validator():
        return FileExtensionValidator(["png", "jpg", "jpeg"])


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    return response


def get_real_ip_addr(request):

    real_ip = request.META.get("REAL_IP")
    remote_addr = request.META.get("REMOTE_ADDR")
    if real_ip:
        ip = real_ip
    elif remote_addr:
        ip = remote_addr
    else:
        ip = request.META.get("REAL_IP")
    return ip


def generate_unique_uuid():
    return str(uuid.uuid4())


def string_to_model(model_name):
    ct = ContentType.objects.get(model=model_name.lower())
    return ct.model_class()


def get_model_name(model, attr=None):
    if isinstance(model, str):
        model = string_to_model(model)
    if attr:
        if hasattr(model._meta, attr):
            return getattr(model._meta, attr)
        elif attr == "verbose_name_plural":
            return get_model_name(model, "verbose_name")
        else:
            return model.__name__
    else:
        return model.__name__


def get_kwarg_object(model_name, pk):
    return string_to_model(model_name).objects.get(pk=pk)


class TokenGenerator(PasswordResetTokenGenerator):
    pass


token_generator = TokenGenerator()


def full_url(view_name, *args, **kwargs):

    protocol = "https" if not settings.DEBUG else "http"
    domain = Site.objects.get_current().domain

    return f"{protocol}://{domain}{reverse(view_name, args=args, kwargs=kwargs)}"
