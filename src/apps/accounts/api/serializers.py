from rest_framework import reverse, serializers
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from apps.financial.models import Wallet
from ..models import (
    OtpRequest,
    User,
    UserMeta,
    UserProfile,
)


class UserEmailRegisterSerializer(ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password should be at least %s characters long.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["updated_at", "created_at"]


class UserSerializer(ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")
    role_title = serializers.CharField(source="get_account_role_title")
    profile = UserProfileSerializer("profile")

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "username",
            "email",
            "mobile",
            "full_name",
            "created_at",
            "role_title",
            "profile",
            # "wallet_balance",
        ]
        read_only_fields = ["id", "username"]

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["wallet_balance"] = instance.wallet.balance
    #     return representation

    # def get_follower_count(self, obj):
    #     return obj.followers.count()


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


class UserMetaSerializer(ModelSerializer):
    class Meta:
        model = UserMeta
        fields = "__all__"


class RequestOTPSerialize(serializers.Serializer):
    receiver = serializers.CharField(min_length=11, max_length=11, allow_null=False)


class RequestOTPResponseSerializer(ModelSerializer):
    class Meta:
        model = OtpRequest
        fields = ["request_id", "receiver"]


class VerifyOTPSerialize(serializers.Serializer):
    request_id = serializers.UUIDField(allow_null=False)
    receiver = serializers.CharField(min_length=11, max_length=11, allow_null=False)
    password = serializers.CharField(min_length=6, max_length=6, allow_null=False)


class ObtainTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128, allow_null=False)
    refresh = serializers.CharField(max_length=128, allow_null=False)
    created = serializers.BooleanField()


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


from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, smart_str
from django.contrib.sites.shortcuts import get_current_site


class UserForgotPasswordEmailSerializer(Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            # token = tokens.PasswordResetTokenGenerator().make_token(user)
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
        # if not tokens.PasswordResetTokenGenerator().check_token(user, token):
        #     raise ValidationError("token is not valid")
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
