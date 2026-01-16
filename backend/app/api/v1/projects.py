import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.project import Project
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Project])
def read_projects(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[Project]:
    """
    Retrieve projects for the current user.
    """
    projects = session.exec(
        select(Project)
        .where(Project.user_id == current_user.id)
    ).all()
    return projects
