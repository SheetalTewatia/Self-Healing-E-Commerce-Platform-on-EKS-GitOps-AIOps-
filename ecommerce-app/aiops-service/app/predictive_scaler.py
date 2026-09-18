"""
Enhancement 5 — Predictive Scaling Agent
Runs on a schedule (every hour). Queries Prometheus for CPU/memory trends,
asks Claude to analyse whether pre-emptive scaling is needed,
and executes kubectl scale if Claude recommends it.
"""

import json
import anthropic
from . import config, k8s_client, prometheus_client

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# Services that should never be auto-scaled by this agent
_EXCLUDED = {"mongodb-0", "aiops-service", "ai-service"}

TOOL_DEFINITIONS = [
    {
        "name": "scale_deployment",
        "description": (
            "Scale a Kubernetes deployment to a specific number of replicas. "
            "Use this when CPU trend predicts >70% utilisation, or scale down "
            "when a service has been idle (<5% CPU) for the entire observation window."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "deployment_name": {
                    "type": "string",
                    "description": "Exact deployment name (e.g. user-service)"
                },
                "replicas": {
                    "type": "integer",
                    "description": "Target replica count (1-3)"
                },
                "reason": {
                    "type": "string",
                    "description": "One sentence explaining why this scaling action is needed"
                }
            },
            "required": ["deployment_name", "replicas", "reason"]
        }
    },
    {
        "name": "no_action_needed",
        "description": "Call this when all services are healthy and no scaling is needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Brief summary of current cluster state"
                }
            },
            "required": ["summary"]
        }
    }
]


def _collect_metrics() -> dict:
    pods      = k8s_client.list_pods()
    cpu_now   = prometheus_client.get_pod_cpu()
    mem_now   = prometheus_client.get_pod_memory()
    cpu_trend = prometheus_client.query(
        'rate(container_cpu_usage_seconds_total'
        '{namespace="ecommerce",container!="",container!="POD"}[30m])'
    )
    return {
        "pods":            pods,
        "cpu_current":     cpu_now,
        "memory_current":  mem_now,
        "cpu_30m_trend":   cpu_trend,
        "excluded_from_scaling": list(_EXCLUDED),
        "max_replicas_allowed":  3,
    }


def run() -> dict:
    """
    Called by the APScheduler job every hour.
    Returns a summary of actions taken (or not taken).
    """
    if not config.ANTHROPIC_API_KEY:
        return {"error": "ANTHROPIC_API_KEY not set"}

    metrics = _collect_metrics()
    actions = []
    analysis = ""

    messages = [{
        "role": "user",
        "content": f"""You are an AIOps predictive scaling agent for a Kubernetes cluster.

Current cluster metrics and trends:
{json.dumps(metrics, indent=2)[:4000]}

Your job:
1. Analyse CPU trends over the last 30 minutes
2. If any service is trending toward >70% CPU → pre-emptively scale UP to 2 replicas
3. If any service has been idle (<5% CPU for the full window) → scale DOWN to 1 replica
4. Never scale: {', '.join(_EXCLUDED)}
5. Maximum allowed replicas: 3

Call scale_deployment for each service that needs scaling.
Call no_action_needed if everything is healthy.
Always provide a reason for your decision."""
    }]

    for _ in range(5):   # max 5 tool rounds
        response = _client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Capture final text
        for block in response.content:
            if hasattr(block, "text"):
                analysis = block.text

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                if block.name == "scale_deployment":
                    deployment = block.input["deployment_name"]
                    replicas   = block.input["replicas"]
                    reason     = block.input["reason"]

                    # Guard: never scale excluded services
                    if any(ex in deployment for ex in _EXCLUDED):
                        result = {"skipped": True, "reason": "Service is excluded from auto-scaling"}
                    else:
                        result = k8s_client.scale_deployment(deployment, replicas)
                        actions.append({
                            "service":  deployment,
                            "replicas": replicas,
                            "reason":   reason,
                            "result":   result,
                        })
                        print(f"[predictive-scaler] Scaled {deployment} to {replicas}: {reason}")

                elif block.name == "no_action_needed":
                    result = {"acknowledged": True, "summary": block.input.get("summary", "")}
                    analysis = block.input.get("summary", "")
                    print(f"[predictive-scaler] No action: {analysis}")

                else:
                    result = {"error": f"Unknown tool: {block.name}"}

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result),
                })

            messages.append({"role": "user", "content": tool_results})

    return {"actions_taken": actions, "analysis": analysis}
