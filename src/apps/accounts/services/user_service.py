from datetime import datetime
from typing import Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.aggregates import Sum
from apps.core.services.base_service import BaseService

User = get_user_model()


class UserService(BaseService):
    model = User
    
    def __init__(self, request=None):
        super().__init__(request=request)
    
    @transaction.atomic
    def change_password(self, user, old_password, new_password):
        if not user.check_password(old_password):
            return {"success": False, "error": "رمز فعلی اشتباه است"}

        user.set_password(new_password)
        self.update(user)  # استفاده از متد BaseService

        return {"success": True, "message": "رمز عبور تغییر کرد"}
    
    @transaction.atomic
    def update_profile2(self, user: User, **validated_data) -> User:

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
        pass
        
  
    def update_profile(self, user, **data):
        """ویرایش پروفایل کاربر"""
        allowed_fields = ['first_name', 'last_name', 'avatar', 'bio', 'phone']

        update_data = {}
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        # استفاده از متد update از BaseService
        user = self.update(user, **update_data)

        return {'success': True, 'user': user}

    # ============================
    #   GET USER PROFILE
    # ============================
    def get_user_profile(self, user_id=None, username=None):
        if user_id:
            user = self.get(user_id)
        elif username:
            user = self.get_queryset().filter(username=username).first()
        else:
            user = self.request.user if self.request else None

        if not user:
            return {'success': False, 'error': 'کاربر یافت نشد'}

        return {
            'success': True,
            'user': self._serialize_user(user),
        }

    # ============================
    #   USER LIST (برای ادمین)
    # ============================
    def get_search_users(self, is_active=None, search=None, page=1, limit=20):
        queryset = self.get_queryset()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(mobile__icontains=search)
            )

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit

        users = queryset[start:end]

        return {
            'items': [self._serialize_user(u) for u in users],
            'total': total,
            'page': page,
            'limit': limit,
            'has_next': end < total,
        }

    # ============================
    #   UPDATE USER (ادمین)
    # ============================
    def update_user(self, user_id, **data):
        """ویرایش کاربر توسط ادمین"""
        user = self.get(user_id)
        if not user:
            return {'success': False, 'error': 'کاربر یافت نشد'}

        user = self.update(user, **data)
        return {'success': True, 'user': self._serialize_user(user)}

    # ============================
    #   DELETE USER (ادمین)
    # ============================
    @transaction.atomic
    def delete_user(self, user_id, hard_delete=False):
        """حذف کاربر"""
        user = self.get(user_id)
        if not user:
            return {'success': False, 'error': 'کاربر یافت نشد'}

        if hard_delete:
            # حذف کامل
            self.delete(user)
        else:
            # حذف نرم
            self.update(user, is_active=False)

        return {'success': True, 'message': 'کاربر حذف شد'}

        """درخواست تغییر ایمیل"""
        # اینجا میتوانید ایمیل تاییدیه بفرستید
        pass
