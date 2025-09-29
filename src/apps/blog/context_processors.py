from .models import Category, Tag


def blog_categories(request):
    return {
        'blog_categories': Category.objects.all()
    }


def blog_tags(request):
        return {
        'blog_tags': Tag.objects.all()
    }