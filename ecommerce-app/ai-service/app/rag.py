"""
RAG: fetches product catalog from product-service, embeds with sentence-transformers,
stores in ChromaDB, and retrieves semantically similar products on query.
"""

import chromadb
import requests
from sentence_transformers import SentenceTransformer
from . import config

_client     = chromadb.Client()
_collection = _client.get_or_create_collection("products")
_model      = SentenceTransformer(config.EMBED_MODEL)


def _fetch_products() -> list[dict]:
    try:
        r = requests.get(f"{config.PRODUCT_SERVICE_URL}/api/products", timeout=10)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def index_products():
    products = _fetch_products()
    if not products:
        return 0

    ids, docs, metas = [], [], []
    for p in products:
        pid  = str(p.get("id", p.get("_id", "")))
        text = f"{p['name']} {p.get('description', '')} {p.get('category', '')} ${p.get('price', '')}"
        ids.append(pid)
        docs.append(text)
        metas.append({
            "id":          pid,
            "name":        p.get("name", ""),
            "price":       str(p.get("price", "")),
            "category":    p.get("category", ""),
            "stock":       str(p.get("stockQuantity", 0)),
            "description": p.get("description", ""),
        })

    embeddings = _model.encode(docs).tolist()
    _collection.upsert(ids=ids, embeddings=embeddings, documents=docs, metadatas=metas)
    return len(products)


def search(query: str, top_k: int = 3) -> list[dict]:
    embedding = _model.encode([query]).tolist()
    results   = _collection.query(query_embeddings=embedding, n_results=top_k)
    products  = []
    for i, meta in enumerate(results["metadatas"][0]):
        products.append({
            "id":          meta["id"],
            "name":        meta["name"],
            "price":       meta["price"],
            "category":    meta["category"],
            "stock":       meta["stock"],
            "description": meta["description"],
            "relevance":   round(1 - results["distances"][0][i], 3),
        })
    return products
