from import_export.resources import Resource as ImportExportResource
from .models import Post


class PostResource(ImportExportResource):
    class Meta:
        model = Post
        fields = ["id", "title", "slug", "author__username", "created_at"]
