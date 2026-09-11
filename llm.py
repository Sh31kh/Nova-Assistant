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
            "description": (
                "Open an application on the user's computer. "
                "The application argument may be the application's normal name "
                "or a user-configured alias such as 'VAL'. "
                "Pass the application name or alias exactly as the user said it. "
                "Do not refuse because you do not know the application's Windows "
                "executable name or path; Nova resolves configured names and aliases."
            ),
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
            "description": (
                "Close an application on the user's computer. "
                "The application argument may be the application's normal name "
                "or a user-configured alias such as 'VAL'. "
                "Pass the application name or alias exactly as the user said it. "
                "Nova resolves configured names and aliases."
            ),
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
    "You control tools on the user's computer. "
    "Choose the tool that best matches the user's requested action. "
    "For application actions, pass the application name exactly as "
    "the user said it, including aliases or abbreviations. "
    "Nova will resolve configured aliases and application paths. "
    "Do not refuse an application request because you do not know "
    "the Windows executable name or path. "
    "If no available tool can perform the requested action, call "
    "unsupported_request with a brief explanation. "
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