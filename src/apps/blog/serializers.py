from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from taggit.serializers import TaggitSerializer, TagListSerializerField
from apps.accounts.models import User
from .models import Category, Post


class AuthorSerializer(ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "full_name",
        ]


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class CreateCategoryNodeSerializer(HyperlinkedModelSerializer):
    parent = serializers.IntegerField(required=False)

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)

        if parent is None:
            instance = Category.add_root(**validated_data)
        else:
            parent_node = get_object_or_404(Category, pk=parent)
            instance = parent_node.add_child(**validated_data)
        return instance

    class Meta:
        model = Category
        fields = ["id", "name", "description", "url", "parent"]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "parent",
            "children",
        ]


class PostSerializer(ModelSerializer, TaggitSerializer):
    category = CategorySerializer(many=False)
    tags = TagListSerializerField()
    author = AuthorSerializer()

    class Meta:
        model = Post
        fields = [
            "id",
            "uuid",
            "title",
            "slug",
            "body",
            "thumbnail",
            "created_at",
            "updated_at",
            "category",
            "tags",
            "author",
        ]
