import boto3
import os
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.ses = boto3.client('ses', 
            endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.sender_email = os.environ.get('SES_FROM_EMAIL', 'noreply@dbay.io')

    def send_email(self, to_email, subject, body):
        try:
            self.ses.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            logger.info(f"Email sent to {to_email}")
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")

    def send_notification(self, user_id, message, type):
        # Store in DB for in-app or send push
        # For now just log
        logger.info(f"Notification to {user_id} [{type}]: {message}")

notification_service = NotificationService()
