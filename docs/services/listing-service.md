# Listing Service

**Type:** Django REST Framework microservice
**Port:** 8001
**Database:** PostgreSQL

## Overview

The Listing Service manages product listings, categories, images, and buyer questions. It is the core catalog service for the marketplace.

## API Endpoints

### Listings

| Method | Endpoint                                  | Description                           |
| ------ | ----------------------------------------- | ------------------------------------- |
| GET    | `/api/v1/listings/`                       | List all active listings              |
| POST   | `/api/v1/listings/`                       | Create a new listing                  |
| GET    | `/api/v1/listings/{id}/`                  | Get listing details                   |
| PATCH  | `/api/v1/listings/{id}/`                  | Update listing                        |
| DELETE | `/api/v1/listings/{id}/`                  | Delete listing                        |
| POST   | `/api/v1/listings/{id}/presigned-upload/` | Get S3 presigned URL for image upload |
| POST   | `/api/v1/listings/{id}/watch/`            | Add listing to watchlist              |
| DELETE | `/api/v1/listings/{id}/unwatch/`          | Remove from watchlist                 |

### Categories

| Method | Endpoint                   | Description                |
| ------ | -------------------------- | -------------------------- |
| GET    | `/api/v1/categories/`      | List all categories (tree) |
| POST   | `/api/v1/categories/`      | Create category            |
| GET    | `/api/v1/categories/{id}/` | Get category details       |
| PATCH  | `/api/v1/categories/{id}/` | Update category            |
| DELETE | `/api/v1/categories/{id}/` | Delete category            |

### Questions

| Method | Endpoint                           | Description                     |
| ------ | ---------------------------------- | ------------------------------- |
| GET    | `/api/v1/listings/{id}/questions/` | Get questions for listing       |
| POST   | `/api/v1/listings/{id}/questions/` | Ask a question                  |
| PATCH  | `/api/v1/questions/{id}/`          | Answer a question (seller only) |

### Watchlist

| Method | Endpoint             | Description          |
| ------ | -------------------- | -------------------- |
| GET    | `/api/v1/watchlist/` | Get user's watchlist |

## Models

### Listing

```python
class Listing(models.Model):
    id = UUIDField(primary_key=True)
    seller_id = UUIDField()
    title = CharField(max_length=200)
    description = TextField()
    category = ForeignKey(Category)

    condition = CharField(choices=CONDITIONS)  # NEW, LIKE_NEW, GOOD, FAIR, POOR
    listing_type = CharField(choices=TYPES)    # AUCTION, BUY_IT_NOW, BOTH

    starting_price = DecimalField()
    reserve_price = DecimalField(null=True)
    buy_it_now_price = DecimalField(null=True)

    auction_end_time = DateTimeField(null=True)
    status = CharField(choices=STATUSES)  # DRAFT, ACTIVE, SOLD, ENDED, CANCELLED
```

### Category

```python
class Category(models.Model):
    name = CharField(max_length=100)
    path = LTreeField()  # Hierarchical path (ltree extension)
```

### ListingImage

```python
class ListingImage(models.Model):
    listing = ForeignKey(Listing)
    s3_key = CharField(max_length=500)
    position = PositiveIntegerField()
```

## Events Published

- `listing.created` - When a new listing is created
- `listing.updated` - When listing details change
- `listing.deleted` - When a listing is deleted

## Dependencies

- PostgreSQL (primary data store)
- S3 (image storage)
- EventBridge (event publishing)
- Redis (caching)
