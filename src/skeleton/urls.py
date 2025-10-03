from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from filebrowser.sites import site
from azbankgateways.urls import az_bank_gateways_urls

urlpatterns = [
    path("admin/filebrowser/", site.urls),
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("blog/", include("apps.blog.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    # path('accounts/', include('allauth.urls')),
    path("api/v1/", include("apps.api.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("django_components.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("unicorn/", include("django_unicorn.urls")),
    path("", include("pwa.urls")),
    path("bankgateways/", az_bank_gateways_urls()),
    path('silk/', include('silk.urls', namespace='silk')),
] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# handler404 = error404_handler
