from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from .models import Listing, ListingImage, Watchlist
from categories.models import Category

MAX_LISTING_DAYS = 14

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

    def validate(self, attrs):
        start = attrs.get('start_time')
        end = attrs.get('end_time')
        if start is None and end is not None:
            start = timezone.now()
        if start is not None and end is not None:
            if end <= start:
                raise serializers.ValidationError({"end_time": "End time must be after start time."})
            if (end - start) > timedelta(days=MAX_LISTING_DAYS):
                raise serializers.ValidationError(
                    {"end_time": f"Listing duration cannot exceed {MAX_LISTING_DAYS} days."}
                )
        # DOGE amounts must be whole numbers
        for field in ('starting_price', 'current_price', 'buy_it_now_price', 'reserve_price', 'shipping_cost'):
            val = attrs.get(field)
            if val is not None:
                try:
                    int_val = int(val)
                except (TypeError, ValueError):
                    raise serializers.ValidationError({field: "Must be a whole number (no decimals)."})
                if int_val != float(val):
                    raise serializers.ValidationError({field: "Must be a whole number (no decimals)."})
                attrs[field] = Decimal(int_val)
        return attrs

    def create(self, validated_data):
        return super().create(validated_data)

class WatchlistSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    class Meta:
        model = Watchlist
        fields = ('user_id', 'listing', 'created_at')
        read_only_fields = ('user_id', 'created_at')
