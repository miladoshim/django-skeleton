from django.urls import path, include
from rest_framework import routers
from .views import PostListView, PostDetailView

app_name='blog'

router = routers.DefaultRouter()
# router.register(r'tags', views.UserViewSet)
# router.register(r'posts', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<str:slug>/', PostDetailView.as_view(), name='post_detail'),
    # # re_path(r'(?P<slug>[-\w]+)/',post_detail)
    
    # path('categories', CategoryListView.as_view(), name='blog_category_list'),
    # path('categories/<str:slug>', CategoryDetailView.as_view(), name='blog_category_detail'),
    
    # path('authors', AuthorListView.as_view(), name='author_list'),
    # path('authors/<pk>', AuthorDetailView.as_view(), name='author_detail'),
]
