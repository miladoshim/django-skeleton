from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.models import User as BaseAuthUser, Group as BaseAuthGroup

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

from .models import User

# admin.site.unregister(BaseAuthUser)
admin.site.unregister(BaseAuthGroup)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


# @admin.register(User)
# class UserAdmin(ImportExportModelAdmin):
#     # add_form = CustomUserCreationForm
#     # form = CustomUserChangeForm
#     model = User
#     list_display = ['username', 'email', 'mobile', 'is_staff', 'is_superuser']
#     search_fields = ['username', 'email', 'mobile']
#     list_filter = ['is_staff', 'is_superuser']
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('mobile',)}),
#     )
#     add_fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('mobile',)})
#     )
#     class Meta:
#         pass


@admin.register(BaseAuthGroup)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
