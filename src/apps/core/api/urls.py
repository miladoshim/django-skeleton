from django.urls import include, path
from rest_framework import routers

from apps.core.api.views import TagViewSet

router = routers.DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("", include(router.urls)),
]
