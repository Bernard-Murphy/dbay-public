from rest_framework import serializers
from .models import WalletBalance, LedgerEntry, DepositAddress, WithdrawalRequest

class WalletBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletBalance
        fields = ('user_id', 'available', 'locked', 'pending', 'updated_at')

class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = '__all__'

class DepositAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAddress
        fields = ('address', 'created_at')

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = '__all__'
        read_only_fields = ('id', 'user_id', 'txid', 'status', 'created_at', 'confirmed_at', 'fee')
