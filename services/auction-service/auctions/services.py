import logging
import os
import requests
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from shared.cache import cache
from shared.event_bus import event_bus
from .models import Bid, AuctionState

logger = logging.getLogger(__name__)

LISTING_SERVICE_URL = os.environ.get('LISTING_SERVICE_URL', 'http://listing-service:8001')
WALLET_SERVICE_URL = os.environ.get('WALLET_SERVICE_URL', 'http://wallet-service:8000')

class AuctionService:
    def place_bid(self, listing_id, bidder_id, amount, max_auto_bid=None):
        # DOGE must be whole numbers
        amount = Decimal(int(round(float(amount))))
        if max_auto_bid:
            max_auto_bid = Decimal(max_auto_bid)

        # 1. Distributed Lock
        lock_key = f"lock:auction:{listing_id}"
        lock = cache.redis.lock(lock_key, timeout=10)
        
        if not lock.acquire(blocking=True, blocking_timeout=5):
            raise Exception("Could not acquire lock")
            
        try:
            # 2. Get or Create AuctionState
            state = self.get_or_create_state(listing_id)
            
            if not state:
                 raise Exception("Auction not found")
                 
            # 3. Validation
            now = timezone.now()
            if state.end_time < now:
                raise Exception("Auction ended")
                
            min_increment = Decimal('1.0') # Fixed for now, should be dynamic based on price
            min_bid = state.current_price + min_increment
            
            # If no bids yet, min_bid might be starting_price?
            # get_or_create_state sets current_price to starting_price.
            # If bid_count == 0, min_bid = starting_price.
            if state.bid_count == 0:
                min_bid = state.current_price
            
            if amount < min_bid:
                raise Exception(f"Bid must be at least {min_bid}")
                
            # 4. Lock Funds (Wallet Service)
            self.lock_funds(bidder_id, amount, listing_id)
            
            # 5. Process Bid
            previous_high_bidder = state.high_bidder_id
            previous_price = state.current_price
            
            # Create Bid
            bid = Bid.objects.create(
                listing_id=listing_id,
                bidder_id=bidder_id,
                amount=amount,
                max_auto_bid=max_auto_bid,
                is_winning=True # For now
            )
            
            # Update State
            state.current_price = amount # Simple logic, no proxy bidding complexity yet
            state.high_bidder_id = bidder_id
            state.bid_count += 1
            
            # Anti-sniping
            if state.end_time - now < timedelta(minutes=5):
                state.end_time += timedelta(minutes=5)
                state.is_extended = True
                
            state.save()
            
            # 6. Unlock Funds for previous bidder
            if previous_high_bidder and previous_high_bidder != bidder_id:
                # We need to know previous bid amount?
                # Ideally we query the previous winning bid.
                # Or we just unlock what we locked?
                # We locked the previous high bid amount.
                # But we don't know it here easily without querying Bid history.
                # Let's query previous winning bid.
                # Wait, we just marked new bid as winning.
                # Previous winning bid is now losing.
                # We need to find the bid that WAS winning.
                # But we don't have it easily.
                # Let's assume we unlock `previous_price`? No, price might be lower than bid (proxy).
                # Simple model: `current_price` IS the locked amount.
                # So unlock `previous_price`.
                
                try:
                    self.unlock_funds(previous_high_bidder, previous_price, listing_id)
                    
                    event_bus.publish('dbay.auction-service', 'bid.outbid', {
                        'listing_id': str(listing_id),
                        'bidder_id': str(previous_high_bidder),
                        'amount': str(previous_price)
                    })
                except Exception as e:
                    logger.error(f"Failed to unlock funds for {previous_high_bidder}: {e}")
            
            # 7. Update Redis & Events
            cache.set_json(f"auction:{listing_id}", {
                "current_price": str(state.current_price),
                "bid_count": state.bid_count,
                "high_bidder_id": str(state.high_bidder_id),
                "end_time": state.end_time.isoformat(),
                "extended": state.is_extended
            })
            
            event_bus.publish('dbay.auction-service', 'bid.placed', {
                'listing_id': str(listing_id),
                'bidder_id': str(bidder_id),
                'amount': str(amount),
                'timestamp': bid.created_at.isoformat()
            })
            
            return bid
            
        finally:
            lock.release()

    def get_or_create_state(self, listing_id):
        try:
            return AuctionState.objects.get(listing_id=listing_id)
        except AuctionState.DoesNotExist:
            # Fetch from Listing Service
            try:
                response = requests.get(f"{LISTING_SERVICE_URL}/api/v1/listings/listings/{listing_id}/")
                if response.status_code == 200:
                    data = response.json()
                    if data['listing_type'] != 'AUCTION':
                         return None
                    raw_end = data.get('end_time')
                    if raw_end:
                        end_time = datetime.fromisoformat(str(raw_end).replace('Z', '+00:00'))
                    else:
                        end_time = timezone.now() + timedelta(days=7)
                    state = AuctionState.objects.create(
                        listing_id=listing_id,
                        current_price=Decimal(int(round(float(data['starting_price'] or 0)))),
                        end_time=end_time,
                        bid_count=0
                    )
                    return state
            except Exception as e:
                logger.error(f"Error fetching listing {listing_id}: {e}")
                return None
        return None

    def lock_funds(self, user_id, amount, listing_id):
        response = requests.post(f"{WALLET_SERVICE_URL}/api/v1/wallet/wallet/internal/lock/", json={
            "user_id": str(user_id),
            "amount": str(amount),
            "reference_type": "auction",
            "reference_id": str(listing_id)
        })
        if response.status_code != 200:
             raise Exception(f"Failed to lock funds: {response.text}")

    def unlock_funds(self, user_id, amount, listing_id):
        requests.post(f"{WALLET_SERVICE_URL}/api/v1/wallet/wallet/internal/unlock/", json={
            "user_id": str(user_id),
            "amount": str(amount),
            "reference_type": "auction",
            "reference_id": str(listing_id)
        })

auction_service = AuctionService()
