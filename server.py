import uuid
import time
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import redis
import os

app = FastAPI(title="ShadowChat // BY RUSHAN HAQUE Backend")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis fallback (Local Memory Store if Redis is not available)
class MockRedis:
    def __init__(self):
        self.data = {}
        self.ttls = {}

    def set(self, key, value, ex=None):
        self.data[key] = value
        if ex:
            self.ttls[key] = time.time() + ex

    def get(self, key):
        if key in self.ttls and time.time() > self.ttls[key]:
            self.delete(key)
            return None
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]
        if key in self.ttls:
            del self.ttls[key]

    def exists(self, key):
        if key in self.ttls and time.time() > self.ttls[key]:
            self.delete(key)
            return False
        return key in self.data

    def expire(self, key, seconds):
        if key in self.data:
            self.ttls[key] = time.time() + seconds

try:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    r = redis.from_url(redis_url, decode_responses=True)
    r.ping()
    print(f"Connected to Redis at {redis_url}")
except Exception as e:
    print(f"Redis connection failed: {e}. Using MockRedis")
    r = MockRedis()


# Room and Message Management
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message: dict, room_id: str):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.post("/create-room")
async def create_room():
    room_id = str(uuid.uuid4())
    # Room exists for 1 hour by default
    r.set(f"room:{room_id}:meta", json.dumps({"created_at": time.time()}), ex=3600)
    return {"room_id": room_id}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    # Check if room exists
    if not r.exists(f"room:{room_id}:meta"):
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Room expired or does not exist"})
        await websocket.close()
        return

    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_json()
            # data should be { "type": "msg", "payload": "encrypted_blob" }
            
            if data["type"] == "msg":
                # Burn after reading mechanism: 
                # In a real chat, messages are sent to others and then "burned".
                # For this implementation, we broadcast and then if needed store/delete.
                # However, the user asked for "burn-after-reading" which usually means 
                # once retrieved it's gone. In a WebSocket chat, the "reading" happens
                # when the broadcast is received.
                
                # To simulate "burn after reading" specifically for messages sent while offline:
                # We could store them. But here it's real-time.
                # Let's add a "burn" command.
                
                await manager.broadcast({
                    "type": "msg",
                    "payload": data["payload"],
                    "sender": data.get("sender", "Anonymous"),
                    "timestamp": time.time()
                }, room_id)
            
            elif data["type"] == "burn_signal":
                # Burn after reading: Delete room metadata so link becomes invalid
                r.delete(f"room:{room_id}:meta")
                # Signal to all clients to clear chat
                await manager.broadcast({"type": "burn_all"}, room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable if available (default to 8000 for local dev)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

