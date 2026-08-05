from django.urls import path
from apps.accounts.views.auth_views import (
    UserLoginView,
    forgot_password_mobile,
    forgot_password_mobile_reset,
    user_register_otp_complete,
    user_register_otp_verify,
)

app_name = "accounts"

urlpatterns = [
    # Account Setting
    path("accounts/", UserLoginView.as_view(), name="account_index"),
    path("accounts/setting/", UserLoginView.as_view(), name="account_setting"),
    path(
        "accounts/setting/change_password",
        UserLoginView.as_view(),
        name="account_setting",
    ),
    path("accounts/comments", UserLoginView.as_view(), name="account_setting"),
    # Authentication
    path("auth/register", UserLoginView.as_view(), name="register_view"),
    path("auth/register/otp/request", UserLoginView.as_view(), name="register_view"),
    path("auth/register/otp/verify", UserLoginView.as_view(), name="register_view"),
    path(
        "register/otp/verify/<str:mobile>/<str:reqid>/",
        user_register_otp_verify,
        name="register_otp_verify_view",
    ),
    path(
        "register/otp/complete/<str:mobile>/<str:reqid>/",
        user_register_otp_complete,
        name="register_otp_complete_view",
    ),
    path("auth/register/otp/complete", UserLoginView.as_view(), name="register_view"),
    path("auth/login/", UserLoginView.as_view(), name="login_view"),
    path("auth/logout/", UserLoginView.as_view(), name="logout"),
    path(
        "password/forgot/mobile/",
        forgot_password_mobile,
        name="password_forgot_mobile_view",
    ),
    path(
        "password/forgot/mobile/reset/<str:mobile>/<str:reqid>/",
        forgot_password_mobile_reset,
        name="password_forgot_mobile_reset_view",
    ),
]
