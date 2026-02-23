"""
Build and sign a Dogecoin withdrawal tx: listunspent -> createrawtransaction -> sign with xpriv -> return signed hex.
Expects event: amount, address. Uses HOT_WALLET_DERIVATION_INDEX and WALLET_MASTER_XPRIV (or secret ARN).
"""
import json
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rpc_url = os.environ.get("DOGECOIN_RPC_URL", "http://dogecoin-node:22555")
rpc_user = os.environ.get("DOGECOIN_RPC_USER")
rpc_password = os.environ.get("DOGECOIN_RPC_PASSWORD")
hot_index = int(os.environ.get("HOT_WALLET_DERIVATION_INDEX", "0"))
fee_doge = float(os.environ.get("WITHDRAWAL_FEE_DOGE", "1.0"))


def _get_xpriv():
    xpriv = os.environ.get("WALLET_MASTER_XPRIV")
    if xpriv:
        return xpriv
    arn = os.environ.get("WALLET_MASTER_XPRIV_SECRET_ARN")
    if arn:
        import boto3
        c = boto3.client("secretsmanager")
        r = c.get_secret_value(SecretId=arn)
        return r["SecretString"]
    raise ValueError("WALLET_MASTER_XPRIV or WALLET_MASTER_XPRIV_SECRET_ARN required")


def _rpc(method: str, params: list):
    payload = {"method": method, "params": params, "id": 1, "jsonrpc": "2.0"}
    auth = (rpc_user, rpc_password) if (rpc_user and rpc_password) else None
    resp = requests.post(rpc_url, json=payload, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def _derive_address_and_wif(xpub: str, xpriv: str, path_index: int) -> tuple:
    from hdwallet import HDWallet
    from hdwallet.symbols import DOGE
    from hdwallet.derivations import Derivation
    path = f"m/0/{path_index}"
    derivation = Derivation(path=path, semantic="p2pkh")
    # Address from xpub (for listunspent)
    hd_pub = HDWallet(symbol=DOGE).from_xpublic_key(xpublic_key=xpub).from_path(path=derivation)
    address = hd_pub.address()
    # WIF from xpriv (for signing)
    hd_priv = HDWallet(symbol=DOGE).from_xprivate_key(xprivate_key=xpriv).from_path(path=derivation)
    wif = hd_priv.wif()
    return address, wif


def lambda_handler(event, context):
    amount = float(event.get("amount", 0))
    dest_address = event.get("address")
    if not amount or not dest_address:
        raise ValueError("amount and address required")

    xpub = os.environ.get("WALLET_MASTER_XPUB")
    if not xpub:
        raise ValueError("WALLET_MASTER_XPUB required for listunspent address")
    xpriv = _get_xpriv()
    hot_address, wif = _derive_address_and_wif(xpub, xpriv, hot_index)

    # listunspent: minconf=0, maxconf=999999, addresses=[hot_address]
    unspent = _rpc("listunspent", [0, 9999999, [hot_address]])
    if not unspent:
        raise ValueError("No UTXOs available for hot wallet")

    total_needed = amount + fee_doge
    selected = []
    total_in = 0.0
    for u in sorted(unspent, key=lambda x: -float(x.get("amount", 0))):
        selected.append({"txid": u["txid"], "vout": u["vout"]})
        total_in += float(u["amount"])
        if total_in >= total_needed:
            break
    if total_in < total_needed:
        raise ValueError(f"Insufficient UTXOs: have {total_in}, need {total_needed}")

    change = total_in - total_needed
    outputs = {dest_address: amount}
    if change > 0:
        outputs[hot_address] = round(change, 8)

    raw_hex = _rpc("createrawtransaction", [selected, outputs])
    # signrawtransaction "hex" [] ["wif"]
    signed = _rpc("signrawtransaction", [raw_hex, [], [wif]])
    if not signed.get("complete"):
        raise RuntimeError("Transaction not fully signed: " + str(signed.get("errors")))

    return signed["hex"]