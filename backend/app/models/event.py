import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .competitor import Competitor

class EventType(str, Enum):
    PRICE = "price"
    FEATURE = "feature"
    HEALTH = "health"
    NEW_ENTRANT = "new_entrant"

class Event(SQLModel, table=True):
    __tablename__ = "events"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    competitor_id: uuid.UUID = Field(foreign_key="competitors.id", ondelete="CASCADE")
    event_type: EventType
    description: str
    score: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    competitor: "Competitor" = Relationship(back_populates="events")
