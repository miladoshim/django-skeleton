from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "apps.api"

router = routers.DefaultRouter()
# router.register(r"tags", TagViewSet, basename="tag")
# router.register(r"posts", PostViewSet, basename="post")
# router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("apps.accounts.urls")),
    path("blog/", include("apps.blog.urls")),
    path("financial/", include("apps.financial.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
