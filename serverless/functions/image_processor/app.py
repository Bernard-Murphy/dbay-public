import boto3
import os
import sys
import uuid
import logging
import json
from PIL import Image
from io import BytesIO
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

SIZES = {
    'thumbnail': (150, 150),
    'medium': (400, 400),
    'large': (1200, 1200)
}

def lambda_handler(event, context):
    """
    S3 Object Created Handler
    """
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            logger.info(f"Processing image: {bucket}/{key}")
            
            # Skip if already processed
            if '_thumb' in key or '_medium' in key or '_large' in key:
                logger.info("Skipping already processed image")
                continue
                
            response = s3_client.get_object(Bucket=bucket, Key=key)
            image_content = response['Body'].read()
            
            original_image = Image.open(BytesIO(image_content))
            
            urls = {}
            
            for size_name, size in SIZES.items():
                image = original_image.copy()
                image.thumbnail(size)
                
                buffer = BytesIO()
                image.save(buffer, 'JPEG')
                buffer.seek(0)
                
                new_key = key.rsplit('.', 1)[0] + f'_{size_name}.jpg'
                
                s3_client.put_object(
                    Bucket=bucket,
                    Key=new_key,
                    Body=buffer,
                    ContentType='image/jpeg'
                )
                
                # Construct URL (assuming public or presigned access later)
                urls[f'url_{size_name}'] = f"https://{bucket}.s3.amazonaws.com/{new_key}"
                
            # Update Listing Service via API (or publish event)
            # For simplicity, we'll just log success here. 
            # In production, we'd call an internal API endpoint or update DB if in VPC.
            listing_id = key.split('/')[0]
            logger.info(f"Successfully processed image for listing {listing_id}. URLs: {urls}")
            
            # Make API call to Listing Service to update URLs
            listing_service_url = os.environ.get('LISTING_SERVICE_URL')
            if listing_service_url:
                # Update ListingImage record
                # requests.patch(f"{listing_service_url}/api/v1/listings/{listing_id}/images/{image_id}", json=urls)
                pass

        return {
            'statusCode': 200,
            'body': json.dumps('Image processing complete')
        }
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise e
