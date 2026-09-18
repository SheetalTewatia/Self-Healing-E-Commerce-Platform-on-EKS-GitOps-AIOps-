from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from . import rag, agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    count = rag.index_products()
    print(f"[ai-service] Indexed {count} products into ChromaDB")
    yield


app = FastAPI(title="ShopEasy AI Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    userId:  str | None = None


class SearchRequest(BaseModel):
    query: str
    topK:  int = 4


@app.get("/api/ai/health")
def health():
    return {"status": "ok", "service": "ai-service"}


@app.post("/api/ai/chat")
def chat(req: ChatRequest):
    reply = agent.run(req.message, req.userId)
    return {"reply": reply}


@app.post("/api/ai/search")
def semantic_search(req: SearchRequest):
    results = rag.search(req.query, req.topK)
    return {"products": results}


@app.post("/api/ai/reindex")
def reindex():
    count = rag.index_products()
    return {"indexed": count}
