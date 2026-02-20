from rest_framework import serializers
from .models import Bid, AuctionState

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = '__all__'

class AuctionStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionState
        fields = '__all__'
