from datetime import datetime
from typing import Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from apps.core.services.base_service import BaseService

User = get_user_model()


class UserService(BaseService):
    model = User

    @transaction.atomic
    def update_profile(self, user: User, **validated_data) -> User:

        allowed_fields = [
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "bio",
            "website",
        ]

        data = {k: v for k, v in validated_data.items() if k in allowed_fields}

        if "email" in validated_data and validated_data["email"] != user.email:
            self._request_email_change(user, validated_data["email"])
            del validated_data["email"]

        return self.update(user, **data)

    def get_user_stats(self, user: User) -> Dict[str, Any]:

        return {
            "posts_count": user.posts.count(),
            "comments_count": user.comments.count(),
            "likes_received": user.posts.aggregate(total_likes=Sum("likes_count"))[
                "total_likes"
            ]
            or 0,
            "joined_days": (datetime.now() - user.date_joined).days,
        }

    def get_user_feed(self, user: User, page: int = 1) -> Dict:
        following_users = user.following.values_list("id", flat=True)

        queryset = self.model.posts.filter(
            author_id__in=following_users,
            is_published=True,
        ).order_by("-created_at")

        return {
            "items": queryset[:20],
            "page": page,
            "total": queryset.count(),
        }

    def _request_email_change(self, user: User, new_email: str):
        """درخواست تغییر ایمیل"""
        # اینجا میتوانید ایمیل تاییدیه بفرستید
        pass
