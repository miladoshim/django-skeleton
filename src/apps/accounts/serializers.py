from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from rest_framework import serializers
from .models import User, UserProfile, UserMeta


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
