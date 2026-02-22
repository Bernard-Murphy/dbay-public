from rest_framework import serializers
from .models import Category, CategoryItem


class CategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryItem
        fields = ("id", "name", "sort_order", "image_url")


class CategorySerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id",)

    def get_path(self, obj):
        return str(obj.path) if obj.path else ""


class CategoryWithItemsSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()
    items = CategoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "path", "icon_url", "default_icon", "sort_order", "items")

    def get_path(self, obj):
        return str(obj.path) if obj.path else ""
