# dBay - Dogecoin-Powered Marketplace Platform

## Overview

dBay is a full-featured online auction and marketplace platform where all transactions use Dogecoin cryptocurrency. The platform uses a custodial HD wallet with per-user deposit addresses. Internal payments (bids, purchases, fees) are ledger transfers in the database - only deposits and withdrawals touch the Dogecoin blockchain.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React 18)                     │
│                   CloudFront + S3 / localhost:3000           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (REST + WS)                   │
│                    Lambda Authorizer (JWT)                   │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Django Services │ │ Flask Services  │ │    Serverless   │
│  (EKS/Docker)   │ │  (EKS/Docker)   │ │    (Lambda)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  PostgreSQL │ MongoDB │ Elasticsearch │ Redis │ Memcached   │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer            | Technology                                             |
| ---------------- | ------------------------------------------------------ |
| Frontend         | React 18, TypeScript, Zustand, Tailwind CSS, shadcn/ui |
| API Gateway      | AWS API Gateway (REST + WebSocket)                     |
| Backend (Django) | Listing, Auction, Wallet, User, Order Services         |
| Backend (Flask)  | Notification, Search Gateway, Messaging Services       |
| Serverless       | AWS Lambda, Step Functions, EventBridge                |
| Databases        | PostgreSQL, MongoDB, Elasticsearch, Redis, Memcached   |
| Infrastructure   | Docker, Kubernetes (EKS), AWS SAM, CloudFormation      |

## Project Structure

```
dbay/
├── frontend/               # React 18 SPA (Vite, shadcn/ui)
├── services/               # Microservices
│   ├── listing-service/    # Django - Listings CRUD
│   ├── auction-service/    # Django - Bidding engine
│   ├── wallet-service/     # Django - Dogecoin wallet
│   ├── user-service/       # Django - Auth & profiles
│   ├── order-service/      # Django - Order lifecycle
│   ├── notification-service/ # Flask - Emails/push
│   ├── search-gateway/     # Flask - ES proxy
│   └── messaging-service/  # Flask - Buyer-seller chat
├── serverless/             # SAM template + Lambdas
├── infrastructure/         # CloudFormation
├── kubernetes/             # K8s manifests
├── scripts/                # Utilities
└── docs/                   # Documentation
```

## Setting Up Locally

Full step-by-step instructions are in **[Local Development Setup](./local-development.md)**. Summary:

1. **Prerequisites:** Docker & Docker Compose, Node.js 18+
2. **Start backend and data stores:** `docker-compose up -d --build`
3. **Run migrations** for all Django services (listing, auction, wallet, user, order).
4. **Seed categories and sample listings:** `docker-compose exec listing-service python manage.py seed_data`
5. **Frontend:** `cd frontend && npm install && npm run dev` then open http://localhost:3000

The React frontend (Vite) proxies API requests to the correct backend ports; no API gateway is required for local development.

## Quick Start (after setup)

```bash
# Start all services
docker-compose up -d --build

# Start frontend (from repo root)
cd frontend && npm run dev

# Open app
open http://localhost:3000
```

## Service Endpoints (local)

| Service           | URL                           |
| ----------------- | ----------------------------- |
| Frontend          | http://localhost:3000         |
| Listing           | http://localhost:8001/api/v1/ |
| Auction           | http://localhost:8002/api/v1/ |
| Wallet            | http://localhost:8003/api/v1/ |
| User              | http://localhost:8004/api/v1/ |
| Order             | http://localhost:8005/api/v1/ |
| Notification      | http://localhost:8010/        |
| Search            | http://localhost:8011/api/v1/ |
| Messaging         | http://localhost:8012/api/v1/ |
| LocalStack        | http://localhost:4566         |
| Dogecoin RPC mock | http://localhost:18332        |

## Documentation

- [Local Development Setup](./local-development.md) – run the app locally (Docker, migrations, seed, frontend)
- [Architecture](./architecture.md)
- [Wallet Architecture](./wallet-architecture.md)
- [Event Catalog](./event-catalog.md)
- [API Contracts](./api-contracts/)
- [Runbooks](./runbooks/)

## License

Proprietary
