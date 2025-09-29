from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from utils.helpers import Helpers
from .models import Post


@receiver(post_save, sender=Post)
def create_post(sender, instance, created, *args, **kwargs):
    if created or not instance.slug:
        instance.slug = Helpers.create_unique_slug(instance)
        instance.save()


# @receiver(post_save, sender=Comment)
# def create_post_comment_reply_notification_sinal(sender, instance, created, *args, **kwargs):
#     """
#     create notification when user reply comment
#     """
#     if created and instance.parent_id:
#         if instance.parent.user != instance.user:
#             message = ''
#             post = instance.post
#             Notification.objects.create(user,instance.parent.user, message)


# @receiver(post_save, sender=Post)
# def create_new_post_notification_signal(sender, instance, *args, **kwargs):
#     """
#     create notification when created new post
#     """
#     if created:
#         message = f''
#         post = instance
#         users = User.objects.all()
#         broadcastNotification = BroadcastNotification.objects.create(message=message)
#         broadcastNotification.users.set(users)
