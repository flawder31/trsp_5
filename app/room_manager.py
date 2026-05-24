from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json

class RoomManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        
        self.active_connections[room_id][username] = websocket
        
        await self.broadcast(room_id, {
            "type": "system",
            "text": f"{username} joined the room"
        })

    def disconnect(self, room_id: str, username: str):
        if room_id in self.active_connections:
            if username in self.active_connections[room_id]:
                del self.active_connections[room_id][username]
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, room_id: str, payload: dict):
        if room_id in self.active_connections:
            for username, connection in self.active_connections[room_id].items():
                try:
                    await connection.send_json(payload)
                except:
                    pass

    def get_users(self, room_id: str) -> list:
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []

    async def send_to_user(self, room_id: str, username: str, payload: dict):
        if room_id in self.active_connections:
            if username in self.active_connections[room_id]:
                await self.active_connections[room_id][username].send_json(payload)

room_manager = RoomManager()

def get_room_manager():
    return room_manager