from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.action(description="Mark selected users as verified")
def mark_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = User
    list_display = [
        "username",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
        "date_joined",
    ]
    search_fields = [
        "username",
        "email",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    ordering = ["email"]
    fieldsets = (
        (
            "اطلاعات اولیه",
            {
                "fields": (
                    (
                        "first_name",
                        "last_name",
                    ),
                    "email",
                    "password",
                )
            },
        ),
        (
            "سطح دسترسی ها",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    add_fieldsets = (None, {"fields": ("email",)})
    empty_value_display = "---"

    def combined_title(self, obj):
        return "{}-{}".format(obj.username, obj.email)

    combined_title.__name__ = "User title"

    class Meta:
        pass
