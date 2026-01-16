import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from app.main import app
from app.core.db import get_session
from app.models.user import User, PlanType
from app.models.project import Project
from app.models.competitor import Competitor
from app.models.event import Event, EventType
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

def test_dashboard_stats():
    create_db_and_tables()
    
    with Session(engine) as session:
        # Create User
        user = User(
            email="test_dash@example.com",
            hashed_password="hashed_pw",
            plan_type=PlanType.GROWTH,
            trial_start_date=datetime.now(timezone.utc),
            is_verified=True,
            is_paid=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create Project
        project = Project(
            user_id=user.id,
            url="https://myproject.com",
            description="Test Project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        # Create Competitors
        comp1 = Competitor(project_id=project.id, name="Comp A", score=50)
        comp2 = Competitor(project_id=project.id, name="Comp B", score=80)
        session.add(comp1)
        session.add(comp2)
        session.commit()
        session.refresh(comp1)
        session.refresh(comp2)
        
        # Create Events
        # 1. Breakthrough event (>7)
        event1 = Event(
            competitor_id=comp1.id, 
            event_type=EventType.PRICE, 
            description="Big price drop", 
            score=9,
            timestamp=datetime.utcnow()
        )
        # 2. Normal event
        event2 = Event(
            competitor_id=comp2.id, 
            event_type=EventType.FEATURE, 
            description="Minor update", 
            score=5,
            timestamp=datetime.utcnow() - timedelta(days=1)
        )
        # 3. Old event (older than 30 days) - should not be in timeline? 
        # Actually logic is "last 30 days".
        event3 = Event(
            competitor_id=comp1.id,
            event_type=EventType.HEALTH,
            description="Old news",
            score=8,
            timestamp=datetime.utcnow() - timedelta(days=35)
        )
        
        session.add(event1)
        session.add(event2)
        session.add(event3)
        session.commit()
        
        user_id = user.id

    # Get Token
    access_token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Call Dashboard API
    response = client.get("/api/v1/dashboard/stats", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    
    # Verify Stats
    assert data["total_competitors"] == 2
    # Breakthroughs: event1 (9) and event3 (8). 
    # Logic: "Breakthrough Signals (Event score > 7)". 
    # It doesn't restrict to timeline in the instructions for the count, 
    # usually stats like "Total Breakthroughs" might be all time or filtered.
    # My implementation does NOT filter by date for the count, only for timeline.
    # So expected count is 2.
    assert data["breakthrough_signals_count"] == 2
    
    # Average Threat Score: (50 + 80) / 2 = 65.0
    assert data["average_threat_score"] == 65.0
    
    # Verify Timeline
    timeline = data["timeline_data"]
    assert isinstance(timeline, list)
    assert len(timeline) >= 2 # At least today and yesterday
    
    # Check if we have counts for today and yesterday
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    today_point = next((x for x in timeline if x["date"] == today_str), None)
    yesterday_point = next((x for x in timeline if x["date"] == yesterday_str), None)
    
    assert today_point is not None
    assert today_point["count"] == 1 # event1
    assert yesterday_point is not None
    assert yesterday_point["count"] == 1 # event2
    
    # Ensure old event is NOT in timeline count for that day if we checked that far back,
    # or ensure timeline range is correct.
    # Since I fill 0s for last 30 days, we should have ~30 entries.
    assert len(timeline) >= 30

if __name__ == "__main__":
    test_dashboard_stats()
    print("Dashboard tests passed!")
