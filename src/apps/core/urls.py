from django.urls import path
from django.contrib.sitemaps.views import sitemap as sitemaps_views
from django.views.decorators.cache import cache_page
from apps.blog.sitemaps import PostSitemap, CategorySitemap
from .views import RobotsTxtView


app_name = "core"

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
    path("robots.txt", RobotsTxtView.as_view(content_type="text/plain"), name="robots"),
    
    # path("faqs/", FaqsListView.as_view(), name="faq_list"),
]
