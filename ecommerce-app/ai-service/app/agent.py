"""
Shopping Agent: Claude with tool use.
Runs the agentic loop — calls tools until it has a final answer.
"""

import json
import anthropic
from . import config
from .tools import TOOL_DEFINITIONS, TOOL_MAP

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are ShopBot, the AI shopping assistant for ShopEasy.
You help users find products, get recommendations, check orders, and place orders.

Guidelines:
- Use search_products for any natural language product queries
- Use get_recommendations when users want personalised suggestions
- Use place_order only when the user explicitly says they want to buy/order something
- Always show product name, price, and a one-line reason when recommending
- Keep responses concise and friendly
- If a user is not logged in (no user_id), skip order-related tools and ask them to sign in
"""


def run(message: str, user_id: str | None = None) -> str:
    messages = [{"role": "user", "content": message}]

    for _ in range(8):  # max 8 tool-call rounds
        response = _client.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Final text response — return it
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "I'm not sure how to help with that."

        # Tool use — execute each tool and feed results back
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue
                fn   = TOOL_MAP.get(block.name)
                result = fn(block.input, user_id) if fn else {"error": f"Unknown tool: {block.name}"}
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     json.dumps(result),
                })

            messages.append({"role": "user", "content": tool_results})

    return "I reached my thinking limit. Please try a simpler request."
