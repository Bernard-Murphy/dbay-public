import json
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

WALLET_SERVICE_URL = os.environ.get("WALLET_SERVICE_URL", "http://wallet-service:8003")


def lambda_handler(event, context):
    address = event.get("address")
    amount = event.get("amount")
    txid = event.get("txid")
    if not address or amount is None or not txid:
        raise ValueError("address, amount, and txid required")

    url = f"{WALLET_SERVICE_URL.rstrip('/')}/api/v1/wallet/internal/credit-deposit/"
    payload = {"address": address, "amount": amount, "txid": txid}
    try:
        resp = requests.post(url, json=payload, timeout=30)
    except requests.RequestException as e:
        logger.error(f"Credit deposit request failed: {e}")
        raise

    if resp.status_code == 404:
        logger.warning(f"Unknown deposit address, skipping credit: {address}")
        return {}
    if resp.status_code >= 500:
        resp.raise_for_status()
    resp.raise_for_status()
    return {}
