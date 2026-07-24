import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

import uuid6
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .event import Event
    from .project import Project

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
    score: float | None = Field(default=None)
    last_scanned_at: datetime | None = Field(default=None, nullable=True)

    project: "Project" = Relationship(back_populates="competitors")
    events: list["Event"] = Relationship(back_populates="competitor")