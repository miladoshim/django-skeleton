from django.urls import path

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
    ForgotPasswordView,
    UserLogoutView,
    EmailVerificationView,
)

urlpatterns = [
    path("register/", UserClassicRegisterView.as_view(), name="register_classic"),
    path(
        "email/verify/<str:uid>/<str:token>/",
        EmailVerificationView.as_view(),
        name="email_activation",
    ),
    # path(
    #     "register/otp/request/",
    #     UserOTPRegisterRequestView.as_view(),
    #     name="register_otp_view",
    # ),
    # path(
    #     "register/otp/verify/",
    #     UserOTPRegisterVerifyView.as_view(),
    #     name="register_otp_verify_view",
    # ),
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
    # path("register/otp/complete", UserLoginView.as_view(), name="register_view"),
    path("login/", UserLoginView.as_view(), name="login_classic"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password_forgot_view"),
    path(
        "password/forgot/done/",
        ForgotPasswordDoneView.as_view(),
        name="password_forgot_done_view",
    ),
    path(
        "password/reset/<str:uid>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
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
    path("login/<str:provider>/", SocialLoginView.as_view(), name="social_login"),
    path(
        "callback/<str:provider>/",
        SocialCallbackView.as_view(),
        name="social_callback",
    ),
    path(
        "social/accounts/",
        SocialAccountsListView.as_view(),
        name="social_accounts",
    ),
    path(
        "disconnect/<str:provider>/",
        SocialDisconnectView.as_view(),
        name="social_disconnect",
    ),
]
