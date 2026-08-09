import hashlib
import json
from typing import Any
from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from jalali_date import datetime2jalali
from persiantools.jdatetime import JalaliDate

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context["request"].path
    if path == pattern:
        return "active"
    return ""


@register.filter("jalali")
def jalali(value):
    return datetime2jalali(value).strftime("%y/%m/%d _ %H:%M:%S")


@register.filter(name="custom_date")
def custom_date(value, arg="%c"):
    return JalaliDate(value, locale=("fa")).strftime("%c")


# {{ my_date|custom_date:"d F Y" }}


@register.simple_tag
def settings_value(name):
    return mark_safe(getattr(settings, name, ""))


@register.filter
def json_dumps(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


@register.filter
def md5(value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()


@register.filter
def format_price(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", "٬")
    except (ValueError, TypeError):
        return value


# @register.simple_tag(takes_context=True)
# def is_bookmarked_tag(context, obj):
#     request = context.get("request")
#     if not request or not request.user.is_authenticated:
#         return False
#     return is_bookmarked(request.user, obj)


# @register.simple_tag(takes_context=True)
# def webp(context, img_url):
#     static_path = settings.STATIC_URL + img_url

#     try:
#         request = context["request"]

#         if "image/webp" in request.META.get("HTTP_ACCEPT", ""):
#             webp_static_path = settings.STATIC_URL + img_url.rsplit(".", 1)[0] + ".webp"

#             web_file_path = os.path.join(
#                 settings.APPS_DIR, "static", img_url.rsplit(".", 1)[0] + ".webp"
#             )
#             if os.path.exists(web_file_path):
#                 return web_file_path
#             else:
#                 convert_to_webp(os.path.join(settings.APPS_DIR, "static", img_url))
#                 return webp_static_path
#     except KeyError:
#         return static_path


# @register.inclusion_tag('comment/comment/comments.html')
# def render_comments(request, obj, settings_slug):
#     context = {
#         'object': obj,
#         'request': request,
#         'settings': CommentSettings.objects.get(slug=settings_slug),
#         'object_info': {
#             'app_name': type(obj)._meta.app_label,
#             'model_name': type(obj).__name__,
#             'content_type': ContentType.objects.get_for_model(obj),
#             'object_id': obj.id
#         }
#     }
#     return context
