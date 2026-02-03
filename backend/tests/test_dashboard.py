from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.project import Project
from app.models.competitor import Competitor
from app.models.event import Event, EventType
from datetime import datetime

import uuid

def get_auth_header(client: TestClient, email: str):
    client.post("/api/v1/auth/register", json={"email": email, "password": "password"})
    login_res = client.post("/api/v1/auth/login", data={"username": email, "password": "password"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_dashboard_stats(client: TestClient, session: Session):
    headers = get_auth_header(client, "dash@test.com")
    user_id_str = client.get("/api/v1/auth/me", headers=headers).json()["id"]
    user_id = uuid.UUID(user_id_str)
    
    # Setup data
    project = Project(user_id=user_id, url="https://dash.com")
    session.add(project)
    session.commit()
    
    comp = Competitor(project_id=project.id, name="C1", url="url", score=80)
    session.add(comp)
    session.commit()
    
    event = Event(competitor_id=comp.id, type=EventType.PRICE, description="D", score=90, timestamp=datetime.utcnow())
    session.add(event)
    session.commit()
    
    response = client.get("/api/v1/dashboard/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_competitors"] == 1
    assert data["breakthroughs_today"] == 1
    assert data["avg_threat_score"] == 80.0
    assert len(data["chart_data"]) >= 1
