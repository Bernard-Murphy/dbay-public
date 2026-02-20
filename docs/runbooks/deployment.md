# Deployment Runbook

## Prerequisites

- AWS CLI configured with appropriate credentials
- SAM CLI installed
- kubectl configured for EKS cluster
- Docker logged into ECR

## Deploying Serverless Stack

```bash
cd serverless

# Build
sam build

# Deploy to dev
sam deploy --config-env dev

# Deploy to production
sam deploy --config-env prod --parameter-overrides Environment=prod
```

## Deploying Microservices to EKS

### Build and Push Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Build and push each service
for service in listing-service auction-service wallet-service user-service order-service notification-service search-gateway messaging-service; do
  docker build -t dbay/$service services/$service
  docker tag dbay/$service:latest <account>.dkr.ecr.us-east-1.amazonaws.com/dbay/$service:latest
  docker push <account>.dkr.ecr.us-east-1.amazonaws.com/dbay/$service:latest
done
```

### Apply Kubernetes Manifests

```bash
# Apply namespace
kubectl apply -f kubernetes/namespace.yaml

# Apply secrets (ensure they exist in Secrets Manager first)
kubectl apply -f kubernetes/secrets/

# Apply deployments
kubectl apply -f kubernetes/deployments/

# Apply services
kubectl apply -f kubernetes/services/

# Apply ingress
kubectl apply -f kubernetes/ingress.yaml
```

### Rolling Update

```bash
# Update a specific deployment
kubectl rollout restart deployment/listing-service -n dbay

# Watch rollout status
kubectl rollout status deployment/listing-service -n dbay

# Rollback if needed
kubectl rollout undo deployment/listing-service -n dbay
```

## Database Migrations

**Important:** Run migrations before deploying new code that requires schema changes.

```bash
# Connect to bastion host
ssh bastion.dbay.example

# Run migrations for each service
kubectl exec -it deployment/listing-service -n dbay -- python manage.py migrate
kubectl exec -it deployment/auction-service -n dbay -- python manage.py migrate
kubectl exec -it deployment/wallet-service -n dbay -- python manage.py migrate
kubectl exec -it deployment/user-service -n dbay -- python manage.py migrate
kubectl exec -it deployment/order-service -n dbay -- python manage.py migrate
```

## Frontend Deployment

```bash
cd frontend

# Build production bundle
npm run build

# Deploy to S3
aws s3 sync dist/ s3://dbay-frontend-prod --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"
```

## Health Checks

After deployment, verify all services are healthy:

```bash
# Check EKS pods
kubectl get pods -n dbay

# Check Lambda functions
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'dbay')]"

# Test API Gateway
curl -H "Authorization: Bearer $TOKEN" https://api.dbay.example/health
```

## Rollback Procedures

### Serverless Rollback

```bash
# List previous versions
aws lambda list-versions-by-function --function-name dbay-auction-closer

# Point alias to previous version
aws lambda update-alias --function-name dbay-auction-closer --name prod --function-version <prev>
```

### EKS Rollback

```bash
kubectl rollout undo deployment/listing-service -n dbay
```

### Database Rollback

```bash
# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier dbay-prod-restored \
  --db-snapshot-identifier dbay-prod-pre-migration
```
