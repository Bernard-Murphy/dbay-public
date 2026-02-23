import json
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rpc_url = os.environ.get("DOGECOIN_RPC_URL", "http://dogecoin-node:22555")
rpc_user = os.environ.get("DOGECOIN_RPC_USER")
rpc_password = os.environ.get("DOGECOIN_RPC_PASSWORD")


def _rpc(method: str, params: list):
    payload = {"method": method, "params": params, "id": 1, "jsonrpc": "2.0"}
    auth = None
    if rpc_user and rpc_password:
        from requests.auth import HTTPBasicAuth
        auth = HTTPBasicAuth(rpc_user, rpc_password)
    resp = requests.post(rpc_url, json=payload, auth=auth, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def lambda_handler(event, context):
    # Support both deposit (txid string) and withdrawal (txid may be object from BroadcastTx)
    raw = event.get("txid")
    txid = raw.get("txid", raw) if isinstance(raw, dict) else raw
    if not txid:
        return 0
    try:
        result = _rpc("gettransaction", [txid])
        return int(result.get("confirmations", 0))
    except Exception as e:
        logger.warning(f"gettransaction failed for {txid}: {e}")
        return 0
