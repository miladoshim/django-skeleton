from celery import shared_task

from apps.blog.models import Post
from .models import User


@shared_task
def users_count():
    count = User.objects.count()
    return f"Count of Users: {count}"

@shared_task
def posts_count():
    count = Post.objects.count()
    return f"Count of Posts: {count}"
    

@shared_task
def send_welcome_message(receiver: str):
    pass
    # new_user = User.objects.filter("username" == receiver)
    # send sms or email
