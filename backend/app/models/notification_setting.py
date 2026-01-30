import uuid
from enum import Enum
from typing import TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6
import sqlalchemy as sa

if TYPE_CHECKING:
    from .user import User


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"

    def __str__(self):
        return self.value


class NotificationSetting(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, index=True)
    channel: NotificationChannel = Field(
        sa_column=sa.Column(sa.Enum(NotificationChannel, values_callable=lambda x: [e.value for e in x]), nullable=False)
    )
    min_score: int = Field(default=70, nullable=False)
    enabled: bool = Field(default=True, nullable=False)

    user: "User" = Relationship(back_populates="notification_settings")
