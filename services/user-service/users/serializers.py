from rest_framework import serializers
from .models import User, UserAddress, SellerRating

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class SellerRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRating
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    addresses = UserAddressSerializer(many=True, read_only=True)
    seller_rating = SellerRatingSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'display_name', 'avatar_url', 'seller_verified', 'created_at', 'updated_at', 'addresses', 'seller_rating')
        read_only_fields = ('id', 'email', 'created_at', 'updated_at', 'seller_verified')
