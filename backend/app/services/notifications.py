import logging
from typing import Optional
from sqlmodel import Session, select
from app.models.event import Event
from app.models.notification import NotificationSettings, NotificationChannel
from app.models.competitor import Competitor
from app.models.project import Project
from app.models.user import User, PlanType

logger = logging.getLogger(__name__)

# Ultimate-only channels
ULTIMATE_ONLY_CHANNELS = {NotificationChannel.WHATSAPP}

# Score normalization factor (event scores are 1-10, thresholds are 0-100)
SCORE_NORMALIZATION_FACTOR = 10


def dispatch_notification(event: Event, db: Session):
    """
    Centralize notification logic to route alerts to the correct channels based on user
    preferences and event scores.
    """
    # 1. Retrieve the user owner of the competitor/project
    competitor = db.get(Competitor, event.competitor_id)
    if not competitor:
        logger.warning(f"Competitor {event.competitor_id} not found for event {event.id}")
        return

    project = db.get(Project, competitor.project_id)
    if not project:
        logger.warning(f"Project {competitor.project_id} not found for competitor {competitor.id}")
        return

    user_id = project.user_id
    user = db.get(User, user_id)
    if not user:
        logger.warning(f"User {user_id} not found for project {project.id}")
        return

    # 2. Retrieve notification preferences for the user
    statement = select(NotificationSettings).where(
        NotificationSettings.user_id == user_id,
        NotificationSettings.enabled == True
    )
    settings = db.exec(statement).all()

    if not settings:
        logger.debug(f"No enabled notification settings found for user {user_id}")
        return

    # 3. Normalize event score to match threshold scale (0-100)
    normalized_score = event.score * SCORE_NORMALIZATION_FACTOR

    # 4. For each enabled channel, verify threshold and plan restrictions
    for setting in settings:
        # Check Ultimate-only restriction
        if setting.channel in ULTIMATE_ONLY_CHANNELS and user.plan_type != PlanType.ULTIMATE:
            logger.warning(
                f"🚫 [RESTRICTION] User {user.email} (plan: {user.plan_type.value}) "
                f"attempted to use {setting.channel.value} channel. "
                f"Channel is restricted to ULTIMATE plan users only."
            )
            continue

        # Compare normalized score with threshold
        if normalized_score >= setting.min_score:
            _dispatch_to_provider(setting.channel, event, user, normalized_score)
        else:
            logger.debug(
                f"Event {event.id} normalized score {normalized_score} "
                f"below threshold {setting.min_score} "
                f"for channel {setting.channel.value}"
            )


def _dispatch_to_provider(channel: NotificationChannel, event: Event, user: User, normalized_score: int):
    """
    Route notification to the appropriate provider based on channel type.
    """
    if channel == NotificationChannel.EMAIL:
        send_email_notification(user, event, normalized_score)
    elif channel == NotificationChannel.SLACK:
        send_slack_notification(user, event, normalized_score)
    elif channel == NotificationChannel.DISCORD:
        send_discord_notification(user, event, normalized_score)
    elif channel == NotificationChannel.WHATSAPP:
        send_whatsapp_notification(user, event, normalized_score)
    else:
        logger.warning(f"Unknown notification channel: {channel}")


def send_email_notification(user: User, event: Event, normalized_score: int):
    """
    Mock Email provider - logs notification details for email channel.
    """
    log_msg = (
        f"📧 [EMAIL PROVIDER] Sending email notification\n"
        f"  ┌─ Target: {user.email}\n"
        f"  ├─ Event ID: {event.id}\n"
        f"  ├─ Competitor ID: {event.competitor_id}\n"
        f"  ├─ Event Type: {event.event_type}\n"
        f"  ├─ Raw Score: {event.score}/10\n"
        f"  ├─ Normalized Score: {normalized_score}/100\n"
        f"  └─ Timestamp: {event.timestamp}"
    )
    print(log_msg)
    logger.info(log_msg)


def send_slack_notification(user: User, event: Event, normalized_score: int):
    """
    Mock Slack provider - logs notification details for Slack channel.
    In production, this would send to user's configured Slack webhook URL.
    """
    log_msg = (
        f"💬 [SLACK PROVIDER] Sending Slack notification\n"
        f"  ┌─ Target User: {user.email}\n"
        f"  ├─ Webhook: [User's configured Slack webhook]\n"
        f"  ├─ Event ID: {event.id}\n"
        f"  ├─ Competitor ID: {event.competitor_id}\n"
        f"  ├─ Event Type: {event.event_type}\n"
        f"  ├─ Raw Score: {event.score}/10\n"
        f"  ├─ Normalized Score: {normalized_score}/100\n"
        f"  └─ Timestamp: {event.timestamp}"
    )
    print(log_msg)
    logger.info(log_msg)


def send_discord_notification(user: User, event: Event, normalized_score: int):
    """
    Mock Discord provider - logs notification details for Discord channel.
    In production, this would send to user's configured Discord webhook URL.
    """
    log_msg = (
        f"🎮 [DISCORD PROVIDER] Sending Discord notification\n"
        f"  ┌─ Target User: {user.email}\n"
        f"  ├─ Webhook: [User's configured Discord webhook]\n"
        f"  ├─ Event ID: {event.id}\n"
        f"  ├─ Competitor ID: {event.competitor_id}\n"
        f"  ├─ Event Type: {event.event_type}\n"
        f"  ├─ Raw Score: {event.score}/10\n"
        f"  ├─ Normalized Score: {normalized_score}/100\n"
        f"  └─ Timestamp: {event.timestamp}"
    )
    print(log_msg)
    logger.info(log_msg)


def send_whatsapp_notification(user: User, event: Event, normalized_score: int):
    """
    Mock WhatsApp provider - logs notification details for WhatsApp channel.
    In production, this would send to user's configured WhatsApp phone number.
    ULTIMATE PLAN ONLY - enforced in dispatch_notification().
    """
    log_msg = (
        f"📱 [WHATSAPP PROVIDER] Sending WhatsApp notification\n"
        f"  ┌─ Target User: {user.email}\n"
        f"  ├─ Phone: [User's configured WhatsApp number]\n"
        f"  ├─ Plan: {user.plan_type.value} (Ultimate verified)\n"
        f"  ├─ Event ID: {event.id}\n"
        f"  ├─ Competitor ID: {event.competitor_id}\n"
        f"  ├─ Event Type: {event.event_type}\n"
        f"  ├─ Raw Score: {event.score}/10\n"
        f"  ├─ Normalized Score: {normalized_score}/100\n"
        f"  └─ Timestamp: {event.timestamp}"
    )
    print(log_msg)
    logger.info(log_msg)


def notify_subscribers(event: Event, db: Session):
    """
    Integration point called after an event is created or scored.
    """
    dispatch_notification(event, db)
