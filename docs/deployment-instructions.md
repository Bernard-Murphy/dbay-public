# Production Deployment Instructions

This document describes how to deploy all DBay services to production: infrastructure, microservices, serverless (Lambda/Step Functions/EventBridge), frontend, and required environment variables.

For quick reference after initial setup, see [runbooks/deployment.md](runbooks/deployment.md).

---

## 1. Overview

Production typically runs:

- **API Gateway** (HTTP API + WebSocket) – public entry point; Lambda authorizer for JWT (Cognito).
- **Microservices** (Django/Flask) – run on EKS, ECS, or equivalent; internal URLs used by API Gateway and Lambdas.
- **Serverless** – Lambdas, Step Functions, EventBridge (deposit/withdrawal workflows, auction closer, search indexer, etc.).
- **Data layer** – RDS (PostgreSQL), DocumentDB (MongoDB), ElastiCache (Redis), OpenSearch, optional Memcached.
- **Frontend** – Static build (Vite) on S3 + CloudFront.
- **Cognito** – User pool and app client for auth.

---

## 2. Prerequisites

- AWS CLI configured with credentials for the target account/region.
- SAM CLI installed (`sam --version`) for serverless deploy.
- Docker (for building service images).
- For EKS: `kubectl` and cluster access.
- For ECS: AWS CLI and task definition tooling.

---

## 3. Infrastructure (Data Layer)

Provision before deploying services.

| Component  | AWS Service            | Notes                                                        |
| ---------- | ---------------------- | ------------------------------------------------------------ |
| PostgreSQL | RDS (or Aurora)        | One instance/cluster shared by all Django services.          |
| MongoDB    | DocumentDB             | For messaging, attributes, audit-style data.                 |
| Redis      | ElastiCache            | Auction state, locks, sessions.                              |
| Search     | OpenSearch             | Replace Elasticsearch; same API.                             |
| Memcached  | ElastiCache (optional) | Warm cache; can share Redis or omit.                         |
| Event bus  | EventBridge            | Create custom bus `dbay-events` if not created by SAM.       |
| S3         | S3                     | Bucket for listing images (e.g. `dbay-listing-images-prod`). |
| SES        | SES                    | Verified domain/address for notification emails.             |
| SQS        | SQS                    | Queue for notifications (subscription from EventBridge).     |

**Secrets:** Store production secrets in **AWS Secrets Manager** (e.g. DB passwords, `WALLET_MASTER_XPRIV`, Cognito client secret). Reference by ARN in task definitions or Lambda env.

---

## 4. Environment Variables by Service

Use these when configuring EKS/ECS task definitions or container env. Omit `AWS_ENDPOINT_URL` in production (use real AWS services).

### 4.1 Shared (all Django services)

| Variable                                      | Required                      | Description                                                      |
| --------------------------------------------- | ----------------------------- | ---------------------------------------------------------------- |
| `DATABASE_URL`                                | Yes                           | PostgreSQL URL, e.g. `postgresql://user:pass@rds-host:5432/dbay` |
| `REDIS_URL`                                   | Yes                           | Redis URL, e.g. `redis://elasticache-host:6379/0`                |
| `MEMCACHED_URL`                               | No                            | Memcached host:port, or omit                                     |
| `DJANGO_SECRET_KEY`                           | Yes                           | Random secret for Django (e.g. from Secrets Manager)             |
| `AWS_REGION`                                  | Yes                           | e.g. `us-east-1`                                                 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | If not using IAM roles        | Omit if using IRSA/task role                                     |
| `EVENT_BUS_NAME`                              | Yes                           | EventBridge bus name, e.g. `dbay-events`                         |
| `ELASTICSEARCH_URL`                           | Yes (listing, search-gateway) | OpenSearch endpoint, e.g. `https://...es.amazonaws.com`          |
| `MONGO_URI`                                   | If using Mongo                | DocumentDB connection string (services that use it)              |

Do **not** set `AWS_ENDPOINT_URL` in production (that is for LocalStack).

