from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from apps.accounts.views.account_views import (
    DashboardView,
    DashboardSettingView,
    DashboardChangePasswordView,
)
from apps.accounts.views.auth_views import (
    UserLoginView,
    UserClassicRegisterView,
    UserOTPRegisterRequestView,
    UserOTPRegisterVerifyView,
    ForgotPasswordView,
)

app_name = "apps.accounts"

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    # Account Setting
    path("accounts/", DashboardView.as_view(), name="dashboard_index"),
    path("accounts/setting/", DashboardSettingView.as_view(), name="dashboard_setting"),
    path(
        "accounts/setting/change_password/",
        DashboardChangePasswordView.as_view(),
        name="dashboard_setting_password",
    ),
    # path("accounts/comments", UserLoginView.as_view(), name="account_setting"),
    # # Authentication
    path("auth/register/", UserClassicRegisterView.as_view(), name="register_view"),
    path(
        "auth/register/otp/request/",
        UserOTPRegisterRequestView.as_view(),
        name="register_otp_view",
    ),
    path(
        "auth/register/otp/verify/",
        UserOTPRegisterVerifyView.as_view(),
        name="register_otp_verify_view",
    ),
    # path(
    #     "register/otp/verify/<str:mobile>/<str:reqid>/",
    #     user_register_otp_verify,
    #     name="register_otp_verify_view",
    # ),
    # path(
    #     "register/otp/complete/<str:mobile>/<str:reqid>/",
    #     user_register_otp_complete,
    #     name="register_otp_complete_view",
    # ),
    # path("auth/register/otp/complete", UserLoginView.as_view(), name="register_view"),
    path("auth/login/", UserLoginView.as_view(), name="login_view"),
    # path("auth/logout/", UserLoginView.as_view(), name="logout"),
    path(
        "password/forgot/",
        ForgotPasswordView.as_view(),
        name="password_forgot_view",
    ),
    # path(
    #     "password/forgot/mobile/reset/<str:mobile>/<str:reqid>/",
    #     forgot_password_mobile_reset,
    #     name="password_forgot_mobile_reset_view",
    # ),
    # path("auth/token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
