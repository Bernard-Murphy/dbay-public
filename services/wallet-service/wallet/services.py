import logging
import os
import requests
import uuid
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from .models import WalletBalance, LedgerEntry, DepositAddress, WithdrawalRequest, Escrow
from hdwallet import HDWallet
from hdwallet.symbols import DOGE
from hdwallet.derivations import Derivation
from shared.event_bus import event_bus

logger = logging.getLogger(__name__)


def _derive_deposit_address(master_xpub: str, path_index: int) -> str:
    """Derive P2PKH address from account-level xpub at path m/0/path_index (BIP44 change=0, address=path_index)."""
    hd = (
        HDWallet(symbol=DOGE)
        .from_xpublic_key(xpublic_key=master_xpub)
        .from_path(path=Derivation(path=f"m/0/{path_index}", semantic="p2pkh"))
    )
    return hd.p2pkh_address()

class WalletService:
    def __init__(self):
        # In production load from Secrets Manager; dev uses env. Empty = use mock address (no real HD derivation).
        self.master_xpub = (os.environ.get('WALLET_MASTER_XPUB') or '').strip()

    def get_or_create_wallet(self, user_id):
        wallet, created = WalletBalance.objects.get_or_create(user_id=user_id)
        if created:
            self.generate_deposit_address(user_id)
        return wallet

    def generate_deposit_address(self, user_id):
        with transaction.atomic():
            path_index = DepositAddress.objects.select_for_update().count() + 1
            derivation_path = f"m/44'/3'/0'/0/{path_index}"
            if self.master_xpub:
                address = _derive_deposit_address(self.master_xpub, path_index)
            else:
                address = f"D{uuid.uuid4().hex[:33]}"
            DepositAddress.objects.create(
                user_id=user_id,
                address=address,
                derivation_path=derivation_path,
            )
        return address

    def credit_deposit_by_address(self, address: str, amount, txid: str) -> bool:
        """Resolve user_id from deposit address and credit. Returns True if credited, False if unknown address (caller may treat as 404)."""
        try:
            rec = DepositAddress.objects.get(address=address)
        except DepositAddress.DoesNotExist:
            return False
        self.process_deposit(rec.user_id, amount, txid, address)
        return True

    @transaction.atomic
    def process_deposit(self, user_id, amount, txid, address):
        amount = Decimal(int(round(float(amount))))
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        idempotency_key = f"deposit:{txid}:{address}"

        if LedgerEntry.objects.filter(idempotency_key=idempotency_key).exists():
            return

        balance_after = wallet.available + amount

        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='DEPOSIT',
            credit=amount,
            balance_after=balance_after,
            reference_type='tx',
            reference_id=txid,
            description=f"Deposit from {address}",
            idempotency_key=idempotency_key
        )

        wallet.available = F('available') + amount
        wallet.save()

        event_bus.publish('dbay.wallet-service', 'deposit.credited', {
            'user_id': str(user_id),
            'amount': str(amount),
            'txid': txid
        })

    @transaction.atomic
    def request_withdrawal(self, user_id, amount, address):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        # DOGE must be whole numbers
        amount = Decimal(int(round(float(amount))))
        fee = Decimal('1.0')
        total_deduction = amount + fee
        
        if wallet.available < total_deduction:
            raise ValueError("Insufficient funds")

        wallet.available = F('available') - total_deduction
        wallet.pending = F('pending') + total_deduction
        wallet.save()
        
        withdrawal_req = WithdrawalRequest.objects.create(
            user_id=user_id,
            amount=amount,
            fee=fee,
            destination_address=address,
            status='REQUESTED'
        )
        
        idempotency_key = f"withdrawal_req:{withdrawal_req.id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='WITHDRAWAL_REQUEST',
            debit=total_deduction,
            balance_after=wallet.available, 
            reference_type='withdrawal',
            reference_id=str(withdrawal_req.id),
            description=f"Withdrawal request to {address}",
            idempotency_key=idempotency_key
        )
        
        event_bus.publish('dbay.wallet-service', 'withdrawal.requested', {
            'withdrawal_id': str(withdrawal_req.id),
            'user_id': str(user_id),
            'amount': str(amount),
            'address': address
        })
        
        return withdrawal_req

    def _rpc_send(self, address, amount_doge):
        """Send DOGE via RPC (mock or real node). Returns txid or None."""
        url = os.environ.get('DOGECOIN_RPC_URL')
        if not url:
            return None
        try:
            # Mock node expects POST with method, params, id
            payload = {"method": "sendtoaddress", "params": [address, float(amount_doge)], "id": 1}
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get('result') or None
        except Exception as e:
            logger.warning(f"RPC sendtoaddress failed: {e}")
            return None

    @transaction.atomic
    def process_withdrawal(self, withdrawal_id):
        """Process a REQUESTED withdrawal: send via RPC (or simulate), mark CONFIRMED, decrement pending."""
        try:
            req = WithdrawalRequest.objects.select_for_update().get(id=withdrawal_id)
        except WithdrawalRequest.DoesNotExist:
            return
        if req.status != 'REQUESTED':
            return
        amount_doge = int(req.amount)
        txid = self._rpc_send(req.destination_address, amount_doge)
        if txid is None:
            txid = f"sim-{uuid.uuid4().hex}"
        req.status = 'CONFIRMED'
        req.txid = txid
        req.confirmed_at = timezone.now()
        req.save()
        wallet = WalletBalance.objects.select_for_update().get(user_id=req.user_id)
        total = req.amount + req.fee
        wallet.pending = F('pending') - total
        wallet.save()

    @transaction.atomic
    def finalize_withdrawal(self, withdrawal_id, txid: str):
        """Set withdrawal CONFIRMED and decrement pending (idempotent). Used by FinalizeLedger Lambda."""
        try:
            req = WithdrawalRequest.objects.select_for_update().get(id=withdrawal_id)
        except WithdrawalRequest.DoesNotExist:
            return
        if req.status != 'REQUESTED':
            return  # idempotency
        req.txid = txid
        req.status = 'CONFIRMED'
        req.confirmed_at = timezone.now()
        req.save()
        wallet = WalletBalance.objects.select_for_update().get(user_id=req.user_id)
        total = req.amount + req.fee
        wallet.pending = F('pending') - total
        wallet.save()

    def simulate_deposit(self, user_id, amount):
        """Credit user's wallet (simulated deposit). For dev/testing."""
        amount = Decimal(int(round(float(amount))))
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.get_or_create_wallet(user_id)
        addr = DepositAddress.objects.get(user_id=user_id)
        txid = f"sim-{uuid.uuid4().hex}"
        self.process_deposit(user_id, amount, txid, addr.address)

    @transaction.atomic
    def lock_funds(self, user_id, amount, reference_type, reference_id):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        amount = Decimal(int(round(float(amount))))
        
        if wallet.available < amount:
            raise ValueError("Insufficient funds")
        balance_after = wallet.available - amount
        wallet.available = F('available') - amount
        wallet.locked = F('locked') + amount
        wallet.save()
        
        idempotency_key = f"lock:{reference_type}:{reference_id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='LOCKED',
            debit=amount,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Locked funds for {reference_type} {reference_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def unlock_funds(self, user_id, amount, reference_type, reference_id):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        amount = Decimal(int(round(float(amount))))
        balance_after = wallet.available + amount
        wallet.locked = F('locked') - amount
        wallet.available = F('available') + amount
        wallet.save()
        
        idempotency_key = f"unlock:{reference_type}:{reference_id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='UNLOCKED',
            credit=amount, 
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Unlocked funds for {reference_type} {reference_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def pay_order(self, buyer_id, seller_id, amount, order_id, fee):
        wallet = WalletBalance.objects.select_for_update().get(user_id=buyer_id)
        amount = Decimal(int(round(float(amount))))
        fee = Decimal(int(round(float(fee))))
        
        if wallet.available < amount:
            raise ValueError("Insufficient funds")
            
        wallet.available = F('available') - amount
        wallet.locked = F('locked') + amount
        wallet.save()
        
        Escrow.objects.create(
            order_id=order_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            amount=amount,
            fee_amount=fee,
            status='LOCKED'
        )
        
        idempotency_key = f"pay_order:{order_id}"
        
        LedgerEntry.objects.create(
            user_id=buyer_id,
            entry_type='PURCHASE',
            debit=amount,
            balance_after=wallet.available,
            reference_type='order',
            reference_id=str(order_id),
            description=f"Payment for order {order_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def convert_lock_to_escrow(self, user_id, amount, lock_reference_id, order_id, seller_id, fee):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        amount = Decimal(int(round(float(amount))))
        fee = Decimal(int(round(float(fee))))
        
        # We assume amount was locked.
        # Reduce Locked (it was locked for auction)
        # But wait, Escrow is ALSO locked.
        # So Locked balance stays same.
        # We just create Escrow record and update Ledger.
        
        Escrow.objects.create(
            order_id=order_id,
            buyer_id=user_id,
            seller_id=seller_id,
            amount=amount,
            fee_amount=fee,
            status='LOCKED'
        )
        
        idempotency_key = f"escrow:{order_id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='ESCROW_LOCK',
            debit=0, 
            credit=0,
            balance_after=wallet.available,
            reference_type='order',
            reference_id=str(order_id),
            description=f"Moved lock from auction {lock_reference_id} to escrow for order {order_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def release_escrow(self, order_id):
        escrow = Escrow.objects.select_for_update().get(order_id=order_id)
        if escrow.status != 'LOCKED':
            return
            
        # Credit seller
        seller_wallet = WalletBalance.objects.select_for_update().get(user_id=escrow.seller_id)
        
        amount_to_seller = escrow.amount - escrow.fee_amount
        
        seller_wallet.available = F('available') + amount_to_seller
        seller_wallet.save()
        
        LedgerEntry.objects.create(
            user_id=escrow.seller_id,
            entry_type='SALE',
            credit=amount_to_seller,
            balance_after=seller_wallet.available, 
            reference_type='order',
            reference_id=str(order_id),
            description=f"Sale revenue for order {order_id}",
            idempotency_key=f"sale:{order_id}"
        )
        
        # Update escrow status
        escrow.status = 'RELEASED'
        escrow.released_at = transaction.now()
        escrow.save()
        
        # Decrement locked balance from buyer
        buyer_wallet = WalletBalance.objects.select_for_update().get(user_id=escrow.buyer_id)
        buyer_wallet.locked = F('locked') - escrow.amount
        buyer_wallet.save()

wallet_service = WalletService()
