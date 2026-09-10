"""tools.py — Phase 0 tool implementations.

Each function returns a structured dict: {"success": bool, "message": str}.
core.py should use "message" for whatever it reports back to the user
(console print now, TTS later) — never invent a success message yourself
in core.py. These functions are the only place that knows what actually
happened.

KNOWN LIMITATION (Phase 0 only): application names are resolved via a
small hardcoded lookup below. This violates the "no hardcoded paths"
principle from the original spec deliberately, as a temporary shortcut —
Phase 1 replaces this with a config-driven app registry (detected/
user-configured executable paths). Log this as a known debt, not
something to quietly forget.
"""

import subprocess
import webbrowser
import urllib.parse
import os

# Phase 0 only — replace with config-driven registry in Phase 1.
# For open_application — full launchable path (.exe or .lnk)
OPEN_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "discord": r"C:\Users\easas\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Discord.lnk",
    "spotify": r"C:\Users\easas\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Spotify.lnk",
}

# For close_application — actual Windows process image name (check Task
# Manager > Details tab while each app is running to confirm these)
CLOSE_PROCESS_NAMES = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "discord": "Discord.exe",
    "spotify": "Spotify.exe",
}


def open_application(application: str) -> dict:
    key = application.strip().lower()
    target = OPEN_PATHS.get(key, key)
    try:
        os.startfile(target)
    except FileNotFoundError:
        return {"success": False, "message": f"Couldn't find or open {application} on this computer."}
    except Exception as e:
        return {"success": False, "message": f"Failed to open {application}: {e}"}
    return {"success": True, "message": f"Opened {application}."}


def close_application(application: str) -> dict:
    key = application.strip().lower()
    process_name = CLOSE_PROCESS_NAMES.get(key, f"{application}.exe")
    try:
        result = subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True, text=True, timeout=10,
        )
    except Exception as e:
        return {"success": False, "message": f"Failed to close {application}: {e}"}
    if result.returncode != 0:
        return {"success": False, "message": f"{application} doesn't appear to be running."}
    return {"success": True, "message": f"Closed {application}."}

def browser_search(query: str) -> dict:
    """Open a Google search for the given query in the default browser."""
    try:
        encoded = urllib.parse.quote_plus(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
    except Exception as e:
        return {"success": False, "message": f"Couldn't perform the search: {e}"}

    return {"success": True, "message": f"Searched for: {query}"}


def unsupported_request(reason: str) -> dict:
    """Called by the LLM when no other tool fits the request.

    Always returns success=False — this represents the assistant
    correctly declining, not an error, but core.py should still treat
    it as "no action was taken" for logging/response purposes.
    """
    return {"success": False, "message": f"I can't do that yet: {reason}"}


# Dispatch table — core.py looks up the LLM's chosen tool name here.
TOOL_REGISTRY = {
    "open_application": open_application,
    "close_application": close_application,
    "browser_search": browser_search,
    "unsupported_request": unsupported_request,
}