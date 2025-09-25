from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from rest_framework import serializers
from .models import OtpRequest, User, UserProfile, UserMeta


class UserSerializer(HyperlinkedModelSerializer):
    posts = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='post_detail')
    class Meta:
        model = User
        fields = ['url', 'id', 'email']


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile


class UserMetaSerializer(ModelSerializer):
    class Meta:
        model = UserMeta
        
        
class RequestOTPSerialize(serializers.Serializer):
    receiver = serializers.CharField(min_length=3, allow_null=False)
    # channel = serializers.ChoiceField(allow_null=False, choices=OtpChannel.channels) 

class VerifyOTPSerialize(serializers.Serializer):
    request_id = serializers.UUIDField(allow_null=False)
    password = serializers.CharField(max_length=4, allow_null=False)
    receiver = serializers.CharField(min_length=3, allow_null=False)


class ObtainTokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=128, allow_null=False)
    refresh = serializers.CharField(max_length=128, allow_null=False)
    created = serializers.BooleanField()



class RequestOTPResponseSerializer(ModelSerializer):
    class Meta:
        model = OtpRequest
        fields = ['request_id']
        

