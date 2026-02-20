import json
import os
import requests
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

auction_service_url = os.environ.get('AUCTION_SERVICE_URL', 'http://auction-service:8002')
step_functions_arn = os.environ.get('AUCTION_CLOSE_WORKFLOW_ARN')
sfn_client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    try:
        # Get auctions ending soon
        response = requests.get(f"{auction_service_url}/api/v1/auction/auctions/ending/")
        if response.status_code != 200:
             logger.error(f"Failed to fetch ending auctions: {response.text}")
             return
             
        auctions = response.json()
        
        for auction in auctions:
            # Start workflow
            execution_name = f"AuctionClose-{auction['listing_id']}-{auction['end_time']}"
            
            sfn_client.start_execution(
                stateMachineArn=step_functions_arn,
                name=execution_name,
                input=json.dumps({
                    'listing_id': auction['listing_id'],
                    'end_time': auction['end_time']
                })
            )
            logger.info(f"Started close workflow for {auction['listing_id']}")
            
        return {
            'statusCode': 200,
            'body': json.dumps(f"Started {len(auctions)} workflows")
        }
    except Exception as e:
        logger.error(f"Error in auction closer: {e}")
        raise e
