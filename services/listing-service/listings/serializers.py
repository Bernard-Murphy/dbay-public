from rest_framework import serializers
from .models import Listing, ListingImage, Watchlist
from categories.models import Category

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = '__all__'
        read_only_fields = ('id', 'url_thumb', 'url_medium', 'url_large', 'created_at')

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('id', 'seller_id', 'created_at', 'updated_at', 'view_count', 'watch_count', 'quantity_sold')
    
    def create(self, validated_data):
        return super().create(validated_data)

class WatchlistSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = Watchlist
        fields = ('user_id', 'listing', 'created_at')
        read_only_fields = ('user_id', 'created_at')
