import logging
import os
import requests
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from shared.event_bus import event_bus
from .models import Order, Dispute

logger = logging.getLogger(__name__)

WALLET_SERVICE_URL = os.environ.get('WALLET_SERVICE_URL', 'http://wallet-service:8003')
LISTING_SERVICE_URL = os.environ.get('LISTING_SERVICE_URL', 'http://listing-service:8001')

class OrderService:
    def create_order(self, listing_id, buyer_id, seller_id, order_type, amount, fee_amount=0):
        # Calculate shipping? Assume passed or calculated from listing
        # For now, simplistic
        order = Order.objects.create(
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            order_type=order_type,
            amount=amount,
            fee_amount=fee_amount,
            status='PENDING_PAYMENT'
        )
        return order

    def mark_paid(self, order_id, escrow_id=None):
        order = Order.objects.get(id=order_id)
        if order.status != 'PENDING_PAYMENT':
             return order # Idempotent?
             
        order.status = 'PAID'
        order.paid_at = timezone.now()
        if escrow_id:
            order.escrow_id = escrow_id
        order.save()
        
        event_bus.publish('dbay.order-service', 'order.paid', {
            'order_id': str(order.id),
            'buyer_id': str(order.buyer_id),
            'seller_id': str(order.seller_id),
            'amount': str(order.amount)
        })
        return order

    def mark_shipped(self, order_id, tracking_number, carrier):
        order = Order.objects.get(id=order_id)
        if order.status != 'PAID':
            raise Exception("Order must be PAID to ship")
            
        order.status = 'SHIPPED'
        order.shipped_at = timezone.now()
        order.shipping_tracking_number = tracking_number
        order.shipping_carrier = carrier
        order.save()
        
        event_bus.publish('dbay.order-service', 'order.shipped', {
            'order_id': str(order.id),
            'tracking_number': tracking_number
        })
        return order

    def complete_order(self, order_id, user_id):
        # Only buyer can complete? Or auto-complete?
        order = Order.objects.get(id=order_id)
        if str(order.buyer_id) != str(user_id):
             raise Exception("Only buyer can complete order")
             
        if order.status not in ['SHIPPED', 'DELIVERED']: # Delivered state might be set by tracking webhook
             pass # Allow completing from SHIPPED
             
        order.status = 'COMPLETED'
        order.completed_at = timezone.now()
        order.save()
        
        # Release Escrow
        self.release_escrow(order.id)
        
        event_bus.publish('dbay.order-service', 'order.completed', {
            'order_id': str(order.id)
        })
        return order

    def release_escrow(self, order_id):
        # Call Wallet Service
        try:
            response = requests.post(f"{WALLET_SERVICE_URL}/api/v1/wallet/internal/release-escrow", json={
                "order_id": str(order_id)
            })
            if response.status_code != 200:
                logger.error(f"Failed to release escrow for {order_id}: {response.text}")
                # Retry logic needed
        except Exception as e:
            logger.error(f"Error calling wallet service: {e}")

    def purchase_listing(self, listing_id, buyer_id):
        # 1. Get Listing
        resp = requests.get(f"{LISTING_SERVICE_URL}/api/v1/listings/{listing_id}/")
        listing = resp.json()
        
        if listing['status'] != 'ACTIVE':
            raise Exception("Listing not active")
            
        amount = Decimal(listing['buy_it_now_price'])
        seller_id = listing['seller_id']
        fee = amount * Decimal('0.03') # 3% fee
        
        # 2. Create Order
        order = self.create_order(listing_id, buyer_id, seller_id, 'BUY_IT_NOW', amount, fee)
        
        # 3. Lock Funds / Transfer to Escrow
        # Call Wallet Service to lock funds and convert to escrow immediately
        # Or just lock funds with reference order_id?
        # Wallet Service needs to support "Purchase" op: Available -> Escrow (Locked)
        
        try:
             # First lock funds
             # Then convert to escrow?
             # Or single call "pay_order"?
             # Let's use `internal/lock` then `internal/convert-to-escrow` or a new endpoint `pay_order`.
             # Creating `pay_order` in Wallet Service would be cleaner.
             # But for now I'll use `lock` then `convert`.
             
             # Actually, `lock` needs `reference_id`.
             # Let's just use `wallet-service` endpoint `pay_order` which does:
             # Debit Buyer Available -> Credit Escrow (Locked)
             
             response = requests.post(f"{WALLET_SERVICE_URL}/api/v1/wallet/internal/pay-order", json={
                 "buyer_id": str(buyer_id),
                 "seller_id": str(seller_id),
                 "amount": str(amount),
                 "order_id": str(order.id),
                 "fee": str(fee)
             })
             
             if response.status_code != 200:
                 order.status = 'CANCELLED'
                 order.save()
                 raise Exception(f"Payment failed: {response.text}")
                 
             self.mark_paid(order.id)
             
             return order
             
        except Exception as e:
             order.status = 'CANCELLED'
             order.save()
             raise e

order_service = OrderService()
