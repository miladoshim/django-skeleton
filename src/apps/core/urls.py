from django.urls import path

from apps.blog.sitemaps import PostSitemap

# app_name = 'apps.core'

sitemaps = {
    'posts' : PostSitemap,
}

urlpatterns = [
    
]
