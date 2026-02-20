# Event Catalog

All events flow through the `dbay-events` EventBridge bus.

## Event Schema

```json
{
  "source": "dbay.<service-name>",
  "detail-type": "<domain>.<action>",
  "detail": {
    // Event-specific payload
  }
}
```

## Listing Events

### listing.created

**Source:** `dbay.listing-service`

```json
{
  "id": "uuid",
  "seller_id": "uuid",
  "title": "string",
  "category_id": "number",
  "listing_type": "AUCTION|BUY_IT_NOW|BOTH",
  "starting_price": "decimal",
  "status": "ACTIVE",
  "created_at": "ISO8601"
}
```

**Consumers:** search-indexer Lambda

### listing.updated

**Source:** `dbay.listing-service`

```json
{
  "id": "uuid",
  "title": "string",
  "current_price": "decimal",
  "status": "string"
}
```

**Consumers:** search-indexer Lambda

### listing.deleted

**Source:** `dbay.listing-service`

```json
{
  "id": "uuid"
}
```

**Consumers:** search-indexer Lambda

---

## Auction Events

### bid.placed

**Source:** `dbay.auction-service`

```json
{
  "listing_id": "uuid",
  "bidder_id": "uuid",
  "amount": "decimal",
  "bid_count": "number",
  "timestamp": "ISO8601"
}
```

**Consumers:** broadcast-update Lambda (WebSocket), notification-service

### bid.outbid

**Source:** `dbay.auction-service`

```json
{
  "listing_id": "uuid",
  "bidder_id": "uuid",
  "amount": "decimal"
}
```

**Consumers:** broadcast-update Lambda, notification-service

### auction.closed

**Source:** `dbay.auction-service`

```json
{
  "listing_id": "uuid",
  "winner_id": "uuid",
  "winning_bid": "decimal"
}
```

**Consumers:** notification-service

---

## Wallet Events

### deposit.detected

**Source:** `dbay.deposit-watcher`

```json
{
  "txid": "string",
  "address": "string",
  "amount": "decimal",
  "confirmations": "number"
}
```

**Consumers:** DepositConfirmationWorkflow (Step Functions)

### deposit.confirmed

**Source:** `dbay.wallet-service`

```json
{
  "user_id": "uuid",
  "amount": "decimal",
  "txid": "string"
}
```

**Consumers:** notification-service

### withdrawal.requested

**Source:** `dbay.wallet-service`

```json
{
  "withdrawal_id": "uuid",
  "user_id": "uuid",
  "amount": "decimal",
  "address": "string"
}
```

**Consumers:** WithdrawalWorkflow (Step Functions)

### withdrawal.confirmed

**Source:** `dbay.wallet-service`

```json
{
  "withdrawal_id": "uuid",
  "txid": "string"
}
```

**Consumers:** notification-service

---

## Order Events

### order.created

**Source:** `dbay.order-service`

```json
{
  "order_id": "uuid",
  "listing_id": "uuid",
  "buyer_id": "uuid",
  "seller_id": "uuid",
  "amount": "decimal"
}
```

### order.paid

**Source:** `dbay.order-service`

```json
{
  "order_id": "uuid",
  "buyer_id": "uuid",
  "seller_id": "uuid"
}
```

**Consumers:** notification-service

### order.shipped

**Source:** `dbay.order-service`

```json
{
  "order_id": "uuid",
  "tracking_number": "string"
}
```

**Consumers:** notification-service

### order.completed

**Source:** `dbay.order-service`

```json
{
  "order_id": "uuid"
}
```

**Consumers:** notification-service, fee-calculator Lambda

---

## User Events

### user.registered

**Source:** `dbay.user-service`

```json
{
  "user_id": "uuid",
  "email": "string",
  "username": "string"
}
```

### feedback.submitted

**Source:** `dbay.user-service`

```json
{
  "feedback_id": "uuid",
  "from_user_id": "uuid",
  "to_user_id": "uuid",
  "rating": "POSITIVE|NEUTRAL|NEGATIVE"
}
```

**Consumers:** notification-service