### 4.2 Listing Service

| Variable             | Required | Description                                                                  |
| -------------------- | -------- | ---------------------------------------------------------------------------- |
| All shared (Django)  | Yes      | Including `DATABASE_URL`, `REDIS_URL`, `ELASTICSEARCH_URL`, `EVENT_BUS_NAME` |
| `AWS_S3_BUCKET_NAME` | Yes      | S3 bucket for listing images, e.g. `dbay-listing-images-prod`                |

### 4.3 Auction Service

| Variable              | Required | Description                                                         |
| --------------------- | -------- | ------------------------------------------------------------------- |
| All shared (Django)   | Yes      |                                                                     |
| `LISTING_SERVICE_URL` | Yes      | Internal URL, e.g. `http://listing-service:8000` or EKS service DNS |
| `WALLET_SERVICE_URL`  | Yes      | Internal URL, e.g. `http://wallet-service:8000`                     |

### 4.4 Wallet Service

| Variable                | Required                      | Description                                                                       |
| ----------------------- | ----------------------------- | --------------------------------------------------------------------------------- |
| All shared (Django)     | Yes                           |                                                                                   |
| `DOGECOIN_RPC_URL`      | Yes (real Doge)               | Remote RPC, e.g. `https://go.getblock.io/<ACCESS_TOKEN>`                          |
| `DOGECOIN_RPC_USER`     | No                            | RPC Basic auth user (if required by provider)                                     |
| `DOGECOIN_RPC_PASSWORD` | No                            | RPC Basic auth password                                                           |
| `WALLET_MASTER_XPUB`    | Yes (real addresses)          | BIP44 account-level xpub; prefer Secrets Manager, inject at runtime               |
| `WALLET_MASTER_XPRIV`   | No (for sync withdrawal only) | Only if using `USE_SYNC_WITHDRAWAL=1`; otherwise Step Function Lambda holds xpriv |
| `USE_SYNC_WITHDRAWAL`   | No                            | Set to `1` only if processing withdrawals synchronously (no Step Function)        |

**Production:** Store `WALLET_MASTER_XPUB` and `WALLET_MASTER_XPRIV` in Secrets Manager; inject via task definition or startup script.

### 4.5 User Service

| Variable             | Required | Description                                       |
| -------------------- | -------- | ------------------------------------------------- |
| All shared (Django)  | Yes      |                                                   |
| `AWS_S3_BUCKET_NAME` | Yes      | Same bucket as listing service for avatars/images |

### 4.6 Order Service

| Variable              | Required | Description                     |
| --------------------- | -------- | ------------------------------- |
| All shared (Django)   | Yes      |                                 |
| `LISTING_SERVICE_URL` | Yes      | Internal URL to listing service |
| `WALLET_SERVICE_URL`  | Yes      | Internal URL to wallet service  |

### 4.7 Notification Service (Flask)

| Variable                                      | Required              | Description                                        |
| --------------------------------------------- | --------------------- | -------------------------------------------------- |
| `AWS_REGION`                                  | Yes                   |                                                    |
| `SQS_QUEUE_URL`                               | Yes                   | SQS queue URL for notification events              |
| `SES_FROM_EMAIL`                              | Yes                   | Verified SES sender, e.g. `noreply@yourdomain.com` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | If not using IAM role | Omit if using task role                            |

### 4.8 Search Gateway (Flask)

| Variable            | Required | Description         |
| ------------------- | -------- | ------------------- |
| `ELASTICSEARCH_URL` | Yes      | OpenSearch endpoint |
| `MEMCACHED_URL`     | No       | Optional cache      |

### 4.9 Messaging Service (Flask)

| Variable     | Required | Description                               |
| ------------ | -------- | ----------------------------------------- |
| `MONGO_URI`  | Yes      | DocumentDB (or MongoDB) connection string |
| `AWS_REGION` | Yes      | For any AWS SDK use                       |

---

## 5. Deploying Microservices (EKS / ECS)

### 5.1 Build and push images

