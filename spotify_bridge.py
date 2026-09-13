# spotify_bridge.py
import asyncio
import json
from websockets.asyncio.server import serve

HOST = "127.0.0.1"
PORT = 8765

clients = {"spicetify": None, "nova": None}


async def handle_client(websocket):
    role = None
    try:
        async for raw in websocket:
            msg = json.loads(raw)

            if msg.get("type") == "register":
                role = msg.get("client")
                clients[role] = websocket
                print(f"[spotify] {role} registered.")
                continue

            if msg.get("type") == "command":
                target = clients.get("spicetify")
                if target is None:
                    await websocket.send(json.dumps({
                        "type": "result", "success": False,
                        "error": "Spicetify not connected"
                    }))
                    continue
                await target.send(json.dumps(msg))
                print(f"[spotify] Forwarded command to Spicetify: {msg}")

            if msg.get("type") == "result":
                target = clients.get("nova")
                if target is not None:
                    await target.send(raw)
                print(f"[spotify] Forwarded result to Nova: {msg}")

    except Exception as e:
        print(f"[spotify] Connection error ({role}): {e}")
    finally:
        if role:
            clients[role] = None
            print(f"[spotify] {role} disconnected.")


async def main():
    print(f"[spotify] Starting bridge on ws://{HOST}:{PORT}")
    async with serve(handle_client, HOST, PORT):
        print("[spotify] Bridge ready.")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())