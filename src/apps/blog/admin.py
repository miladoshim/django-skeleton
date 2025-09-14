from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from apps.blog.models import Category, Tag, Post
from apps.blog.resources import PostResource


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin, ExportActionMixin):
    list_display = ["id", "title", "slug"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    list_display = ["id", "title", "published_status", "created_at"]
    list_filter = ["published_status", "created_at"]
    #     search_fields = ['title', 'author__username']
    list_display_links = ["id", "title"]
    #     inlines = [CommentInline]
    prepopulated_fields = {"slug": ["title"]}
    fields = ["title", "body", "published_status"]


#     fieldsets = (
#         (None, {'fields': ('title','slug', 'body','thumbnail', 'author', 'category')}),
#         ("وضعیت", {'fields': ('published_status',)})
#     )
#     # filter_horizontal = ['tags']
#     # resource_class = PostResource

#     def tags_to_str(self, obj):
#         return ", ".join(tag.title for tag in obj.tags.all())

#     tags_to_str.short_description = _('برسب ها')

# def get_queryset(self, request):
#     return super().get_queryset(request).prefetch_related('tags')

# def tag_list(self, obj):
#     return u", ".join(o.name for o in obj.tags.all())


# @admin.register(RecyclePost)
# class PostAdmin(admin.ModelAdmin):

#     actions = ['recover']

#     def get_queryset(self, request):
#         return RecyclePost.deleted.filter(is_deleted=True)

#     @admin.action(description='Recover deleted item')
#     def recover(self, request, queryset):
#         queryset.update(is_deleted=False, deleted_at=None)

#     @admin.action(description="Draft posts to published")
#     def draft_to_published_posts(self, request, queryset):
#         rows_updated = queryset.update(status="p")
#         if rows_updated == 1:
#             message_bit = 'منتشر شد.'
#         else:
#             message_bit = 'منتشر شدند.'
#         self.message_user(request, "{} مقاله {}".format(
#             rows_updated, message_bit))

#     @admin.action(description="Published posts to draft")
#     def published_to_draft_posts(self, request, queryset):
#         queryset.update(status="d")


@admin.register(Category)
class CategoryAdmin(TreeAdmin):
    form = movenodeform_factory(Category)
    prepopulated_fields = {"slug": ["name"]}
