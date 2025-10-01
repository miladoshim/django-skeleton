from django_filters import FilterSet
from rest_framework import filters
from apps.blog.models import Post

class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = ('title', 'body')
        
        
class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock=0)