# dBay - Dogecoin-Powered Marketplace Platform

## Overview

dBay is a full-featured online auction and marketplace platform where all transactions use Dogecoin cryptocurrency. The platform uses a custodial HD wallet with per-user deposit addresses. Internal payments (bids, purchases, fees) are ledger transfers in the database - only deposits and withdrawals touch the Dogecoin blockchain.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
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

| Layer            | Technology                                           |
| ---------------- | ---------------------------------------------------- |
| Frontend         | Vue 3, TypeScript, Pinia, Tailwind CSS               |
| API Gateway      | AWS API Gateway (REST + WebSocket)                   |
| Backend (Django) | Listing, Auction, Wallet, User, Order Services       |
| Backend (Flask)  | Notification, Search Gateway, Messaging Services     |
| Serverless       | AWS Lambda, Step Functions, EventBridge              |
| Databases        | PostgreSQL, MongoDB, Elasticsearch, Redis, Memcached |
| Infrastructure   | Docker, Kubernetes (EKS), AWS SAM, CloudFormation    |

## Project Structure

```
dbay/
├── frontend/               # Vue 3 SPA
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

## Quick Start

```bash
# Start all services locally
docker-compose up -d --build

# Access frontend
open http://localhost:3000

# Service endpoints
# Listing:      http://localhost:8001/api/v1/listings/
# Auction:      http://localhost:8002/api/v1/auctions/
# Wallet:       http://localhost:8003/api/v1/wallet/
# User:         http://localhost:8004/api/v1/user/
# Order:        http://localhost:8005/api/v1/order/
# Notification: http://localhost:8010/
# Search:       http://localhost:8011/api/v1/search
# Messaging:    http://localhost:8012/api/v1/messaging/
```

## Documentation

- [Architecture](./architecture.md)
- [Wallet Architecture](./wallet-architecture.md)
- [Event Catalog](./event-catalog.md)
- [API Contracts](./api-contracts/)
- [Runbooks](./runbooks/)

## License

Proprietary
