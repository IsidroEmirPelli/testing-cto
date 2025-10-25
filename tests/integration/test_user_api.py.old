import pytest
from fastapi.testclient import TestClient

from src.presentation.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_user():
    user_data = {
        "email": "test@example.com",
        "name": "Test User"
    }
    response = client.post("/users", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data
    assert data["is_active"] is True


def test_get_user():
    user_data = {
        "email": "gettest@example.com",
        "name": "Get Test User"
    }
    create_response = client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    response = client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == user_data["email"]


def test_get_user_not_found():
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{fake_uuid}")
    
    assert response.status_code == 404


def test_list_users():
    response = client.get("/users")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_user():
    user_data = {
        "email": "updatetest@example.com",
        "name": "Original Name"
    }
    create_response = client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    update_data = {"name": "Updated Name"}
    response = client.put(f"/users/{user_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["updated_at"] is not None


def test_delete_user():
    user_data = {
        "email": "deletetest@example.com",
        "name": "Delete Test User"
    }
    create_response = client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    response = client.delete(f"/users/{user_id}")
    
    assert response.status_code == 204
    
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_create_user_duplicate_email():
    user_data = {
        "email": "duplicate@example.com",
        "name": "Duplicate Test"
    }
    
    client.post("/users", json=user_data)
    response = client.post("/users", json=user_data)
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
