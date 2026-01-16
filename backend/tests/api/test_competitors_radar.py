import sys
import os
import uuid
from datetime import datetime, timezone

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from app.main import app
from app.core.db import get_session
from app.models.user import User, PlanType
from app.models.project import Project
from app.core.security import create_access_token

# Setup Test DB (In-memory)
engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override

client = TestClient(app)

def test_competitors_flow():
    create_db_and_tables()
    
    # 1. Create User and Project directly in DB
    with Session(engine) as session:
        user = User(
            email="test_comp@example.com",
            hashed_password="hashed_pw",
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.now(timezone.utc),
            is_verified=True,
            is_paid=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        project = Project(
            user_id=user.id,
            url="https://myproject.com",
            description="Test Project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        user_id = user.id
        project_id = project.id

    # 2. Get Token
    access_token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create Competitor
    response = client.post(
        "/api/v1/competitors/",
        headers=headers,
        json={
            "project_id": str(project_id),
            "name": "Test Competitor",
            "url": "https://competitor.com"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Competitor"
    assert "id" in data
    competitor_id = data["id"]

    # 4. List Competitors
    response = client.get(
        f"/api/v1/competitors/?project_id={project_id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == competitor_id

    # 5. Update Competitor
    response = client.patch(
        f"/api/v1/competitors/{competitor_id}",
        headers=headers,
        json={"name": "Updated Competitor"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Competitor"

    # 6. Delete Competitor
    response = client.delete(
        f"/api/v1/competitors/{competitor_id}",
        headers=headers
    )
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(
        f"/api/v1/competitors/?project_id={project_id}",
        headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_radar_flow():
    # Reuse DB state or existing session, but lets create a new user just in case
    # or just use the same engine since it's in-memory static pool
    
    with Session(engine) as session:
        user = User(
            email="test_radar@example.com",
            hashed_password="hashed_pw",
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.now(timezone.utc),
            is_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    # 2. Get Token
    access_token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Call Radar API
    response = client.get(
        "/api/v1/radar/",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "name" in item
        assert "threat_score" in item
        assert "insights" in item

if __name__ == "__main__":
    test_competitors_flow()
    test_radar_flow()
    print("All tests passed!")
