from django.contrib.sitemaps.views import sitemap as sitemaps_views
from django.urls import path
from django.views.decorators.cache import cache_page
from apps.academy.sitemaps import CourseSitemap, EpisodeSitemap
from apps.blog.sitemaps import CategorySitemap, PostSitemap
from apps.library.sitemaps import BookSitemap
from apps.shop.sitemaps import BrandSitemap, ProductCategorySitemap
from .views import (
    bookmarks_toggle,
    comment_reply,
    error404_handler,
    error500_handler,
)

app_name = "apps.core"

sitemaps = {
    "posts": PostSitemap,
    "categories": CategorySitemap,
    "courses": CourseSitemap,
    "episodes": EpisodeSitemap,
    "books": BookSitemap,
    "product_categories": ProductCategorySitemap,
    "brands": BrandSitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        cache_page(60)(sitemaps_views),
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # path("robots.txt", RobotsTxtView.as_view(content_type="text/plain"), name="robots"),
    path("bookmarks/toggle/", bookmarks_toggle, name="bookmarks_toggle"),
    path("bookmarks/remove/", bookmarks_toggle, name="bookmarks_remove"),
    path(
        "comment/reply/<int:object_id>/<str:object_type>/",
        comment_reply,
        name="comment_reply",
    ),
]


handler404 = error404_handler
handler500 = error500_handler
