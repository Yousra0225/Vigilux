import uuid
from typing import List, Optional
from pydantic import BaseModel
from app.models.notification_setting import NotificationChannel


class NotificationSettingBase(BaseModel):
    channel: NotificationChannel
    min_score: int
    enabled: bool


class NotificationSettingCreate(NotificationSettingBase):
    pass


class NotificationSettingUpdate(BaseModel):
    min_score: Optional[int] = None
    enabled: Optional[bool] = None


class NotificationSettingRead(NotificationSettingBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class NotificationSettingsList(BaseModel):
    settings: List[NotificationSettingRead]
