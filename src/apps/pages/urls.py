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
    # path("", HomePageView.as_view(), name="home_view"),
    # path("about/", AboutView.as_view(), name="about_view"),
    # path("contact/", ContactCreateView.as_view(), name="contact_view"),
    # path("faqs/", FaqView.as_view(), name="faqs_view"),
    # path("search/", search, name="search"),
]
