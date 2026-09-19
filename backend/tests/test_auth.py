import pytest
from app.core.config import settings

def test_admin_login_success(client):
    response = client.post("/api/auth/admin/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"
    assert data["user"]["email"] == settings.ADMIN_EMAIL

def test_admin_login_invalid_password(client):
    response = client.post("/api/auth/admin/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": "wrongpassword123"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Invalid administrator credentials. Access denied."

def test_admin_login_invalid_email(client):
    response = client.post("/api/auth/admin/login", json={
        "email": "hacker@evil.com",
        "password": settings.ADMIN_PASSWORD
    })
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Invalid administrator credentials. Access denied."

def test_user_registration_and_login(client):
    # Register
    reg_res = client.post("/api/auth/register", json={
        "email": "newdriver@parkvision.ai",
        "password": "secureuser123",
        "full_name": "Test Driver"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["role"] == "USER"
    assert "access_token" in reg_data

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": "newdriver@parkvision.ai",
        "password": "secureuser123"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["role"] == "USER"

def test_protected_admin_routes_unauthenticated(client):
    response = client.get("/api/admin/dashboard")
    assert response.status_code == 401

def test_protected_admin_routes_forbidden_for_normal_user(client):
    # Register normal user & get token
    reg_res = client.post("/api/auth/register", json={
        "email": "normaluser@parkvision.ai",
        "password": "userpass123",
        "full_name": "Normal User"
    })
    token = reg_res.json()["access_token"]

    # Try admin endpoint with user token
    response = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_protected_admin_routes_success_for_admin(client):
    # Login as Admin
    admin_res = client.post("/api/auth/admin/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD
    })
    admin_token = admin_res.json()["access_token"]

    # Access Admin Dashboard
    dash_res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["facility_status"] == "OPERATIONAL"
    assert dash_data["total_lots"] >= 1

    # Access Admin Users list
    users_res = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert users_res.status_code == 200
    assert isinstance(users_res.json(), list)

def test_admin_space_status_lock_unlock(client):
    # Get Admin token
    admin_res = client.post("/api/auth/admin/login", json={
        "email": settings.ADMIN_EMAIL,
        "password": settings.ADMIN_PASSWORD
    })
    token = admin_res.json()["access_token"]

    # Lock space 1
    lock_res = client.post("/api/admin/spaces/1/status?status_action=LOCK", headers={"Authorization": f"Bearer {token}"})
    assert lock_res.status_code == 200
    assert lock_res.json()["status"] == "RESERVED"

    # Unlock space 1
    unlock_res = client.post("/api/admin/spaces/1/status?status_action=UNLOCK", headers={"Authorization": f"Bearer {token}"})
    assert unlock_res.status_code == 200
    assert unlock_res.json()["status"] == "AVAILABLE"
