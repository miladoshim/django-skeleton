from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    CategoryListView,
    CategoryDetailView,
    PostCommentCreateView,
)

app_name = "apps.blog"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("<str:slug>/", PostDetailView.as_view(), name="post_detail"),
    path(
        "<slug:slug>/comment/",
        PostCommentCreateView.as_view(),
        name="post_comment_create",
    ),
    path("categories", CategoryListView.as_view(), name="category_list"),
    path("categories/<str:slug>", CategoryDetailView.as_view(), name="category_detail"),
]
