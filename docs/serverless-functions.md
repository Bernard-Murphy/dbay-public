# Serverless Functions

## Overview

dBay uses AWS Lambda functions for event-driven processing, scheduled tasks, and Step Functions workflow steps. All functions are defined in `serverless/template.yaml` using AWS SAM.

## Functions

### image-processor

**Trigger:** S3 `ObjectCreated` event on uploads bucket

**Purpose:** Resize uploaded images into multiple sizes for responsive display.

**Process:**

1. Receive S3 event with original image key
2. Download original image
3. Generate resized versions:
   - Thumbnail: 150x150 (cover)
   - Medium: 600x600 (contain)
   - Large: 1200x1200 (contain)
4. Upload resized images to same bucket
5. (Future) Update Listing Service with image URLs

**Configuration:**

- Memory: 512MB
- Timeout: 30s

---

### auction-closer

**Trigger:** CloudWatch Events schedule (every 1 minute)

**Purpose:** Find ended auctions and initiate close workflow.

**Process:**

1. Call Auction Service `/internal/ending/` endpoint
2. For each ended auction, start `AuctionCloseStateMachine` execution
3. Pass listing_id to state machine

**Configuration:**

- Memory: 256MB
- Timeout: 30s

---

### deposit-watcher

**Trigger:** CloudWatch Events schedule (every 30 seconds)

**Purpose:** Poll Dogecoin node for new deposits.

**Process:**

1. Call Dogecoin RPC `listtransactions`
2. Filter for incoming transactions
3. Match addresses to users via Wallet Service
4. Publish `deposit.detected` events to EventBridge

**Configuration:**

- Memory: 256MB
- Timeout: 30s

---

### search-indexer

**Trigger:** EventBridge rule for `listing.*` events

**Purpose:** Keep Elasticsearch in sync with listings.

**Process:**

1. Receive listing event
2. Based on event type:
   - `listing.created`: Index new document
   - `listing.updated`: Update document
   - `listing.deleted`: Delete document
3. Use bulk API for efficiency when batched

**Configuration:**

- Memory: 256MB
- Timeout: 30s

---

### websocket-handler

**Trigger:** API Gateway WebSocket routes

**Purpose:** Manage WebSocket connections and subscriptions.

**Routes:**

- `$connect`: Store connection ID in Redis
- `$disconnect`: Remove connection from Redis
- `subscribe`: Add connection to channel (e.g., `auction:{listing_id}`)
- `unsubscribe`: Remove connection from channel

**Data Structure (Redis):**

```
connections:{connection_id} → {user_id, connected_at}
subscriptions:auction:{listing_id} → Set of connection_ids
```

**Configuration:**

- Memory: 256MB
- Timeout: 10s

---

### broadcast-update

**Trigger:** EventBridge rule for `bid.placed` events

**Purpose:** Push real-time updates to connected WebSocket clients.

**Process:**

1. Receive bid event
2. Get all subscribers from Redis `subscriptions:auction:{listing_id}`
3. For each connection, call API Gateway Management API `postToConnection`
4. Handle stale connections (remove from Redis on 410 Gone)

**Configuration:**

- Memory: 256MB
- Timeout: 30s

---

### blockchain-broadcaster

**Trigger:** Step Functions `WithdrawalWorkflow`

**Purpose:** Sign and broadcast Dogecoin transactions.

**Process:**

1. Receive unsigned transaction data
2. Retrieve master key from Secrets Manager
3. Sign transaction
4. Broadcast via Dogecoin RPC
5. Return txid

**Security:**

- Only accessible within VPC
- Secrets Manager access via VPC endpoint
- IAM role with minimal permissions

**Configuration:**

- Memory: 512MB
- Timeout: 60s
- VPC: Private subnet

---

### fee-calculator

**Trigger:** EventBridge `order.completed` events

**Purpose:** Calculate and record platform fees.

**Fee Structure:**

- Standard: 5% of sale price
- High-value (>10000 DOGE): 3%
- Minimum fee: 1 DOGE

**Configuration:**

- Memory: 256MB
- Timeout: 10s

---

## Step Functions Workflows

### AuctionCloseStateMachine

**States:**

1. `VerifyAuctionEnded` - Confirm auction is actually ended
2. `DetermineWinner` - Get high bidder from Auction Service
3. `CreateOrder` - Create order via Order Service
4. `LockEscrow` - Convert bid lock to escrow via Wallet Service
5. `UpdateOrderPaid` - Mark order as paid
6. `NotifyUsers` - Send winner/seller notifications
7. `WaitForDelivery` - Wait state (parallel branch)
8. `CheckDispute` - Choice state for dispute path
9. `ReleaseEscrow` or `RefundBuyer` - Final escrow action

---

### WithdrawalStateMachine

**States:**

1. `ValidateBalance` - Confirm funds available
2. `FraudCheck` - Run fraud rules
3. `DebitLedger` - Move to pending in Wallet Service
4. `BuildTransaction` - Create unsigned tx
5. `SignTransaction` - Call blockchain-broadcaster
6. `BroadcastTransaction` - Submit to network
7. `WaitForConfirmation` - Poll for confirmations (loop)
8. `FinalizeLedger` - Update withdrawal status

---

### DepositConfirmationStateMachine

**States:**

1. `RecordPendingDeposit` - Create pending ledger entry
2. `WaitForConfirmations` - Wait 60s
3. `CheckConfirmations` - Poll Dogecoin node
4. `ChoiceConfirmed` - If <6, loop back to wait
5. `CreditUser` - Credit available balance

---

### DisputeStateMachine

**States:**

1. `FreezeEscrow` - Mark escrow as DISPUTED
2. `NotifyParties` - Send emails to buyer/seller
3. `CollectEvidence` - Wait for task token (human input)
4. `AdminReview` - Wait for task token (admin decision)
5. `ResolveDispute` - Choice based on decision
6. `RefundBuyer` or `ReleaseSeller` - Execute resolution
7. `UpdateOrder` - Set final order status
8. `NotifyResolution` - Send outcome notifications
