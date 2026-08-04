from django.urls import path
from django.views.decorators.cache import cache_page
from .views import (
    PostListView,
    post_detail,
    CategoryListView,
    CategoryDetailView,
)

app_name = "apps.blog"

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    # path("", cache_page(60 * 15)(PostListView.as_view()), name="post_list"),
    path(
        "<str:slug>/", post_detail, name="post_detail"
    ),
    path("categories", CategoryListView.as_view(), name="category_list"),
    path("categories/<str:slug>", CategoryDetailView.as_view(), name="category_detail"),
]
