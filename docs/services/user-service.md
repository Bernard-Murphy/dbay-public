# User Service

**Type:** Django REST Framework microservice
**Port:** 8004
**Database:** PostgreSQL

## Overview

The User Service manages user profiles, authentication metadata, and the feedback/rating system for sellers. Authentication itself is handled by AWS Cognito; this service stores supplementary profile data.

## API Endpoints

### Profiles

| Method | Endpoint                          | Description                |
| ------ | --------------------------------- | -------------------------- |
| GET    | `/api/v1/users/me/`               | Get current user's profile |
| PATCH  | `/api/v1/users/me/`               | Update profile             |
| GET    | `/api/v1/users/{id}/`             | Get public user profile    |
| GET    | `/api/v1/users/{id}/seller-info/` | Get seller rating summary  |

### Feedback

| Method | Endpoint                         | Description                     |
| ------ | -------------------------------- | ------------------------------- |
| POST   | `/api/v1/feedback/`              | Submit feedback for transaction |
| GET    | `/api/v1/feedback/?user_id={id}` | Get feedback for user           |
| POST   | `/api/v1/feedback/{id}/reply/`   | Reply to feedback (seller)      |

### Addresses (Shipping)

| Method | Endpoint                           | Description          |
| ------ | ---------------------------------- | -------------------- |
| GET    | `/api/v1/users/me/addresses/`      | List saved addresses |
| POST   | `/api/v1/users/me/addresses/`      | Add new address      |
| PATCH  | `/api/v1/users/me/addresses/{id}/` | Update address       |
| DELETE | `/api/v1/users/me/addresses/{id}/` | Delete address       |

## Models

### UserProfile

```python
class UserProfile(models.Model):
    id = UUIDField(primary_key=True)  # Matches Cognito sub
    username = CharField(max_length=50, unique=True)
    display_name = CharField(max_length=100)
    avatar_url = URLField(null=True)
    bio = TextField(blank=True)
    location = CharField(max_length=100, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    is_seller = BooleanField(default=False)
```

### SellerRating (Materialized)

```python
class SellerRating(models.Model):
    user_id = UUIDField(primary_key=True)
    positive_count = IntegerField(default=0)
    neutral_count = IntegerField(default=0)
    negative_count = IntegerField(default=0)
    score = DecimalField()  # Calculated percentage
    last_updated = DateTimeField()
```

### Feedback

```python
class Feedback(models.Model):
    RATINGS = ['POSITIVE', 'NEUTRAL', 'NEGATIVE']

    id = UUIDField(primary_key=True)
    order_id = UUIDField()
    from_user_id = UUIDField()
    to_user_id = UUIDField()
    rating = CharField(choices=RATINGS)
    comment = TextField()
    reply = TextField(null=True)  # Seller's response
    created_at = DateTimeField(auto_now_add=True)
```

### Address

```python
class Address(models.Model):
    id = UUIDField(primary_key=True)
    user_id = UUIDField()
    name = CharField(max_length=100)  # "Home", "Work"
    street_1 = CharField(max_length=200)
    street_2 = CharField(max_length=200, blank=True)
    city = CharField(max_length=100)
    state = CharField(max_length=100)
    postal_code = CharField(max_length=20)
    country = CharField(max_length=2)  # ISO code
    is_default = BooleanField(default=False)
```

## Feedback Flow

1. Order is completed
2. Buyer/Seller can leave feedback within 30 days
3. Feedback is linked to order (one per party per order)
4. SellerRating is recalculated on new feedback:
   ```python
   score = (positive_count / total_count) * 100
   ```

## Events Published

- `user.registered` - New user created profile
- `feedback.submitted` - New feedback submitted

## Dependencies

- PostgreSQL (profiles, feedback)
- AWS Cognito (authentication source of truth)
- EventBridge (event publishing)