Build from repo root; tag and push to ECR (replace `<account>` and `<region>`):

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

for service in listing-service auction-service wallet-service user-service order-service notification-service search-gateway messaging-service; do
  docker build -t dbay/$service -f services/$service/Dockerfile .
  docker tag dbay/$service:latest <account>.dkr.ecr.<region>.amazonaws.com/dbay/$service:latest
  docker push <account>.dkr.ecr.<region>.amazonaws.com/dbay/$service:latest
done
```

Build context may need to be `services/$service` if Dockerfiles expect it; adjust `-f` and context as in your repo.

### 5.2 Kubernetes (EKS)

- Create namespace (e.g. `dbay`).
- Create Secrets or use External Secrets for `DATABASE_URL`, `DJANGO_SECRET_KEY`, `WALLET_MASTER_XPUB`, etc.
- Deploy each service as Deployment + Service; set env from ConfigMap/Secret.
- Internal DNS: `listing-service.dbay.svc.cluster.local:8000`, etc. Use these for `*_SERVICE_URL` and for SAM parameter overrides (`WALLET_SERVICE_URL`, etc.).

### 5.3 ECS

- Create task definitions per service; set environment variables or use Secrets Manager integration.
- Create services (Fargate or EC2); ensure tasks can reach RDS, Redis, OpenSearch, and each other (e.g. via Service Connect or NLB).
- Use same internal URLs for `LISTING_SERVICE_URL`, `WALLET_SERVICE_URL`, etc., when configuring API Gateway integration or Lambda env.

---

## 6. Deploying Serverless (SAM)

Lambdas and Step Functions need to reach the microservices (in VPC if services are private) and need RPC/Secrets for Dogecoin.

### 6.1 SAM parameters (production)

Create a `samconfig.toml` or pass `--parameter-overrides`. Key parameters:

| Parameter                                 | Description                                                     | Example                           |
| ----------------------------------------- | --------------------------------------------------------------- | --------------------------------- |
| `RedisUrl`                                | ElastiCache Redis URL                                           | `redis://...:6379/0`              |
| `DogecoinRpcUrl`                          | Dogecoin RPC (e.g. GetBlock)                                    | `https://go.getblock.io/<token>`  |
| `DogecoinRpcUser` / `DogecoinRpcPassword` | Optional RPC auth                                               |                                   |
| `ElasticsearchUrl`                        | OpenSearch endpoint                                             | `https://...es.amazonaws.com`     |
| `WalletMasterXpub`                        | Account xpub (or leave empty and use Secrets Manager in Lambda) | From `scripts/generate_wallet.py` |
| `WalletMasterXprivSecretArn`              | ARN of secret containing xpriv (for BuildAndSignTx)             | `arn:aws:secretsmanager:...`      |
| `CognitoUserPoolId`                       | User pool ID for authorizer                                     | `us-east-1_xxxxx`                 |
| `UserServiceUrl`                          | User service URL for authorizer (resolve cognito_sub → user_id) | `http://user-service:8000`        |

Ensure Lambdas that call the wallet/listing/auction/order services have **VPC config** and **security groups** that allow outbound to the service endpoints (and to GetBlock if RPC is public). Set `WALLET_SERVICE_URL`, `LISTING_SERVICE_URL`, etc., to the internal URLs (e.g. `http://wallet-service.dbay.svc.cluster.local:8000` or NLB DNS).

### 6.2 Deploy commands

```bash
cd serverless
sam build
sam deploy --guided   # first time
# or
sam deploy --config-env prod --parameter-overrides ...
```

After deploy, EventBridge rules and Step Functions will use the configured event bus and Lambda ARNs.

---

## 7. Frontend

- Set **production** env at build time (e.g. in CI):
  - `VITE_API_BASE_URL` – API Gateway base URL, e.g. `https://xxxx.execute-api.us-east-1.amazonaws.com/prod/api/v1`
  - `VITE_USE_COGNITO=true`
  - `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_AWS_REGION`
