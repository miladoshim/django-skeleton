from django import template

register = template.Library()


@register.filter
def is_following(user, target_user):
    if not user or not user.is_authenticated:
        return False
    if not target_user:
        return False
    return user.is_following(target_user)


@register.filter
def is_followed_by(user, target_user):
    if not user or not user.is_authenticated:
        return False
    if not target_user:
        return False
    return user.is_followed_by(target_user)
