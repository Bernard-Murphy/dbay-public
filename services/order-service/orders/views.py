from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, Dispute
from .serializers import OrderSerializer, DisputeSerializer
from .services import order_service

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            return Order.objects.all() # Or empty
        return Order.objects.filter(models.Q(buyer_id=user_id) | models.Q(seller_id=user_id))

    @action(detail=False, methods=['post'], url_path='purchase')
    def purchase(self, request):
        listing_id = request.data.get('listing_id')
        buyer_id = request.headers.get('X-User-ID') or 'test-buyer'
        
        if not listing_id:
             return Response({'error': 'listing_id required'}, status=status.HTTP_400_BAD_REQUEST)
             
        try:
            order = order_service.purchase_listing(listing_id, buyer_id)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='internal/create')
    def internal_create(self, request):
        # Internal endpoint for Auction Closer
        listing_id = request.data.get('listing_id')
        buyer_id = request.data.get('buyer_id')
        seller_id = request.data.get('seller_id') # Auction Service must provide this
        amount = request.data.get('amount')
        
        # Need to fetch seller_id if not provided?
        # Listing Service has it.
        # But let's assume caller provides it.
        
        try:
            order = order_service.create_order(listing_id, buyer_id, seller_id, 'AUCTION', amount)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        # Internal or external?
        # For auctions, paid via escrow conversion.
        # This endpoint might set status=PAID if external payment?
        # But we only use Dogecoin wallet.
        # So this should be internal only or protected.
        
        escrow_id = request.data.get('escrow_id')
        try:
            order = order_service.mark_paid(pk, escrow_id)
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='ship')
    def ship(self, request, pk=None):
        tracking_number = request.data.get('tracking_number')
        carrier = request.data.get('carrier')
        
        try:
            order = order_service.mark_shipped(pk, tracking_number, carrier)
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        user_id = request.headers.get('X-User-ID') or 'test-buyer'
        try:
            order = order_service.complete_order(pk, user_id)
            return Response(OrderSerializer(order).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
