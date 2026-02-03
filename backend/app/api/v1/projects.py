from typing import List, Any, Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.models.project import Project

router = APIRouter()

@router.get("/", response_model=List[Project])
def read_projects(
    *,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve projects.
    """
    statement = select(Project).where(Project.user_id == current_user.id).offset(skip).limit(limit)
    projects = session.exec(statement).all()
    return projects
