from django.urls import path
from django.contrib.sitemaps.views import sitemap as sitemaps_views
from django.views.decorators.cache import cache_page
from apps.blog.sitemaps import PostSitemap, CategorySitemap
from .views import HomePageView

app_name = "apps.pages"

sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        cache_page(86400)(sitemaps_views),
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("", HomePageView.as_view(), name="home_view"),
]
