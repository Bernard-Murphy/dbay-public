from rest_framework import serializers
from .models import Order, Dispute

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at', 'completed_at', 'escrow_id')

class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = '__all__'
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')
