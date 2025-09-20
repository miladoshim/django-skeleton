from django.urls import path

from apps.blog.sitemaps import PostSitemap

app_name = 'core'

sitemaps = {
    'posts' : PostSitemap,
}

urlpatterns = [
    
]
