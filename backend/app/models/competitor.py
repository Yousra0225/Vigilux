import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .project import Project
    from .event import Event

class TrackingStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Competitor(SQLModel, table=True):
    __tablename__ = "competitors"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="projects.id", ondelete="CASCADE")
    name: str = Field(max_length=255)
    url: Optional[str] = Field(default=None, max_length=2048)
    score: int = Field(default=0)
    tracking_status: TrackingStatus = Field(default=TrackingStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    project: "Project" = Relationship(back_populates="competitors")
    events: List["Event"] = Relationship(back_populates="competitor")


class CompetitorCreate(SQLModel):
    project_id: uuid.UUID
    name: str = Field(max_length=255)
    url: Optional[str] = Field(default=None, max_length=2048)


class CompetitorRead(SQLModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    url: Optional[str]
    score: int
    tracking_status: TrackingStatus
    created_at: datetime


class CompetitorUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=255)
    url: Optional[str] = Field(default=None, max_length=2048)
    tracking_status: Optional[TrackingStatus] = None
