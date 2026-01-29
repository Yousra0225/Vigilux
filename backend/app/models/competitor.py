import uuid
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .project import Project
    from .event import Event

class CompetitorStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class Competitor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False)
    name: str = Field(nullable=False)
    url: str = Field(nullable=False)
    status: CompetitorStatus = Field(default=CompetitorStatus.ACTIVE, nullable=False)
    score: Optional[float] = Field(default=None)

    project: "Project" = Relationship(back_populates="competitors")
    events: List["Event"] = Relationship(back_populates="competitor")
