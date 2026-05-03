from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WorldWide Chat")


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        self.active_connections[websocket] = username
        await self.broadcast(
            {
                "type": "system",
                "message": f"{username} joined the chat",
                "sentAt": utc_now(),
            }
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        username = self.active_connections.pop(websocket, "Anonymous")
        await self.broadcast(
            {
                "type": "system",
                "message": f"{username} left the chat",
                "sentAt": utc_now(),
            }
        )

    async def broadcast(self, payload: dict) -> None:
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_json(payload)
            except RuntimeError:
                dead.append(conn)
        for conn in dead:
            self.active_connections.pop(conn, None)


manager = ConnectionManager()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/")
async def index() -> HTMLResponse:
    html = Path("static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "Anonymous") -> None:
    await manager.connect(websocket, username=username.strip() or "Anonymous")
    try:
        while True:
            data = await websocket.receive_json()
            message = str(data.get("message", "")).strip()
            if not message:
                continue
            await manager.broadcast(
                {
                    "type": "chat",
                    "username": manager.active_connections.get(websocket, "Anonymous"),
                    "message": message,
                    "sentAt": utc_now(),
                }
            )
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
