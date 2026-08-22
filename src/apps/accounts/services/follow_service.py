from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()


class FollowService:
    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def toggle_follow(self, target_user_uuid):
        try:

            target = get_object_or_404(User, uuid=target_user_uuid, is_active=True)

            if self.user == target:
                return {"success": False, "message": "نمی‌توانید خودتان را دنبال کنید"}

            return self.user.toggle_follow(target)

        except Exception as e:
            return {"success": False, "message": "خطا در فالو کردن"}

    def get_followers(self, user_id=None, page=1, limit=20):
        user = self._get_user(user_id)
        followers = user.get_followers()
        return self._paginate(followers, page, limit)

    def get_following(self, user_id=None, page=1, limit=20):
        user = self._get_user(user_id)
        following = user.get_following()
        return self._paginate(following, page, limit)

    def get_stats(self, user_id=None):
        user = self._get_user(user_id)
        return {
            "user_id": user.id,
            "username": user.username,
            "fullname": user.get_full_name,
            "followers_count": user.followers_count,
            "following_count": user.following_count,
            "is_following_me": (
                user.is_followed_by(self.user) if self.user.is_authenticated else False
            ),
            "i_am_following": (
                user.is_following(self.user) if self.user.is_authenticated else False
            ),
        }

    def get_follow_status(self, target_user_id):
        target = get_object_or_404(User, id=target_user_id)
        return {
            "is_following": self.user.is_following(target),
            "is_followed_by": target.is_following(self.user),
            "followers_count": target.followers_count,
            "following_count": target.following_count,
        }

    def get_follow_suggestions(self, limit=10):
        suggestions = self.user.get_follow_suggestions(limit)
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "followers_count": user.followers_count,
                "is_following": self.user.is_following(user),
            }
            for user in suggestions
        ]

    def _get_user(self, user_id=None):
        if user_id:
            return get_object_or_404(
                User,
                id=user_id,
                is_active=True,
            )
        return self.user

    def _paginate(self, queryset, page, limit):
        start = (page - 1) * limit
        end = start + limit
        items = queryset[start:end]

        return {
            "items": [
                {
                    "id": item.id,
                    "username": item.username,
                    "email": item.email,
                    "first_name": item.first_name,
                    "last_name": item.last_name,
                    "followers_count": item.followers_count,
                    "following_count": item.following_count,
                    "is_following": (
                        self.user.is_following(item)
                        if self.user.is_authenticated
                        else False
                    ),
                    "is_followed_by": (
                        item.is_following(self.user)
                        if self.user.is_authenticated
                        else False
                    ),
                }
                for item in items
            ],
            "total": queryset.count(),
            "page": page,
            "limit": limit,
            "has_next": end < queryset.count(),
        }
