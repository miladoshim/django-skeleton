from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"
    
    def items(self):
        return ["contact", "faqs"]

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def location(self, item):
        return item.get_absolute_url()


class PostSitemap(Sitemap):
    protocol = "https"
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated_at
