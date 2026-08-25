from django.urls import include, path
from rest_framework import routers

from apps.blog.api.views import PostViewSet, CategoryViewSet

router = routers.DefaultRouter()

router.register(r"posts", PostViewSet, basename="post")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]
