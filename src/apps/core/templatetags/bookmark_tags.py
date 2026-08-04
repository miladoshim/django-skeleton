# bookmark/templatetags/bookmark_tags.py
from django import template
from django.contrib.contenttypes.models import ContentType
from apps.core.services.bookmark_services import BookmarkService

register = template.Library()


@register.simple_tag(takes_context=True)
def is_bookmarked(context, obj):
    user = context["request"].user
    if user.is_authenticated:
        return BookmarkService.is_bookmarked(user, obj)
    return False


@register.simple_tag(takes_context=True)
def bookmark_url(context, obj):
    content_type = ContentType.objects.get_for_model(obj)
    return "{% url 'apps.core:bookmarks_toggle' content_type.id obj.id %}"


@register.inclusion_tag("bookmark/button.html", takes_context=True)
def bookmark_button(context, obj):
    user = context["request"].user
    is_bookmarked = (
        BookmarkService.is_bookmarked(user, obj) if user.is_authenticated else False
    )

    content_type = ContentType.objects.get_for_model(obj)

    return {
        "is_bookmarked": is_bookmarked,
        "object_id": obj.id,
        "content_type_id": content_type.id,
        "user": user,
        "next_url": context["request"].path,
    }
