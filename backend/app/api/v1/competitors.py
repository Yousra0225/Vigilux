import uuid
from typing import List, Any, Annotated, Optional
import random

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from celery.result import AsyncResult

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.models.competitor import Competitor
from app.models.project import Project
from app.schemas.competitor import CompetitorCreate, CompetitorRead, CompetitorUpdate, RadarResult, CompetitorDetail
from app.services.quota import QuotaService
from app.models.event import Event
from app.tasks.radar import perform_market_scan
from app.tasks.scraping import scrape_competitor_task

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

@router.get("/radar/scan", response_model=dict)
def radar_scan(
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    query: str = Query(..., min_length=3, description="Market keyword to scan"),
    num_results: int = Query(5, ge=1, le=20, description="Number of results to return")
) -> Any:
    """
    Trigger an async market scan for competitors.
    Returns immediately with a task_id for tracking progress.
    """
    # Trigger async task
    task = perform_market_scan.delay(query, str(current_user.id), num_results)

    return {
        "task_id": task.id,
        "status": "PENDING",
        "message": f"Market scan for '{query}' started. Use /tasks/{task.id} to check status."
    }


@router.get("/radar", response_model=List[RadarResult])
def radar_scan_sync(
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    query: str = Query(..., min_length=3, description="Market keyword to scan")
) -> Any:
    """
    Synchronous market scan for competitors (legacy endpoint).
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


@router.get("/tasks/{task_id}", response_model=dict)
def get_task_status(
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    task_id: str
) -> Any:
    """
    Check the status of an async task.
    Returns task status and result if available.
    """
    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.state == "PENDING":
        response["message"] = "Task is waiting to be processed."
    elif task.state == "STARTED":
        response["message"] = "Task has been started."
    elif task.state == "SUCCESS":
        response["result"] = task.result
        response["message"] = "Task completed successfully."
    elif task.state == "FAILURE":
        response["error"] = str(task.info)
        response["message"] = "Task failed."
    else:
        response["message"] = f"Task state: {task.state}"

    return response

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


@router.post("/{competitor_id}/refresh", response_model=dict)
def refresh_competitor(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    competitor_id: uuid.UUID,
    location: Optional[str] = None,
) -> Any:
    """
    Manually trigger a refresh for a specific competitor.

    This initiates an asynchronous scrape and analysis pipeline:
    1. Scrapes Google Maps for updated competitor data
    2. Normalizes the scraped data
    3. Updates competitor record
    4. Triggers AI analysis for insights

    Rate limits apply based on user plan:
    - Starter: 1 refresh per 24 hours
    - Growth: 10 refreshes per 24 hours
    - Ultimate: No daily limit (1 per minute throttle)

    Args:
        competitor_id: UUID of the competitor to refresh
        location: Geographic location for the search (optional)

    Returns:
        Dictionary with task_id for tracking progress
    """
    # 1. Verify competitor exists and user owns it
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # 2. Check quota/rate limit
    # Note: Competitor model doesn't have last_scanned_at field yet,
    # so we'll pass None for now. When the field is added, this check
    # will be more effective.
    if not QuotaService.can_refresh_competitor(current_user, last_refresh=None):
        effective_plan = QuotaService.get_effective_plan(current_user)
        if effective_plan.value == "starter":
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded: Starter plan allows 1 refresh per 24 hours"
            )
        elif effective_plan.value == "growth":
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded: Growth plan allows 10 refreshes per 24 hours"
            )
        else:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded: Please wait before refreshing again"
            )

    # 3. Trigger the scrape task (which will trigger analysis)
    task = scrape_competitor_task.delay(str(competitor_id), location)

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Refresh task started. Use /tasks/" + task.id + " to check status."
    }

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
