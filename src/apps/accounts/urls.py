from django.urls import path
from apps.accounts.views.account_views import (
    DashboardView,
    DashboardSettingView,
    DashboardChangePasswordView,
    FollowersListView,
    FollowingListView,
    ToggleFollowView,
    UserProfileView,
)
from apps.accounts.views.auth_views import (
    ForgotPasswordDoneView,
    ForgotPasswordMobileResetView,
    ForgotPasswordMobileVerifyView,
    PasswordResetConfirmView,
    ResendOtpView,
    SocialAccountsListView,
    SocialCallbackView,
    SocialDisconnectView,
    SocialLoginView,
    UserLoginView,
    UserClassicRegisterView,
    UserOTPRegisterRequestView,
    UserOTPRegisterVerifyView,
    ForgotPasswordView,
    UserLogoutView,
    EmailVerificationView,
)

app_name = "apps.accounts"

urlpatterns = [
    # Account Setting
    path("@<str:username>/", UserProfileView.as_view(), name="user_profile"),
    path(
        "@<str:username>/posts/", UserProfileView.as_view(), name="user_profile_posts"
    ),
    path(
        "@<str:username>/followers/",
        UserProfileView.as_view(),
        name="user_profile_followers",
    ),
    path(
        "@<str:username>/following/",
        UserProfileView.as_view(),
        name="user_profile_following",
    ),
    path(
        "accounts/follow/<uuid:uuid>/",
        ToggleFollowView.as_view(),
        name="toggle_follow",
    ),
    path(
        "accounts/followers/<uuid:uuid>/",
        FollowersListView.as_view(),
        name="followers_list",
    ),
    path(
        "accounts/following/<uuid:uuid>/",
        FollowingListView.as_view(),
        name="following_list",
    ),
    path("accounts/", DashboardView.as_view(), name="dashboard_index"),
    path("accounts/setting/", DashboardSettingView.as_view(), name="dashboard_setting"),
    path(
        "accounts/setting/change_password/",
        DashboardChangePasswordView.as_view(),
        name="dashboard_setting_password",
    ),
    # Authentication
    path("auth/register/", UserClassicRegisterView.as_view(), name="register_classic"),
    path(
        "auth/email/verify/<str:uid>/<str:token>/",
        EmailVerificationView.as_view(),
        name="email_activation",
    ),
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
    path("auth/login/", UserLoginView.as_view(), name="login_classic"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password_forgot_view"),
    path(
        "password/forgot/done/",
        ForgotPasswordDoneView.as_view(),
        name="password_forgot_done_view",
    ),
    path(
        "password/forgot/mobile/verify/",
        ForgotPasswordMobileVerifyView.as_view(),
        name="password_forgot_mobile_verify_view",
    ),
    path(
        "password/forgot/mobile/reset/",
        ForgotPasswordMobileResetView.as_view(),
        name="password_forgot_mobile_reset_view",
    ),
    path(
        "password/forgot/mobile/resend/",
        ResendOtpView.as_view(),
        name="password_forgot_mobile_resend",
    ),
    path(
        "auth/password/reset/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/login/<str:provider>/", SocialLoginView.as_view(), name="social_login"),
    path(
        "auth/callback/<str:provider>/",
        SocialCallbackView.as_view(),
        name="social_callback",
    ),
    path(
        "auth/social/accounts/",
        SocialAccountsListView.as_view(),
        name="social_accounts",
    ),
    path(
        "auth/disconnect/<str:provider>/",
        SocialDisconnectView.as_view(),
        name="social_disconnect",
    ),
]
