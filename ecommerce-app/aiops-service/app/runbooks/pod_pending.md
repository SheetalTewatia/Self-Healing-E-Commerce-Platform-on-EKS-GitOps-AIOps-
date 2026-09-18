# Runbook: Pod Stuck in Pending

## Symptoms
- Pod status is Pending for > 2 minutes
- Not being scheduled to any node

## Common Causes
1. Insufficient CPU/memory on all nodes — node is full
2. PersistentVolumeClaim not bound (StorageClass issue)
3. Node selector or affinity rules not satisfied
4. Image pull taking very long (large image)

## Diagnostic Steps
1. `kubectl describe pod <pod> -n ecommerce` → look at Events section
2. Check node resources: `kubectl describe nodes`
3. Check PVC: `kubectl get pvc -n ecommerce`
4. Check StorageClass: `kubectl get storageclass`

## Resolution
- If insufficient resources: delete low-priority pods or scale down other deployments
- If PVC pending: check StorageClass is gp2 and EBS CSI driver is running
- If EBS CSI issue: check IMDS hop limit is set to 2 on EC2 nodes

## Severity: HIGH
## Auto-action: describe pod and notify team with findings
