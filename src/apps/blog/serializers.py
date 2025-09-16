from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer
from taggit.serializers import TagListSerializerField, TaggitSerializer

from .models import Category, Post, Tag


class CategorySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug", "url"]


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
        fields = ["id", "name", "description", "is_active", "url", "parent"]


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return CategoryTreeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active", "children"]


class TagSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "url"]


# TaggitSerializer
class PostSerializer(HyperlinkedModelSerializer, TaggitSerializer):
    # category = CategorySerializer(many=False)
    tags = TagListSerializerField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ["title", "slug", "created_at", "updated_at", "url", 'tags', 'author',]
