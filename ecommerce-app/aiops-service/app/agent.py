"""
AIOps Agent: Claude analyses cluster alerts, retrieves runbooks via RAG,
decides on remediation actions, executes them via K8s client.
"""

import json
import requests
import anthropic
from . import config, rag
from . import k8s_client, prometheus_client

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an AIOps engineer responsible for maintaining a Kubernetes cluster running ShopEasy.

When you receive an alert:
1. Use list_pods to see current pod states
2. Use get_pod_logs or describe_pod on affected pods to understand the root cause
3. Use search_runbook to retrieve the relevant runbook for this type of issue
4. Use query_prometheus to get supporting metrics if needed
5. Take a remediation action (restart_deployment or scale_deployment) if appropriate
6. Always explain what you found and what action you took (or why you didn't act)

Be precise and conservative. Only restart/scale if you're confident it will help.
"""

TOOL_DEFINITIONS = [
    {
        "name": "list_pods",
        "description": "List all pods in the ecommerce namespace with status and restart count.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_pod_logs",
        "description": "Retrieve recent logs from a pod to diagnose the issue.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pod_name": {"type": "string"},
                "lines":    {"type": "integer", "description": "Number of log lines (default 50)"}
            },
            "required": ["pod_name"]
        }
    },
    {
        "name": "describe_pod",
        "description": "Get detailed pod description including events and container state.",
        "input_schema": {
            "type": "object",
            "properties": {"pod_name": {"type": "string"}},
            "required": ["pod_name"]
        }
    },
    {
        "name": "search_runbook",
        "description": "Search the runbook knowledge base (RAG) for the relevant incident runbook.",
        "input_schema": {
            "type": "object",
            "properties": {
                "alert_description": {
                    "type": "string",
                    "description": "Description of the alert or issue to find the relevant runbook"
                }
            },
            "required": ["alert_description"]
        }
    },
    {
        "name": "query_prometheus",
        "description": "Run a PromQL query against Prometheus to get cluster metrics.",
        "input_schema": {
            "type": "object",
            "properties": {
                "promql": {"type": "string", "description": "The PromQL expression to run"}
            },
            "required": ["promql"]
        }
    },
    {
        "name": "restart_deployment",
        "description": "Trigger a rolling restart of a Kubernetes deployment.",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string", "description": "Name of the deployment to restart"}
            },
            "required": ["deployment_name"]
        }
    },
    {
        "name": "scale_deployment",
        "description": "Scale a Kubernetes deployment to a specific number of replicas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {"type": "string"},
                "replicas":        {"type": "integer"}
            },
            "required": ["deployment_name", "replicas"]
        }
    },
]


def _execute_tool(name: str, args: dict) -> dict:
    match name:
        case "list_pods":
            return {"pods": k8s_client.list_pods()}
        case "get_pod_logs":
            return {"logs": k8s_client.get_pod_logs(args["pod_name"], args.get("lines", 50))}
        case "describe_pod":
            return k8s_client.describe_pod(args["pod_name"])
        case "search_runbook":
            return {"runbooks": rag.search(args["alert_description"])}
        case "query_prometheus":
            return prometheus_client.query(args["promql"])
        case "restart_deployment":
            return k8s_client.restart_deployment(args["deployment_name"])
        case "scale_deployment":
            return k8s_client.scale_deployment(args["deployment_name"], args["replicas"])
        case _:
            return {"error": f"Unknown tool: {name}"}


def _notify(message: str):
    try:
        requests.post(
            f"{config.NOTIFICATION_SERVICE_URL}/api/notifications",
            json={"userId": "system", "message": f"[AIOps] {message}", "type": "ALERT"},
            timeout=5,
        )
    except Exception:
        pass


def analyse(alert: dict) -> str:
    alert_text = f"Alert: {alert.get('alertname', 'Unknown')} — {alert.get('summary', '')}. Pod: {alert.get('pod', 'unknown')}"
    messages   = [{"role": "user", "content": alert_text}]

    for _ in range(10):
        response = _client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            final = next((b.text for b in response.content if hasattr(b, "text")), "Analysis complete.")
            _notify(final[:500])
            return final

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                result = _execute_tool(block.name, block.input)
                results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result),
                })
            messages.append({"role": "user", "content": results})

    return "Agent reached max iterations."
