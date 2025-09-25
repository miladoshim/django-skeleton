from django.urls import reverse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str,force_bytes, force_str, DjangoUnicodeDecodeError
from django.contrib import auth
from django.contrib.auth import tokens
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from apps.accounts.models import User
from utils.helpers import Helpers


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username" "email",
            "first_name",
            "last_name",
            "password",
            "password_confirmation",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        username = attrs.get("username", "")
        if not username.isalnum():
            raise ValidationError("The username should be contain alpha chars")
        if attrs["password"] != attrs["password_confirmation"]:
            raise ValidationError("password and password confirmation does not match!")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserLoginSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)
        
        if not user:
            raise AuthenticationFailed("Invalid credentials!")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled!")

        # if user is not None:
        #         token = Helpers.get_tokens_for_user(user)
        #         context = {"user": user, "token": token, "msg": "login successful"}
        #         return Response(context, status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         "email or password is wrong", status=status.HTTP_404_NOT_FOUND
        #     )
        return {
            "email": email,
            "username": user.username,
            "tokens": Helpers.get_tokens_for_user(user),
        }


class RegisterSerializer(Serializer):
    # email = serializers.EmailField(required=True, validator=[UniqueValidator])
    password_1 = serializers.CharField(required=True)
    password_2 = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password_1",
            "password_2",
            "firsts_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password_1"] != attrs["password_2"]:
            raise ValidationError({"password": "Passwords not same"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password_1"])
        user.save()

class UserLogoutSerializer(Serializer):
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        self.token = attrs.get('refresh')
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
        old_password = attrs.get("old_password")
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")

        if password != password2:
            raise ValidationError({"password": "Passwords not same"})

        user.set_password(password)
        user.save()
        return attrs


class UserForgotPasswordSerializer(Serializer):
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
            relativeLink = reverse('')
            link = 'https://localhost:3000/api/password_reset/'+uid+'/'+token
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
