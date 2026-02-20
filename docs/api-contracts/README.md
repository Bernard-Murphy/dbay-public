# API Contracts

This directory contains API contract documentation for inter-service communication.

## Service API Documentation

- [Listing Service](../services/listing-service.md)
- [Auction Service](../services/auction-service.md)
- [Wallet Service](../services/wallet-service.md)
- [User Service](../services/user-service.md)
- [Order Service](../services/order-service.md)
- [Notification Service](../services/notification-service.md)
- [Search Gateway](../services/search-gateway.md)
- [Messaging Service](../services/messaging-service.md)

## Common Response Formats

### Success Response

```json
{
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [{ "field": "amount", "message": "Must be positive" }]
  }
}
```

## HTTP Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Created               |
| 204  | No Content            |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 409  | Conflict              |
| 422  | Unprocessable Entity  |
| 429  | Too Many Requests     |
| 500  | Internal Server Error |

## Authentication

All API requests require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

Internal service-to-service calls use a shared secret or service mesh authentication.

## Rate Limiting

| Endpoint Category  | Limit   |
| ------------------ | ------- |
| Public read        | 100/min |
| Authenticated read | 300/min |
| Write operations   | 60/min  |
| Bidding            | 30/min  |
| Withdrawals        | 10/hour |

Rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```
