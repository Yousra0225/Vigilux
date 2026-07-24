import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

import uuid6
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .competitor import Competitor

import sqlalchemy as sa


class EventType(str, Enum):
    PRICE = "PRICE"
    FEATURE = "FEATURE"
    HEALTH = "HEALTH"
    NEW_ENTRANT = "NEW_ENTRANT"

    def __str__(self):
        return self.value

class Event(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    competitor_id: uuid.UUID = Field(foreign_key="competitor.id", nullable=False)
    type: EventType = Field(
        sa_column=sa.Column(sa.Enum(EventType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    )
    description: str = Field(nullable=False)
    score: float | None = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    competitor: "Competitor" = Relationship(back_populates="events")