- Build: `npm run build` in `frontend/`.
- Deploy `dist/` to S3 and optionally put CloudFront in front (see [runbooks/deployment.md](runbooks/deployment.md)).

---

## 8. Cognito

- Create a User Pool; configure app client (e.g. public client for SPA).
- In API Gateway/Lambda authorizer: set `COGNITO_USER_POOL_ID` and optionally `USER_SERVICE_URL` for user resolution.
- In frontend: set `VITE_COGNITO_*` and `VITE_USE_COGNITO=true` for production builds.

---

## 9. Dogecoin / Wallet (Production)

- **RPC:** Use a hosted JSON-RPC endpoint (e.g. GetBlock). Set `DOGECOIN_RPC_URL` (token-in-URL or Basic auth via `DOGECOIN_RPC_USER`/`DOGECOIN_RPC_PASSWORD`).
- **Keys:** Generate HD keys with `scripts/generate_wallet.py` (run offline). Store:
  - `WALLET_MASTER_XPUB` – in Secrets Manager or task env; wallet service needs it for deposit addresses.
  - `WALLET_MASTER_XPRIV` – in Secrets Manager only; grant **BuildAndSignTx** Lambda read access; set `WalletMasterXprivSecretArn` in SAM (or provide xpriv via Lambda env for dev).
- **Withdrawals:** In production, do **not** set `USE_SYNC_WITHDRAWAL`. Withdrawal flow goes through Step Functions (ValidateBalance → FraudCheck → DebitLedger → BuildAndSignTx → BroadcastTx → CheckConfirmations → FinalizeLedger).
- Ensure wallet service and Lambdas (deposit_watcher, check_confirmations, build_and_sign_tx, blockchain_broadcaster) can reach `DOGECOIN_RPC_URL`.

---

## 10. Post-Deploy Checklist

1. **Migrations:** Run Django migrations for each service (see [runbooks/deployment.md](runbooks/deployment.md)).
2. **EventBridge:** Confirm custom bus `dbay-events` exists and rules target the correct Step Functions/Lambdas.
3. **Wallet service → EventBridge:** Wallet service must publish `withdrawal.requested` to EventBridge (not only in-process). Ensure `EVENT_BUS_NAME` and AWS credentials (or IAM role) are set so `put_events` succeeds.
4. **Health checks:** Hit a known endpoint (e.g. `/api/v1/listings/listings/` or health if implemented) via API Gateway with a valid JWT.
5. **Deposit/withdrawal:** Test with small amounts; confirm deposit watcher and withdrawal workflow run (check Step Function executions and wallet balance).

---

## 11. Quick reference: where each variable is used

| Variable               | Used by                                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `DATABASE_URL`         | All Django services                                                                             |
| `REDIS_URL`            | Listing, auction, wallet, user, order                                                           |
| `EVENT_BUS_NAME`       | Listing, auction, wallet, order (event_bus), Lambdas                                            |
| `WALLET_MASTER_XPUB`   | Wallet service (deposit addresses), BuildAndSignTx Lambda                                       |
| `WALLET_MASTER_XPRIV`  | BuildAndSignTx Lambda (or wallet service if USE_SYNC_WITHDRAWAL=1)                              |
| `DOGECOIN_RPC_URL`     | Wallet service, deposit_watcher, check_confirmations, build_and_sign_tx, blockchain_broadcaster |
| `WALLET_SERVICE_URL`   | Auction, order, Lambdas (CreditUser, FinalizeLedger, LockEscrow, etc.)                          |
| `LISTING_SERVICE_URL`  | Auction, order, search indexer Lambda                                                           |
| `ORDER_SERVICE_URL`    | Lambdas (CreateOrder, UpdateOrderPaid, etc.)                                                    |
| `COGNITO_USER_POOL_ID` | Lambda authorizer                                                                               |
| `USER_SERVICE_URL`     | Lambda authorizer (resolve cognito_sub → user_id)                                               |

For a minimal production checklist, use the tables in **Section 4** when configuring each service and **Section 6.1** for SAM.
