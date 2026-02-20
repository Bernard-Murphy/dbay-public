# Local Development Setup

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development outside Docker)
- Python 3.12+ (for running tests outside Docker)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/dbay.git
cd dbay

# Start all services
docker-compose up -d --build

# Watch logs
docker-compose logs -f
```

## Service URLs

| Service              | URL                           | Description       |
| -------------------- | ----------------------------- | ----------------- |
| Frontend             | http://localhost:3000         | Vue.js SPA        |
| Listing Service      | http://localhost:8001/api/v1/ | Django REST       |
| Auction Service      | http://localhost:8002/api/v1/ | Django REST       |
| Wallet Service       | http://localhost:8003/api/v1/ | Django REST       |
| User Service         | http://localhost:8004/api/v1/ | Django REST       |
| Order Service        | http://localhost:8005/api/v1/ | Django REST       |
| Notification Service | http://localhost:8010/        | Flask             |
| Search Gateway       | http://localhost:8011/api/v1/ | Flask             |
| Messaging Service    | http://localhost:8012/api/v1/ | Flask             |
| LocalStack           | http://localhost:4566         | AWS services mock |
| Dogecoin RPC Mock    | http://localhost:18332        | Mock blockchain   |

## Infrastructure Services

| Service       | Port  | Purpose                |
| ------------- | ----- | ---------------------- |
| PostgreSQL    | 5432  | Primary database       |
| MongoDB       | 27017 | Documents, messages    |
| Elasticsearch | 9200  | Search index           |
| Redis         | 6379  | Cache, locks, sessions |
| Memcached     | 11211 | Warm cache             |

## Database Access

```bash
# PostgreSQL
docker exec -it dbay-postgres psql -U dbay -d dbay

# MongoDB
docker exec -it dbay-mongo mongosh

# Redis
docker exec -it dbay-redis redis-cli
```

## Running Migrations

```bash
# All Django services
docker-compose exec listing-service python manage.py migrate
docker-compose exec auction-service python manage.py migrate
docker-compose exec wallet-service python manage.py migrate
docker-compose exec user-service python manage.py migrate
docker-compose exec order-service python manage.py migrate
```

## Running Tests

```bash
# Django service tests
docker-compose exec listing-service pytest

# Flask service tests
docker-compose exec search-gateway pytest

# Frontend tests
cd frontend && npm test
```

## Hot Reloading

All services are configured with volume mounts for hot reloading:

- Django services reload on Python file changes
- Flask services reload on Python file changes
- Vue.js frontend has Vite HMR enabled

## Environment Variables

Key environment variables are set in `docker-compose.yaml`:

```yaml
DJANGO_DEBUG: "True"
DATABASE_URL: postgres://dbay:dbay@postgres:5432/dbay
REDIS_URL: redis://redis:6379/0
MONGO_URI: mongodb://mongo:27017/dbay
ELASTICSEARCH_URL: http://elasticsearch:9200
AWS_ENDPOINT_URL: http://localstack:4566
```

## Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>
```

### Database connection issues

```bash
# Verify PostgreSQL is ready
docker-compose exec postgres pg_isready

# Check service can reach database
docker-compose exec listing-service python -c "import django; django.setup(); from django.db import connection; cursor = connection.cursor()"
```

### Clear all data

```bash
# Stop and remove containers + volumes
docker-compose down -v

# Start fresh
docker-compose up -d --build
```

### Port conflicts

If a port is already in use, edit `docker-compose.yaml` to change the host port mapping.
