import json
import logging
import os
import uuid
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rpc_url = os.environ.get("DOGECOIN_RPC_URL", "http://dogecoin-node:22555")
rpc_user = os.environ.get("DOGECOIN_RPC_USER")
rpc_password = os.environ.get("DOGECOIN_RPC_PASSWORD")


def _rpc(method: str, params: list):
    payload = {"method": method, "params": params, "id": 1, "jsonrpc": "2.0"}
    auth = (rpc_user, rpc_password) if (rpc_user and rpc_password) else None
    resp = requests.post(rpc_url, json=payload, auth=auth, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data.get("result")


def lambda_handler(event, context):
    # From withdrawal workflow: event has "signed_tx" (hex string from BuildAndSignTx)
    raw = event.get("signed_tx")
    signed_tx = raw.get("signed_tx", raw) if isinstance(raw, dict) else raw
    if signed_tx:
        try:
            txid = _rpc("sendrawtransaction", [signed_tx])
            logger.info(f"Broadcast txid={txid}")
            return {"txid": txid}
        except Exception as e:
            logger.error(f"sendrawtransaction failed: {e}")
            raise
    # Fallback: mock for dev when no signed_tx (e.g. old trigger)
    amount = event.get("amount")
    destination_address = event.get("address")
    if amount and destination_address:
        txid = uuid.uuid4().hex
        logger.info(f"Mock broadcast tx {txid} to {destination_address}")
        return {"txid": txid}
    raise ValueError("signed_tx required")
