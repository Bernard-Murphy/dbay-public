# Search Gateway Service

**Type:** Flask microservice
**Port:** 8011

## Overview

The Search Gateway provides a unified search interface over Elasticsearch. It handles full-text search, faceted filtering, autocomplete, and saved searches.

## API Endpoints

### Search

| Method | Endpoint                      | Description              |
| ------ | ----------------------------- | ------------------------ |
| GET    | `/api/v1/search`              | Search listings          |
| GET    | `/api/v1/search/autocomplete` | Autocomplete suggestions |

### Saved Searches

| Method | Endpoint                      | Description               |
| ------ | ----------------------------- | ------------------------- |
| GET    | `/api/v1/saved-searches`      | Get user's saved searches |
| POST   | `/api/v1/saved-searches`      | Save a search             |
| DELETE | `/api/v1/saved-searches/{id}` | Delete saved search       |

## Search Parameters

```
GET /api/v1/search?q=vintage+camera&category=123&min_price=100&max_price=500&condition=GOOD&sort=price_asc&page=1&per_page=20
```

| Parameter      | Type    | Description         |
| -------------- | ------- | ------------------- |
| `q`            | string  | Search query        |
| `category`     | int     | Category ID filter  |
| `min_price`    | decimal | Minimum price       |
| `max_price`    | decimal | Maximum price       |
| `condition`    | string  | Condition filter    |
| `listing_type` | string  | AUCTION, BUY_IT_NOW |
| `seller_id`    | uuid    | Filter by seller    |
| `sort`         | string  | Sort order          |
| `page`         | int     | Page number         |
| `per_page`     | int     | Results per page    |

### Sort Options

- `relevance` (default)
- `price_asc`
- `price_desc`
- `ending_soon`
- `newest`

## Response Format

```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Vintage Camera",
      "price": 250.0,
      "image_url": "https://...",
      "seller_rating": 98.5,
      "bid_count": 12,
      "ends_at": "2024-01-15T18:00:00Z"
    }
  ],
  "facets": {
    "categories": [
      { "id": 1, "name": "Electronics", "count": 45 },
      { "id": 2, "name": "Cameras", "count": 23 }
    ],
    "conditions": [
      { "value": "NEW", "count": 10 },
      { "value": "LIKE_NEW", "count": 15 }
    ],
    "price_ranges": [
      { "min": 0, "max": 100, "count": 5 },
      { "min": 100, "max": 500, "count": 12 }
    ]
  },
  "total": 156,
  "page": 1,
  "per_page": 20
}
```

## Elasticsearch Index

### Index: `listings`

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "title": { "type": "text", "analyzer": "english" },
      "description": { "type": "text", "analyzer": "english" },
      "category_id": { "type": "integer" },
      "category_path": { "type": "keyword" },
      "price": { "type": "float" },
      "condition": { "type": "keyword" },
      "listing_type": { "type": "keyword" },
      "seller_id": { "type": "keyword" },
      "seller_rating": { "type": "float" },
      "image_url": { "type": "keyword" },
      "bid_count": { "type": "integer" },
      "ends_at": { "type": "date" },
      "created_at": { "type": "date" },
      "status": { "type": "keyword" }
    }
  }
}
```

## Indexing

Listings are indexed via the `search-indexer` Lambda, which is triggered by EventBridge events:

- `listing.created` → Index new document
- `listing.updated` → Update document
- `listing.deleted` → Delete document

## Saved Searches

Stored in MongoDB:

```json
{
  "_id": "ObjectId",
  "user_id": "uuid",
  "name": "Vintage Cameras under 500",
  "query": {
    "q": "vintage camera",
    "max_price": 500
  },
  "created_at": "ISODate"
}
```

Used for email alerts when matching listings are posted.

## Dependencies

- Elasticsearch (OpenSearch in AWS)
- MongoDB (saved searches)
- Redis (autocomplete cache)
