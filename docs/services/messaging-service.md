# Messaging Service

**Type:** Flask microservice
**Port:** 8012

## Overview

The Messaging Service enables direct communication between buyers and sellers. It provides threaded conversations linked to listings, with support for attachments.

## API Endpoints

| Method | Endpoint                                  | Description                |
| ------ | ----------------------------------------- | -------------------------- |
| GET    | `/api/v1/messaging/threads`               | Get user's message threads |
| POST   | `/api/v1/messaging/threads`               | Create new thread          |
| GET    | `/api/v1/messaging/threads/{id}`          | Get thread details         |
| GET    | `/api/v1/messaging/threads/{id}/messages` | Get messages in thread     |
| POST   | `/api/v1/messaging/threads/{id}/messages` | Send message               |
| PATCH  | `/api/v1/messaging/threads/{id}/read`     | Mark thread as read        |

## Data Model (MongoDB)

### Thread

```json
{
  "_id": "ObjectId",
  "listing_id": "uuid",
  "participants": ["user_id_1", "user_id_2"],
  "last_message_at": "ISODate",
  "last_message_preview": "string (truncated)",
  "unread_count": {
    "user_id_1": 0,
    "user_id_2": 2
  },
  "created_at": "ISODate"
}
```

### Message

```json
{
  "_id": "ObjectId",
  "thread_id": "ObjectId",
  "sender_id": "uuid",
  "content": "string",
  "attachments": [
    {
      "url": "https://s3.../attachment.jpg",
      "type": "image",
      "name": "photo.jpg"
    }
  ],
  "created_at": "ISODate"
}
```

## API Examples

### Create Thread

```http
POST /api/v1/messaging/threads
Content-Type: application/json

{
  "listing_id": "uuid",
  "recipient_id": "uuid",
  "message": "Is this item still available?"
}
```

### Send Message

```http
POST /api/v1/messaging/threads/{thread_id}/messages
Content-Type: application/json

{
  "content": "Yes, it's available. Would you like to make an offer?"
}
```

### Get Threads

```http
GET /api/v1/messaging/threads

Response:
{
  "threads": [
    {
      "id": "thread_id",
      "listing": {
        "id": "uuid",
        "title": "Vintage Camera",
        "image_url": "https://..."
      },
      "other_participant": {
        "id": "uuid",
        "username": "seller123"
      },
      "last_message": "Yes, it's available...",
      "last_message_at": "2024-01-15T10:30:00Z",
      "unread_count": 2
    }
  ]
}
```

## Features

### Thread Creation Rules

- One thread per listing per user pair
- If thread exists, return existing instead of creating new
- Seller can always be contacted about their listings

### Notifications

On new message, publish event for notification service:

```json
{
  "source": "dbay.messaging-service",
  "detail-type": "message.received",
  "detail": {
    "thread_id": "id",
    "recipient_id": "uuid",
    "sender_username": "string",
    "preview": "string"
  }
}
```

### Moderation (Future)

- Content filtering for spam/abuse
- Report message functionality
- Admin message visibility

## Configuration

| Variable     | Description               |
| ------------ | ------------------------- |
| `MONGO_URI`  | MongoDB connection string |
| `S3_BUCKET`  | Bucket for attachments    |
| `AWS_REGION` | AWS region                |

## Dependencies

- MongoDB (messages, threads)
- S3 (attachments)
- EventBridge (new message notifications)
