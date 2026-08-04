from apps.core.models import Bookmark
from iranian_cities.models import Province
from rest_framework import serializers


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ["name", "code"]


class BookmarkSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField()
    target_id = serializers.IntegerField(source="object_id")

    class Meta:
        model = Bookmark
        fields = ["id", "target_type", "target_id", "created_at"]

    def get_target_type(self, obj):
        return f"{obj.content_type.app_label}.{obj.content_type.model}"
