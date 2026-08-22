from django.urls import path

from apps.accounts.views.account_views import (
    DashboardActiveSessionsView,
    DashboardView,
    DashboardSettingView,
    DashboardChangePasswordView,
    TerminateSessionView,
    ToggleFollowView,
    UserProfileView,
    UserProfilePostsView,
    UserProfileFollowersView,
    UserProfileFollowingView,
)

urlpatterns = [
    path("@<str:username>/", UserProfileView.as_view(), name="user_profile"),
    path(
        "@<str:username>/posts/",
        UserProfilePostsView.as_view(),
        name="user_profile_posts",
    ),
    path(
        "@<str:username>/followers/",
        UserProfileFollowersView.as_view(),
        name="user_profile_followers",
    ),
    path(
        "@<str:username>/following/",
        UserProfileFollowingView.as_view(),
        name="user_profile_following",
    ),
    path(
        "accounts/follow/<uuid:uuid>/",
        ToggleFollowView.as_view(),
        name="toggle_follow",
    ),
    path("accounts/", DashboardView.as_view(), name="dashboard_index"),
    path("accounts/setting/", DashboardSettingView.as_view(), name="dashboard_setting"),
    path(
        "accounts/setting/change_password/",
        DashboardChangePasswordView.as_view(),
        name="dashboard_setting_password",
    ),
    path(
        "accounts/sessions/",
        DashboardActiveSessionsView.as_view(),
        name="dashboard_sessions",
    ),
    path(
        "accounts/sessions/terminate/<int:session_id>/",
        TerminateSessionView.as_view(),
        name="terminate_session",
    ),
]
