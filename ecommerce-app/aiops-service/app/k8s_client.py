"""
Kubernetes client tools — used by the AIOps agent to inspect and act on the cluster.
Runs inside the cluster using the pod's ServiceAccount token.
"""

from kubernetes import client, config as k8s_config
from . import config


def _load():
    try:
        k8s_config.load_incluster_config()   # running inside K8s pod
    except Exception:
        k8s_config.load_kube_config()        # local dev fallback


_load()
_core  = client.CoreV1Api()
_apps  = client.AppsV1Api()
NS     = config.K8S_NAMESPACE


def list_pods() -> list[dict]:
    pods = _core.list_namespaced_pod(namespace=NS)
    return [
        {
            "name":     p.metadata.name,
            "status":   p.status.phase,
            "restarts": sum(cs.restart_count for cs in (p.status.container_statuses or [])),
            "ready":    all(cs.ready for cs in (p.status.container_statuses or [])),
        }
        for p in pods.items
    ]


def get_pod_logs(pod_name: str, lines: int = 50) -> str:
    try:
        return _core.read_namespaced_pod_log(
            name=pod_name, namespace=NS, tail_lines=lines, previous=False
        )
    except Exception as e:
        try:
            return _core.read_namespaced_pod_log(
                name=pod_name, namespace=NS, tail_lines=lines, previous=True
            )
        except Exception:
            return f"Could not retrieve logs: {e}"


def describe_pod(pod_name: str) -> dict:
    try:
        pod    = _core.read_namespaced_pod(name=pod_name, namespace=NS)
        events = _core.list_namespaced_event(namespace=NS, field_selector=f"involvedObject.name={pod_name}")
        return {
            "phase":  pod.status.phase,
            "conditions": [{"type": c.type, "status": c.status} for c in (pod.status.conditions or [])],
            "containerStatuses": [
                {
                    "name":     cs.name,
                    "ready":    cs.ready,
                    "restarts": cs.restart_count,
                    "state":    str(cs.state),
                }
                for cs in (pod.status.container_statuses or [])
            ],
            "events": [{"reason": e.reason, "message": e.message} for e in events.items[-5:]],
        }
    except Exception as e:
        return {"error": str(e)}


def restart_deployment(deployment_name: str) -> dict:
    try:
        import datetime
        patch = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow().isoformat()
                        }
                    }
                }
            }
        }
        _apps.patch_namespaced_deployment(name=deployment_name, namespace=NS, body=patch)
        return {"success": True, "message": f"Deployment {deployment_name} restarted"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def scale_deployment(deployment_name: str, replicas: int) -> dict:
    try:
        _apps.patch_namespaced_deployment_scale(
            name=deployment_name, namespace=NS, body={"spec": {"replicas": replicas}}
        )
        return {"success": True, "message": f"Scaled {deployment_name} to {replicas} replicas"}
    except Exception as e:
        return {"success": False, "error": str(e)}
