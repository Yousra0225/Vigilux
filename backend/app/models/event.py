import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .competitor import Competitor

class Event(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    competitor_id: uuid.UUID = Field(foreign_key="competitor.id", nullable=False)
    type: str = Field(nullable=False)
    description: str = Field(nullable=False)
    score: Optional[float] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    competitor: "Competitor" = Relationship(back_populates="events")
