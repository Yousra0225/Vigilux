import uuid
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .project import Project
    from .event import Event

import sqlalchemy as sa

class TrackingStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

    def __str__(self):
        return self.value

class Competitor(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    project_id: uuid.UUID = Field(foreign_key="project.id", nullable=False)
    name: str = Field(nullable=False)
    url: str = Field(nullable=False)
    status: TrackingStatus = Field(
        default=TrackingStatus.ACTIVE, 
        sa_column=sa.Column(sa.Enum(TrackingStatus, values_callable=lambda x: [e.value for e in x]), nullable=False)
    )
    score: Optional[float] = Field(default=None)

    project: "Project" = Relationship(back_populates="competitors")
    events: List["Event"] = Relationship(back_populates="competitor")