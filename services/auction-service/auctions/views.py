from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bid, AuctionState
from .serializers import BidSerializer, AuctionStateSerializer
from .services import auction_service
from django.utils import timezone
from datetime import timedelta

class AuctionViewSet(viewsets.ViewSet):
    @action(detail=True, methods=['post'], url_path='bid')
    def place_bid(self, request, pk=None):
        listing_id = pk
        bidder_id = request.headers.get('X-User-ID') or 'test-user-id'
        amount = request.data.get('amount')
        
        try:
            bid = auction_service.place_bid(listing_id, bidder_id, amount)
            return Response(BidSerializer(bid).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def state(self, request, pk=None):
        state = auction_service.get_or_create_state(pk)
        if not state:
            return Response({'error': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AuctionStateSerializer(state).data)

    @action(detail=True, methods=['get'])
    def bids(self, request, pk=None):
        bids = Bid.objects.filter(listing_id=pk).order_by('-amount')
        return Response(BidSerializer(bids, many=True).data)

    @action(detail=False, methods=['get'], url_path='ending')
    def ending(self, request):
        now = timezone.now()
        # Find auctions ending in the next minute or already ended but not closed
        # Ideally check status='OPEN'
        states = AuctionState.objects.filter(end_time__lte=now + timedelta(minutes=1), status='OPEN')
        return Response(AuctionStateSerializer(states, many=True).data)

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        # Internal endpoint called by Step Function
        # Verify it ended
        state = AuctionState.objects.get(listing_id=pk)
        if state.status == 'CLOSED':
            return Response({'status': 'already_closed'})
            
        now = timezone.now()
        if state.end_time > now:
             return Response({'error': 'Auction not ended yet'}, status=status.HTTP_400_BAD_REQUEST)
             
        state.status = 'CLOSED'
        state.save()
        
        # Return winner info
        winner_id = state.high_bidder_id
        winning_bid = state.current_price
        
        return Response({
            'listing_id': pk,
            'winner_id': winner_id,
            'winning_bid': winning_bid
        })
