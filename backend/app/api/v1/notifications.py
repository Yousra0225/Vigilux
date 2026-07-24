from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.notification_setting import NotificationChannel, NotificationSetting
from app.models.user import User
from app.schemas.notification import NotificationSettingRead, NotificationSettingUpdate

router = APIRouter()


@router.get("/users/me/notifications", response_model=list[NotificationSettingRead])
def get_notification_settings(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[NotificationSetting]:
    """
    Get all notification settings for the current user.
    """
    statement = select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    settings = session.exec(statement).all()
    return settings


@router.patch("/users/me/notifications/{channel}", response_model=NotificationSettingRead)
def update_notification_setting(
    channel: NotificationChannel,
    setting_update: NotificationSettingUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NotificationSetting:
    """
    Update a specific notification channel setting for the current user.
    """
    statement = select(NotificationSetting).where(
        NotificationSetting.user_id == current_user.id,
        NotificationSetting.channel == channel
    )
    setting = session.exec(statement).first()

    if not setting:
        raise HTTPException(
            status_code=404,
            detail=f"Notification setting for channel '{channel}' not found"
        )

    # Update only provided fields
    if setting_update.min_score is not None:
        setting.min_score = setting_update.min_score
    if setting_update.enabled is not None:
        setting.enabled = setting_update.enabled

    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


@router.post("/users/me/notifications/reset", response_model=list[NotificationSettingRead])
def reset_notification_settings(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[NotificationSetting]:
    """
    Reset notification settings to defaults.
    """
    # Delete existing settings
    statement = select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    existing_settings = session.exec(statement).all()
    for setting in existing_settings:
        session.delete(setting)

    # Create default settings
    default_settings = [
        NotificationSetting(
            user_id=current_user.id,
            channel=NotificationChannel.EMAIL,
            min_score=70,
            enabled=True
        ),
        NotificationSetting(
            user_id=current_user.id,
            channel=NotificationChannel.SMS,
            min_score=85,
            enabled=False
        ),
        NotificationSetting(
            user_id=current_user.id,
            channel=NotificationChannel.WEBHOOK,
            min_score=75,
            enabled=False
        ),
        NotificationSetting(
            user_id=current_user.id,
            channel=NotificationChannel.IN_APP,
            min_score=60,
            enabled=True
        ),
    ]

    for setting in default_settings:
        session.add(setting)

    session.commit()
    for setting in default_settings:
        session.refresh(setting)

    return default_settings
