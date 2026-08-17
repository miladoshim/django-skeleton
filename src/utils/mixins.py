import hashlib
from django.core.cache import cache
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import AccessMixin
from rest_framework.response import Response
from apps.blog.models import Post


class AuthorAccessMixin:
    def dispatch(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        if post.author == request.user or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)


class SuperUserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)


class IsUnAuthenticatedMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect("apps.pages:home_view")


class CacheMixin:
    cache_timeout = 60 * 15
    cache_key_prefix = "api"
    cache_vary_on_user = False

    def _generate_cache_key(self):
        prefix = self.cache_key_prefix

        if self.cache_vary_on_user:
            if self.request.user.is_authenticated:
                prefix = f"{prefix}_user_{self.request.user.id}"
            else:
                prefix = f"{prefix}_anon"

        if self.request.GET:
            query_hash = hashlib.md5(self.request.GET.urlencode().encode()).hexdigest()[
                :8
            ]
            prefix = f"{prefix}_{query_hash}"

        prefix = f"{prefix}_{self.request.method}"

        return prefix

    def get_cache_data(self):
        cache_key = self._generate_cache_key()
        return cache.get(cache_key)

    def set_cache_data(self, data):
        cache_key = self._generate_cache_key()
        cache.set(cache_key, data, self.cache_timeout)

    def get(self, request, *args, **kwargs):
        if hasattr(self, "get_cache_data"):
            cached = self.get_cache_data()
            if cached is not None:
                return Response(cached)

        response = super().get(request, *args, **kwargs)

        if hasattr(self, "set_cache_data") and response.status_code == 200:
            self.set_cache_data(response.data)

        return response


def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


class GroupRequiredMixin(AccessMixin):
    group_required = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user_groups = request.user.groups.values_list("name", flat=True)
        if not any(group in user_groups for group in self.group_required):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
