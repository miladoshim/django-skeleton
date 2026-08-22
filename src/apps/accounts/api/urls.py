from django.urls import path
from apps.accounts.api.accounts_views import (
    FollowStatsAPIView,
    FollowStatusAPIView,
    FollowersListAPIView,
    FollowingListAPIView,
    FollowSuggestionsAPIView,
    ToggleFollowAPIView,
    UserPostsAPIView,
    UserProfileAPIView,
    UserChangePasswordAPIView,
    UserProfileUpdateAPIView,
)
from .auth_views import (
    SocialLoginAPIView,
    UserEmailRegisterView,
)

urlpatterns = [
    path("profile/", UserProfileAPIView.as_view(), name="user_profile_api"),
    path("accounts/update/", UserProfileUpdateAPIView.as_view(), name="account_update"),
    path(
        "accounts/change_password/",
        UserChangePasswordAPIView.as_view(),
        name="account_change_password",
    ),
    path("accounts/posts/", UserPostsAPIView.as_view(), name="account_posts"),
    path(
        "profile/friends/<uuid:uuid>/",
        ToggleFollowAPIView.as_view(),
        name="api_toggle_follow",
    ),
    path(
        "profile/friends/stats/<uuid:uuid>/",
        FollowStatsAPIView.as_view(),
        name="api_follow_stats",
    ),
    path(
        "profile/friends/status/<uuid:uuid>/",
        FollowStatusAPIView.as_view(),
        name="api_follow_status",
    ),
    path(
        "profile/friends/followers/<uuid:uuid>/",
        FollowersListAPIView.as_view(),
        name="api_followers",
    ),
    path(
        "profile/friends/following/<uuid:uuid>/",
        FollowingListAPIView.as_view(),
        name="api_following",
    ),
    path(
        "profile/friends/followers/suggestions/",
        FollowSuggestionsAPIView.as_view(),
        name="api_suggestions",
    ),
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
