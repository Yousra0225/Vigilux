import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.project import Project

def get_auth_header(client: TestClient, email: str):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password"})
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": "password"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_competitor_crud(client: TestClient, session: Session):
    headers = get_auth_header(client, "comp@test.com")
    
    # 1. Create a project first
    user_res = client.get("/api/v1/auth/me", headers=headers)
    user_id = uuid.UUID(user_res.json()["id"])
    
    project = Project(user_id=user_id, url="https://test.com")
    session.add(project)
    session.commit()
    session.refresh(project)
    
    # 2. Create Competitor
    comp_data = {
        "name": "Target Corp",
        "url": "https://target.com",
        "project_id": str(project.id)
    }
    response = client.post("/api/v1/competitors/", json=comp_data, headers=headers)
    assert response.status_code == 200
    comp_id = response.json()["id"]
    
    # 3. Read Competitors
    read_res = client.get("/api/v1/competitors/", headers=headers)
    assert len(read_res.json()) >= 1
    
    # 4. Update
    client.patch(f"/api/v1/competitors/{comp_id}", json={"name": "Updated Name"}, headers=headers)
    
    # 5. Read Detail
    detail_res = client.get(f"/api/v1/competitors/{comp_id}", headers=headers)
    assert detail_res.json()["name"] == "Updated Name"
    assert "pitch" in detail_res.json()
    
    # 6. Delete
    del_res = client.delete(f"/api/v1/competitors/{comp_id}", headers=headers)
    assert del_res.status_code == 200

def test_radar_scan(client: TestClient):
    headers = get_auth_header(client, "radar@test.com")
    # The API expects 'query' as per backend/app/api/v1/competitors.py
    response = client.get("/api/v1/competitors/radar?query=artificial", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert "threat_score" in response.json()[0]
