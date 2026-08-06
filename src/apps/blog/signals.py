import os
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from utils.helpers import Helpers
from .models import Post, Category


@receiver([post_delete, post_save], sender=Post)
def invalidate_posts_cache(sender, instance, **kwargs):
    cache.delete_pattern("*posts_list*")


@receiver([post_delete, post_save], sender=Category)
def invalidate_posts_cache(sender, instance, **kwargs):
    cache.delete_pattern("*post_category_list*")


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(post_delete, sender=Post)
def delete_post(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        _delete_file(instance.thumbnail.path)


@receiver(post_save, sender=Post)
def create_post(sender, instance, created, *args, **kwargs):
    if created or not instance.slug:
        instance.slug = Helpers.create_unique_slug(instance)
        instance.save()
