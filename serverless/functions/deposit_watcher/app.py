import json
import os
import requests
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rpc_url = os.environ.get('DOGECOIN_RPC_URL', 'http://dogecoin-node:22555')
rpc_user = os.environ.get('DOGECOIN_RPC_USER')
rpc_password = os.environ.get('DOGECOIN_RPC_PASSWORD')
event_bus_name = os.environ.get('EVENT_BUS_NAME', 'dbay-events')
events_client = boto3.client('events')


def _rpc_post(payload):
    auth = None
    if rpc_user and rpc_password:
        auth = (rpc_user, rpc_password)
    return requests.post(rpc_url, json=payload, auth=auth, timeout=30)


def lambda_handler(event, context):
    try:
        payload = {
            "method": "listtransactions",
            "params": ["*", 10, 0],
            "id": 1,
            "jsonrpc": "2.0"
        }
        response = _rpc_post(payload)
        response.raise_for_status()
        result = response.json().get('result', [])
        
        new_txs = []
        # Filter for 'receive' category
        for tx in result:
            if tx.get('category') == 'receive':
                # Check if processed (idempotency handled by consumer/workflow)
                # But to avoid spamming events, we might want to store last processed txid in SSM or DynamoDB.
                # For simplicity, we just publish everything and let the consumer handle idempotency.
                
                detail = {
                    "txid": tx.get('txid'),
                    "address": tx.get('address'),
                    "amount": str(tx.get('amount')),
                    "confirmations": tx.get('confirmations')
                }
                
                # Publish event
                events_client.put_events(
                    Entries=[
                        {
                            'Source': 'dbay.deposit-watcher',
                            'DetailType': 'deposit.detected',
                            'Detail': json.dumps(detail),
                            'EventBusName': event_bus_name
                        }
                    ]
                )
                new_txs.append(detail)
                
        logger.info(f"Processed {len(new_txs)} transactions")
        return {
            'statusCode': 200,
            'body': json.dumps(f"Processed {len(new_txs)} transactions")
        }
        
    except Exception as e:
        logger.error(f"Error checking deposits: {e}")
        raise e
