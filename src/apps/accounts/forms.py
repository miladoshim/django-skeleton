from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import Form, ModelForm
from .models import User, UserProfile


class UserEmailRegisterForm(Form):
    first_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
        ],
        label="نام",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "نام", "class": "form-control"}),
    )

    last_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
        ],
        label="نام خانوادگی",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "نام خانوادگی", "class": "form-control"},
        ),
    )
    email = forms.EmailField(
        min_length=5,
        max_length=150,
        label="ایمیل",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "مثال : youremail@gmail.com",
                "class": "form-control",
            },
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="رمز عبور",
    )


class UserLoginForm(Form):
    mobile = forms.CharField(
        max_length=11,
        label="شماره موبایل",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "مثال:‌09121236515"},
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور"},
        ),
        min_length=8,
        max_length=30,
    )


class ClassicLoginForm(forms.Form):
    username = forms.CharField(
        label="ایمیل، موبایل یا نام کاربری",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "ایمیل، موبایل یا نام کاربری",
                "autofocus": True,
            },
        ),
        validators=[
            validators.MinLengthValidator(6),
        ],
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور"},
        ),
        min_length=8,
        max_length=30,
    )

    def clean_username(self):

        username = self.cleaned_data.get("username", "").strip().lower()

        if not username:
            raise ValidationError(_("نام کاربری یا ایمیل یا موبایل الزامی است"))

        if len(username) < 3:
            raise ValidationError(_("نام کاربری یا ایمیل حداقل ۳ کاراکتر باید باشد"))

        user = User.objects.filter(
            Q(username__iexact=username)
            | Q(email__iexact=username)
            | Q(mobile__iexact=username)
        ).first()

        if user is None:
            raise ValidationError("کاربری با این مشخصات یافت نشد")

        # if not user.is_active:
        #     raise ValidationError(_("حساب کاربری شما غیرفعال است"))

        # if getattr(user, "is_blocked", False):
        #     raise ValidationError(_("حساب کاربری شما مسدود شده است"))

        return username

    def clean_password(self):
        password = self.cleaned_data.get("password", "")

        if not password:
            raise ValidationError("رمز عبور الزامی است")

        if len(password) < 8:
            raise ValidationError("رمز عبور حداقل ۸ کاراکتر باید باشد")

        return password

    # def clean(self):

    #     cleaned_data = super().clean()

    #     username = cleaned_data.get("username")
    #     password = cleaned_data.get("password")

    #     # اگر هر دو فیلد معتبر بودند
    #     if username and password:

    #         # پیدا کردن کاربر
    #         user = User.objects.filter(
    #             Q(username__iexact=username) | Q(email__iexact=username)
    #         ).first()

    #         if user is not None:
    #             # بررسی رمز عبور
    #             if not user.check_password(password):
    #                 # ثبت تلاش ناموفق
    #                 self._handle_failed_login(user)
    #                 raise ValidationError(
    #                     _("رمز عبور اشتباه است"), code="invalid_password"
    #                 )

    #             # بررسی تعداد تلاش‌های ناموفق
    #             if (
    #                 hasattr(user, "failed_login_attempts")
    #                 and user.failed_login_attempts >= 5
    #             ):
    #                 raise ValidationError(
    #                     _(
    #                         "تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفا بعدا تلاش کنید"
    #                     )
    #                 )
    #         else:
    #             raise ValidationError(_("کاربری با این مشخصات یافت نشد"))

    #     return cleaned_data

    # def _handle_failed_login(self, user):
    #     """
    #     ثبت تلاش ناموفق ورود
    #     """
    #     if hasattr(user, "failed_login_attempts"):
    #         user.failed_login_attempts += 1
    #         user.save(update_fields=["failed_login_attempts"])


class UserOtpForm(Form):
    mobile = forms.CharField(
        min_length=11,
        max_length=11,
        label="شماره موبایل",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "مثال:‌09121236515", "class": "form-control"},
        ),
    )


class UserOtpVerifyForm(Form):
    receiver = forms.HiddenInput()
    request_id = forms.HiddenInput()
    code = forms.CharField(
        min_length=6,
        max_length=6,
        label="کد تایید",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "کد 6 رقمی ارسال شده به شماره موبایل",
                "class": "form-control",
                "pattern": "[0-9]{6}",
            },
        ),
    )


class UserOtpCompleteForm(Form):
    receiver = forms.HiddenInput()
    request_id = forms.HiddenInput()
    first_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
        ],
        label="نام",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "نام", "class": "form-control"}),
    )
    last_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
        ],
        label="نام خانوادگی",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "نام خانوادگی", "class": "form-control"},
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="رمز عبور",
    )


