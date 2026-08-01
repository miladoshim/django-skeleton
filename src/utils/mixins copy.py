import hashlib
from django.core.cache import cache
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from jalali_date import datetime2jalali
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import AccessMixin
from rest_framework import status
from rest_framework.response import Response
from apps.blog.models import Post
from apps.core.managers import SoftDeleteManager
from utils.enums import PublishStatusChoice


class BaseAdminMixin:
    empty_value_display = "---"
    date_hierarchy = "created_at"

    @admin.display(description="تاریخ ایجاد", ordering="created_at")
    def get_created_at(self, obj):
        return datetime2jalali(obj.created_at).strftime("%Y/%m/%d _ %H:%M:%S")

    @admin.display(description="تاریخ بروزرسانی", ordering="updated_at")
    def get_updated_at(self, obj):
        return datetime2jalali(obj.updated_at).strftime("%Y/%m/%d _ %H:%M:%S")


class BootstrapHelperForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = ["CheckboxInput", "ClearableFileInput", "FileInput", "DatePickerInput"]
        for field in self.fields:
            widget_name = self.fields[field].widget.__class__.__name__
            if widget_name not in fields:
                self.fields[field].widget.attrs.update({"class": "form-control"})


class FieldsMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.fields = []
        elif request.user.is_author:
            self.fields = []
        else:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class FormValidMixin:
    def form_valid(self, form):
        if self.request.user.is_superuser:
            form.save()
        else:
            self.obj = form.save(commit=False)
            self.obj.author = self.request.user
            self.obj.status = PublishStatusChoice.draft.value
        return super().form_valid(form)


class AuthorAccessMixin:
    def dispatch(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        if post.author == request.user or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)


class SuperUserAccessMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)


class HasAuthorMixin:
    pass


class IsUnAuthenticatedMixin(UserPassesTestMixin):
    """
    Allows access only to non authenticated users.
    """

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect("apps.pages:home_view")


class CommentMixin(LoginRequiredMixin):
    def has_object_permission(self, obj):
        return True if obj.user == self.request.user else False

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if self.has_object_permission(obj):
            return obj
        else:
            raise PermissionDenied("Access Denied : update or delete comment.")


class CacheMixin:
    """Caching Api Views"""

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


class JsonableResponseMixin:
    """
    Mixin to add JSON support to a form.
    Must be used with an object-based FormView (e.g. CreateView).
    """

    accepted_media_types = ["text/html", "application/json"]

    def dispatch(self, request, *args, **kwargs):
        if request.get_preferred_type(self.accepted_media_types) is None:
            # No format in common.
            return HttpResponse(
                status_code=406, headers={"Accept": ",".join(self.accepted_media_types)}
            )

        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        accepted_type = self.request.get_preferred_type(self.accepted_media_types)
        if accepted_type == "text/html":
            return response
        elif accepted_type == "application/json":
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        accepted_type = self.request.get_preferred_type(self.accepted_media_types)
        if accepted_type == "text/html":
            return response
        elif accepted_type == "application/json":
            data = {
                "pk": self.object.pk,
            }
            return JsonResponse(data)


def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


class GroupRequiredMixin(AccessMixin):
    group_required = []  # List of groups allowed to access the view

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user_groups = request.user.groups.values_list("name", flat=True)
        if not any(group in user_groups for group in self.group_required):
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
