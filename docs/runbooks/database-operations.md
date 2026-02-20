# Database Operations Runbook

## PostgreSQL (RDS)

### Connection

```bash
# Via bastion
psql -h dbay-prod.xxxxx.us-east-1.rds.amazonaws.com -U dbay -d dbay

# Via kubectl (from pod)
kubectl exec -it deployment/listing-service -n dbay -- python manage.py dbshell
```

### Backup & Restore

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier dbay-prod \
  --db-snapshot-identifier dbay-manual-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier dbay-prod

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier dbay-prod-restored \
  --db-snapshot-identifier dbay-prod-20240115
```

### Common Queries

```sql
-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Active connections by application
SELECT application_name, state, count(*)
FROM pg_stat_activity
GROUP BY application_name, state;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state != 'idle'
AND now() - pg_stat_activity.query_start > interval '5 minutes';

-- Kill query
SELECT pg_terminate_backend(<pid>);

-- Wallet balance reconciliation
SELECT
  user_id,
  available + locked + pending as balance_total,
  (SELECT COALESCE(SUM(credit) - SUM(debit), 0) FROM wallet_ledgerentry WHERE wallet_ledgerentry.user_id = wallet_walletbalance.user_id) as ledger_total
FROM wallet_walletbalance
WHERE available + locked + pending !=
  (SELECT COALESCE(SUM(credit) - SUM(debit), 0) FROM wallet_ledgerentry WHERE wallet_ledgerentry.user_id = wallet_walletbalance.user_id);
```

---

## MongoDB (DocumentDB)

### Connection

```bash
# Via mongosh
mongosh "mongodb://dbay-docdb.xxxxx.us-east-1.docdb.amazonaws.com:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false" --username dbay --password
```

### Common Operations

```javascript
// Switch to database
use dbay

// Collection sizes
db.getCollectionNames().forEach(function(c) {
  var stats = db[c].stats();
  print(c + ": " + stats.count + " docs, " + (stats.size / 1024 / 1024).toFixed(2) + " MB");
});

// Recent messages
db.messages.find().sort({created_at: -1}).limit(10);

// Saved searches count per user
db.saved_searches.aggregate([
  { $group: { _id: "$user_id", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
]);
```

---

## Elasticsearch (OpenSearch)

### Health Check

```bash
# Cluster health
curl http://elasticsearch:9200/_cluster/health?pretty

# Index status
curl http://elasticsearch:9200/_cat/indices?v

# Shard allocation
curl http://elasticsearch:9200/_cat/shards?v
```

### Reindexing

```bash
# Create new index with updated mappings
curl -X PUT "http://elasticsearch:9200/listings-v2" -H 'Content-Type: application/json' -d @mapping.json

# Reindex from old to new
curl -X POST "http://elasticsearch:9200/_reindex" -H 'Content-Type: application/json' -d '{
  "source": { "index": "listings" },
  "dest": { "index": "listings-v2" }
}'

# Update alias
curl -X POST "http://elasticsearch:9200/_aliases" -H 'Content-Type: application/json' -d '{
  "actions": [
    { "remove": { "index": "listings", "alias": "listings-alias" } },
    { "add": { "index": "listings-v2", "alias": "listings-alias" } }
  ]
}'
```

---

## Redis (ElastiCache)

### Connection

```bash
redis-cli -h dbay-redis.xxxxx.cache.amazonaws.com -p 6379
```

### Common Operations

```bash
# Memory usage
INFO memory

# Key statistics
INFO keyspace

# Find large keys
redis-cli --bigkeys

# Monitor commands (careful in prod)
MONITOR

# Clear auction caches
KEYS "auction:*" | xargs DEL

# Clear all (DANGEROUS)
FLUSHALL
```

---

## Data Migration

### Django Migrations

```bash
# Create migration
python manage.py makemigrations

# Show migration SQL
python manage.py sqlmigrate <app> <migration_number>

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate <app> <previous_migration>
```

### Data Export/Import

```bash
# PostgreSQL dump
pg_dump -h host -U user -d dbay > backup.sql

# PostgreSQL restore
psql -h host -U user -d dbay < backup.sql

# MongoDB dump
mongodump --uri="mongodb://..." --out=./backup

# MongoDB restore
mongorestore --uri="mongodb://..." ./backup
```
