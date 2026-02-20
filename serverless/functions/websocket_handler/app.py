import json
import os
import boto3
import redis
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

redis_url = os.environ.get('REDIS_URL', 'redis://redis-cluster:6379/0')
redis_client = redis.from_url(redis_url, decode_responses=True)

def lambda_handler(event, context):
    try:
        connection_id = event['requestContext']['connectionId']
        route_key = event['requestContext']['routeKey']
        
        if route_key == '$connect':
            # Optionally verify auth in header/query string
            redis_client.set(f"connection:{connection_id}", "connected", ex=3600)
            return {'statusCode': 200, 'body': 'Connected'}
            
        elif route_key == '$disconnect':
            redis_client.delete(f"connection:{connection_id}")
            # Also remove from all subscriptions?
            # We need a reverse mapping or scan?
            # Scan is expensive.
            # Ideally store subscriptions in a Set `con_subs:{connection_id}`.
            subs = redis_client.smembers(f"con_subs:{connection_id}")
            for channel in subs:
                redis_client.srem(f"channel:{channel}", connection_id)
            redis_client.delete(f"con_subs:{connection_id}")
            return {'statusCode': 200, 'body': 'Disconnected'}
            
        elif route_key == 'subscribe':
            body = json.loads(event.get('body', '{}'))
            listing_id = body.get('listing_id')
            if listing_id:
                redis_client.sadd(f"channel:{listing_id}", connection_id)
                redis_client.sadd(f"con_subs:{connection_id}", listing_id)
                return {'statusCode': 200, 'body': f"Subscribed to {listing_id}"}
                
        elif route_key == 'unsubscribe':
            body = json.loads(event.get('body', '{}'))
            listing_id = body.get('listing_id')
            if listing_id:
                redis_client.srem(f"channel:{listing_id}", connection_id)
                redis_client.srem(f"con_subs:{connection_id}", listing_id)
                return {'statusCode': 200, 'body': f"Unsubscribed from {listing_id}"}
        
        return {'statusCode': 400, 'body': 'Unknown route'}
        
    except Exception as e:
        logger.error(f"Error handling websocket: {e}")
        return {'statusCode': 500, 'body': 'Internal Server Error'}
