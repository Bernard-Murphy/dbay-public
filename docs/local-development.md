# Local Development Setup

This guide walks you through setting up DBay for local development: backend services (Docker), databases, migrations, seed data, and the React frontend.

## Prerequisites

- **Docker & Docker Compose** – for running PostgreSQL, Redis, MongoDB, Elasticsearch, and all microservices
- **Node.js 18+** – for the React frontend (run locally or in Docker)
- **Python 3.12+** – optional, for running Django management commands or tests on the host

## 1. Clone and enter the repo

```bash
git clone https://github.com/bernard-murphy/dbay.git
cd dbay
```

## 2. Start backend and infrastructure

From the repo root:

```bash
docker compose up -d --build
```

This starts:

- **Databases:** PostgreSQL (port 5439), MongoDB (27019), Redis (6379), Memcached (11211), Elasticsearch (9200)
- **Infrastructure:** LocalStack (4566), mock Dogecoin RPC (18332)
- **Microservices:** listing (8001), auction (8002), wallet (8003), user (8004), order (8005), notification (8010), search-gateway (8011), messaging (8012)
- **Frontend (in Docker):** optional; see step 5 for running the frontend on the host instead

Wait until containers are healthy. Check logs if needed:

```bash
docker compose logs -f
```

## 3. Run database migrations

Generate migrations first from the service directory (e.g. `listing-service`) with `python manage.py makemigrations`:

```bash
docker compose exec listing-service python manage.py makemigrations
docker compose exec auction-service python manage.py makemigrations
docker compose exec wallet-service python manage.py makemigrations
docker compose exec user-service python manage.py makemigrations
docker compose exec order-service python manage.py makemigrations
```

Run migrations for each Django service so tables exist:

```bash
docker compose exec listing-service python manage.py migrate
docker compose exec auction-service python manage.py migrate
docker compose exec wallet-service python manage.py migrate
docker compose exec user-service python manage.py migrate
docker compose exec order-service python manage.py migrate
```

## 4. Seed categories and sample listings

Populate categories, category items, and sample listings so the home page and search have data:

```bash
docker compose exec listing-service python manage.py seed_data
```

Alternatively, from repo root (with Python and Django deps available):

```bash
python scripts/seed_data.py
```

## 5. Set up and run the frontend

The frontend is a React 18 app (Vite, TypeScript, Tailwind, shadcn/ui). You can run it on the host or use the Dockerized dev server.

### Option A: Run frontend on the host (recommended for development)

```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:3000**. Vite will proxy API requests to the correct backend ports (see `frontend/vite.config.ts`).

### Option B: Run frontend in Docker

If the `frontend` service is defined in `docker compose.yaml`:

```bash
docker compose up -d frontend
```

Then open **http://localhost:3000**. Ensure `VITE_API_BASE_URL` or the proxy config in the frontend matches how the browser will reach the backends (e.g. via host ports when using Docker).

## 6. Verify the setup

- **Frontend:** http://localhost:3000 – home page with search and category grid; login/register (auth dialog).
- **Listing API:** http://localhost:8001/api/v1/listings/listings/
- **Categories with items:** http://localhost:8001/api/v1/categories/with-items/

---

## Service URLs reference

| Service           | URL                           | Description       |
| ----------------- | ----------------------------- | ----------------- |
| Frontend          | http://localhost:3000         | React SPA (Vite)  |
| Listing Service   | http://localhost:8001/api/v1/ | Django REST       |
| Auction Service   | http://localhost:8002/api/v1/ | Django REST       |
| Wallet Service    | http://localhost:8003/api/v1/ | Django REST       |
| User Service      | http://localhost:8004/api/v1/ | Django REST       |
| Order Service     | http://localhost:8005/api/v1/ | Django REST       |
| Notification      | http://localhost:8010/        | Flask             |
| Search Gateway    | http://localhost:8011/api/v1/ | Flask             |
| Messaging         | http://localhost:8012/api/v1/ | Flask             |
| LocalStack        | http://localhost:4566         | AWS services mock |
| Dogecoin RPC mock | http://localhost:18332        | Mock blockchain   |

## Infrastructure (ports on host)

| Service       | Port  | Purpose                |
| ------------- | ----- | ---------------------- |
| PostgreSQL    | 5439  | Primary database       |
| MongoDB       | 27019 | Documents, messages    |
| Elasticsearch | 9200  | Search index           |
| Redis         | 6379  | Cache, locks, sessions |
| Memcached     | 11211 | Warm cache             |

## Database access

Use the **service names** from `docker compose` (not container IDs):

```bash
# PostgreSQL (user: dbay_user, db: dbay)
docker compose exec postgres psql -U dbay_user -d dbay

# MongoDB
docker compose exec mongodb mongosh

# Redis
docker compose exec redis redis-cli
```

## Running tests

```bash
# Django service tests
docker compose exec listing-service pytest

# Flask service tests
docker compose exec search-gateway pytest

# Frontend (when test script exists)
cd frontend && npm test
```

## Hot reloading

- **Django/Flask:** Volume mounts allow code changes to be picked up (restart or use your dev server’s reload).
- **React frontend:** Vite HMR is enabled when running `npm run dev` on the host.

## Environment variables

Key variables are set in `docker compose.yaml` for each service, for example:

- `DATABASE_URL` – PostgreSQL URL for Django services
- `REDIS_URL`, `MONGO_URI`, `ELASTICSEARCH_URL`, `AWS_ENDPOINT_URL` for caches and external services
- Frontend: `VITE_API_BASE_URL` (optional; Vite proxy is used when running locally)

## Troubleshooting

### Service won’t start

```bash
docker compose logs <service-name>
docker compose restart <service-name>
```

### Database connection errors

```bash
# Check PostgreSQL is ready
docker compose exec postgres pg_isready -U dbay_user -d dbay

# Test from a Django service
docker compose exec listing-service python -c "
import django; django.setup()
from django.db import connection; connection.ensure_connection(); print('OK')
"
```

### Frontend can’t reach the API

- Ensure backends are up: `docker compose ps`
- When running the frontend on the host, use `npm run dev` so Vite’s proxy is active (see `frontend/vite.config.ts`).
- If you use the Dockerized frontend, ensure it can reach the other services by host name/port as configured in the proxy.

### Clear all data and start over

```bash
docker compose down -v
docker compose up -d --build
# Then run migrations and seed again (steps 3 and 4)
```

### "No migrations to apply" but seed fails with "relation does not exist"

This usually means either (1) the scripts were run from a directory other than the repo root so `docker compose` used the wrong project, or (2) the service images are stale and don’t include the migration files. Fix it by:

1. **Using the scripts from repo root** (or run the script by path; it will `cd` to the repo root for you):
   ```bash
   cd /path/to/dbay
   ./migrate.sh
   ```
2. **Rebuilding images and re-running migrations** so containers have the latest code and migrations:
   ```bash
   docker compose build listing-service auction-service wallet-service user-service order-service
   docker compose up -d
   ./migrate.sh
   docker compose exec listing-service python manage.py seed_data
   ```
   If the database is in a bad state, reset it and start over (see "Clear all data and start over" above).

### Port already in use

Change the host port in `docker compose.yaml` for the service that fails (e.g. `"3001:3000"` for the frontend if 3000 is taken).
