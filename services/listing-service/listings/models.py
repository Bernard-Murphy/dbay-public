import uuid
from django.db import models
from categories.models import Category

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('LIKE_NEW', 'Like New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ]
    
    LISTING_TYPE_CHOICES = [
        ('AUCTION', 'Auction'),
        ('BUY_IT_NOW', 'Buy It Now'),
        ('BOTH', 'Both'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('ENDED', 'Ended'),
        ('SOLD', 'Sold'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller_id = models.UUIDField() # ID from User Service
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='listings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    
    buy_it_now_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    starting_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    reserve_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    current_price = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    
    quantity = models.IntegerField(default=1)
    quantity_sold = models.IntegerField(default=0)
    
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    view_count = models.IntegerField(default=0)
    watch_count = models.IntegerField(default=0)
    
    shipping_cost = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    shipping_from_country = models.CharField(max_length=100)
    returns_accepted = models.BooleanField(default=False)
    return_period_days = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ListingImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    s3_key = models.CharField(max_length=1024)
    url_thumb = models.URLField(blank=True, null=True)
    url_medium = models.URLField(blank=True, null=True)
    url_large = models.URLField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order']

class Watchlist(models.Model):
    user_id = models.UUIDField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watchers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'listing')
