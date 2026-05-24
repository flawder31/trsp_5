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
def auth_headers():
    return {"X-User-Id": "10"}

def test_create_task_success(client, auth_headers):
    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "Test Description",
        "status": "todo",
        "priority": 3
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["owner_id"] == 10
    assert "id" in data

def test_create_task_invalid_title(client, auth_headers):
    response = client.post("/tasks/", json={
        "title": "ab",
        "description": "Test",
        "status": "todo",
        "priority": 3
    }, headers=auth_headers)
    
    assert response.status_code == 422

def test_create_task_no_auth(client):
    response = client.post("/tasks/", json={
        "title": "Test Task",
        "description": "Test",
        "status": "todo",
        "priority": 3
    })
    
    assert response.status_code == 401

def test_user_sees_only_own_tasks(client, auth_headers):
    client.post("/tasks/", json={
        "title": "Task 1",
        "status": "todo",
        "priority": 3
    }, headers=auth_headers)
    
    client.post("/tasks/", json={
        "title": "Task 2",
        "status": "done",
        "priority": 4
    }, headers={"X-User-Id": "20"})
    
    response = client.get("/tasks/", headers=auth_headers)
    tasks = response.json()
    
    assert all(task["owner_id"] == 10 for task in tasks)

def test_filter_tasks(client, auth_headers):
    client.post("/tasks/", json={
        "title": "Task 1",
        "status": "todo",
        "priority": 2
    }, headers=auth_headers)
    
    client.post("/tasks/", json={
        "title": "Task 2",
        "status": "in_progress",
        "priority": 4
    }, headers=auth_headers)
    
    client.post("/tasks/", json={
        "title": "Task 3",
        "status": "todo",
        "priority": 5
    }, headers=auth_headers)
    
    response = client.get("/tasks/?status=todo&min_priority=3", headers=auth_headers)
    tasks = response.json()
    
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"
    assert tasks[0]["priority"] >= 3

def test_update_task_status(client, auth_headers):
    create_response = client.post("/tasks/", json={
        "title": "Update Test",
        "status": "todo",
        "priority": 3
    }, headers=auth_headers)
    
    task_id = create_response.json()["id"]
    
    response = client.patch(f"/tasks/{task_id}/status", json={
        "status": "done"
    }, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["status"] == "done"

def test_access_foreign_task_404(client, auth_headers):
    create_response = client.post("/tasks/", json={
        "title": "Foreign Task",
        "status": "todo",
        "priority": 3
    }, headers={"X-User-Id": "20"})
    
    task_id = create_response.json()["id"]
    
    response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 404

def test_delete_task_success(client, auth_headers):
    create_response = client.post("/tasks/", json={
        "title": "Delete Test",
        "status": "todo",
        "priority": 3
    }, headers=auth_headers)
    
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204
    
    get_response = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}