import datetime
from django import template
from apps.blog.models import Post

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.publish.count()



@register.filter(name='isNew')
def is_new_post(value):
    created_date = value.strftime("%d %m %y")
    now_date = datetime.now().strftime(created_date, "%d %m %y")
    created_date_prime = datetime.strptime(created_date, "%d %m %y")
    now_date_prime = datetime.strptime(now_date, "%d %m %y")
    return (now_date_prime - created_date_prime).days < 7

# def number_of_posts(for_today=False):
#     if for_today:
#         today = datetime.date.today()
#         return Post.published.filter(created_at__year=today.year, created_at__month=today.month, created_at__day=today.day).count()

#     return Post.published.count()


# @register.simple_tag
# def latest_posts(count=8):
#     return Post.published.order_by('-created_at')[:count]


# @register.inclusion_tag("blog/partials/category_navbar")
# def category_navbar():
#     return {
#         'categories': Category.objects.all()
#     }

# @register.inclusion_tag('partials/link.html')
# def link(request, link_name, content):
#     return {
#         'request': request,
#         'link_name': link_name,
#         'link': '',
#         'content': content
#     }
