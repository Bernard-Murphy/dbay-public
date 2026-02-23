import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

WALLET_SERVICE_URL = os.environ.get("WALLET_SERVICE_URL", "http://wallet-service:8003")


def lambda_handler(event, context):
    withdrawal_id = event.get("withdrawal_id")
    raw_txid = event.get("txid")
    txid = raw_txid.get("txid", raw_txid) if isinstance(raw_txid, dict) else raw_txid
    if not withdrawal_id or not txid:
        raise ValueError("withdrawal_id and txid required")

    url = f"{WALLET_SERVICE_URL.rstrip('/')}/api/v1/wallet/internal/finalize-withdrawal/"
    payload = {"withdrawal_id": withdrawal_id, "txid": txid}
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return {}