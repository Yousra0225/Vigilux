import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum

if TYPE_CHECKING:
    from .user import User


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WHATSAPP = "whatsapp"


class NotificationSettings(SQLModel, table=True):
    __tablename__ = "notification_settings"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    channel: NotificationChannel = Field(default=NotificationChannel.EMAIL)
    min_score: int = Field(default=50, ge=0, le=100)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="notification_settings")


class NotificationSettingsCreate(SQLModel):
    channel: NotificationChannel
    min_score: int = Field(default=50, ge=0, le=100)
    enabled: bool = True


class NotificationSettingsRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    channel: NotificationChannel
    min_score: int
    enabled: bool
    created_at: datetime
    updated_at: datetime


class NotificationSettingsUpdate(SQLModel):
    channel: Optional[NotificationChannel] = None
    min_score: Optional[int] = Field(default=None, ge=0, le=100)
    enabled: Optional[bool] = None
