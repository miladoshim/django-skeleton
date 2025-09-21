from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from filebrowser.sites import site

urlpatterns = [
    path('admin/filebrowser/', site.urls),
    path('grappelli/', include('grappelli.urls')),
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("django_components.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("unicorn/", include("django_unicorn.urls")),
    path('', include('pwa.urls')), 

] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# handler404 = error404_handler
