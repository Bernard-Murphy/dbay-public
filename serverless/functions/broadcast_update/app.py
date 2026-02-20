import json
import os
import boto3
import redis
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

redis_url = os.environ.get('REDIS_URL', 'redis://redis-cluster:6379/0')
redis_client = redis.from_url(redis_url, decode_responses=True)

# API Gateway endpoint
apigw_url = os.environ.get('APIGW_URL', 'https://api-gateway-url/@connections')
apigw_client = boto3.client('apigatewaymanagementapi', endpoint_url=apigw_url)

def lambda_handler(event, context):
    try:
        detail = event.get('detail', {})
        listing_id = detail.get('listing_id')
        
        if not listing_id:
            logger.warning("No listing_id in event")
            return
            
        # Get subscribers
        channel_key = f"channel:{listing_id}"
        connections = redis_client.smembers(channel_key)
        
        message = json.dumps(detail)
        
        for conn_id in connections:
            try:
                apigw_client.post_to_connection(
                    ConnectionId=conn_id,
                    Data=message
                )
            except apigw_client.exceptions.GoneException:
                # Connection is dead, clean up
                redis_client.srem(channel_key, conn_id)
            except Exception as e:
                logger.error(f"Error sending to {conn_id}: {e}")
                
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        raise e
