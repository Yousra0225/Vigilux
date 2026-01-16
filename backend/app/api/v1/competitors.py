import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.competitor import Competitor, CompetitorCreate, CompetitorRead, CompetitorUpdate
from app.models.user import User
from app.models.project import Project
from app.services.quota import check_competitor_quota

router = APIRouter()

@router.get("/", response_model=List[CompetitorRead])
def read_competitors(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: uuid.UUID = Query(..., description="Project ID to filter competitors by"),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> List[Competitor]:
    """
    Retrieve competitors for a specific project.
    """
    # Verify project belongs to user
    project = session.get(Project, project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    competitors = session.exec(
        select(Competitor)
        .where(Competitor.project_id == project_id)
        .offset(offset)
        .limit(limit)
    ).all()
    return competitors


@router.post("/", response_model=CompetitorRead)
def create_competitor(
    competitor_in: CompetitorCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Competitor:
    """
    Create a new competitor.
    Enforces quota limits based on user's plan.
    """
    # Verify project belongs to user
    project = session.get(Project, competitor_in.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check Quota
    check_competitor_quota(current_user, session)

    competitor = Competitor.model_validate(competitor_in)
    session.add(competitor)
    session.commit()
    session.refresh(competitor)
    return competitor


@router.patch("/{competitor_id}", response_model=CompetitorRead)
def update_competitor(
    competitor_id: uuid.UUID,
    competitor_in: CompetitorUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Competitor:
    """
    Update a competitor.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Verify ownership through project
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized")

    update_data = competitor_in.model_dump(exclude_unset=True)
    competitor.sqlmodel_update(update_data)
    session.add(competitor)
    session.commit()
    session.refresh(competitor)
    return competitor


@router.delete("/{competitor_id}")
def delete_competitor(
    competitor_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Delete a competitor.
    """
    competitor = session.get(Competitor, competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")

    # Verify ownership through project
    project = session.get(Project, competitor.project_id)
    if not project or project.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(competitor)
    session.commit()
    return {"ok": True}
