from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from .models import (
    OtpRequest,
    UserMeta,
    UserProfile,
)

User = get_user_model()


@admin.action(description="Mark selected users as verified")
def mark_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "avatar", "gender", "created_at"]
    list_display_links = ["id", "user"]
    search_fields = ["user"]
    can_delete = False
    fk_name = "user"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@admin.register(UserMeta)
class UserMetaAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "updated_at", "created_at"]
    list_display_links = ["id", "user"]
    search_fields = ["user"]
    can_delete = False
    fk_name = "user"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=...):
        return False

    def has_delete_permission(self, request, obj=...):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = User
    list_display = [
        "id",
        "username",
        "first_name",
        "last_name",
        "mobile",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "role",
        "created_at",
    ]
    list_display_links = ["id", "username", "mobile"]
    search_fields = ["mobile", "email", "first_name", "last_name"]
    list_filter = ["is_staff", "is_active", "is_superuser", "role"]
    ordering = ["-created_at"]
    list_editable = ("role",)
    fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": (
                    (
                        "first_name",
                        "last_name",
                    ),
                    ("email", "mobile"),
                )
            },
        ),
        (
            "سطح دسترسی ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    ("role"),
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            "اطلاعات کاربر",
            {
                "fields": (
                    (
                        "first_name",
                        "last_name",
                    ),
                    (
                        "mobile",
                        "email",
                        "password1",
                    ),
                    ("role"),
                ),
            },
        ),
    )

    empty_value_display = "---"
    list_select_related = ["profile", "meta"]

    def combined_title(self, obj):
        return "{}-{}".format(obj.username, obj.get_full_name)

    combined_title.__name__ = "User title"


@admin.register(OtpRequest)
class OtpRequestAdmin(admin.ModelAdmin):
    list_display = [
        "request_id",
        "channel",
        "receiver",
        "password",
        "created_at",
        "expired_at",
    ]
    search_fields = ["receiver"]
    ordering = ["-expired_at"]
    readonly_fields = ["request_id", "password"]
    empty_value_display = "---"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
