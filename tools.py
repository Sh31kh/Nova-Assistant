# tools.py
"""tools.py — Phase 1 tool implementations, config-driven.

open_application now supports optional launch_args (e.g. Steam's
-applaunch <appid>). Apps with no args behave exactly as before —
os.startfile for the plain case, subprocess.Popen only when args exist,
since os.startfile can't pass command-line arguments at all.
"""

import subprocess
import webbrowser
import urllib.parse
import os

_cfg = None


def configure(cfg):
    global _cfg
    _cfg = cfg


def open_application(application: str) -> dict:
    if _cfg is None:
        return {"success": False, "message": "Tools not configured — call configure(cfg) at startup."}

    target = _cfg.app_open_path(application)
    if target is None:
        return {
            "success": False,
            "message": f"{application} isn't in my configured app list. Add it to config.yaml.",
        }

    args = _cfg.app_open_args(application)

    try:
        if args:
            # Needs real arguments (e.g. Steam's -applaunch) — os.startfile
            # can't pass these, so use Popen. Requires a real .exe path,
            # not a .lnk shortcut (Popen won't resolve shortcuts).
            subprocess.Popen([target, *args])
        else:
            # Plain launch, no arguments — os.startfile handles both .exe
            # and .lnk correctly, so keep using it for the simple case.
            os.startfile(target)
    except FileNotFoundError:
        return {
            "success": False,
            "message": f"Couldn't find {application} at its configured path — check config.yaml.",
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to open {application}: {e}"}

    return {"success": True, "message": f"Opened {application}."}


def close_application(application: str) -> dict:
    if _cfg is None:
        return {"success": False, "message": "Tools not configured — call configure(cfg) at startup."}

    process_name = _cfg.app_close_process(application)
    if process_name is None:
        return {
            "success": False,
            "message": f"{application} isn't in my configured app list. Add it to config.yaml.",
        }

    try:
        result = subprocess.run(
            ["taskkill", "/IM", process_name, "/F"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        return {"success": False, "message": f"Failed to close {application}: {e}"}

    if result.returncode != 0:
        return {
            "success": False,
            "message": f"{application} doesn't appear to be running.",
        }

    return {"success": True, "message": f"Closed {application}."}


def browser_search(query: str) -> dict:
    try:
        encoded = urllib.parse.quote_plus(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
    except Exception as e:
        return {"success": False, "message": f"Couldn't perform the search: {e}"}

    return {"success": True, "message": f"Searched for: {query}"}


def unsupported_request(reason: str) -> dict:
    return {"success": False, "message": f"I can't do that yet: {reason}"}

def browser_open_site(site: str) -> dict:
    if _cfg is None:
        return {"success": False, "message": "Tools not configured — call configure(cfg) at startup."}

    url = _cfg.site_url(site)
    if url is None:
        return {
            "success": False,
            "message": f"{site} isn't in my configured sites. Add it to config.yaml, or I can search for it instead.",
        }

    try:
        webbrowser.open(url)
    except Exception as e:
        return {"success": False, "message": f"Failed to open {site}: {e}"}

    return {"success": True, "message": f"Opened {site}."}


TOOL_REGISTRY = {
    "open_application": open_application,
    "close_application": close_application,
    "browser_search": browser_search,
    "browser_open_site": browser_open_site,
    "unsupported_request": unsupported_request,
}