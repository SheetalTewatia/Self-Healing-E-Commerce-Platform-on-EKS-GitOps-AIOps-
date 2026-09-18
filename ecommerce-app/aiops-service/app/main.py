"""
AIOps Service — receives Prometheus alertmanager webhooks and runs the AIOps agent.
Also exposes a manual trigger endpoint and a health check.
Enhancement 3 & 5 wired in:
  - APScheduler runs predictive_scaler.run() every hour
  - POST /api/aiops/post-deploy-watch starts the auto-rollback watcher
"""

import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from . import rag, agent, k8s_client, prometheus_client, predictive_scaler, auto_rollback

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    count = rag.index_runbooks()
    print(f"[aiops-service] Indexed {count} runbooks into ChromaDB")

    # Predictive scaler fires every hour
    scheduler.add_job(predictive_scaler.run, "interval", hours=1, id="predictive-scaler")
    scheduler.start()
    print("[aiops-service] Predictive scaler scheduled (every 1 hour)")

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(title="ShopEasy AIOps Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AlertPayload(BaseModel):
    alerts: list[dict]


class ManualAlert(BaseModel):
    alertname: str
    summary:   str
    pod:       str = ""


class DeployWatchRequest(BaseModel):
    image_tag:     str
    watch_minutes: int = 5


@app.get("/api/aiops/health")
def health():
    return {"status": "ok", "service": "aiops-service"}


@app.post("/api/aiops/webhook")
async def prometheus_webhook(payload: AlertPayload, background: BackgroundTasks):
    """Prometheus Alertmanager sends alerts here."""
    for alert in payload.alerts:
        labels  = alert.get("labels", {})
        summary = alert.get("annotations", {}).get("summary", "")
        background.add_task(agent.analyse, {
            "alertname": labels.get("alertname", "Unknown"),
            "summary":   summary,
            "pod":       labels.get("pod", ""),
        })
    return {"received": len(payload.alerts)}


@app.post("/api/aiops/analyse")
async def manual_analyse(alert: ManualAlert, background: BackgroundTasks):
    """Manually trigger agent analysis — useful for testing."""
    background.add_task(agent.analyse, alert.model_dump())
    return {"message": "Analysis started in background"}


@app.post("/api/aiops/post-deploy-watch")
async def post_deploy_watch(req: DeployWatchRequest, background: BackgroundTasks):
    """
    Called by Jenkins after ArgoCD sync completes.
    Watches metrics for watch_minutes then asks Claude: KEEP or ROLLBACK.
    """
    background.add_task(
        asyncio.ensure_future,
        auto_rollback.watch_and_decide(req.image_tag, req.watch_minutes)
    )
    return {
        "message": f"Watching deployment {req.image_tag} for {req.watch_minutes} minutes",
        "image_tag": req.image_tag,
    }


@app.post("/api/aiops/scale-now")
def scale_now():
    """Manually trigger a predictive scaling check."""
    result = predictive_scaler.run()
    return result


@app.get("/api/aiops/pods")
def get_pods():
    return {"pods": k8s_client.list_pods()}


@app.get("/api/aiops/metrics")
def get_metrics():
    return {
        "cpu":      prometheus_client.get_pod_cpu(),
        "memory":   prometheus_client.get_pod_memory(),
        "restarts": prometheus_client.get_pod_restarts(),
    }
