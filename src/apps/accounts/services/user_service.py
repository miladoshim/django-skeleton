from typing import Optional, Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from apps.core.services.base_service import BaseService

User = get_user_model()


class UserService(BaseService):

    model = User

    @transaction.atomic
    def register_user(
        self,
        email: str,
        password: str,
        username: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> User:
        """ثبتنام کاربر جدید"""

        # بررسی یکتا بودن ایمیل
        if User.objects.filter(email=email).exists():
            raise ValueError("این ایمیل قبلاً ثبت شده است")

        # ساخت کاربر
        user = User.objects.create_user(
            email=email,
            password=password,
            username=username or email.split("@")[0],
            phone=phone or "",
        )

        # ارسال ایمیل خوشآمد
        self._send_welcome_email(user)

        return user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """احراز هویت کاربر"""
        from django.contrib.auth import authenticate

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            return user
        return None

    def update_profile(self, user: User, **validated_data) -> User:
        """بهروزرسانی پروفایل کاربر"""

        allowed_fields = [
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "bio",
            "website",
        ]

        data = {k: v for k, v in validated_data.items() if k in allowed_fields}

        # بررسی تغییر ایمیل (نیاز به تایید)
        if "email" in validated_data and validated_data["email"] != user.email:
            self._request_email_change(user, validated_data["email"])
            del validated_data["email"]

        return self.update(user, **data)

    def change_password(self, user: User, old_password: str, new_password: str) -> bool:
        """تغییر رمز عبور"""

        if not user.check_password(old_password):
            raise ValueError("رمز عبور فعلی اشتباه است")

        user.set_password(new_password)
        user.save(update_fields=["password"])

        # ارسال ایمیل اطلاعرسانی
        self._send_password_change_notification(user)

        return True

    def get_user_stats(self, user: User) -> Dict[str, Any]:
        """آمار کاربر"""

        return {
            "posts_count": user.posts.count(),
            "comments_count": user.comments.count(),
            "likes_received": user.posts.aggregate(
                total_likes=models.Sum("likes_count")
            )["total_likes"]
            or 0,
            "joined_days": (timezone.now() - user.date_joined).days,
        }

    def get_user_feed(self, user: User, page: int = 1) -> Dict:
        """فید شخصی کاربر"""

        # پستهای کاربرانی که دنبال میکند
        following_users = user.following.values_list("id", flat=True)

        queryset = self.model.posts.filter(
            author_id__in=following_users, is_published=True
        ).order_by("-created_at")

        return {
            "items": queryset[:20],
            "page": page,
            "total": queryset.count(),
        }

    # ------------------ متدهای خصوصی ------------------

    def _send_welcome_email(self, user: User):
        """ارسال ایمیل خوشآمد"""
        send_mail(
            subject="خوش آمدید!",
            message=f"سلام {user.username}، به سایت ما خوش آمدید!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def _send_password_change_notification(self, user: User):
        """ارسال ایمیل تغییر رمز"""
        send_mail(
            subject="تغییر رمز عبور",
            message="رمز عبور شما با موفقیت تغییر کرد.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def _request_email_change(self, user: User, new_email: str):
        """درخواست تغییر ایمیل"""
        # اینجا میتوانید ایمیل تاییدیه بفرستید
        pass
