import logging
import uuid
import os
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from .models import WalletBalance, LedgerEntry, DepositAddress, WithdrawalRequest, Escrow
from hdwallet import HDWallet
from hdwallet.symbols import DOGE
from shared.event_bus import event_bus

logger = logging.getLogger(__name__)

class WalletService:
    def __init__(self):
        # In production, this would be an xpub key from Secrets Manager
        self.master_xpub = os.environ.get('WALLET_MASTER_XPUB', 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9c6aMufMR9b3LzF4i5G9w1c5s1L1F1F1F1F1F1F1F1F1F1F1')

    def get_or_create_wallet(self, user_id):
        wallet, created = WalletBalance.objects.get_or_create(user_id=user_id)
        if created:
            self.generate_deposit_address(user_id)
        return wallet

    def generate_deposit_address(self, user_id):
        count = DepositAddress.objects.count()
        path_index = count + 1
        derivation_path = f"m/44'/3'/0'/0/{path_index}"
        
        # Mock address generation
        address = f"D{uuid.uuid4().hex[:33]}" 
        
        DepositAddress.objects.create(
            user_id=user_id,
            address=address,
            derivation_path=derivation_path
        )
        return address

    @transaction.atomic
    def process_deposit(self, user_id, amount, txid, address):
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

    @transaction.atomic
    def lock_funds(self, user_id, amount, reference_type, reference_id):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        amount = Decimal(amount)
        
        if wallet.available < amount:
            raise ValueError("Insufficient funds")
            
        wallet.available = F('available') - amount
        wallet.locked = F('locked') + amount
        wallet.save()
        
        idempotency_key = f"lock:{reference_type}:{reference_id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='LOCKED',
            debit=amount,
            balance_after=wallet.available,
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Locked funds for {reference_type} {reference_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def unlock_funds(self, user_id, amount, reference_type, reference_id):
        wallet = WalletBalance.objects.select_for_update().get(user_id=user_id)
        amount = Decimal(amount)
        
        wallet.locked = F('locked') - amount
        wallet.available = F('available') + amount
        wallet.save()
        
        idempotency_key = f"unlock:{reference_type}:{reference_id}"
        
        LedgerEntry.objects.create(
            user_id=user_id,
            entry_type='UNLOCKED',
            credit=amount, 
            balance_after=wallet.available, # approximate
            reference_type=reference_type,
            reference_id=reference_id,
            description=f"Unlocked funds for {reference_type} {reference_id}",
            idempotency_key=idempotency_key
        )

    @transaction.atomic
    def pay_order(self, buyer_id, seller_id, amount, order_id, fee):
        wallet = WalletBalance.objects.select_for_update().get(user_id=buyer_id)
        amount = Decimal(amount)
        fee = Decimal(fee)
        
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
        amount = Decimal(amount)
        fee = Decimal(fee)
        
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
