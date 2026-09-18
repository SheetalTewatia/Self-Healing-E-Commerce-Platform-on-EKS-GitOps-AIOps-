import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY        = os.getenv("ANTHROPIC_API_KEY", "")
PROMETHEUS_URL           = os.getenv("PROMETHEUS_URL", "http://monitoring-kube-prometheus-prometheus.monitoring:9090")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8084")
K8S_NAMESPACE            = os.getenv("K8S_NAMESPACE", "ecommerce")
ARGOCD_URL               = os.getenv("ARGOCD_URL", "https://argocd-server.argocd")
ARGOCD_TOKEN             = os.getenv("ARGOCD_TOKEN", "")
CLAUDE_MODEL             = "claude-haiku-4-5-20251001"
EMBED_MODEL              = "all-MiniLM-L6-v2"
