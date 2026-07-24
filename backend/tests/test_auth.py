from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.user import User


def test_register_user(client: TestClient, session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    
    # Verify in DB
    statement = select(User).where(User.email == "newuser@example.com")
    user = session.exec(statement).first()
    assert user is not None
    assert user.email == "newuser@example.com"

def test_login_access_token(client: TestClient, session: Session):
    # First register
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"}
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_me(client: TestClient):
    # Register and login to get token
    client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123"}
    )
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "me@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

def test_update_niche(client: TestClient):
    # Register and login to get token
    client.post(
        "/api/v1/auth/register",
        json={"email": "niche@example.com", "password": "password123"}
    )
    login_res = client.post(
        "/api/v1/auth/login",
        data={"username": "niche@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check initial niche is None
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.json()["niche"] is None
    
    # Update niche
    response = client.patch(
        "/api/v1/auth/me",
        headers=headers,
        json={"niche": "SaaS"}
    )
    assert response.status_code == 200
    assert response.json()["niche"] == "SaaS"
    
    # Verify persistence
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.json()["niche"] == "SaaS"