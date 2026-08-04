from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Comment


@receiver(post_save, sender=Comment)
def create_post(sender, instance, created, update_fields, *args, **kwargs):
    if created:
        pass  # send notification to user

    if update_fields is None or "is_approved" in update_fields:
        if instance.is_approved == True:
            print(f"Comment {instance.uuid} is approved")
            print(f"Send notification to user {instance.user.mobile}")
            # send_comment_approved_notification


# @receiver(saved_file)
# def generate_thumbnails_async(sender, fieldfile, **kwargs):
#     generate_thumbnails.delay(
#         model=sender, pk=fieldfile.instance.pk, field=fieldfile.field.name
#     )


# @receiver(post_save, sender=Comment)
# def create_post_comment_reply_notification_signal(sender, instance, created, *args, **kwargs):
#     """
#     create notification when user reply comment
#     """
#     if created and instance.parent_id:
#         if instance.parent.user != instance.user:
#             message = ''
#             post = instance.post
#             Notification.objects.create(user,instance.parent.user, message)
