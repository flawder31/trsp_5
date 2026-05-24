import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import get_storage

@pytest.fixture
def client():
    storage = get_storage()
    storage.clear()
    return TestClient(app)

@pytest.fixture
def user_headers():
    return {"X-User-Id": "10", "X-User-Role": "user"}

@pytest.fixture
def admin_headers():
    return {"X-User-Id": "1", "X-User-Role": "admin"}

def test_users_me_endpoint(client, user_headers):
    response = client.get("/users/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"

def test_no_user_id_header_returns_401(client):
    response = client.get("/users/me")
    assert response.status_code == 401

def test_regular_user_cannot_access_admin_stats(client, user_headers):
    response = client.get("/admin/stats", headers=user_headers)
    assert response.status_code == 403

def test_admin_can_access_stats(client, admin_headers, user_headers):
    client.post("/tasks/", json={
        "title": "Task 1",
        "status": "todo",
        "priority": 3
    }, headers=user_headers)
    
    client.post("/tasks/", json={
        "title": "Task 2",
        "status": "done",
        "priority": 4
    }, headers=user_headers)
    
    response = client.get("/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 2
    assert "todo" in data["by_status"]
    assert "done" in data["by_status"]

def test_regular_user_cannot_delete_foreign_task(client, user_headers):
    create_response = client.post("/tasks/", json={
        "title": "Foreign Task",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "20", "X-User-Role": "user"})
    
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers=user_headers)
    assert response.status_code == 404

def test_admin_can_delete_any_task(client, admin_headers):
    create_response = client.post("/tasks/", json={
        "title": "Any Task",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "20", "X-User-Role": "user"})
    
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/admin/tasks/{task_id}", headers=admin_headers)
    assert response.status_code == 204

def test_swagger_ui_has_tags(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    paths = data.get("paths", {})
    tasks_paths = any("/tasks" in path for path in paths.keys())
    users_paths = any("/users" in path for path in paths.keys())
    admin_paths = any("/admin" in path for path in paths.keys())
    
    assert tasks_paths
    assert users_paths
    assert admin_paths