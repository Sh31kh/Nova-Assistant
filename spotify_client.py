"""spotify_client.py — local WebSocket bridge to the Spicetify extension.

Runs the server in a background thread with its own asyncio event loop.
Exposes send_command() as a plain synchronous function so tools.py (which
is entirely synchronous) can call it without knowing anything about
asyncio — the cross-thread handoff uses asyncio.run_coroutine_threadsafe,
the standard pattern for calling into a background event loop from a
regular thread.
"""

import asyncio
import threading
import json
from websockets.asyncio.server import serve

HOST = "127.0.0.1"
PORT = 8765

_spicetify_ws = None
_loop = None
_pending_future = None


async def _handle_client(websocket):
    global _spicetify_ws
    role = None
    try:
        async for raw in websocket:
            msg = json.loads(raw)

            if msg.get("type") == "register":
                role = msg.get("client")
                if role == "spicetify":
                    _spicetify_ws = websocket
                    print("[spotify] Spicetify registered.")
                continue

            if msg.get("type") == "result":
                if _pending_future is not None and not _pending_future.done():
                    _pending_future.set_result(msg)

    except Exception as e:
        print(f"[spotify] Connection error: {e}")
    finally:
        if role == "spicetify":
            _spicetify_ws = None
            print("[spotify] Spicetify disconnected.")


async def _server_main():
    async with serve(_handle_client, HOST, PORT):
        print("[spotify] Bridge ready.")
        await asyncio.Future()


async def _send_command_async(command: str, timeout: float) -> dict:
    global _pending_future

    if _spicetify_ws is None:
        return {"success": False, "error": "Spicetify not connected"}

    _pending_future = asyncio.get_event_loop().create_future()
    await _spicetify_ws.send(json.dumps({"type": "command", "command": command}))

    try:
        return await asyncio.wait_for(_pending_future, timeout=timeout)
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timed out waiting for Spicetify"}


def send_command(command: str, timeout: float = 5.0) -> dict:
    """The actual entry point — call this from tools.py. Looks and
    behaves like a normal blocking function call; the asyncio machinery
    is entirely hidden behind it."""
    if _loop is None:
        return {"success": False, "error": "Bridge not running"}

    future = asyncio.run_coroutine_threadsafe(
        _send_command_async(command, timeout), _loop
    )
    return future.result(timeout=timeout + 1)


def start_bridge_in_background():
    """Call once from core.py's main(). Same background-thread pattern
    as the tray icon — starts and runs forever, invisibly, alongside
    the normal synchronous voice loop."""
    global _loop

    def _run():
        global _loop
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        _loop.run_until_complete(_server_main())

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()