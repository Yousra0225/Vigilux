import uuid

from pydantic import BaseModel

from app.models.notification_setting import NotificationChannel


class NotificationSettingBase(BaseModel):
    channel: NotificationChannel
    min_score: int
    enabled: bool
    destination: str | None = None


class NotificationSettingCreate(NotificationSettingBase):
    pass


class NotificationSettingUpdate(BaseModel):
    min_score: int | None = None
    enabled: bool | None = None
    destination: str | None = None


class NotificationSettingRead(NotificationSettingBase):
    id: uuid.UUID
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class NotificationSettingsList(BaseModel):
    settings: list[NotificationSettingRead]
