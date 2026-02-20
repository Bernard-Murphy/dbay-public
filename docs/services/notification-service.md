# Notification Service

**Type:** Flask microservice
**Port:** 8010

## Overview

The Notification Service handles all outbound communications: email via AWS SES, in-app notifications, and push notifications. It consumes events from an SQS queue that is subscribed to the EventBridge bus.

## API Endpoints

| Method | Endpoint                     | Description                |
| ------ | ---------------------------- | -------------------------- |
| POST   | `/api/v1/notifications/send` | Manually send notification |

## Event Consumers

The service runs a background SQS consumer that processes events:

### Supported Events

| Event                  | Action                                         |
| ---------------------- | ---------------------------------------------- |
| `order.paid`           | Email buyer (confirmation) + seller (new sale) |
| `order.shipped`        | Email buyer with tracking                      |
| `bid.outbid`           | Email previous high bidder                     |
| `auction.closed`       | Email winner + seller                          |
| `withdrawal.confirmed` | Email user                                     |
| `deposit.confirmed`    | Email user                                     |
| `feedback.submitted`   | Email recipient                                |

## Notification Channels

### Email (SES)

```python
def send_email(to: str, subject: str, template: str, context: dict):
    ses_client.send_templated_email(
        Source='noreply@dbay.example',
        Destination={'ToAddresses': [to]},
        Template=template,
        TemplateData=json.dumps(context)
    )
```

### In-App (MongoDB)

```python
def create_in_app(user_id: str, notification_type: str, data: dict):
    db.notifications.insert_one({
        'user_id': user_id,
        'type': notification_type,
        'data': data,
        'read': False,
        'created_at': datetime.utcnow()
    })
```

### Push (SNS/FCM - Future)

Placeholder for mobile push notifications.

## Email Templates

Templates are stored in SES and include:

- `order-confirmation` - Buyer purchase confirmation
- `new-sale` - Seller sale notification
- `item-shipped` - Shipping notification with tracking
- `outbid` - Outbid alert
- `auction-won` - Winner notification
- `auction-ended-seller` - Seller notification (with/without sale)
- `deposit-confirmed` - Deposit credited
- `withdrawal-confirmed` - Withdrawal broadcast

## Configuration

| Variable        | Description               |
| --------------- | ------------------------- |
| `AWS_REGION`    | AWS region for SES        |
| `SQS_QUEUE_URL` | Events queue URL          |
| `FROM_EMAIL`    | Sender email address      |
| `MONGO_URI`     | MongoDB connection string |

## Dependencies

- AWS SES (email sending)
- AWS SQS (event consumption)
- MongoDB (in-app notifications store)
