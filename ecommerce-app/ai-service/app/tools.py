"""
Tool implementations: each function calls existing microservices via HTTP.
These become the "hands" of the Claude agent.
"""

import requests
from . import config, rag


def search_products(query: str) -> dict:
    results = rag.search(query, top_k=4)
    if not results:
        return {"message": "No products found matching your query.", "products": []}
    return {"products": results}


def list_products(category: str = None) -> dict:
    url = f"{config.PRODUCT_SERVICE_URL}/api/products"
    if category:
        url += f"?category={category}"
    try:
        r = requests.get(url, timeout=10)
        return {"products": r.json()} if r.status_code == 200 else {"error": "Failed to fetch products"}
    except Exception as e:
        return {"error": str(e)}


def get_product(product_id: str) -> dict:
    try:
        r = requests.get(f"{config.PRODUCT_SERVICE_URL}/api/products/{product_id}", timeout=10)
        return r.json() if r.status_code == 200 else {"error": "Product not found"}
    except Exception as e:
        return {"error": str(e)}


def place_order(user_id: str, product_id: str, quantity: int = 1) -> dict:
    payload = {"userId": user_id, "productId": product_id, "quantity": quantity}
    try:
        r = requests.post(f"{config.ORDER_SERVICE_URL}/api/orders", json=payload, timeout=10)
        if r.status_code in (200, 201):
            data = r.json()
            return {"success": True, "orderId": data.get("id"), "message": f"Order placed! Order ID: {data.get('id')}"}
        return {"success": False, "error": r.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_orders(user_id: str) -> dict:
    try:
        r = requests.get(f"{config.ORDER_SERVICE_URL}/api/orders/user/{user_id}", timeout=10)
        return {"orders": r.json()} if r.status_code == 200 else {"error": "Failed to fetch orders"}
    except Exception as e:
        return {"error": str(e)}


def get_recommendations(user_id: str) -> dict:
    orders = get_orders(user_id).get("orders", [])
    if not orders:
        return search_products("popular electronics fashion")

    # Build context from past orders to find similar products via RAG
    bought = " ".join(o.get("productName", "") for o in orders[:5])
    results = rag.search(f"similar to {bought}", top_k=4)
    return {"products": results, "basedOn": "your order history"}


# Tool definitions in Anthropic API format
TOOL_DEFINITIONS = [
    {
        "name": "search_products",
        "description": (
            "Search the product catalog using natural language. "
            "Use this when the user asks for product recommendations, "
            "wants to find something specific, or describes what they need."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query, e.g. 'wireless headphones under $400' or 'shoes for running'"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "list_products",
        "description": "List all products, optionally filtered by category (Electronics, Fashion, Books).",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter: Electronics, Fashion, or Books"
                }
            }
        }
    },
    {
        "name": "get_product",
        "description": "Get full details of a specific product by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "The product ID"}
            },
            "required": ["product_id"]
        }
    },
    {
        "name": "place_order",
        "description": "Place an order for a product on behalf of the logged-in user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id":    {"type": "string", "description": "The user's ID"},
                "product_id": {"type": "string", "description": "The product ID to order"},
                "quantity":   {"type": "integer", "description": "Quantity to order (default 1)"}
            },
            "required": ["user_id", "product_id"]
        }
    },
    {
        "name": "get_orders",
        "description": "Retrieve the order history for a user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The user's ID"}
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "get_recommendations",
        "description": "Get personalized product recommendations based on the user's purchase history using RAG.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "The user's ID"}
            },
            "required": ["user_id"]
        }
    },
]

TOOL_MAP = {
    "search_products":    lambda args, _uid: search_products(**args),
    "list_products":      lambda args, _uid: list_products(**args),
    "get_product":        lambda args, _uid: get_product(**args),
    "place_order":        lambda args, uid:  place_order(user_id=uid, **args),
    "get_orders":         lambda args, _uid: get_orders(**args),
    "get_recommendations":lambda args, _uid: get_recommendations(**args),
}
