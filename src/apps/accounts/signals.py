import os
from django.db.models.signals import post_save, pre_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import User, UserProfile, UserMeta


@receiver(post_save, sender=User)
def create_user_signal(sender, instance, created, *args, **kwargs):
    if created:
        # os.mkdir(f"media/users/{instance.username}")
        UserProfile.objects.create(user=instance)
        UserMeta.objects.create(user=instance)


@receiver(user_logged_in, sender=User)
def user_logged_in_signal(sender, request, user, *args, **kwargs):
    pass


@receiver(user_logged_out, sender=User)
def user_logged_out_signal(sender, request, user, *args, **kwargs):
    pass

# @receiver(pre_delete, sender=User)
# def user_deleted_signal():
#     pass