import uuid
from django.db import models

class Bid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing_id = models.UUIDField(db_index=True)
    bidder_id = models.UUIDField(db_index=True)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    max_auto_bid = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True) # For proxy bidding
    is_winning = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount', 'created_at']
        indexes = [
            models.Index(fields=['listing_id', '-amount']),
        ]

    def __str__(self):
        return f"{self.amount} on {self.listing_id} by {self.bidder_id}"

class AuctionState(models.Model):
    listing_id = models.UUIDField(primary_key=True)
    current_price = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    bid_count = models.IntegerField(default=0)
    high_bidder_id = models.UUIDField(null=True, blank=True)
    end_time = models.DateTimeField()
    is_extended = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='OPEN')
    updated_at = models.DateTimeField(auto_now=True)
