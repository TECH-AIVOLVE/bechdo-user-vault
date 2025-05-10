
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data
    
def test_login(test_user):
    """Test user login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(test_user):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401

def test_verify_email():
    """Test email verification"""
    # We would normally test this with a mocked token verification function
    # Since token verification depends on the JWT secret, we'll just test the endpoint behavior
    
    # Invalid token case
    response = client.post(
        "/api/v1/auth/verify-email",
        params={"token": "invalid-token"}
    )
    assert response.status_code == 400
    
def test_forgot_password():
    """Test forgot password endpoint"""
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200
    # We don't reveal if the email exists for security reasons
    assert "message" in response.json()
    
def test_reset_password():
    """Test reset password endpoint"""
    # Invalid token case
    response = client.post(
        "/api/v1/auth/reset-password",
        params={"token": "invalid-token", "new_password": "newpassword123"}
    )
    assert response.status_code == 400
