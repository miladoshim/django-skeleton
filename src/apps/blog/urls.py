from django.urls import path
from django.views.decorators.cache import cache_page
from .views import PostListView, PostDetailView, CategoryListView, CategoryDetailView

app_name = "blog"

urlpatterns = [
    path("", cache_page(60 * 15)(PostListView.as_view()), name="post_list"),
    path("<str:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("categories", CategoryListView.as_view(), name="category_list"),
    path("categories/<str:slug>", CategoryDetailView.as_view(), name="category_detail"),
    
    # path('authors', AuthorListView.as_view(), name='author_list'),
    # path('authors/<pk>', AuthorDetailView.as_view(), name='author_detail'),
]
