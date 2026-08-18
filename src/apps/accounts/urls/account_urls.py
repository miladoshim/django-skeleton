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

urlpatterns = [
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
]
