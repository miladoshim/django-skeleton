from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from apps.financial.models import Wallet

from utils import validators
from .models import (
    OtpRequest,
    User,
    UserMeta,
    UserProfile,
)


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["updated_at", "created_at"]


class UserSerializer(ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")
    role_title = serializers.CharField(source="get_account_role_title")
    profile = UserProfileSerializer("profile")
    # follower_count = serializers.SerializerMethodField()
    # posts = serializers.HyperlinkedRelatedField(
    #     many=True, read_only=True, view_name="post_detail"
    # )

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


class UserAddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "title"]
