"""
Enhancement 3 — AI Auto-Rollback
After ArgoCD deploys a new image tag, this module watches Prometheus metrics
for a configurable window. If Claude detects degradation, it calls the
ArgoCD API to rollback to the previous revision.
"""

import asyncio
import json
import requests
import anthropic
from . import config, prometheus_client

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# In-memory store: {image_tag: previous_argocd_revision_id}
_deployment_history: dict[str, int] = {}


def record_deployment(image_tag: str, prev_revision_id: int):
    """Call this before a new deployment so we know what to roll back to."""
    _deployment_history[image_tag] = prev_revision_id


def _get_argocd_headers() -> dict:
    return {"Authorization": f"Bearer {config.ARGOCD_TOKEN}",
            "Content-Type": "application/json"}


def _get_argocd_history() -> list[dict]:
    try:
        r = requests.get(
            f"{config.ARGOCD_URL}/api/v1/applications/ecommerce-app",
            headers=_get_argocd_headers(),
            verify=False, timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("status", {}).get("history", [])
    except Exception as e:
        print(f"[auto-rollback] ArgoCD API error: {e}")
    return []


def _trigger_rollback(revision_id: int) -> dict:
    try:
        r = requests.post(
            f"{config.ARGOCD_URL}/api/v1/applications/ecommerce-app/rollback",
            headers=_get_argocd_headers(),
            json={"id": revision_id, "dryRun": False},
            verify=False, timeout=15,
        )
        return {"success": r.status_code == 200, "status": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _snapshot_metrics() -> dict:
    return {
        "error_rate": prometheus_client.query(
            'sum(rate(http_server_requests_seconds_count'
            '{namespace="ecommerce",status=~"5.."}[2m])) or vector(0)'
            ' / sum(rate(http_server_requests_seconds_count{namespace="ecommerce"}[2m])) or vector(1)'
        ),
        "p95_latency_s": prometheus_client.query(
            'histogram_quantile(0.95, sum(rate('
            'http_server_requests_seconds_bucket{namespace="ecommerce"}[2m])) by (le))'
        ),
        "pod_restarts": prometheus_client.query(
            'sum(increase(kube_pod_container_status_restarts_total{namespace="ecommerce"}[5m]))'
        ),
    }


def _claude_decision(image_tag: str, baseline: dict, samples: list[dict]) -> dict:
    prompt = f"""You are an AIOps deployment health analyser.

A new deployment with image tag "{image_tag}" went live.
You have collected metrics every 60 seconds for {len(samples)} minute(s).

Baseline (before deployment):
{json.dumps(baseline, indent=2)[:600]}

Post-deployment samples (chronological):
{json.dumps(samples, indent=2)[:1500]}

Rules for ROLLBACK decision:
- Error rate increased by more than 5x vs baseline → ROLLBACK
- P95 latency increased by more than 3x vs baseline → ROLLBACK
- Pod restarts > 3 in 5 minutes → ROLLBACK
- Otherwise → KEEP

Respond ONLY with valid JSON, no other text:
{{
  "decision": "KEEP" or "ROLLBACK",
  "confidence_pct": <0-100>,
  "reason": "<one sentence>",
  "key_metric": "<which metric drove the decision>"
}}"""

    response = _client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    try:
        start = text.find("{")
        end   = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {"decision": "KEEP", "confidence_pct": 40,
                "reason": "Could not parse Claude response — defaulting to KEEP",
                "key_metric": "none"}


async def watch_and_decide(image_tag: str, watch_minutes: int = 5) -> dict:
    """
    Main entry point. Called after ArgoCD sync completes.
    Polls metrics every 60s for `watch_minutes`, then asks Claude.
    Returns the decision dict.
    """
    print(f"[auto-rollback] Watching deployment {image_tag} for {watch_minutes} min...")

    # Wait 60s for traffic to shift to new pods before baselining
    await asyncio.sleep(60)
    baseline = _snapshot_metrics()

    samples = []
    for i in range(watch_minutes):
        await asyncio.sleep(60)
        snap = _snapshot_metrics()
        samples.append(snap)
        print(f"[auto-rollback] Sample {i+1}/{watch_minutes} collected")

    decision = _claude_decision(image_tag, baseline, samples)
    print(f"[auto-rollback] Decision: {decision['decision']} "
          f"(confidence {decision['confidence_pct']}%) — {decision['reason']}")

    if decision["decision"] == "ROLLBACK":
        history = _get_argocd_history()
        if len(history) >= 2:
            prev_id = history[-2].get("id")
            result  = _trigger_rollback(prev_id)
            decision["rollback_result"] = result
            print(f"[auto-rollback] Rollback triggered: {result}")
        else:
            decision["rollback_result"] = {"error": "No previous revision found in ArgoCD"}

    return decision
