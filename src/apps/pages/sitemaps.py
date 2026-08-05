from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "yearly"

    def items(self):
        return [
            "apps.pages:about",
            "apps.pages:contact",
            "apps.pages:faqs",
            "apps.pages:index",
        ]

    def location(self, item):
        return reverse(item)
