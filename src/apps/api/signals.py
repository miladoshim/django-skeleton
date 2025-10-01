from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from rest_framework.authtoken.models import Token

from apps.blog.models import Post


@receiver([post_delete, post_save], sender=Post)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete_pattern('*post_list*')

# @receiver(post_save, sender=User)
# def create_auth_token(sender, instance, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)
