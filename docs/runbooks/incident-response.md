# Incident Response Runbook

## Severity Levels

| Level | Description       | Response Time | Examples                        |
| ----- | ----------------- | ------------- | ------------------------------- |
| SEV1  | Complete outage   | Immediate     | Platform down, payments failing |
| SEV2  | Major degradation | 15 minutes    | Search down, slow responses     |
| SEV3  | Minor issue       | 1 hour        | Single feature broken           |
| SEV4  | Low impact        | 24 hours      | Cosmetic issues                 |

## On-Call Contacts

- Primary: Check PagerDuty
- Secondary: Check PagerDuty
- Escalation: Engineering Manager

## Incident Workflow

1. **Acknowledge** - Accept alert in PagerDuty
2. **Assess** - Determine severity and impact
3. **Communicate** - Update status page, notify stakeholders
4. **Mitigate** - Stop the bleeding
5. **Resolve** - Fix root cause
6. **Postmortem** - Document and learn

## Common Issues

### API Gateway 5xx Errors

**Symptoms:** High 5xx rate in CloudWatch

**Investigation:**

```bash
# Check Lambda errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/dbay-authorizer \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Check EKS pod status
kubectl get pods -n dbay
kubectl describe pod <failing-pod> -n dbay
kubectl logs <failing-pod> -n dbay
```

**Mitigation:**

- If Lambda: Check for timeouts, memory issues
- If EKS: Restart pods, check resource limits

---

### Database Connection Exhaustion

**Symptoms:** "too many connections" errors

**Investigation:**

```sql
-- Connect to RDS
SELECT count(*) FROM pg_stat_activity;
SELECT application_name, state, count(*)
FROM pg_stat_activity
GROUP BY application_name, state;
```

**Mitigation:**

```bash
# Restart affected service pods (releases connections)
kubectl rollout restart deployment/listing-service -n dbay

# Long-term: Increase connection pool settings or RDS instance size
```

---

### High Redis Memory

**Symptoms:** Redis memory alerts, eviction warnings

**Investigation:**

```bash
redis-cli -h <redis-host> INFO memory
redis-cli -h <redis-host> INFO keyspace
redis-cli -h <redis-host> MEMORY DOCTOR
```

**Mitigation:**

```bash
# Clear auction state cache (will rebuild)
redis-cli -h <redis-host> KEYS "auction:*" | xargs redis-cli -h <redis-host> DEL

# If WebSocket connections are orphaned
redis-cli -h <redis-host> KEYS "connections:*" | xargs redis-cli -h <redis-host> DEL
```

---

### Auction Closer Not Running

**Symptoms:** Auctions not closing at end time

**Investigation:**

```bash
# Check CloudWatch Events rule
aws events describe-rule --name dbay-auction-closer-schedule

# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=dbay-auction-closer \
  --start-time $(date -d '1 hour ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 300 \
  --statistics Sum
```

**Mitigation:**

```bash
# Manually invoke to process backlog
aws lambda invoke \
  --function-name dbay-auction-closer \
  --payload '{}' \
  response.json
```

---

### Dogecoin Node Issues

**Symptoms:** Deposits not detecting, withdrawals failing

**Investigation:**

```bash
# Check deposit-watcher logs
aws logs tail /aws/lambda/dbay-deposit-watcher --follow

# Test RPC connection
curl -X POST http://dogecoin-node:22555/ \
  -H "Content-Type: application/json" \
  -d '{"method":"getblockcount","params":[],"id":1}'
```

**Mitigation:**

- If node is down: Restart node container/instance
- If sync issue: Wait for catch-up, monitor block height
- If RPC timeout: Increase Lambda timeout

---

### Elasticsearch Cluster Red

**Symptoms:** Search returning errors, cluster health RED

**Investigation:**

```bash
curl http://elasticsearch:9200/_cluster/health?pretty
curl http://elasticsearch:9200/_cat/indices?v
curl http://elasticsearch:9200/_cat/shards?v | grep -v STARTED
```

**Mitigation:**

```bash
# If unassigned shards
curl -X POST "http://elasticsearch:9200/_cluster/reroute?retry_failed=true"

# If disk full, clear old indices
curl -X DELETE "http://elasticsearch:9200/listings-2023*"
```

## Communication Templates

### Status Page Update

```
[INVESTIGATING] We are investigating issues with [component].
[IDENTIFIED] The issue has been identified. We are working on a fix.
[MONITORING] A fix has been implemented. We are monitoring.
[RESOLVED] The incident has been resolved.
```

### Stakeholder Update

```
Subject: [SEV1] dBay Platform Incident - [Brief Description]

Impact: [What users are experiencing]
Status: [Current state]
ETA: [Expected resolution time]
Next Update: [When]
```
