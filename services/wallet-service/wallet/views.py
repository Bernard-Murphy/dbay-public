import os
import uuid
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import WalletBalance, LedgerEntry, DepositAddress, WithdrawalRequest
from .serializers import WalletBalanceSerializer, LedgerEntrySerializer, DepositAddressSerializer, WithdrawalRequestSerializer
from .services import wallet_service

logger = logging.getLogger(__name__)

# Fixed dev UUID when X-User-ID is missing or not a valid UUID (e.g. 'test-user-id')
DEV_USER_ID = "00000000-0000-0000-0000-000000000001"


def _user_id_from_request(request):
    raw = request.headers.get("X-User-ID") or DEV_USER_ID
    try:
        return str(uuid.UUID(raw))
    except (ValueError, TypeError):
        return DEV_USER_ID


class WalletViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated] # Assuming auth middleware handles user context

    @action(detail=False, methods=['get'])
    def balance(self, request):
        user_id = _user_id_from_request(request)
        wallet = wallet_service.get_or_create_wallet(user_id)
        serializer = WalletBalanceSerializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='deposit-address')
    def deposit_address(self, request):
        user_id = _user_id_from_request(request)
        try:
            address = DepositAddress.objects.get(user_id=user_id)
        except DepositAddress.DoesNotExist:
            wallet_service.get_or_create_wallet(user_id)
            try:
                address = DepositAddress.objects.get(user_id=user_id)
            except DepositAddress.DoesNotExist:
                wallet_service.generate_deposit_address(user_id)
                address = DepositAddress.objects.get(user_id=user_id)
        serializer = DepositAddressSerializer(address)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        user_id = _user_id_from_request(request)
        amount = request.data.get('amount')
        address = request.data.get('address') or request.data.get('destination_address')
        if not amount or not address:
             return Response({"error": "Amount and address required"}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            withdrawal = wallet_service.request_withdrawal(user_id, amount, address)
            # Withdrawal is processed asynchronously by WithdrawalStateMachine (EventBridge).
            # For local dev with sync flow, set USE_SYNC_WITHDRAWAL=1 to call process_withdrawal here.
            if os.environ.get("USE_SYNC_WITHDRAWAL") == "1":
                wallet_service.process_withdrawal(withdrawal.id)
            withdrawal.refresh_from_db()
            serializer = WithdrawalRequestSerializer(withdrawal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing withdrawal: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='simulate-deposit')
    def simulate_deposit(self, request):
        """Simulate a deposit (dev/testing). Credits DOGE to the current user's wallet."""
        user_id = _user_id_from_request(request)
        amount = request.data.get('amount')
        if amount is None:
            return Response({"error": "amount required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wallet_service.simulate_deposit(user_id, amount)
            wallet = wallet_service.get_or_create_wallet(user_id)
            serializer = WalletBalanceSerializer(wallet)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

    @action(detail=False, methods=['post'], url_path='internal/credit-deposit')
    def internal_credit_deposit(self, request):
        """Internal: credit a deposit by address (used by CreditUser Lambda). Body: address, amount, txid."""
        address = request.data.get('address')
        amount = request.data.get('amount')
        txid = request.data.get('txid')
        if not address or amount is None or not txid:
            return Response(
                {'error': 'address, amount, and txid required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            if wallet_service.credit_deposit_by_address(address, amount, txid):
                return Response({'status': 'credited'})
            return Response({'error': 'unknown address'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error crediting deposit: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='internal/finalize-withdrawal')
    def internal_finalize_withdrawal(self, request):
        """Internal: set withdrawal CONFIRMED and decrement pending (used by FinalizeLedger Lambda)."""
        withdrawal_id = request.data.get('withdrawal_id')
        txid = request.data.get('txid')
        if not withdrawal_id or not txid:
            return Response(
                {'error': 'withdrawal_id and txid required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            wallet_service.finalize_withdrawal(withdrawal_id, txid)
            return Response({'status': 'finalized'})
        except Exception as e:
            logger.error(f"Error finalizing withdrawal: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def history(self, request):
        user_id = _user_id_from_request(request)
        entries = LedgerEntry.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = LedgerEntrySerializer(entries, many=True)
        return Response(serializer.data)
