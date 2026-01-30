import pytest
from fastapi.testclient import TestClient
from app.models.notification_setting import NotificationChannel

def get_auth_header(client: TestClient, email: str):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password"})
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": "password"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_notification_settings_flow(client: TestClient):
    headers = get_auth_header(client, "notif@test.com")
    
    # 1. Reset/Initialize
    client.post("/api/v1/notifications/users/me/notifications/reset", headers=headers)
    
    # 2. Get settings
    response = client.get("/api/v1/notifications/users/me/notifications", headers=headers)
    assert response.status_code == 200
    settings = response.json()
    assert len(settings) > 0
    
    # 3. Update a setting
    channel = NotificationChannel.EMAIL
    update_data = {"enabled": False, "min_score": 90}
    patch_res = client.patch(
        f"/api/v1/notifications/users/me/notifications/{channel}",
        json=update_data,
        headers=headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["enabled"] is False
    assert patch_res.json()["min_score"] == 90
