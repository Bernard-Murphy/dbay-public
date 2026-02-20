import uuid
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
        ('DISPUTED', 'Disputed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing_id = models.UUIDField()
    buyer_id = models.UUIDField()
    seller_id = models.UUIDField()
    order_type = models.CharField(max_length=20, choices=[('AUCTION', 'Auction'), ('BUY_IT_NOW', 'Buy It Now')])
    
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    shipping_cost = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    fee_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    
    shipping_tracking_number = models.CharField(max_length=100, blank=True)
    shipping_carrier = models.CharField(max_length=50, blank=True)
    
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    escrow_id = models.UUIDField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Dispute(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('EVIDENCE_COLLECTION', 'Evidence Collection'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED_BUYER', 'Resolved for Buyer'),
        ('RESOLVED_SELLER', 'Resolved for Seller'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='dispute')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    buyer_evidence = models.TextField(blank=True)
    seller_evidence = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
