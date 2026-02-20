import uuid
from django.db import models
from django.db.models import F, Sum
from django.db import transaction

class WalletBalance(models.Model):
    user_id = models.UUIDField(primary_key=True)
    available = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    locked = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    pending = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=0) # For optimistic locking

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(available__gte=0), name='available_positive'),
            models.CheckConstraint(check=models.Q(locked__gte=0), name='locked_positive'),
            models.CheckConstraint(check=models.Q(pending__gte=0), name='pending_positive'),
        ]

class DepositAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    address = models.CharField(max_length=100, unique=True)
    derivation_path = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class LedgerEntry(models.Model):
    ENTRY_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('BID_LOCK', 'Bid Lock'),
        ('BID_UNLOCK', 'Bid Unlock'),
        ('ESCROW_LOCK', 'Escrow Lock'),
        ('ESCROW_RELEASE', 'Escrow Release'),
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('FEE', 'Fee'),
        ('REFUND', 'Refund'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    debit = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    credit = models.DecimalField(max_digits=20, decimal_places=8, default=0.00)
    balance_after = models.DecimalField(max_digits=20, decimal_places=8)
    
    reference_type = models.CharField(max_length=50) # e.g., 'order', 'tx', 'auction'
    reference_id = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    
    idempotency_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DepositTransaction(models.Model):
    STATUS_CHOICES = [
        ('DETECTED', 'Detected'),
        ('CONFIRMED', 'Confirmed'),
        ('CREDITED', 'Credited'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    address = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    txid = models.CharField(max_length=100)
    confirmations = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DETECTED')
    detected_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('txid', 'address') # A tx can have multiple outputs to different addresses

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('PROCESSING', 'Processing'),
        ('SIGNED', 'Signed'),
        ('BROADCAST', 'Broadcast'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8)
    destination_address = models.CharField(max_length=100)
    txid = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

class Escrow(models.Model):
    STATUS_CHOICES = [
        ('LOCKED', 'Locked'),
        ('RELEASED', 'Released'),
        ('REFUNDED', 'Refunded'),
        ('DISPUTED', 'Disputed'),
        ('EXPIRED', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField()
    buyer_id = models.UUIDField()
    seller_id = models.UUIDField()
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    fee_amount = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LOCKED')
    locked_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
