import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.room_manager import get_room_manager

@pytest.fixture
def client():
    manager = get_room_manager()
    manager.active_connections.clear()
    return TestClient(app)

def test_websocket_connect_valid(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "system"
        assert "joined" in data["text"]

def test_websocket_connect_no_username(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/rooms/test") as websocket:
            pass

def test_websocket_send_message(client):
    with client.websocket_connect("/ws/rooms/chat?username=alice") as websocket:
        websocket.receive_json()
        
        websocket.send_json({"type": "message", "text": "Hello!"})
        response = websocket.receive_json()
        
        assert response["type"] == "message"
        assert response["text"] == "Hello!"
        assert response["username"] == "alice"
        assert response["room_id"] == "chat"

def test_two_clients_same_room(client):
    with client.websocket_connect("/ws/rooms/lobby?username=alice") as ws1:
        # Получаем сообщение о подключении alice
        join_msg1 = ws1.receive_json()
        assert join_msg1["type"] == "system"
        assert "alice" in join_msg1["text"]
        
        with client.websocket_connect("/ws/rooms/lobby?username=bob") as ws2:
            # Получаем сообщение о подключении bob для ws2
            join_msg2 = ws2.receive_json()
            assert join_msg2["type"] == "system"
            assert "bob" in join_msg2["text"]
            
            # ws1 также получает сообщение о подключении bob
            join_msg1_for_ws1 = ws1.receive_json()
            assert join_msg1_for_ws1["type"] == "system"
            assert "bob" in join_msg1_for_ws1["text"]
            
            ws1.send_json({"type": "message", "text": "Hello everyone!"})
            
            response1 = ws1.receive_json()
            response2 = ws2.receive_json()
            
            assert response1["type"] == "message"
            assert response1["text"] == "Hello everyone!"
            assert response1["username"] == "alice"
            
            assert response2["type"] == "message"
            assert response2["text"] == "Hello everyone!"
            assert response2["username"] == "alice"

def test_different_rooms_isolated(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1:
        ws1.receive_json()
        
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            ws2.receive_json()
            
            ws1.send_json({"type": "message", "text": "Secret message"})
            
            response1 = ws1.receive_json()
            
            with pytest.raises(Exception):
                ws2.receive_json(timeout=1)

def test_message_too_long(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        websocket.receive_json()
        
        long_message = "x" * 301
        websocket.send_json({"type": "message", "text": long_message})
        
        error_response = websocket.receive_json()
        assert error_response["type"] == "error"
        assert "too long" in error_response["detail"].lower()

def test_user_leaves_room(client):
    with client.websocket_connect("/ws/rooms/test?username=alice") as websocket:
        websocket.receive_json()
    
    response = client.get("/rooms/test/users")
    assert response.json()["users"] == []