from rest_framework import serializers
from .models import Category, CategoryItem


class CategoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryItem
        fields = ("id", "name", "sort_order")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id",)


class CategoryWithItemsSerializer(serializers.ModelSerializer):
    items = CategoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "path", "icon_url", "sort_order", "items")
