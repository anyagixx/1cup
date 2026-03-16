# FILE: backend/app/websocket/hub.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: WebSocket connection management and event broadcasting
#   SCOPE: Connection lifecycle, message broadcasting, heartbeat
#   DEPENDS: M-BE-CORE, M-BE-CACHE, M-BE-AUTH
#   LINKS: M-BE-WS
# END_MODULE_CONTRACT

import asyncio
import json
from typing import Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from app.logging_config import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    async def disconnect(self, connection_id: str) -> None:
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_personal_message(
        self,
        message: dict,
        connection_id: str,
    ) -> bool:
        async with self._lock:
            websocket = self.active_connections.get(connection_id)
        
        if websocket:
            try:
                await websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                await self.disconnect(connection_id)
        return False
    
    async def broadcast(
        self,
        message: dict,
        exclude: Optional[list[str]] = None,
    ) -> int:
        exclude = exclude or []
        sent_count = 0
        
        async with self._lock:
            connections = list(self.active_connections.items())
        
        for connection_id, websocket in connections:
            if connection_id in exclude:
                continue
            
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {connection_id}: {e}")
                await self.disconnect(connection_id)
        
        return sent_count
    
    async def broadcast_to_topic(
        self,
        topic: str,
        message: dict,
    ) -> int:
        message_with_topic = {**message, "topic": topic}
        return await self.broadcast(message_with_topic)
    
    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()


async def broadcast_event(
    event_type: str,
    data: dict,
    topic: Optional[str] = None,
) -> int:
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    if topic:
        return await manager.broadcast_to_topic(topic, message)
    return await manager.broadcast(message)


async def websocket_endpoint(
    websocket: WebSocket,
    connection_id: str,
):
    await manager.connect(websocket, connection_id)
    
    try:
        await manager.send_personal_message(
            {"type": "connected", "connection_id": connection_id},
            connection_id,
        )
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0,
                )
                
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await manager.send_personal_message(
                            {"type": "pong"},
                            connection_id,
                        )
                except json.JSONDecodeError:
                    pass
            
            except asyncio.TimeoutError:
                await manager.send_personal_message(
                    {"type": "ping"},
                    connection_id,
                )
    
    except WebSocketDisconnect:
        await manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        await manager.disconnect(connection_id)
