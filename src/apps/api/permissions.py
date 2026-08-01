from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user and request.user.is_superuser
        )


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user == obj.author.user
        )


class IsCoach(BasePermission):
    def has_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS or request.user and request.user.is_coach
        )
