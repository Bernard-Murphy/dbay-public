import boto3
import json
import os
import time
import logging
from .services import notification_service

logger = logging.getLogger(__name__)

def poll_queue():
    sqs = boto3.client('sqs', 
        endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )
    queue_url = os.environ.get('SQS_QUEUE_URL')
    
    logger.info(f"Polling SQS: {queue_url}")
    
    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )
            
            messages = response.get('Messages', [])
            for msg in messages:
                body = json.loads(msg['Body'])
                # EventBridge wraps the event in 'Message' if using SNS topic? 
                # If direct to SQS from EventBridge rule, structure is different.
                # Assuming EventBridge -> SQS directly.
                
                detail = body.get('detail', {})
                detail_type = body.get('detail-type')
                
                logger.info(f"Received event: {detail_type}")
                
                # Handle events
                if detail_type == 'order.paid':
                    notification_service.send_email(
                        'seller@example.com', # Need to fetch user email? Yes.
                        'Order Paid',
                        f"Order {detail.get('order_id')} has been paid."
                    )
                elif detail_type == 'auction.closed':
                    notification_service.send_email(
                        'winner@example.com', 
                        'You won!',
                        f"You won auction {detail.get('listing_id')}"
                    )
                
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=msg['ReceiptHandle']
                )
                
        except Exception as e:
            logger.error(f"Error polling SQS: {e}")
            time.sleep(5)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    poll_queue()
