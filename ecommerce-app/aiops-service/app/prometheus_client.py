"""
Prometheus HTTP API client for querying cluster metrics.
"""

import requests
from . import config


def query(promql: str) -> dict:
    try:
        r = requests.get(
            f"{config.PROMETHEUS_URL}/api/v1/query",
            params={"query": promql},
            timeout=10,
        )
        data = r.json()
        if data.get("status") == "success":
            return {"result": data["data"]["result"]}
        return {"error": data.get("error", "Unknown Prometheus error")}
    except Exception as e:
        return {"error": str(e)}


def get_pod_restarts(namespace: str = "ecommerce") -> dict:
    promql = f'kube_pod_container_status_restarts_total{{namespace="{namespace}"}}'
    return query(promql)


def get_pod_cpu(namespace: str = "ecommerce") -> dict:
    promql = f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",container!=""}}[5m])'
    return query(promql)


def get_pod_memory(namespace: str = "ecommerce") -> dict:
    promql = f'container_memory_usage_bytes{{namespace="{namespace}",container!=""}}'
    return query(promql)


def get_node_cpu() -> dict:
    return query("100 - (avg by(instance)(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)")
