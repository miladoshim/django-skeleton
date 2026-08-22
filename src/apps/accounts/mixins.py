from django.db import models, transaction
from django.db.models import Q


class FollowMixin(models.Model):

    class Meta:
        abstract = True

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def get_followers(self):
        return self.followers.select_related("follower").all()

    def get_following(self):
        return self.following.select_related("following").all()

    def is_following(self, user):
        """آیا این کاربر را دنبال می‌کند"""
        if not user:
            return False

        return self.following.filter(following=user).exists()

    def is_followed_by(self, user):
        """آیا این کاربر مرا دنبال می‌کند"""
        if not user:
            return False
        return self.followers.filter(follower=user).exists()

    @transaction.atomic
    def follow(self, user):
        if self == user:
            return {"success": False, "message": "نمی‌توانید خودتان را دنبال کنید"}

        if self.is_following(user):
            return {"success": False, "message": "در حال حاضر دنبال میکنید"}

        self.followers.create(follower=self, following=user)
        return {"success": True, "message": "با موفقیت دنبال کردید"}

    @transaction.atomic
    def unfollow(self, user):
        if self == user:
            return {"success": False, "message": "نمی‌توانید خودتان را لغو کنید"}

        deleted, _ = self.following.filter(follower=self, following=user).delete()

        if deleted:
            return {"success": True, "message": "آنفالو کردید"}

        return {"success": False, "message": "شما اینکاربر را دنبال نمیکنید"}

    def toggle_follow(self, target_user):

        if self == target_user:
            return {
                "success": False,
                "is_following": False,
                "message": "نمی‌توانید خودتان را دنبال کنید",
            }

        if not target_user or not target_user.is_authenticated:
            return {
                "success": False,
                "is_following": False,
                "message": "کاربر نامعتبر است",
            }

        is_following = self.following.filter(following=target_user).exists()

        if is_following:
            self.following.filter(following=target_user).delete()
            return {
                "success": True,
                "is_following": False,
                "message": f"دنبال کردن {target_user.username} لغو شد",
            }
        else:
            self.following.create(following=target_user)
            return {
                "success": True,
                "is_following": True,
                "message": f"شما {target_user.username} را دنبال میکنید",
            }

    def get_mutual_followers(self, user):
        """دنبال‌کننده‌های مشترک"""
        my_followers = set(self.followers.values_list("follower_id", flat=True))
        their_followers = set(user.followers.values_list("follower_id", flat=True))
        mutual_ids = my_followers & their_followers
        return self.__class__.objects.filter(id__in=mutual_ids)

    def get_follow_suggestions(self, limit=10):

        # افرادی که من دنبال می‌کنم
        following_ids = self.following.values_list("following_id", flat=True)

        # افرادی که من را دنبال می‌کنند
        follower_ids = self.followers.values_list("follower_id", flat=True)

        # همه به جز من و افرادی که دنبال می‌کنم
        suggestions = (
            self.__class__.objects.filter(
                is_active=True,
            )
            .exclude(Q(id=self.id) | Q(id__in=following_ids))
            .exclude(
                id__in=follower_ids  # کسانی که من را دنبال می‌کنند ولی من دنبال نمی‌کنم
            )
            .order_by("?")[:limit]
        )

        return suggestions
