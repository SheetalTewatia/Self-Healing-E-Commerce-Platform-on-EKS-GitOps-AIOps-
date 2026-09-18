# Runbook: OOMKilled (Out of Memory)

## Symptoms
- Pod exit code 137
- Container state shows OOMKilled
- Pod restarts repeatedly

## Common Causes
1. Memory limit set too low in deployment.yaml
2. Memory leak in application
3. Large data processing without pagination
4. JVM heap not configured — uses all available RAM

## Diagnostic Steps
1. Check exit code: `kubectl describe pod <pod> -n ecommerce`
2. Check memory usage graph in Grafana: container_memory_usage_bytes
3. Review application for unbounded list queries

## Resolution
- Increase memory limit in deployment.yaml resources.limits.memory
- For Java: set explicit heap `-Xmx384m -Xms256m`
- Add pagination to MongoDB queries
- Redeploy after config change via ArgoCD

## Severity: HIGH  
## Auto-action: notify team — cannot auto-fix without code change
