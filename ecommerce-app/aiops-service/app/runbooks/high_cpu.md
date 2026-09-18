# Runbook: High CPU Usage

## Symptoms
- Pod CPU usage > 80% for more than 5 minutes
- Node CPU utilisation > 70%
- Response latency increasing

## Common Causes
1. Traffic spike — more requests than expected
2. Infinite loop or inefficient query in application code
3. GC pressure in JVM (Java services)
4. MongoDB slow queries causing thread blocking

## Diagnostic Steps
1. Check Prometheus: `rate(container_cpu_usage_seconds_total[5m])`
2. Check which endpoint is being hit most
3. Review application logs for slow query warnings
4. Check MongoDB: slow query logs

## Resolution
- Short term: Scale up replicas → `kubectl scale deployment/<svc> --replicas=2 -n ecommerce`
- If JVM: add `-Xmx512m` to JVM args in deployment env
- If specific endpoint: add rate limiting at API gateway
- If DB: add index to MongoDB collection

## Severity: MEDIUM
## Auto-action: scale deployment to 2 replicas
