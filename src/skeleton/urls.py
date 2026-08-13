from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from azbankgateways.urls import az_bank_gateways_urls

urlpatterns = [
    path("admin/", include("django_admin_trap.urls")),
    path("secret/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("", include("apps.pages.urls")),
    path("", include("apps.accounts.urls")),
    path("blog/", include("apps.blog.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("", include("pwa.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("bankgateways/", az_bank_gateways_urls()),
    path("taggit/", include("taggit_selectize.urls")),
    path("schema-viewer/", include("schema_viewer.urls")),
]


if not settings.TESTING:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
