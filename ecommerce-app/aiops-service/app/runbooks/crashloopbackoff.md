# Runbook: CrashLoopBackOff

## Symptoms
- Pod status shows CrashLoopBackOff
- Pod restarts > 5 times
- Kubernetes back-off delay increasing between restarts

## Common Causes
1. Application failing to start (bad config, missing env var)
2. MongoDB connection refused (DB not ready yet)
3. Out of memory — container killed by OOMKiller
4. Wrong Docker image or entrypoint

## Diagnostic Steps
1. Get pod logs: `kubectl logs <pod> -n ecommerce --previous`
2. Describe pod: `kubectl describe pod <pod> -n ecommerce`
3. Check events for OOMKilled or ImagePullBackOff

## Resolution
- If MongoDB connection error: wait 30s and restart → `kubectl rollout restart deployment/<svc> -n ecommerce`
- If missing env var: check K8s Secret and ConfigMap
- If OOMKilled: increase memory limit in deployment.yaml
- If image pull error: check ECR credentials and image tag in deployment.yaml

## Severity: HIGH
## Auto-action: restart deployment after checking logs
