# Auction Service

**Type:** Django REST Framework microservice
**Port:** 8002
**Database:** PostgreSQL, Redis

## Overview

The Auction Service handles real-time bidding, auction state management, and anti-sniping protection. It coordinates with the Wallet Service to lock funds for bids.

## API Endpoints

### Public Endpoints

| Method | Endpoint                               | Description               |
| ------ | -------------------------------------- | ------------------------- |
| POST   | `/api/v1/auctions/{listing_id}/bid/`   | Place a bid               |
| GET    | `/api/v1/auctions/{listing_id}/state/` | Get current auction state |
| GET    | `/api/v1/auctions/{listing_id}/bids/`  | Get bid history           |

### Internal Endpoints (Service-to-Service)

| Method | Endpoint                               | Description                                   |
| ------ | -------------------------------------- | --------------------------------------------- |
| GET    | `/api/v1/auctions/ending/`             | Get auctions ending soon (for auction-closer) |
| POST   | `/api/v1/auctions/{listing_id}/close/` | Mark auction as closed                        |

## Models

### Bid

```python
class Bid(models.Model):
    id = UUIDField(primary_key=True)
    listing_id = UUIDField()
    bidder_id = UUIDField()
    amount = DecimalField(max_digits=20, decimal_places=8)
    max_bid = DecimalField(null=True)  # Proxy bidding
    created_at = DateTimeField(auto_now_add=True)
```

### AuctionState

```python
class AuctionState(models.Model):
    listing_id = UUIDField(primary_key=True)
    current_price = DecimalField()
    bid_count = IntegerField(default=0)
    high_bidder_id = UUIDField(null=True)
    auction_end_time = DateTimeField()
    status = CharField(choices=STATUSES)  # ACTIVE, CLOSED, SOLD, NO_SALE
    version = IntegerField(default=0)  # Optimistic locking
```

## Bidding Logic

### Placing a Bid

1. Acquire Redis distributed lock for listing
2. Validate bid ≥ current_price + minimum_increment
3. Call Wallet Service to lock bidder's funds
4. If previous high bidder exists, unlock their funds
5. Update AuctionState (optimistic locking)
6. Create Bid record
7. Check anti-sniping extension
8. Publish `bid.placed` event
9. Release lock

### Anti-Sniping Extension

If a bid is placed within 5 minutes of auction end:

```python
if (auction_end_time - now) < timedelta(minutes=5):
    auction_state.auction_end_time = now + timedelta(minutes=5)
```

### Minimum Bid Increments

| Current Price     | Minimum Increment |
| ----------------- | ----------------- |
| 0 - 100 DOGE      | 1 DOGE            |
| 100 - 1000 DOGE   | 5 DOGE            |
| 1000 - 10000 DOGE | 25 DOGE           |
| 10000+ DOGE       | 100 DOGE          |

## Events Published

- `bid.placed` - New bid placed
- `bid.outbid` - Bidder was outbid
- `auction.closed` - Auction ended (with or without winner)

## Events Consumed

- `listing.created` - Initialize auction state (if type=AUCTION)

## Dependencies

- PostgreSQL (bid history, auction state)
- Redis (distributed locking, real-time state cache)
- Wallet Service (fund locking/unlocking)
- EventBridge (event publishing)
