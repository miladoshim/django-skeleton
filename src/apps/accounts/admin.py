from django.contrib import admin
from django.contrib.auth.admin import (
    UserAdmin as BaseUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from django.contrib.auth.models import User as BaseAuthUser, Group as BaseAuthGroup
from import_export.admin import ImportExportModelAdmin, ExportActionMixin

from .models import User

# admin.site.unregister(BaseAuthUser)
admin.site.unregister(BaseAuthGroup)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = User
    list_display = ['username', 'email', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email',]
    list_filter = ['is_staff', 'is_superuser']
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     (None, {'fields': ('mobile',)}),
    # )
    # add_fieldsets = BaseUserAdmin.fieldsets + (
    #     (None, {'fields': ('mobile',)})
    # )
    class Meta:
        pass
