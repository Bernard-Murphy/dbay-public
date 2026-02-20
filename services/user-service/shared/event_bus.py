import boto3
import json
import os
import logging

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self.client = boto3.client('events', 
            endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bus_name = os.environ.get('EVENT_BUS_NAME', 'dbay-events')

    def publish(self, source, detail_type, detail):
        """
        Publish an event to EventBridge
        """
        try:
            response = self.client.put_events(
                Entries=[
                    {
                        'Source': source,
                        'DetailType': detail_type,
                        'Detail': json.dumps(detail),
                        'EventBusName': self.bus_name
                    }
                ]
            )
            if response['FailedEntryCount'] > 0:
                logger.error(f"Failed to publish event: {response}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False

event_bus = EventBus()
