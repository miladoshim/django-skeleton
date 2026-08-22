import json
import hashlib
from typing import Any
from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from jalali_date import datetime2jalali
from persiantools.jdatetime import JalaliDate

from apps.core.services.bookmark_service import BookmarkService
from apps.core.services.like_service import LikeService

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname, *args):
    try:
        pattern = reverse(pattern_or_urlname, args=args)
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


@register.filter
def disabled_attributes(user):
    if user.meta.email_verified_at:
        return "disabled readonly"
    return ""


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


@register.filter
def is_liked(obj, user):
    if not user.is_authenticated:
        return False
    return LikeService(user).is_liked(obj)


@register.filter
def is_bookmarked(obj, user):
    if not user.is_authenticated:
        return False
    return BookmarkService(user).is_bookmarked(obj)


@register.simple_tag
def like_count(obj):
    return obj.likes_count


@register.simple_tag
def bookmark_count(obj):
    return obj.bookmarks_count
