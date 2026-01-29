import uuid
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .project import Project

class PlanType(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ULTIMATE = "ultimate"

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    plan_type: PlanType = Field(default=PlanType.STARTER, nullable=False)
    trial_start_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    
    projects: List["Project"] = Relationship(back_populates="user")
