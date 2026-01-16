import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.notification import (
    NotificationSettings,
    NotificationSettingsCreate,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    NotificationChannel,
)
from app.models.user import User

router = APIRouter()


def _get_or_create_default_settings(session: Session, user_id: uuid.UUID) -> NotificationSettings:
    """
    Get existing notification settings for user, or create defaults if none exist.
    Returns the settings object.
    """
    settings = session.exec(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == user_id)
        .where(NotificationSettings.channel == NotificationChannel.EMAIL)
    ).first()

    if not settings:
        settings = NotificationSettings(
            user_id=user_id,
            channel=NotificationChannel.EMAIL,
            min_score=50,
            enabled=True,
        )
        session.add(settings)
        session.commit()
        session.refresh(settings)

    return settings


@router.get("/me/notifications", response_model=List[NotificationSettingsRead])
def read_notification_settings(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[NotificationSettings]:
    """
    Retrieve all notification settings for the current user.
    Creates default settings if none exist.
    """
    settings = session.exec(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == current_user.id)
    ).all()

    if not settings:
        # Create default settings on first access
        default_settings = _get_or_create_default_settings(session, current_user.id)
        return [default_settings]

    return settings


@router.post("/me/notifications", response_model=NotificationSettingsRead)
def create_notification_setting(
    setting_in: NotificationSettingsCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NotificationSettings:
    """
    Create a new notification setting for the current user.
    """
    # Check if setting already exists for this channel
    existing = session.exec(
        select(NotificationSettings)
        .where(NotificationSettings.user_id == current_user.id)
        .where(NotificationSettings.channel == setting_in.channel)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Notification settings for channel '{setting_in.channel.value}' already exist. Use PATCH to update.",
        )

    setting = NotificationSettings(
        user_id=current_user.id,
        channel=setting_in.channel,
        min_score=setting_in.min_score,
        enabled=setting_in.enabled,
    )
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


@router.patch("/me/notifications/{setting_id}", response_model=NotificationSettingsRead)
def update_notification_setting(
    setting_id: uuid.UUID,
    setting_in: NotificationSettingsUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> NotificationSettings:
    """
    Update a specific notification setting for the current user.
    """
    setting = session.get(NotificationSettings, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Notification setting not found")

    # Verify ownership
    if setting.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = setting_in.model_dump(exclude_unset=True)
    setting.sqlmodel_update(update_data)
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting


@router.delete("/me/notifications/{setting_id}")
def delete_notification_setting(
    setting_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """
    Delete a specific notification setting for the current user.
    """
    setting = session.get(NotificationSettings, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Notification setting not found")

    # Verify ownership
    if setting.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(setting)
    session.commit()
    return {"ok": True}
