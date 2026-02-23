# DBay Architecture

## System Components

### Frontend Layer

**Vue.js 3 SPA**

- Composition API with TypeScript
- Pinia for state management
- Vue Router for navigation
- Tailwind CSS for styling
- WebSocket client for real-time auction updates

### API Gateway Layer

**AWS API Gateway**

- REST APIs for synchronous operations
- WebSocket API for real-time bidding
- Lambda Authorizer for JWT validation
- Rate limiting and throttling

### Microservices Layer

#### Django Services (Port 800x)

| Service         | Port | Responsibilities                                 |
| --------------- | ---- | ------------------------------------------------ |
| Listing Service | 8001 | CRUD listings, categories, images, Q&A           |
| Auction Service | 8002 | Bid placement, auction state, anti-sniping       |
| Wallet Service  | 8003 | HD wallet, ledger, deposits, withdrawals, escrow |
| User Service    | 8004 | Auth, profiles, feedback/ratings                 |
| Order Service   | 8005 | Order lifecycle, shipping, disputes              |

#### Flask Services (Port 801x)

| Service              | Port | Responsibilities                        |
| -------------------- | ---- | --------------------------------------- |
| Notification Service | 8010 | Email (SES), push, in-app notifications |
| Search Gateway       | 8011 | Elasticsearch query proxy, autocomplete |
| Messaging Service    | 8012 | Buyer-seller messaging threads          |

### Serverless Layer

**Lambda Functions**

- `image-processor` - S3 trigger, creates thumbnails
- `auction-closer` - Scheduled, closes ended auctions
- `deposit-watcher` - Scheduled, polls Dogecoin node
- `search-indexer` - EventBridge trigger, indexes to ES
- `websocket-handler` - WebSocket connection management
- `blockchain-broadcaster` - Signs and broadcasts Doge transactions

**Step Functions Workflows**

- `AuctionCloseWorkflow` - End auction, create order, lock escrow
- `WithdrawalWorkflow` - Validate, sign, broadcast, confirm
- `DepositConfirmationWorkflow` - Wait for confirmations, credit
- `DisputeWorkflow` - Evidence collection, admin review, resolution

### Data Layer

| Store         | Technology                 | Purpose                          |
| ------------- | -------------------------- | -------------------------------- |
| Transactional | PostgreSQL (RDS)           | Users, listings, orders, wallet  |
| Documents     | MongoDB (DocumentDB)       | Attributes, messages, audit logs |
| Search        | Elasticsearch (OpenSearch) | Full-text search, facets         |
| Hot Cache     | Redis (ElastiCache)        | Auction state, locks, sessions   |
| Warm Cache    | Memcached                  | Categories, search results       |

## Communication Patterns

### Synchronous (HTTP)

- Frontend → API Gateway → Services
- Service → Service (internal APIs)

### Asynchronous (Events)

- Services → EventBridge → Lambda/Step Functions
- EventBridge → SQS → Notification Service

### Real-time (WebSocket)

- Frontend ↔ API Gateway WebSocket ↔ Lambda
- Redis Pub/Sub for fan-out

## Security

- JWT tokens from Cognito
- Lambda authorizer validates tokens
- RBAC at service level
- All services in private VPC
- API Gateway is only public endpoint
- Secrets in AWS Secrets Manager

### Authentication (Cognito)

- **Production:** Frontend uses AWS Amplify to sign in with Cognito; sends `Authorization: Bearer <idToken>` to the API. The Lambda authorizer (`serverless/functions/authorizer`) validates the JWT with the User Pool JWKS, optionally resolves `cognito_sub` to app `user_id` via the User service internal `/api/v1/user/internal/resolve/` endpoint, and returns context that API Gateway maps to request headers: `X-Cognito-Sub`, `X-Cognito-Username`, `X-Cognito-Email`, `X-User-ID`. User and Listing services trust these headers.
- **Local dev:** Set `VITE_USE_COGNITO=false` (default). Frontend uses `POST /user/login/` (dev-only) and sends `X-User-ID` from the auth store; no Cognito or authorizer. User service `/users/me/` accepts either `X-Cognito-Sub` or `X-User-ID`.
