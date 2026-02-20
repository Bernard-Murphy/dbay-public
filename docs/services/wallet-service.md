# Wallet Service

**Type:** Django REST Framework microservice
**Port:** 8003
**Database:** PostgreSQL

## Overview

The Wallet Service manages the custodial Dogecoin wallet system. It handles user balances via double-entry ledger accounting, HD wallet address derivation, deposits, withdrawals, fund locking for bids, and escrow management.

## API Endpoints

### Public Endpoints

| Method | Endpoint                          | Description                                     |
| ------ | --------------------------------- | ----------------------------------------------- |
| GET    | `/api/v1/wallet/balance/`         | Get user's balance (available, locked, pending) |
| GET    | `/api/v1/wallet/deposit-address/` | Get user's deposit address                      |
| POST   | `/api/v1/wallet/withdraw/`        | Request withdrawal                              |
| GET    | `/api/v1/wallet/history/`         | Get ledger history                              |

### Internal Endpoints (Service-to-Service)

| Method | Endpoint                                     | Description              |
| ------ | -------------------------------------------- | ------------------------ |
| POST   | `/api/v1/wallet/internal/lock/`              | Lock funds for bid       |
| POST   | `/api/v1/wallet/internal/unlock/`            | Unlock funds (outbid)    |
| POST   | `/api/v1/wallet/internal/pay-order/`         | Pay for order (BIN)      |
| POST   | `/api/v1/wallet/internal/convert-to-escrow/` | Convert lock to escrow   |
| POST   | `/api/v1/wallet/internal/release-escrow/`    | Release escrow to seller |
| POST   | `/api/v1/wallet/internal/refund-escrow/`     | Refund escrow to buyer   |

## Models

### WalletBalance

```python
class WalletBalance(models.Model):
    user_id = UUIDField(primary_key=True)
    available = DecimalField(default=0)  # Can spend
    locked = DecimalField(default=0)     # In bids/escrow
    pending = DecimalField(default=0)    # Pending withdrawal
    version = IntegerField(default=0)    # Optimistic locking
```

### LedgerEntry

```python
class LedgerEntry(models.Model):
    ENTRY_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('BID_LOCK', 'Bid Lock'),
        ('BID_UNLOCK', 'Bid Unlock'),
        ('ESCROW_LOCK', 'Escrow Lock'),
        ('SALE_CREDIT', 'Sale Credit'),
        ('FEE_DEBIT', 'Fee Debit'),
        ('REFUND', 'Refund'),
    ]

    id = UUIDField(primary_key=True)
    user_id = UUIDField()
    entry_type = CharField(choices=ENTRY_TYPES)
    debit = DecimalField(default=0)
    credit = DecimalField(default=0)
    balance_after = DecimalField()
    reference_type = CharField()  # 'order', 'auction', 'tx'
    reference_id = CharField()
    idempotency_key = CharField(unique=True)
    created_at = DateTimeField(auto_now_add=True)
```

### DepositAddress

```python
class DepositAddress(models.Model):
    user_id = UUIDField(unique=True)
    address = CharField(max_length=100, unique=True)
    derivation_index = IntegerField(unique=True)
```

### WithdrawalRequest

```python
class WithdrawalRequest(models.Model):
    STATUSES = ['PENDING', 'PROCESSING', 'BROADCAST', 'CONFIRMED', 'FAILED']

    id = UUIDField(primary_key=True)
    user_id = UUIDField()
    amount = DecimalField()
    fee = DecimalField()
    destination_address = CharField()
    status = CharField(choices=STATUSES)
    txid = CharField(null=True)
```

### Escrow

```python
class Escrow(models.Model):
    STATUSES = ['LOCKED', 'RELEASED', 'REFUNDED', 'DISPUTED']

    id = UUIDField(primary_key=True)
    order_id = UUIDField()
    buyer_id = UUIDField()
    seller_id = UUIDField()
    amount = DecimalField()
    fee_amount = DecimalField()
    status = CharField(choices=STATUSES)
```

## Service Methods

### get_or_create_wallet(user_id)

Creates wallet if not exists, returns balance info.

### generate_deposit_address(user_id)

Derives next HD address, stores mapping, returns address.

### process_deposit(user_id, amount, txid)

Credits available balance, creates ledger entry.

### request_withdrawal(user_id, amount, address)

Validates balance, moves to pending, publishes event.

### lock_funds(user_id, amount, reference_type, reference_id)

Moves from available to locked (for bids).

### unlock_funds(user_id, amount, reference_type, reference_id)

Moves from locked back to available (outbid).

### pay_order(user_id, amount, order_id)

Debit available, creates escrow record.

### release_escrow(escrow_id)

Credits seller (minus fee), updates escrow status.

### refund_escrow(escrow_id)

Returns funds to buyer, updates escrow status.

## Events Published

- `deposit.confirmed` - Deposit credited to user
- `withdrawal.requested` - User requested withdrawal
- `withdrawal.confirmed` - Withdrawal broadcast and confirmed

## Critical Requirements

1. **Atomicity**: All balance operations use `SELECT FOR UPDATE` + `transaction.atomic()`
2. **Idempotency**: Every ledger entry has unique idempotency key
3. **Audit Trail**: Ledger is append-only, never modified
4. **Non-Negative**: Available balance cannot go below 0

## Dependencies

- PostgreSQL (balances, ledger, escrow)
- AWS Secrets Manager (master HD key)
- Dogecoin RPC (address derivation, tx broadcasting)
- EventBridge (event publishing)
