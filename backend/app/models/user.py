import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .project import Project
    from .notification import NotificationSettings

class PlanType(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ULTIMATE = "ultimate"

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    plan_type: PlanType = Field(default=PlanType.GROWTH)
    trial_start_date: Optional[datetime] = Field(default=None)
    is_paid: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    projects: List["Project"] = Relationship(back_populates="user")
    notification_settings: List["NotificationSettings"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: uuid.UUID
    email: str
    plan_type: PlanType
    is_verified: bool
    created_at: datetime
    updated_at: datetime
