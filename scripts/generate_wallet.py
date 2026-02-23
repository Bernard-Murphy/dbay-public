#!/usr/bin/env python3
"""
Generate BIP44 Dogecoin account-level xpub/xpriv for WALLET_MASTER_XPUB and WALLET_MASTER_XPRIV.

Run OFFLINE. Do not use on a machine connected to the internet for production keys.
Requires: pip install hdwallet (and, for generating a new mnemonic, pip install mnemonic).

Usage:
  python scripts/generate_wallet.py              # generate new mnemonic and keys
  python scripts/generate_wallet.py --mnemonic "word1 word2 ..."  # derive from existing mnemonic
"""
import argparse
import sys


def _generate_mnemonic():
    """Return a new BIP39 mnemonic (12 words, 128-bit)."""
    try:
        from mnemonic import Mnemonic
        return Mnemonic("english").generate(strength=128)
    except ImportError:
        raise SystemExit(
            "Error: for new wallet generation, install mnemonic: pip install mnemonic"
        ) from None


def main():
    parser = argparse.ArgumentParser(
        description="Generate Dogecoin BIP44 account-level xpub/xpriv (for WALLET_MASTER_XPUB/PRIV)."
    )
    parser.add_argument(
        "--mnemonic",
        type=str,
        default=None,
        help="Existing BIP39 mnemonic (12 or 24 words). If omitted, a new one is generated.",
    )
    parser.add_argument(
        "--passphrase",
        type=str,
        default="",
        help="BIP39 passphrase (optional). Default empty.",
    )
    args = parser.parse_args()

    try:
        from hdwallet import HDWallet
        from hdwallet.symbols import DOGE
        from hdwallet.derivations import Derivation
    except ImportError:
        print("Error: hdwallet is required. Install with: pip install hdwallet", file=sys.stderr)
        sys.exit(1)

    # BIP44 account level for Dogecoin: m/44'/3'/0'
    account_derivation = Derivation(path="m/44'/3'/0'", semantic="p2pkh")

    if args.mnemonic:
        mnemonic_str = args.mnemonic.strip()
        words = mnemonic_str.split()
        if len(words) not in (12, 15, 18, 21, 24):
            print("Error: mnemonic must be 12, 15, 18, 21, or 24 words", file=sys.stderr)
            sys.exit(1)
        try:
            hd = (
                HDWallet(symbol=DOGE)
                .from_mnemonic(mnemonic=mnemonic_str, passphrase=args.passphrase)
                .from_path(path=account_derivation)
            )
        except Exception as e:
            print(f"Error deriving from mnemonic: {e}", file=sys.stderr)
            sys.exit(1)
        print("# Derived from existing mnemonic (do not share)")
        mnemonic_str_to_print = None
    else:
        mnemonic_str = _generate_mnemonic()
        try:
            hd = (
                HDWallet(symbol=DOGE)
                .from_mnemonic(mnemonic=mnemonic_str, passphrase=args.passphrase)
                .from_path(path=account_derivation)
            )
        except Exception as e:
            print(f"Error generating wallet: {e}", file=sys.stderr)
            sys.exit(1)
        print("# New wallet – backup the mnemonic and keep it secret")
        mnemonic_str_to_print = mnemonic_str

    xpub = hd.xpublic_key()
    xpriv = hd.xprivate_key()

    print()
    print("WALLET_MASTER_XPUB=" + xpub)
    print("WALLET_MASTER_XPRIV=" + xpriv)
    if mnemonic_str_to_print:
        print()
        print("# BIP39 mnemonic (backup securely):")
        print(mnemonic_str_to_print)
    print()
    print("# Add the first two lines to your .env (or secrets). Do not commit WALLET_MASTER_XPRIV or mnemonic.")


if __name__ == "__main__":
    main()
