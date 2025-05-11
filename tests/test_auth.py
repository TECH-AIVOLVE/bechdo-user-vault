
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.core.security import create_email_verification_token

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

def test_verify_email(test_db):
    """Test email verification"""
    # Create an unverified user
    test_email = "unverified@example.com"
    test_user = {
        "email": test_email,
        "username": "unverified_user",
        "hashed_password": "hashed_password",  # Not needed for this test
        "full_name": "Unverified User",
        "role": "basic_user",
        "is_active": False,
        "is_verified": False
    }
    # Insert user directly into test database
    test_db.users.insert_one(test_user)
    
    # Generate a valid verification token
    valid_token = create_email_verification_token(test_email)
    
    # Test with valid token
    response = client.post(
        "/api/v1/auth/verify-email",
        params={"token": valid_token}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify user status has been updated
    verified_user = test_db.users.find_one({"email": test_email})
    assert verified_user["is_verified"] == True
    assert verified_user["is_active"] == True
    
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
