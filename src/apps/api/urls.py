from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = "apps.api"


urlpatterns = [
    path("", include("apps.accounts.api.urls")),
    path("", include("apps.core.api.urls")),
    path("blog/", include("apps.blog.api.urls")),
    path("financial/", include("apps.financial.api.urls")),
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
