from django.urls import include, path

app_name = "apps.accounts"

urlpatterns = [
    path("", include("apps.accounts.urls.account_urls")),
    path("auth/", include("apps.accounts.urls.auth_urls")),
]
