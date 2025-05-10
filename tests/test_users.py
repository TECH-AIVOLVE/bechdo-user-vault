
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_current_user(test_user):
    """Test getting current user profile"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    
def test_update_current_user(test_user):
    """Test updating current user profile"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    
def test_read_user_profile(test_user):
    """Test getting a user's public profile"""
    response = client.get(f"/api/v1/users/profile/{test_user['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["username"] == test_user["username"]
    # Email should not be included in public profile
    assert "email" not in data

def test_admin_get_users(test_admin):
    """Test admin getting all users"""
    headers = {"Authorization": f"Bearer {test_admin['access_token']}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
def test_non_admin_get_users(test_user):
    """Test non-admin trying to get all users"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403
    
def test_admin_update_user(test_admin, test_user):
    """Test admin updating a user"""
    headers = {"Authorization": f"Bearer {test_admin['access_token']}"}
    response = client.patch(
        f"/api/v1/users/{test_user['id']}",
        headers=headers,
        json={"role": "seller", "is_active": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "seller"
    assert data["is_active"] == True
    
def test_non_admin_update_user(test_user):
    """Test non-admin trying to update another user"""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.patch(
        f"/api/v1/users/{test_user['id']}",
        headers=headers,
        json={"role": "admin"}
    )
    assert response.status_code == 403
