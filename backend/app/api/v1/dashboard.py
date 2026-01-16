from typing import Any, List, Dict, Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.user import User
from app.models.project import Project
from app.models.competitor import Competitor
from app.models.event import Event

router = APIRouter()

class TimelinePoint(BaseModel):
    date: str
    count: int

class DashboardStats(BaseModel):
    total_competitors: int
    breakthrough_signals_count: int
    average_threat_score: float
    timeline_data: List[TimelinePoint]

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DashboardStats:
    """
    Get aggregated statistics for the dashboard.
    """
    
    # 1. Total Competitors
    total_competitors = session.exec(
        select(func.count(Competitor.id))
        .join(Project)
        .where(Project.user_id == current_user.id)
    ).one() or 0

    # 2. Breakthrough Signals (Event score > 7)
    breakthrough_signals_count = session.exec(
        select(func.count(Event.id))
        .join(Competitor)
        .join(Project)
        .where(Project.user_id == current_user.id)
        .where(Event.score > 7)
    ).one() or 0

    # 3. Average Threat Score
    # Note: If no competitors, avg returns None. Handle that.
    avg_score = session.exec(
        select(func.avg(Competitor.score))
        .join(Project)
        .where(Project.user_id == current_user.id)
    ).one()
    
    average_threat_score = float(avg_score) if avg_score is not None else 0.0

    # 4. Timeline Data (Last 30 days)
    # Fetch events and aggregate in Python to be DB-dialect neutral for dates
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    events = session.exec(
        select(Event.timestamp)
        .join(Competitor)
        .join(Project)
        .where(Project.user_id == current_user.id)
        .where(Event.timestamp >= cutoff_date)
        .order_by(Event.timestamp)
    ).all()

    # Aggregate
    date_counts: Dict[str, int] = {}
    
    # Initialize last 30 days with 0 to show gaps (optional but good for charts)
    for i in range(30):
        d = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        date_counts[d] = 0
        
    for timestamp in events:
        date_str = timestamp.strftime("%Y-%m-%d")
        if date_str in date_counts:
            date_counts[date_str] += 1
        else:
             # Just in case there's a slight drift or it's today
             date_counts[date_str] = date_counts.get(date_str, 0) + 1

    # Convert to list and sort
    timeline_data = [
        TimelinePoint(date=d, count=c) 
        for d, c in date_counts.items()
    ]
    # Sort by date
    timeline_data.sort(key=lambda x: x.date)

    return DashboardStats(
        total_competitors=total_competitors,
        breakthrough_signals_count=breakthrough_signals_count,
        average_threat_score=round(average_threat_score, 1),
        timeline_data=timeline_data
    )
