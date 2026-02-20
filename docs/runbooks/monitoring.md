# Monitoring Runbook

## CloudWatch Dashboards

Access at: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=dbay-main

### Key Metrics

| Metric                  | Warning       | Critical      | Description       |
| ----------------------- | ------------- | ------------- | ----------------- |
| API Gateway 5xx rate    | > 1%          | > 5%          | Server errors     |
| API Gateway latency p99 | > 1s          | > 3s          | Response time     |
| Lambda errors           | > 5/min       | > 20/min      | Function failures |
| Lambda duration p99     | > 80% timeout | > 90% timeout | Near timeouts     |
| RDS CPU                 | > 70%         | > 90%         | Database load     |
| RDS connections         | > 80% max     | > 95% max     | Connection pool   |
| Redis memory            | > 70%         | > 90%         | Cache pressure    |
| ES cluster health       | Yellow        | Red           | Index status      |

## Log Queries

### CloudWatch Logs Insights

**Lambda Errors**

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100
```

**Slow Requests**

```
fields @timestamp, @duration, @message
| filter @duration > 5000
| sort @duration desc
| limit 50
```

**Bid Activity**

```
fields @timestamp, @message
| filter @message like /bid.placed/
| stats count() by bin(5m)
```

### Service Logs (EKS)

```bash
# Tail logs for a service
kubectl logs -f deployment/listing-service -n dbay

# Get logs from crashed pod
kubectl logs <pod-name> -n dbay --previous

# Search logs with stern
stern listing-service -n dbay --since 1h | grep ERROR
```

## Alerts

### PagerDuty Integration

Alerts flow: CloudWatch Alarm → SNS → PagerDuty

### Alert Runbooks

**HighErrorRate**

- Check Lambda logs for errors
- Check EKS pod status
- Check downstream dependencies

**HighLatency**

- Check RDS performance insights
- Check Redis memory/connections
- Check ES cluster health

**LambdaThrottling**

- Check concurrent execution limits
- Increase reserved concurrency if needed

**DatabaseConnectionsHigh**

- Identify services with connection leaks
- Restart affected pods
- Consider increasing pool/RDS size

## X-Ray Tracing

Enable tracing in Lambda functions and API Gateway to trace requests across services.

```bash
# View traces
aws xray get-trace-summaries \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --filter-expression 'service("dbay-listing-service") AND responsetime > 1'
```

## Health Endpoints

Each service exposes health endpoints:

| Service      | Endpoint     |
| ------------ | ------------ |
| Listing      | GET /health/ |
| Auction      | GET /health/ |
| Wallet       | GET /health/ |
| User         | GET /health/ |
| Order        | GET /health/ |
| Notification | GET /health  |
| Search       | GET /health  |
| Messaging    | GET /health  |

Health check script:

```bash
#!/bin/bash
services=("listing:8001" "auction:8002" "wallet:8003" "user:8004" "order:8005")
for svc in "${services[@]}"; do
  name="${svc%%:*}"
  port="${svc##*:}"
  status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port/health/")
  echo "$name: $status"
done
```

## Cost Monitoring

Track costs by:

- AWS Cost Explorer with tags
- Tag all resources with `Project: dbay`, `Environment: prod|dev`

Key cost drivers:

- RDS instance hours
- Lambda invocations
- Data transfer
- ElastiCache nodes
- OpenSearch instances
