from django.contrib.auth import tokens
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import OtpRequest, User


class UserLoginSerializer(serializers.Serializer):
    mobile = serializers.CharField(
        min_length=11,
        max_length=11,
        allow_null=False,
    )
    password = serializers.CharField(
        min_length=5,
        max_length=64,
        write_only=True,
    )


# class UserRegisterSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "email",
#             "password",
#         ]
#         extra_kwargs = {"password": {"write_only": True,}}

#     def validate(self, attrs):
#         username = attrs.get("username", "")
#         if not username.isalnum():
#             raise ValidationError("The username should be contain alpha chars")
#         if attrs["password"] != attrs["password2"]:
#             raise ValidationError("password and password confirmation does not match!")

#         return attrs


#     def create(self, validated_data):
#         password = validated_data.pop("password", None)
#         instance = self.Meta.model(**validated_data)
#         if password is not None:
#             instance.set_password(password)
#         instance.save()
#         return instance
#
class RegisterSerializer(Serializer):
    mobile = serializers.CharField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValidationError({"password2": "رمز عبور یکسان نیست!"})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as e:
            raise ValidationError({"password": list(e.messages)})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            mobile=validated_data["mobile"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    pass


class UserLogoutSerializer(Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get("refresh")
        return attrs

    def save(self, **kwargs):
        RefreshToken(self.token).blacklist()

        return super().save(**kwargs)


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "uuid", "email", "first_name", "last_name", "username"]


class UserChangePasswordSerializer(Serializer):
    old_password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        fields = ["old_password", "password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")

        if password != password2:
            raise ValidationError({"password": "Passwords not same"})

        user.set_password(password)
        user.save()
        return attrs


class UserForgotPasswordMobileSerializer(Serializer):
    mobile = serializers.CharField(min_length=11, max_length=11)

    class Meta:
        fields = ["mobile"]

    def validate(self, attrs):
        mobile = attrs.get("mobile", "")
        if User.objects.filter(mobile=mobile).exists():
            user = User.objects.get(mobile=mobile)

            otp_data = {
                "channel": "p",
                "receiver": mobile,
            }
            otp = OtpRequest.objects.generate_otp(otp_data)

            # send sms

            return response(
                reverse(
                    "apps.accounts:password_forgot_mobile_reset_view",
                    kwargs={"mobile": mobile, "reqid": otp.request_id},
                )
            )

            return attrs
        else:
            raise ValidationError("همچین کاربری پیدا نشد.")


class UserForgotPasswordEmailSerializer(Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = tokens.PasswordResetTokenGenerator().make_token(user)
            currentSite = get_current_site().domain
            relativeLink = reverse("")
            link = "https://localhost:3000/api/password_reset/" + uid + "/" + token
            return attrs
        else:
            raise ValidationError("email not found")


class UserResetPasswordSerializer(Serializer):
    def validate(self, attrs):
        uid = self.context.get("uid")
        token = self.context.get("token")
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise ValidationError({"password": "Passwords not same"})

        id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=id)
        if not tokens.PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError("token is not valid")
        user.set_password(password)
        user.save()
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data["user_id"] = self.user.id
        validated_data["user_uuid"] = self.user.uuid
        validated_data["user_mobile"] = self.user.mobile
        return validated_data


# class DocumentSerializer(serializers.ModelSerializer):
#     """Serializer for document uploads via API"""

#     file_url = serializers.SerializerMethodField()
#     filename = serializers.SerializerMethodField()

#     class Meta:
#         model = Document
#         fields = [
#             "id",
#             "title",
#             "file",
#             "file_url",
#             "filename",
#             "category",
#             "description",
#             "file_size",
#             "uploaded_at",
#         ]
#         read_only_fields = ["file_size", "uploaded_at"]

#     def get_file_url(self, obj):
#         """Return full URL for the file"""
#         request = self.context.get("request")
#         if obj.file and request:
#             return request.build_absolute_uri(obj.file.url)
#         return None

#     def get_filename(self, obj):
#         return obj.filename

#     def validate_file(self, value):
#         """Validate uploaded file"""
#         validate_file_size(value, max_size_mb=10)
#         validate_file_type(value, ALLOWED_DOCUMENT_TYPES)
#         return value


# class PhotoSerializer(serializers.ModelSerializer):
#     """Serializer for photo uploads with thumbnails"""

#     thumbnail_url = serializers.SerializerMethodField()

#     class Meta:
#         model = Photo
#         fields = ["id", "title", "original", "thumbnail_url", "uploaded_at"]
#         read_only_fields = ["uploaded_at"]

#     def get_thumbnail_url(self, obj):
#         request = self.context.get("request")
#         if obj.thumbnail and request:
#             return request.build_absolute_uri(obj.thumbnail.url)
#         return None
