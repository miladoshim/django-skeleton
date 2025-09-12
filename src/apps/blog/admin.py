from django.contrib import admin
from unfold.admin import ModelAdmin
from import_export.admin import ImportExportModelAdmin
from unfold.contrib.import_export.forms import ExportForm, ImportForm, SelectableFieldsExportForm

from apps.blog.models import Tag

@admin.register(Tag)
class TagAdmin(ModelAdmin, ImportExportModelAdmin):
    list_display = ['id', 'title', 'slug']
    import_form_class = ImportForm
    export_form_class = ExportForm
    search_fields = ['title']
    prepopulated_fields = {
            'slug' : ['title']
    }
    
# @admin.register(Post)
# class PostAdmin(ImportExportModelAdmin):
#     list_display = ['id', 'title', 'category',
#                     'author', 'published_status', 'created_at',]
#     list_filter = ['published_status', 'author','created_at']
#     search_fields = ['title', 'author__username']
#     list_display_links = ['id', 'title']
#     inlines = [CommentInline]
#     prepopulated_fields = {
#         'slug' : ['title']
#     }
#     # fields = ['title', 'body', 'published_status']
#     fieldsets = (
#         (None, {'fields': ('title','slug', 'body','thumbnail', 'author', 'category')}),
#         ("وضعیت", {'fields': ('published_status',)})
#     )
#     # filter_horizontal = ['tags']
#     # resource_class = PostResource

#     def tags_to_str(self, obj):
#         return ", ".join(tag.title for tag in obj.tags.all())
#     tags_to_str.short_description = _('برسب ها')


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


# @admin.register(BlogCategory)
# class BlogCategoryAdmin(TreeAdmin):
#     form = movenodeform_factory(BlogCategory)
#     prepopulated_fields = {
#         'slug' : ['name']
#     }