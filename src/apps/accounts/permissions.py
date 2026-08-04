from django.contrib.auth.models import Permission
from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to non authenticated users.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated()


class CanEditPost(Permission):
    name = "Can edit any post"
    codename = "can_edit_post"
