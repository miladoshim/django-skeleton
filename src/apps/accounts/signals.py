import uuid
import datetime
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db.models.base import pre_save
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from apps.financial.models import Wallet
from utils.helpers import get_user_ip_address
from .models import User, UserMeta, UserProfile


@receiver(post_save, sender=User)
def user_created_signal(sender, instance, created, *args, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserMeta.objects.create(user=instance)
        Wallet.objects.create(user=instance)
        instance.username = "COND" + str(uuid.uuid4())[:4]
        instance.save()


@receiver(post_delete, sender=User)
def user_created_signal(sender, instance, *args, **kwargs):
    UserProfile.objects.filter(user=instance).delete()
    UserMeta.objects.filter(user=instance).delete()
    Wallet.objects.filter(user=instance).delete()


@receiver(user_logged_in, sender=User)
def user_logged_in_signal(sender, request, user, *args, **kwargs):
    meta = UserMeta.objects.get(user=user)
    meta.last_login_at = datetime.datetime.now()
    meta.last_login_ip = get_user_ip_address(request)
    # meta.last_login_agent = ""
    meta.save()
    # send_login_message.apply_async(receiver=user.mobile)


@receiver(user_logged_out, sender=User)
def user_logged_out_signal(sender, request, user, *args, **kwargs):
    meta = UserMeta.objects.get(user=user)
    meta.last_logout_at = datetime.datetime.now()
    meta.save()


@receiver(user_login_failed, sender=User)
def user_login_failed_signal(sender, request, user, *args, **kwargs):
    log_msg = str(user.mobile) + "failed to login"
    print(log_msg)


def delete_user_avatar_and_banner(old_instance: User, instance: User):
    try:

        if old_instance.profile.avatar and (
            not instance.profile.avatar
            or old_instance.profile.avatar != instance.profile.avatar
        ):
            if default_storage.exists(old_instance.profile.avatar.name):
                default_storage.delete(old_instance.profile.avatar.name)
                print("avatar deleted.")

        if old_instance.profile.banner and (
            not instance.profile.banner
            or old_instance.profile.banner != instance.profile.banner
        ):
            if default_storage.exists(old_instance.profile.banner.name):
                default_storage.delete(old_instance.profile.banner.name)
                print("banner deleted.")

    except Exception as e:
        print("Error in Delete user profile avatar and banner")


@receiver(pre_delete, sender=User, dispatch_uid="user_delete_signal")
def user_deleted_signal(sender, instance, *args, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

    delete_user_avatar_and_banner(old_instance, instance)
