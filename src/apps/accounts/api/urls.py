from django.urls import include, path

from apps.accounts.api.accounts_views import (
    FollowStatsAPIView,
    FollowStatusAPIView,
    FollowersListAPIView,
    FollowingListAPIView,
    SuggestionsAPIView,
    ToggleFollowAPIView,
    UserProfileAPIView,
)

from .auth_views import (
    SocialLoginAPIView,
    UserEmailRegisterView,
)

# from .accounts_views import ()

urlpatterns = [
    path("profile/", UserProfileAPIView.as_view(), name="user_profile_api"),
    # path("accounts/setting/", UserLoginView.as_view(), name="account_setting"),
    # path(
    #     "accounts/setting/change_password",
    #     UserLoginView.as_view(),
    #     name="account_setting",
    # ),
    # path("accounts/comments", UserLoginView.as_view(), name="account_setting"),
    path(
        "api/follow/<uuid:user_id>/",
        ToggleFollowAPIView.as_view(),
        name="api_toggle_follow",
    ),
    path(
        "api/follow/stats/<uuid:user_id>/",
        FollowStatsAPIView.as_view(),
        name="api_follow_stats",
    ),
    path(
        "api/follow/status/<uuid:user_id>/",
        FollowStatusAPIView.as_view(),
        name="api_follow_status",
    ),
    path(
        "api/followers/<uuid:user_id>/",
        FollowersListAPIView.as_view(),
        name="api_followers",
    ),
    path(
        "api/following/<uuid:user_id>/",
        FollowingListAPIView.as_view(),
        name="api_following",
    ),
    path("api/suggestions/", SuggestionsAPIView.as_view(), name="api_suggestions"),
    # Authentication
    path(
        "auth/email/register/",
        UserEmailRegisterView.as_view(),
        name="email_register_view",
    ),
    # path("auth/register/otp/request", UserLoginView.as_view(), name="register_view"),
    # path("auth/register/otp/verify", UserLoginView.as_view(), name="register_view"),
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
    # path("auth/login/", UserLoginView.as_view(), name="login_view"),
    # path("auth/logout/", UserLoginView.as_view(), name="logout"),
    # path(
    #     "password/forgot/mobile/",
    #     forgot_password_mobile,
    #     name="password_forgot_mobile_view",
    # ),
    # path(
    #     "password/forgot/mobile/reset/<str:mobile>/<str:reqid>/",
    #     forgot_password_mobile_reset,
    #     name="password_forgot_mobile_reset_view",
    # ),
    # path("auth/token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "api/auth/social/<str:provider>/",
        SocialLoginAPIView.as_view(),
        name="api_social_login",
    ),
]
