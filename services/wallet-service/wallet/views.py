from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WalletBalance, LedgerEntry, DepositAddress, WithdrawalRequest
from .serializers import WalletBalanceSerializer, LedgerEntrySerializer, DepositAddressSerializer, WithdrawalRequestSerializer
from .services import wallet_service
import logging

logger = logging.getLogger(__name__)

class WalletViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated] # Assuming auth middleware handles user context

    @action(detail=False, methods=['get'])
    def balance(self, request):
        user_id = request.headers.get('X-User-ID') or 'test-user-id' # Mock
        if not user_id:
            return Response({"error": "User ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
        wallet = wallet_service.get_or_create_wallet(user_id)
        serializer = WalletBalanceSerializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def deposit_address(self, request):
        user_id = request.headers.get('X-User-ID') or 'test-user-id'
        
        try:
            address = DepositAddress.objects.get(user_id=user_id)
        except DepositAddress.DoesNotExist:
            # Should have been created with wallet
            wallet_service.get_or_create_wallet(user_id)
            address = DepositAddress.objects.get(user_id=user_id)
            
        serializer = DepositAddressSerializer(address)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        user_id = request.headers.get('X-User-ID') or 'test-user-id'
        amount = request.data.get('amount')
        address = request.data.get('address')
        
        if not amount or not address:
             return Response({"error": "Amount and address required"}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            withdrawal = wallet_service.request_withdrawal(user_id, amount, address)
            serializer = WithdrawalRequestSerializer(withdrawal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing withdrawal: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='internal/lock')
    def internal_lock(self, request):
        # TODO: verify internal secret
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        reference_type = request.data.get('reference_type')
        reference_id = request.data.get('reference_id')
        
        try:
            wallet_service.lock_funds(user_id, amount, reference_type, reference_id)
            return Response({'status': 'locked'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='internal/unlock')
    def internal_unlock(self, request):
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        reference_type = request.data.get('reference_type')
        reference_id = request.data.get('reference_id')
        
        try:
            wallet_service.unlock_funds(user_id, amount, reference_type, reference_id)
            return Response({'status': 'unlocked'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='internal/convert-to-escrow')
    def internal_convert_to_escrow(self, request):
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        lock_reference_id = request.data.get('lock_reference_id')
        order_id = request.data.get('order_id')
        seller_id = request.data.get('seller_id')
        fee = request.data.get('fee', 0)
        
        try:
            wallet_service.convert_lock_to_escrow(user_id, amount, lock_reference_id, order_id, seller_id, fee)
            return Response({'status': 'converted'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='internal/pay-order')
    def internal_pay_order(self, request):
        buyer_id = request.data.get('buyer_id')
        seller_id = request.data.get('seller_id')
        amount = request.data.get('amount')
        order_id = request.data.get('order_id')
        fee = request.data.get('fee', 0)
        
        try:
            wallet_service.pay_order(buyer_id, seller_id, amount, order_id, fee)
            return Response({'status': 'paid'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='internal/release-escrow')
    def internal_release_escrow(self, request):
        order_id = request.data.get('order_id')
        
        try:
            wallet_service.release_escrow(order_id)
            return Response({'status': 'released'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def history(self, request):
        user_id = request.headers.get('X-User-ID') or 'test-user-id'
        entries = LedgerEntry.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = LedgerEntrySerializer(entries, many=True)
        return Response(serializer.data)
