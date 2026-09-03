import re
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import Form
from apps.accounts.backends import EmailMobileUsernameBackend
from utils.validators import validate_phone_number
from .models import User


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
                "placeholder": "مثال : youremail@email.com",
                "class": "form-control",
            },
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "رمز عبور قوی انتخاب کنید", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="رمز عبور",
    )


class ClassicLoginForm(Form):
    identifier = forms.CharField(
        label="ایمیل، موبایل یا نام کاربری",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@email.com یا 09123456789 یا username",
                "autofocus": True,
            },
        ),
        validators=[
            validators.MinLengthValidator(6),
            validators.MaxLengthValidator(100),
        ],
    )

    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "رمز عبور"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            backend = EmailMobileUsernameBackend()
            user = backend.authenticate(self.request, identifier, password)

            if not user:
                self.add_error("identifier","اطلاعات وارد شده اشتباه است")
                return cleaned_data

            cleaned_data["user"] = user

        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get("password", "")

        if not password:
            raise ValidationError("رمز عبور الزامی است")

        if len(password) < 8:
            raise ValidationError("رمز عبور حداقل ۸ کاراکتر باید باشد")

        return password

class ForgotPasswordForm(Form):
    identifier = forms.CharField(
        label="ایمیل یا شماره موبایل",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "example@email.com یا 09123456789",
                "autofocus": True,
            }
        ),
    )
    
    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier", "").strip().lower()

        if not identifier:
            self.add_error("identifier", "این فیلد الزامی است")
            return cleaned_data

        # ایمیل
        if "@" in identifier:
            if not User.objects.filter(email__iexact=identifier).exists():
                self.add_error("identifier", "کاربری با این ایمیل یافت نشد")
                return cleaned_data

        # موبایل
        try:
            validate_phone_number(identifier)
        except:
            self.add_error("identifier", "شماره موبایل معتبر نیست")
            return cleaned_data

        if not User.objects.filter(mobile=identifier).exists():
            self.add_error("identifier", "کاربری با این شماره موبایل یافت نشد")
            return cleaned_data

        cleaned_data['identifier'] = identifier
        return cleaned_data


class ForgotPasswordResetForm(Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "رمز جدید (حداقل ۸ کاراکتر)",
                "class": "form-control",
            },
        ),
        validators=[
            validators.MinLengthValidator(8),
            validators.MaxLengthValidator(100),
        ],
        label="رمز عبور جدید",
    )

    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "تایید رمز عبور", "class": "form-control"},
        ),
        validators=[
            validators.MinLengthValidator(8),
        ],
        label="تایید رمز عبور",
    )

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data["password_confirmation"]

        if password and password_confirmation and password != password_confirmation:
            raise ValidationError("رمز عبور ها یکی نیستند")
        return password_confirmation


class ResetPasswordMobileForm(Form):
    mobile = forms.CharField(widget=forms.HiddenInput())
    reqid = forms.CharField(widget=forms.HiddenInput())

    code = forms.CharField(
        min_length=6,
        max_length=6,
        label="کد تایید",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "کد 6 رقمی ارسال شده به شماره موبایل",
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
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "تایید رمز عبور", "class": "form-control"},
        ),
        label="تایید رمز عبور",
        validators=[
            validators.MinLengthValidator(8),
        ],
    )

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if not code or len(code) != 6:
            raise forms.ValidationError("کد باید ۶ رقم باشد")
        return code

    def clean_password_confirmation(self):
        password = self.cleaned_data.get("password")
        password_confirmation = self.cleaned_data["password_confirmation"]

        if password != password_confirmation:
            raise forms.ValidationError("رمز عبور ها یکی نیستند")
        return password_confirmation


class UserOtpForm(Form):
    mobile = forms.CharField(
        min_length=11,
        max_length=11,
        label="شماره موبایل",
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "مثال:‌09121236515",
                "class": "form-control",
            },
        ),
    )

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile", "").strip().lower()

        if not mobile:
            raise ValidationError("موبایل الزامی است")

        validate_phone_number(mobile)

        return mobile


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

    short_bio = forms.CharField(
        label="تیر تخصص یا شغلی",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    birthday_day = forms.CharField(
        label="روز تولد",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    birthday_month = forms.CharField(
        label="ماه تولد",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    birthday_year = forms.CharField(
        label="سال تولد",
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
        mobile = self.cleaned_data.get("mobile", "").strip().lower()

        if not mobile:
            raise ValidationError("موبایل الزامی است")

        validate_phone_number(mobile)

        return mobile

    def _get_avatar(self):
        if hasattr(self.user, "profile"):
            return self.user.profile.avatar or getattr(self.user, "avatar", None)
        return getattr(self.user, "avatar", None)

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")

        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("حجم عکس نباید بیشتر از 2 مگابایت باشد")

            allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            ext = avatar.name.lower()
            if not any(ext.endswith(e) for e in allowed_extensions):
                raise ValidationError("فرمت عکس باید jpg, jpeg, png, gif یا webp باشد")

        return avatar
