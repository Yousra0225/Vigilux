import uuid
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .project import Project
    from .notification_setting import NotificationSetting

import sqlalchemy as sa

class PlanType(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    ULTIMATE = "ultimate"

    def __str__(self):
        return self.value

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    plan_type: PlanType = Field(
        default=PlanType.STARTER, 
        sa_column=sa.Column(sa.Enum(PlanType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    )
    trial_start_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    
    projects: List["Project"] = Relationship(back_populates="user")
    notification_settings: List["NotificationSetting"] = Relationship(back_populates="user")
