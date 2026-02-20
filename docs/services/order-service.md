# Order Service

**Type:** Django REST Framework microservice
**Port:** 8005
**Database:** PostgreSQL

## Overview

The Order Service manages the complete order lifecycle from creation through completion. It handles both auction wins and Buy It Now purchases, shipping tracking, and dispute initiation.

## API Endpoints

### Orders

| Method | Endpoint                        | Description                         |
| ------ | ------------------------------- | ----------------------------------- |
| GET    | `/api/v1/orders/`               | List user's orders (buyer + seller) |
| GET    | `/api/v1/orders/{id}/`          | Get order details                   |
| POST   | `/api/v1/orders/{id}/ship/`     | Mark as shipped (seller)            |
| POST   | `/api/v1/orders/{id}/complete/` | Confirm receipt (buyer)             |
| POST   | `/api/v1/orders/{id}/dispute/`  | Open dispute                        |

### Internal Endpoints (Service-to-Service)

| Method | Endpoint                             | Description                       |
| ------ | ------------------------------------ | --------------------------------- |
| POST   | `/api/v1/orders/internal/create/`    | Create order (from auction close) |
| POST   | `/api/v1/orders/internal/mark-paid/` | Mark order as paid                |
| POST   | `/api/v1/orders/{id}/purchase/`      | Buy It Now purchase               |

### Disputes (Admin)

| Method | Endpoint                 | Description               |
| ------ | ------------------------ | ------------------------- |
| GET    | `/api/v1/disputes/`      | List all disputes (admin) |
| GET    | `/api/v1/disputes/{id}/` | Get dispute details       |
| PATCH  | `/api/v1/disputes/{id}/` | Update dispute (resolve)  |

## Models

### Order

```python
class Order(models.Model):
    STATUSES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('DISPUTED', 'Disputed'),
        ('REFUNDED', 'Refunded'),
    ]

    id = UUIDField(primary_key=True)
    listing_id = UUIDField()
    buyer_id = UUIDField()
    seller_id = UUIDField()

    amount = DecimalField()  # Purchase price
    fee_amount = DecimalField()  # Platform fee
    shipping_cost = DecimalField(default=0)

    status = CharField(choices=STATUSES)

    shipping_address = JSONField()
    tracking_number = CharField(null=True)
    carrier = CharField(null=True)

    escrow_id = UUIDField(null=True)  # Wallet Service escrow

    created_at = DateTimeField(auto_now_add=True)
    paid_at = DateTimeField(null=True)
    shipped_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
```

### Dispute

```python
class Dispute(models.Model):
    STATUSES = ['OPEN', 'EVIDENCE', 'REVIEW', 'RESOLVED', 'CLOSED']
    RESOLUTIONS = ['REFUND_BUYER', 'RELEASE_SELLER', 'PARTIAL_REFUND', 'NO_ACTION']

    id = UUIDField(primary_key=True)
    order = OneToOneField(Order)
    opened_by = UUIDField()  # User who opened
    reason = TextField()
    evidence = JSONField(default=list)  # URLs to uploaded evidence
    status = CharField(choices=STATUSES)
    resolution = CharField(choices=RESOLUTIONS, null=True)
    admin_notes = TextField(blank=True)
    resolved_at = DateTimeField(null=True)
```

## Order Lifecycle

### Auction Win

```
PENDING_PAYMENT → (AuctionCloseWorkflow pays) → PAID → SHIPPED → COMPLETED
```

### Buy It Now

```
POST /purchase → Order created PENDING → Wallet debited → PAID → SHIPPED → COMPLETED
```

### With Dispute

```
PAID/SHIPPED → DISPUTED → (DisputeWorkflow) → REFUNDED or COMPLETED
```

## Service Methods

### create_order(listing_id, buyer_id, seller_id, amount)

Creates order in PENDING_PAYMENT status.

### mark_paid(order_id, escrow_id)

Updates status to PAID, links escrow.

### mark_shipped(order_id, tracking_number, carrier)

Updates status to SHIPPED, sends notification.

### complete_order(order_id)

Updates status to COMPLETED, triggers escrow release.

### purchase_listing(listing_id, user_id)

Full Buy It Now flow - create order, call Wallet to pay.

## Events Published

- `order.created` - New order created
- `order.paid` - Payment confirmed
- `order.shipped` - Seller shipped item
- `order.completed` - Buyer confirmed receipt
- `order.disputed` - Dispute opened

## Escrow Release

After `complete_order()`:

1. Call Wallet Service `/internal/release-escrow/`
2. Wallet credits seller (amount - fee)
3. Order status becomes COMPLETED

Auto-completion occurs 7 days after SHIPPED if buyer doesn't act.

## Dependencies

- PostgreSQL (orders, disputes)
- Wallet Service (escrow management)
- Listing Service (listing details)
- EventBridge (event publishing)
