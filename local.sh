#!/usr/bin/env bash
#
# Stand up DBay locally from scratch (as if you had just cloned the repo).
# Requires: Docker and Docker Compose. Optional: Node.js 18+ if you want to run
# the frontend on the host instead of using the Dockerized frontend.
#
set -e
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

echo "==> Checking Docker and Docker Compose..."
if ! command -v docker &>/dev/null; then
  echo "Error: Docker is not installed or not in PATH." >&2
  exit 1
fi
if ! docker compose version &>/dev/null; then
  echo "Error: Docker Compose (v2) is not available. Run: docker compose version" >&2
  exit 1
fi

echo "==> Starting backend, infrastructure, and frontend (docker compose up -d --build)..."
docker compose up -d --build

echo "==> Waiting for PostgreSQL to be ready..."
for i in $(seq 1 60); do
  if docker compose exec -T postgres pg_isready -U dbay_user -d dbay &>/dev/null; then
    echo "    PostgreSQL is ready."
    break
  fi
  if [[ $i -eq 60 ]]; then
    echo "Error: PostgreSQL did not become ready in time." >&2
    exit 1
  fi
  sleep 2
done

echo "==> Waiting for Elasticsearch to be ready..."
for i in $(seq 1 30); do
  if curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/_cluster/health 2>/dev/null | grep -qE '^200$'; then
    echo "    Elasticsearch is ready."
    break
  fi
  if [[ $i -eq 30 ]]; then
    echo "Error: Elasticsearch did not become ready in time." >&2
    exit 1
  fi
  sleep 2
done

echo "==> Creating Elasticsearch index dbay-listings..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/dbay-listings 2>/dev/null | grep -qE '^200$'; then
  echo "    Index dbay-listings already exists."
else
  curl -s -X PUT "http://localhost:9200/dbay-listings" -H "Content-Type: application/json" -d '{
    "mappings": {
      "properties": {
        "listing_id": { "type": "keyword" },
        "title": { "type": "text" },
        "description": { "type": "text" },
        "category_id": { "type": "keyword" },
        "listing_type": { "type": "keyword" },
        "current_price": { "type": "float" },
        "status": { "type": "keyword" },
        "created_at": { "type": "date" },
        "end_time": { "type": "date" },
        "images": { "type": "object", "enabled": false }
      }
    }
  }' >/dev/null && echo "    Index dbay-listings created." || { echo "Error: Failed to create index dbay-listings." >&2; exit 1; }
fi

echo "==> Running database migrations (makemigrations)..."
docker compose exec -T listing-service python manage.py makemigrations
docker compose exec -T auction-service python manage.py makemigrations
docker compose exec -T wallet-service python manage.py makemigrations
docker compose exec -T user-service python manage.py makemigrations
docker compose exec -T order-service python manage.py makemigrations

echo "==> Applying migrations..."
docker compose exec -T listing-service python manage.py migrate
docker compose exec -T auction-service python manage.py migrate
docker compose exec -T wallet-service python manage.py migrate
docker compose exec -T user-service python manage.py migrate
docker compose exec -T order-service python manage.py migrate

echo "==> Seeding categories and sample listings..."
docker compose exec -T listing-service python manage.py seed_data

echo "==> Backfilling search index (dbay-listings)..."
docker compose exec -T listing-service python manage.py index_listings

echo ""
echo "==> DBay is up locally."
echo ""
echo "  Frontend:        http://localhost:3000"
echo "  Listing API:     http://localhost:8001/api/v1/"
echo "  Auction API:     http://localhost:8002/api/v1/"
echo "  Wallet API:      http://localhost:8003/api/v1/"
echo "  User API:        http://localhost:8004/api/v1/"
echo "  Order API:       http://localhost:8005/api/v1/"
echo ""
echo "  To view logs:    docker compose logs -f"
echo "  To stop:         docker compose down"
echo ""
