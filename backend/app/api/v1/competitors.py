import uuid
from typing import List, Any, Annotated
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.models.competitor import Competitor
from app.models.project import Project
from app.schemas.competitor import CompetitorCreate, CompetitorRead, CompetitorUpdate, RadarResult, CompetitorDetail
from app.services.quota import QuotaService
from app.services.scoring import ScoringService
from app.models.event import EventType, Event

router = APIRouter()

@router.get("/", response_model=List[CompetitorRead])
def read_competitors(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    project_id: uuid.UUID = None
) -> Any:
    """
    Retrieve competitors.
    """
    statement = select(Competitor).join(Project).where(Project.user_id == current_user.id)
    
    if project_id:
        statement = statement.where(Competitor.project_id == project_id)
        
    statement = statement.offset(skip).limit(limit)
    competitors = session.exec(statement).all()
    return competitors

@router.post("/", response_model=CompetitorRead)
def create_competitor(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_in: CompetitorCreate,
) -> Any:
    """
    Create new competitor.
    """
    # 1. Verify Project Ownership
    project = session.get(Project, competitor_in.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Check Quota
    # Count all competitors for this user
    count_statement = select(func.count(Competitor.id)).join(Project).where(Project.user_id == current_user.id)
    current_count = session.exec(count_statement).one()
    
    if not QuotaService.can_add_competitor(current_user, current_count):
        raise HTTPException(status_code=403, detail="Plan quota exceeded")

    # 3. Create Competitor
    competitor = Competitor.model_validate(competitor_in)
    session.add(competitor)
    session.commit()
    session.refresh(competitor)
    return competitor

@router.get("/radar", response_model=List[RadarResult])
def radar_scan(
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    query: str = Query(..., min_length=3, description="Market keyword to scan")
) -> Any:
    """
    Simulate a market scan for competitors.
    Returns mock data with generated threat scores.
    """
    # Mock data generation
    mock_suffixes = ["Solutions", "Tech", "Systems", "AI", "Soft", "Hub", "Lab"]
    mock_pitches = ["Disrupting the industry with AI-driven insights.", "Next-generation automation for modern enterprises.", "The complete toolkit for scaling digital infrastructure.", "Revolutionizing customer engagement through predictive modeling."]
    mock_strengths = ["Strong community", "Rapid innovation", "User-friendly UI", "Low cost", "Global reach"]
    mock_weaknesses = ["Limited integration", "High complexity", "New player", "Fragmented support"]
    
    results = []
    
    for _ in range(5):
        name = f"{query.capitalize()} {random.choice(mock_suffixes)}"
        threat_score = random.randint(30, 95)
        
        market_presence = "Medium"
        if threat_score > 80:
            market_presence = "High"
        elif threat_score < 40:
            market_presence = "Low"

        results.append(RadarResult(
            name=name,
            url=f"https://www.{name.lower().replace(' ', '')}.com",
            threat_score=threat_score,
            market_presence=market_presence,
            pitch=random.choice(mock_pitches),
            strengths=random.sample(mock_strengths, 2),
            weaknesses=random.sample(mock_weaknesses, 2)
        ))
        
    return results

@router.get("/{competitor_id}", response_model=CompetitorDetail)
def read_competitor(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_id: uuid.UUID,
) -> Any:
    """
    Get competitor by ID with detailed insights.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    # Verify ownership
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Generate mock details
    mock_pitches = ["Disrupting the industry with AI-driven insights.", "Next-generation automation for modern enterprises.", "The complete toolkit for scaling digital infrastructure.", "Revolutionizing customer engagement through predictive modeling."]
    mock_strengths = ["Strong community", "Rapid innovation", "User-friendly UI", "Low cost", "Global reach"]
    mock_weaknesses = ["Limited integration", "High complexity", "New player", "Fragmented support"]
    
    return CompetitorDetail(
        **competitor.model_dump(),
        pitch=random.choice(mock_pitches),
        estimated_revenue=f"${random.randint(1, 50)}M",
        strengths=random.sample(mock_strengths, 2),
        weaknesses=random.sample(mock_weaknesses, 2),
        market_sentiment=random.choice(["Positive", "Neutral", "Mixed"])
    )

@router.patch("/{competitor_id}", response_model=CompetitorRead)
def update_competitor(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_id: uuid.UUID,
    competitor_in: CompetitorUpdate,
) -> Any:
    """
    Update competitor.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    update_data = competitor_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(competitor, key, value)
        
    session.add(competitor)
    session.commit()
    session.refresh(competitor)
    return competitor

@router.delete("/{competitor_id}")
def delete_competitor(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_id: uuid.UUID,
) -> Any:
    """
    Delete competitor.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    session.delete(competitor)
    session.commit()
    return {"ok": True}

@router.get("/{competitor_id}/events", response_model=List[Event])
def read_competitor_events(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_id: uuid.UUID,
    limit: int = 50,
) -> Any:
    """
    Get events for a competitor.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
        
    events = session.exec(
        select(Event)
        .where(Event.competitor_id == competitor_id)
        .order_by(Event.timestamp.desc())
        .limit(limit)
    ).all()
    
    return events
