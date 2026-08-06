import strawberry
from typing import Optional
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.exceptions import ValidationError
from strawberry.types import Info

from apps.accounts.graphql.types import UserType, UserPublicType
from apps.blog.validators import UserValidators

User = get_user_model()


@strawberry.type
class AuthMutation:
    """Mutation های احراز هویت"""

    @strawberry.mutation
    def register(
        self,
        info: Info,
        email: str,
        username: str,
        password: str,
        first_name: Optional[str] = "",
        last_name: Optional[str] = "",
    ) -> UserPublicType:
        """ثبت‌نام کاربر جدید"""

        # اعتبارسنجی
        try:
            UserValidators.validate_email(email)
            UserValidators.validate_username(username)
            UserValidators.validate_password(password)
        except ValidationError as e:
            raise ValueError(str(e))

        # بررسی یکتا بودن
        if User.objects.filter(email=email).exists():
            raise ValueError("این ایمیل قبلاً ثبت شده است")
        if User.objects.filter(username=username).exists():
            raise ValueError("این نام کاربری قبلاً ثبت شده است")

        # ایجاد کاربر
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        return user

    @strawberry.mutation
    def login(self, info: Info, email: str, password: str) -> UserType:
        """ورود کاربر"""

        user = authenticate(email=email, password=password)

        if not user:
            raise ValueError("ایمیل یا رمز عبور اشتباه است")

        if not user.is_active:
            raise ValueError("حساب کاربری شما غیرفعال است")

        # لاگین در session (برای وب)
        login(info.context.request, user)

        return user

    @strawberry.mutation
    def logout(self, info: Info) -> bool:
        """خروج کاربر"""

        if info.context.request.user.is_authenticated:
            logout(info.context.request)
            return True
        return False

    @strawberry.mutation
    def change_password(
        self,
        info: Info,
        old_password: str,
        new_password: str,
    ) -> bool:
        """تغییر رمز عبور"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        # بررسی رمز فعلی
        if not user.check_password(old_password):
            raise ValueError("رمز عبور فعلی اشتباه است")

        # اعتبارسنجی رمز جدید
        try:
            UserValidators.validate_password(new_password)
        except ValidationError as e:
            raise ValueError(str(e))

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return True

    @strawberry.mutation
    def update_profile(
        self,
        info: Info,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        bio: Optional[str] = None,
        website: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> UserType:
        """به‌روزرسانی پروفایل"""

        user = info.context.request.user
        if not user.is_authenticated:
            raise ValueError("ابتدا وارد شوید")

        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if bio is not None:
            user.bio = bio
        if website is not None:
            user.website = website
        if avatar is not None:
            user.avatar = avatar

        user.save()
        return user
