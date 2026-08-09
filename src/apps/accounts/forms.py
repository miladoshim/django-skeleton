from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.core import validators
from django.core.exceptions import ValidationError
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
    old_password = forms.PasswordInput()
    password = forms.PasswordInput()
    password_confirmation = forms.PasswordInput()

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                "گذرواژه فعلی تان اشتباه وارد شد. لطفا دوباره تلاش کنید"
            )
        return old_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز عبور باید بیشتر از 8 کاراکتر باشد")
        else:
            return password

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
        label="ایمیل",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            },
        ),
    )

    mobile = forms.CharField(
        label="موبایل",
        required=False,
        widget=forms.TextInput(
            attrs={
                "disabled": "disabled",
                "readonly": "readonly",
                "class": "form-control",
            },
        ),
    )

    bio = forms.CharField(
        validators=[
            validators.MinLengthValidator(10),
        ],
        label="بیوگرافی",
        required=True,
        widget=forms.Textarea(
            attrs={"placeholder": "بیوگرافی", "class": "form-control"},
        ),
    )


class UserProfileEditForm(ModelForm):
    # avatar = forms.ImageField(widget=ImageUploaderWidget())

    bio = forms.CharField(
        label="بیوگرافی",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "style": "text-align: right;direction: ltr;line-height: 24px;",
            }
        ),
        required=True,
    )
    # gender = forms.ChoiceField(
    #     choices=Gender,
    #     widget=forms.RadioSelect,
    # )

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "gender",
            "bio",
        ]
        labels = {
            "avatar": "تصویر پروفایل",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # def __init__(self, *args, **kwargs):
    #     super(UserProfileEditForm, self).__init__(*args, **kwargs)
    #     self.fields["birthday"] = JalaliDateField(
    #         label="تاریخ تولد", widget=AdminJalaliDateWidget
    #     )

    def save(self, commit):
        super(UserProfileEditForm, self).save(commit=False)


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
