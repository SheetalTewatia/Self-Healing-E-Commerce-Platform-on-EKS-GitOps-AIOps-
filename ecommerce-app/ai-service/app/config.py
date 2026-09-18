import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
PRODUCT_SERVICE_URL  = os.getenv("PRODUCT_SERVICE_URL",  "http://product-service:8082")
ORDER_SERVICE_URL    = os.getenv("ORDER_SERVICE_URL",    "http://order-service:8083")
USER_SERVICE_URL     = os.getenv("USER_SERVICE_URL",     "http://user-service:8081")
EMBED_MODEL          = "all-MiniLM-L6-v2"
CLAUDE_MODEL         = "claude-haiku-4-5-20251001"
