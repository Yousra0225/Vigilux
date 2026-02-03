import logging
import json
from typing import List, Optional
from sqlmodel import Session, select

from app.models.event import Event
from app.models.user import User, PlanType
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
        # Fetch user to check plan
        user = session.get(User, user_id)
        if not user:
            logger.error(f"User {user_id} not found for notification dispatch")
            return

        # Get user's notification settings
        settings = NotificationService.get_user_notification_settings(session, user_id)

        # Check if event has a score
        if event.score is None:
            return

        # Find matching notification channels
        for setting in settings:
            if setting.enabled and event.score >= setting.min_score:
                # Plan Tier Restrictions
                if setting.channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP]:
                    if user.plan_type != PlanType.ULTIMATE:
                        logger.warning(
                            f"Blocking {setting.channel} notification for user {user.email}. "
                            f"Plan {user.plan_type} does not support this channel."
                        )
                        continue
                
                NotificationService._send_notification(
                    setting.channel, 
                    event, 
                    event.score, 
                    setting.destination
                )

    @staticmethod
    def _send_notification(
        channel: NotificationChannel, 
        event: Event, 
        score: float, 
        destination: Optional[str] = None
    ) -> None:
        """
        Send a notification through the specified channel.
        Implements stubs and mock integrations.
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

        content = (
            f"Event detected! Type: {event.type.value}, Score: {score:.0f}/100 - {event.description}"
        )
        
        message = f"[NOTIF][{channel_str}] [{urgency}] {content}"

        # Mock Channel Integrations
        if channel == NotificationChannel.WEBHOOK and destination:
            NotificationService._mock_webhook_call(destination, event, score, urgency)
        elif channel in [NotificationChannel.SLACK, NotificationChannel.DISCORD] and destination:
            NotificationService._mock_social_dispatch(channel_str, destination, content, urgency)
        elif channel in [NotificationChannel.SMS, NotificationChannel.WHATSAPP] and destination:
            NotificationService._mock_mobile_dispatch(channel_str, destination, content, urgency)
        elif channel == NotificationChannel.EMAIL and destination:
            NotificationService._mock_email_dispatch(destination, content, urgency)

        logger.info(message)
        print(message)

    @staticmethod
    def _mock_webhook_call(url: str, event: Event, score: float, urgency: str) -> None:
        payload = {
            "event_id": str(event.id),
            "type": event.type.value,
            "description": event.description,
            "score": score,
            "urgency": urgency,
            "timestamp": event.timestamp.isoformat()
        }
        logger.info(f"MOCK WEBHOOK: Dispatching to {url} with payload: {json.dumps(payload)}")

    @staticmethod
    def _mock_social_dispatch(channel: str, webhook_url: str, content: str, urgency: str) -> None:
        logger.info(f"MOCK {channel}: Sending to {webhook_url} | Urgency: {urgency} | Content: {content}")

    @staticmethod
    def _mock_mobile_dispatch(channel: str, phone: str, content: str, urgency: str) -> None:
        logger.info(f"MOCK {channel}: Sending to {phone} | Urgency: {urgency} | Content: {content}")

    @staticmethod
    def _mock_email_dispatch(email: str, content: str, urgency: str) -> None:
        logger.info(f"MOCK EMAIL: Sending to {email} | Urgency: {urgency} | Content: {content}")

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
