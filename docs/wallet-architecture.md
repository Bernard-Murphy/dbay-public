# Wallet Architecture

## Overview

DBay uses a **custodial HD wallet** system where the platform holds Dogecoin on behalf of users. Each user gets a unique deposit address derived from a master key. All internal transactions (bids, purchases, fees) happen as database ledger entries - only deposits and withdrawals interact with the Dogecoin blockchain.

## HD Wallet Structure

```
Master Key (BIP44: m/44'/3'/0')
├── User 1: m/44'/3'/0'/0/0  → DDeposit111...
├── User 2: m/44'/3'/0'/0/1  → DDeposit222...
├── User 3: m/44'/3'/0'/0/2  → DDeposit333...
└── User N: m/44'/3'/0'/0/N  → DDepositNNN...
```

The master key is stored encrypted in AWS Secrets Manager and never leaves that service except during withdrawal signing (in an isolated Lambda).

## Database Schema

### wallet_balances

```sql
user_id     UUID PRIMARY KEY
available   DECIMAL(20,8)  -- Can spend
locked      DECIMAL(20,8)  -- In escrow/bids
pending     DECIMAL(20,8)  -- Pending withdrawals
version     INTEGER        -- Optimistic locking
```

### ledger_entries (Append-Only)

```sql
id              UUID PRIMARY KEY
user_id         UUID
entry_type      ENUM  -- DEPOSIT, WITHDRAWAL, BID_LOCK, ESCROW_LOCK, SALE, FEE, etc.
debit           DECIMAL(20,8)
credit          DECIMAL(20,8)
balance_after   DECIMAL(20,8)
reference_type  VARCHAR  -- 'order', 'tx', 'auction'
reference_id    VARCHAR
idempotency_key VARCHAR UNIQUE
created_at      TIMESTAMP
```

### escrow

```sql
id          UUID PRIMARY KEY
order_id    UUID
buyer_id    UUID
seller_id   UUID
amount      DECIMAL(20,8)
fee_amount  DECIMAL(20,8)
status      ENUM  -- LOCKED, RELEASED, REFUNDED, DISPUTED
```

## Flow: Deposit

```
1. User views Wallet page
2. Frontend requests deposit address
3. Wallet Service returns/generates HD-derived address
4. User sends DOGE from external wallet
5. deposit-watcher Lambda polls Dogecoin node (every 30s)
6. Detects new transaction → publishes deposit.detected event
7. DepositConfirmationWorkflow (Step Functions):
   a. Record pending deposit
   b. Loop: Wait 60s → Check confirmations
   c. After 6 confirmations → Credit user balance
8. User sees updated balance
```

## Flow: Withdrawal

```
1. User submits withdrawal request (amount, destination)
2. Wallet Service:
   a. Validate balance ≥ amount + fee
   b. Move funds: available → pending
   c. Create WithdrawalRequest record
   d. Publish withdrawal.requested event
3. WithdrawalWorkflow (Step Functions):
   a. Fraud check (velocity, thresholds)
   b. Build unsigned transaction
   c. Sign transaction (Lambda with Secrets Manager access)
   d. Broadcast to Dogecoin network
   e. Loop: Wait → Check confirmations
   f. After 6 confirmations → Finalize ledger
4. User sees confirmed withdrawal
```

## Flow: Purchase (Buy It Now)

```
1. Buyer clicks "Buy Now"
2. Order Service:
   a. Create order (PENDING_PAYMENT)
   b. Call Wallet Service /internal/pay-order
3. Wallet Service:
   a. SELECT FOR UPDATE on buyer's wallet
   b. Debit buyer's available balance
   c. Create Escrow record (LOCKED)
   d. Create ledger entry
4. Order marked PAID
5. Seller ships item
6. Buyer confirms receipt OR 7 days pass
7. Order Service calls Wallet /internal/release-escrow
8. Wallet Service:
   a. Credit seller (amount - fee)
   b. Update escrow status to RELEASED
   c. Decrement buyer's locked balance
```

## Flow: Auction Win

```
1. Bidder places winning bid
   - Funds locked (available → locked)
2. Auction ends (auction-closer Lambda)
3. AuctionCloseWorkflow:
   a. Verify auction ended
   b. Determine winner
   c. Convert lock to escrow
   d. Create order
   e. Mark order PAID
4. Same escrow release flow as Buy It Now
```

## Critical Rules

1. **All balance changes require `SELECT FOR UPDATE`**
2. **Every change creates an immutable ledger entry**
3. **Idempotency keys prevent double-processing**
4. **Redis distributed lock before DB transaction**
5. **Available balance can NEVER go negative**
6. **Master key never leaves Secrets Manager**

## Reconciliation

A daily reconciliation job verifies:

```sql
SUM(credits) - SUM(debits) = available + locked + pending
```

For each user. Any discrepancy triggers an alert.
