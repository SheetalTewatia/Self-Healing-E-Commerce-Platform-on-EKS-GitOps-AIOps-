"""
RAG: indexes runbook markdown files into ChromaDB.
On an alert, retrieves the most relevant runbook for context.
"""

import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer
from . import config

_client     = chromadb.Client()
_collection = _client.get_or_create_collection("runbooks")
_model      = SentenceTransformer(config.EMBED_MODEL)

RUNBOOKS_DIR = os.path.join(os.path.dirname(__file__), "runbooks")


def index_runbooks():
    files = glob.glob(os.path.join(RUNBOOKS_DIR, "*.md"))
    ids, docs, metas = [], [], []
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r") as f:
            content = f.read()
        ids.append(name)
        docs.append(content)
        metas.append({"filename": name})

    if ids:
        embeddings = _model.encode(docs).tolist()
        _collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    return len(ids)


def search(alert_text: str, top_k: int = 2) -> list[dict]:
    embedding = _model.encode([alert_text]).tolist()
    results   = _collection.query(query_embeddings=embedding, n_results=top_k)
    runbooks  = []
    for i, doc in enumerate(results["documents"][0]):
        runbooks.append({
            "runbook":   results["metadatas"][0][i]["filename"],
            "content":   doc,
            "relevance": round(1 - results["distances"][0][i], 3),
        })
    return runbooks
