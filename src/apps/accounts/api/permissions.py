from django.contrib.auth.models import Permission
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to non authenticated users.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated()


class CanEditPost(Permission):
    name = "Can edit any post"
    codename = "can_edit_post"


class IsSelfOrReadOnly(BasePermission):
    """
    فقط خود کاربر میتواند پروفایل خود را ویرایش کند
    دیگران فقط میتوانند ببینند
    """

    def has_object_permission(self, request, view, obj):
        # اجازه خواندن به همه
        if request.method in SAFE_METHODS:
            return True

        # اجازه ویرایش فقط به خود کاربر یا ادمین
        return obj == request.user or request.user.is_staff


class IsSelfOrStaff(BasePermission):
    """
    فقط خود کاربر یا ادمین میتواند دسترسی داشته باشد
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsActiveUser(BasePermission):
    """
    فقط کاربران فعال میتوانند دسترسی داشته باشند
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )
