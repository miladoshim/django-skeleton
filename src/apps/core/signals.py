from django.dispatch import receiver
from django.db.models.signals import post_save

# @receiver(post_save, sender=Comment)
# def create_comment(sender, instance, created, update_fields, *args, **kwargs):
#     if created:
#         pass

#     if update_fields is None or "is_approved" in update_fields:
#         if instance.is_approved == True:
#             print(f"Comment {instance.uuid} is approved")
#             print(f"Send notification to user {instance.user.mobile}")
#             # send_comment_approved_notification


# @receiver(post_save, sender=Comment)
# def create_comment_reply(sender, instance, created, *args, **kwargs):
#     """
#     create notification when user reply comment
#     """
#     if created and instance.parent.id:
#         if instance.parent.user != instance.user:
#             message = ""
#             # Notification.objects.create(user, instance.parent.user, message)
