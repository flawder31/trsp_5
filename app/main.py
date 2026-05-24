from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routers import tasks, users, admin
from app.room_manager import get_room_manager

app = FastAPI(title="Task Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, username: str = None):
    room_manager = get_room_manager()
    
    if not username or not username.strip():
        await websocket.close(code=1008)
        return
    
    username = username.strip()
    
    try:
        await room_manager.connect(room_id, username, websocket)
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "message":
                text = data.get("text", "")
                
                if len(text) > 300:
                    await room_manager.send_to_user(room_id, username, {
                        "type": "error",
                        "detail": "Message is too long"
                    })
                else:
                    await room_manager.broadcast(room_id, {
                        "type": "message",
                        "room_id": room_id,
                        "username": username,
                        "text": text
                    })
    
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, username)
        await room_manager.broadcast(room_id, {
            "type": "system",
            "text": f"{username} left the room"
        })

@app.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    room_manager = get_room_manager()
    return {
        "room_id": room_id,
        "users": room_manager.get_users(room_id)
    }