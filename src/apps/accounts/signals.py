import uuid
import datetime
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.financial.models import Wallet
from utils.helpers import get_user_agent, get_user_ip_address
from .models import (
    Follow,
    User,
    UserMeta,
    UserProfile,
    UserSession,
)


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, *args, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserMeta.objects.create(user=instance)
        Wallet.objects.create(user=instance)
        instance.username = "SKL" + str(uuid.uuid4())[:4]
        instance.save()


@receiver(user_logged_in, sender=User)
def user_logged_in_signal(sender, request, user, *args, **kwargs):
    meta = UserMeta.objects.get(user=user)
    meta.last_login_at = datetime.datetime.now()
    meta.last_login_ip = get_user_ip_address(request)
    meta.last_login_agent = get_user_agent(request)
    meta.save()


@receiver(user_logged_out, sender=User)
def user_logged_out_signal(sender, request, user, *args, **kwargs):
    meta = UserMeta.objects.get(user=user)
    meta.last_logout_at = datetime.datetime.now()
    meta.save()
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.filter(session_key=session_key).update(
            is_active=False,
            is_current=False,
        )


@receiver(post_save, sender=Follow)
def user_notify_follow(sender, instance, created, **kwargs):
    if created:
        # Notification.objects.create(
        #     user=instance.following,
        #     message=f"{instance.follower.username} شما را دنبال کرد"
        # )
        pass
