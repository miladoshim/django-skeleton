from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class LatestPostFeed(Feed):
    title = "Posts"
    link = "/blog/posts"
    description = "Latest Cocooned Blog Posts"

    def items(self):
        return Post.objects.order_by("-created_at")[:8]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.get_absolute_url()
