# llm.py
"""Ollama tool-calling wrapper — the exact config you already validated."""

import requests

MODEL = "qwen2.5:14b"
OLLAMA_URL = "http://localhost:11434/api/chat"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Open a named application on the user's computer",
            "parameters": {
                "type": "object",
                "properties": {"application": {"type": "string"}},
                "required": ["application"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Close a named application on the user's computer",
            "parameters": {
                "type": "object",
                "properties": {"application": {"type": "string"}},
                "required": ["application"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_search",
            "description": "Search the given query on Google in the default browser",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unsupported_request",
            "description": "Use when the user's request cannot be performed by any available tool",
            "parameters": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
]

SYSTEM_PROMPT = (
    "You control tools on the user's computer. Only call a tool if it "
    "exactly matches what the user asked for. If no available tool can "
    "perform the requested action, call the unsupported_request tool "
    "with a brief explanation of why the request is unsupported. "
    "Never substitute one tool for a different action. "
    "If the user's request contains multiple separate actions, only "
    "handle the first one and ignore the rest."
)


def get_tool_call(transcript: str) -> dict | None:
    """Returns the first tool call {"name": ..., "arguments": ...} or None
    if the model didn't produce a usable tool call. Content is intentionally
    discarded — proven untrustworthy in testing, never surface it."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
                "tools": TOOLS,
                "stream": False,
            },
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[llm] request failed: {e}")
        return None

    message = resp.json().get("message", {})
    calls = message.get("tool_calls")
    if not calls:
        return None  # treated as failure by core.py — not silence

    first = calls[0]["function"]
    return {"name": first["name"], "arguments": first.get("arguments", {})}