class ResetPasswordMobileForm(Form):
    receiver = forms.HiddenInput()
    request_id = forms.HiddenInput()
    code = forms.CharField(
        min_length=6,
        max_length=6,
        label="کد تایید",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "کد ۴ رقمی ارسال شده به شماره موبایل",
                "class": "form-control",
            },
        ),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور", "class": "form-control"},
        ),
        label="رمز عبور",
        validators=[
            validators.MinLengthValidator(8),
        ],
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "تایید رمز عبور", "class": "form-control"},
        ),
        label="تایید رمز عبور",
        validators=[
            validators.MinLengthValidator(8),
        ],
    )

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data["password2"]

        if password != password2:
            raise forms.ValidationError("رمز عبور ها یکی نیستند")
        return password2


class ChangePasswordForm(Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور فعلی", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="رمز عبور فعلی",
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور جدید", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="رمز عبور جدید",
    )

    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "تکرار رمز عبور جدید", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="تکرار رمز عبور جدید",
    )

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data["password_confirmation"]

        if password != password_confirmation:
            raise forms.ValidationError("رمز عبور ها یکی نیستند")
        return password_confirmation


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "email",
            "mobile",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
        )


class UserAccountEditForm(Form):
    first_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
            validators.MaxLengthValidator(20),
        ],
        label="نام",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "نام", "class": "form-control"}),
    )

    last_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(3),
            validators.MaxLengthValidator(20),
        ],
        label="نام خانوادگی",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "نام خانوادگی", "class": "form-control"},
        ),
    )

    username = forms.CharField(
        validators=[
            validators.MinLengthValidator(6),
            validators.MaxLengthValidator(30),
        ],
        label="نام کاربری",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "نام کاربری", "class": "form-control"},
        ),
    )

    email = forms.EmailField(
        label="ایمیل",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    mobile = forms.CharField(
        label="موبایل",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    bio = forms.CharField(
        validators=[
            validators.MinLengthValidator(10),
            validators.MaxLengthValidator(300),
        ],
        label="بیوگرافی",
        required=True,
        widget=forms.Textarea(
            attrs={
                "placeholder": "بیوگرافی",
                "class": "form-control",
                "rows": 6,
            },
        ),
    )

    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["first_name"].initial = self.user.first_name or ""
            self.fields["last_name"].initial = self.user.last_name or ""
            if hasattr(self.user, "profile"):
                self.fields["bio"].initial = self.user.profile.bio or ""

            avatar = self._get_avatar()
            if avatar:
                self.fields["avatar"].initial = avatar

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", "").strip()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name", "").strip()
        return last_name

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "").strip()
        return bio

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile", "").strip()

        # if not User.objects.filter(mobile=mobile).first():
        return mobile
        # else:
        #     raise ValidationError(f"کابری با شماره {mobile} وجود دارد")

    def _get_avatar(self):
        """دریافت آواتار از پروفایل یا مدل کاربر"""
        if hasattr(self.user, "profile"):
            return self.user.profile.avatar or getattr(self.user, "avatar", None)
        return getattr(self.user, "avatar", None)

    def clean_avatar(self):
        """اعتبارسنجی آواتار"""
        avatar = self.cleaned_data.get("avatar")

        if avatar:
            # بررسی حجم (حداکثر 2 مگابایت)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("حجم عکس نباید بیشتر از 2 مگابایت باشد")

            # بررسی پسوند
            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            ext = avatar.name.lower()
            if not any(ext.endswith(e) for e in allowed_extensions):
                raise ValidationError("فرمت عکس باید jpg, jpeg, png, gif یا webp باشد")

        return avatar


# # uploads/forms.py - updated with validators
# from .validators import (
#     validate_file_type,
#     validate_file_size,
#     validate_image_dimensions,
#     sanitize_filename,
#     ALLOWED_DOCUMENT_TYPES,
#     ALLOWED_IMAGE_TYPES,
# )


# class SecureDocumentForm(forms.ModelForm):
#     """Form with comprehensive file validation"""

#     class Meta:
#         model = Document
#         fields = ["title", "file", "category", "description"]

#     def clean_file(self):
#         file = self.cleaned_data.get("file")
#         if file:
#             # Sanitize filename
#             file.name = sanitize_filename(file.name)

#             # Validate file size (max 10MB)
#             validate_file_size(file, max_size_mb=10)

#             # Validate file type by content
#             validate_file_type(file, ALLOWED_DOCUMENT_TYPES)

#         return file


# class SecureImageForm(forms.Form):
#     """Form for secure image upload"""

#     image = forms.ImageField()

#     def clean_image(self):
#         image = self.cleaned_data.get("image")
#         if image:
#             # Sanitize filename
#             image.name = sanitize_filename(image.name)

#             # Validate size
#             validate_file_size(image, max_size_mb=5)

#             # Validate type by content
#             validate_file_type(image, ALLOWED_IMAGE_TYPES)

#             # Validate dimensions
#             validate_image_dimensions(
#                 image, max_width=4096, max_height=4096, min_width=50, min_height=50
#             )

#         return image
