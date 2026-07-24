from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.api.deps import get_current_user, get_session
from app.models.competitor import Competitor
from app.models.event import Event
from app.models.project import Project
from app.models.user import User
from app.schemas.dashboard import DashboardStats, EventCount

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """
    Get aggregated dashboard statistics.
    """
    # Base query for user's projects
    user_projects_subquery = select(Project.id).where(Project.user_id == current_user.id)
    
    # 1. Total Competitors
    total_competitors = session.exec(
        select(func.count(Competitor.id))
        .where(Competitor.project_id.in_(user_projects_subquery))
    ).one()

    # 2. Breakthroughs Today (Score > 70, timestamp >= today start)
    today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    
    breakthroughs_today = session.exec(
        select(func.count(Event.id))
        .join(Competitor)
        .where(Competitor.project_id.in_(user_projects_subquery))
        .where(Event.score > 70)
        .where(Event.timestamp >= today_start)
    ).one()

    # 3. Average Threat Score
    # Note: Competitor.score can be None.
    avg_score = session.exec(
        select(func.avg(Competitor.score))
        .where(Competitor.project_id.in_(user_projects_subquery))
    ).one()
    
    if avg_score is None:
        avg_score = 0.0

    # 4. Chart Data: Events per day for the last 30 days
    thirty_days_ago = today_start - timedelta(days=30)
    
    # Group by date.
    chart_query = (
        select(func.date(Event.timestamp).label("date"), func.count(Event.id).label("count"))
        .join(Competitor)
        .where(Competitor.project_id.in_(user_projects_subquery))
        .where(Event.timestamp >= thirty_days_ago)
        .group_by(func.date(Event.timestamp))
        .order_by(func.date(Event.timestamp))
    )
    
    results = session.exec(chart_query).all()
    
    chart_data = []
    for r_date, r_count in results:
        if isinstance(r_date, str):
            from datetime import date
            parsed_date = date.fromisoformat(r_date)
        else:
            parsed_date = r_date
        chart_data.append(EventCount(date=parsed_date, count=r_count))

    return DashboardStats(
        total_competitors=total_competitors,
        breakthroughs_today=breakthroughs_today,
        avg_threat_score=float(avg_score),
        chart_data=chart_data
    )
