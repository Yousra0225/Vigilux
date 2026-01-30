import logging
from typing import List
from sqlmodel import Session, select

from app.models.event import Event
from app.models.notification_setting import NotificationSetting, NotificationChannel

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for dispatching notifications based on user preferences and event scores.
    """

    @staticmethod
    def get_user_notification_settings(session: Session, user_id: str) -> List[NotificationSetting]:
        """
        Get all notification settings for a user.
        """
        statement = select(NotificationSetting).where(NotificationSetting.user_id == user_id)
        return session.exec(statement).all()

    @staticmethod
    def dispatch_notification(session: Session, user_id: str, event: Event) -> None:
        """
        Dispatch a notification for an event based on user preferences.

        Args:
            session: Database session
            user_id: ID of the user to notify
            event: The event to potentially notify about
        """
        # Get user's notification settings
        settings = NotificationService.get_user_notification_settings(session, user_id)

        # Check if event has a score
        if event.score is None:
            return

        # Find matching notification channels
        for setting in settings:
            if setting.enabled and event.score >= setting.min_score:
                NotificationService._send_notification(setting.channel, event, event.score)

    @staticmethod
    def _send_notification(channel: NotificationChannel, event: Event, score: float) -> None:
        """
        Send a notification through the specified channel.
        For now, this simulates sending by logging to console.
        """
        channel_str = channel.value.upper()

        # Determine notification category based on score
        if score >= 90:
            urgency = "CRITICAL"
        elif score >= 75:
            urgency = "HIGH"
        elif score >= 60:
            urgency = "MEDIUM"
        else:
            urgency = "LOW"

        message = (
            f"[NOTIF][{channel_str}] [{urgency}] Event detected! "
            f"Type: {event.type.value}, Score: {score:.0f}/100 - {event.description}"
        )

        logger.info(message)

        # Also print to console for immediate visibility
        print(message)

    @staticmethod
    def dispatch_bulk_notifications(session: Session, user_ids: List[str], event: Event) -> None:
        """
        Dispatch notifications to multiple users for a single event.

        Args:
            session: Database session
            user_ids: List of user IDs to notify
            event: The event to potentially notify about
        """
        for user_id in user_ids:
            NotificationService.dispatch_notification(session, user_id, event)
