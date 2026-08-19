from django.db import models
from django.db.models import Q
from .models import Follow


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
        if not user or not user.is_authenticated:
            return False
        return self.following.filter(following=user).exists()

    def is_followed_by(self, user):
        """آیا این کاربر مرا دنبال می‌کند"""
        if not user or not user.is_authenticated:
            return False
        return self.followers.filter(follower=user).exists()

    def follow(self, user):
        if self == user:
            return False, "نمی‌توانید خودتان را دنبال کنید"

        if self.is_following(user):
            return False, "در حال حاضر دنبال می‌کنید"

        Follow.objects.create(follower=self, following=user)
        return True, "با موفقیت دنبال کردید"

    def unfollow(self, user):
        if self == user:
            return False, "نمی‌توانید خودتان را لغو کنید"

        from .models import Follow

        deleted, _ = Follow.objects.filter(follower=self, following=user).delete()

        if deleted:
            return True, "لغو دنبال کردید"
        return False, "شما این کاربر را دنبال نمی‌کنید"

    def toggle_follow(self, user):
        if self.is_following(user):
            return self.unfollow(user)
        return self.follow(user)

    def get_mutual_followers(self, user):
        """دنبال‌کننده‌های مشترک"""
        my_followers = set(self.followers.values_list("follower_id", flat=True))
        their_followers = set(user.followers.values_list("follower_id", flat=True))
        mutual_ids = my_followers & their_followers
        return self.__class__.objects.filter(id__in=mutual_ids)

    def get_follow_suggestions(self, limit=10):
        """پیشنهاد کاربران برای دنبال کردن"""

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
