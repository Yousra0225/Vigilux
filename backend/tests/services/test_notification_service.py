import sys
import os
import uuid
from datetime import datetime, timedelta, timezone

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlmodel import Session, SQLModel, create_engine, StaticPool
from app.models.user import User, PlanType
from app.models.project import Project
from app.models.competitor import Competitor
from app.models.event import Event, EventType
from app.models.notification import NotificationSettings, NotificationChannel
from app.services.notifications import notify_subscribers
from app.core.security import get_password_hash

# Setup Test DB (In-memory)
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def print_test_header(test_name: str):
    print(f"\n{'=' * 60}")
    print(f"  TEST: {test_name}")
    print('=' * 60)


def test_basic_provider_dispatch():
    """
    Test 1: Basic provider dispatch with score normalization.
    - Email threshold: 50 (event score 7 => normalized 70, should trigger)
    - Slack threshold: 90 (event score 7 => normalized 70, should NOT trigger)
    - Discord threshold: 30 (event score 7 => normalized 70, should trigger)
    - Discord disabled: should NOT trigger
    """
    print_test_header("Basic Provider Dispatch with Score Normalization")
    create_db_and_tables()

    with Session(engine) as session:
        # 1. Setup Data
        user = User(
            email="test_notif@example.com",
            hashed_password=get_password_hash("password"),
            plan_type=PlanType.GROWTH,
            is_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        project = Project(
            user_id=user.id,
            url="https://test.com",
            description="Test project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        competitor = Competitor(
            project_id=project.id,
            name="Test Competitor",
            url="https://comp.com"
        )
        session.add(competitor)
        session.commit()
        session.refresh(competitor)

        # 2. Setup Notification Settings (using 0-100 scale)
        # Setting 1: Email, min_score 50, enabled -> SHOULD TRIGGER (70 >= 50)
        setting_email = NotificationSettings(
            user_id=user.id,
            channel=NotificationChannel.EMAIL,
            min_score=50,
            enabled=True
        )
        # Setting 2: Slack, min_score 90, enabled -> SHOULD NOT TRIGGER (70 < 90)
        setting_slack = NotificationSettings(
            user_id=user.id,
            channel=NotificationChannel.SLACK,
            min_score=90,
            enabled=True
        )
        # Setting 3: Discord, min_score 30, enabled -> SHOULD TRIGGER (70 >= 30)
        setting_discord = NotificationSettings(
            user_id=user.id,
            channel=NotificationChannel.DISCORD,
            min_score=30,
            enabled=True
        )
        session.add(setting_email)
        session.add(setting_slack)
        session.add(setting_discord)
        session.commit()

        # 3. Create an event with score 7 (normalized to 70)
        event = Event(
            competitor_id=competitor.id,
            event_type=EventType.PRICE,
            description="Price dropped!",
            score=7
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        # 4. Trigger notification
        print("\nExpected: Email and Discord notifications, NOT Slack\n")
        notify_subscribers(event, session)


def test_ultimate_plan_restriction():
    """
    Test 2: Ultimate plan restriction for WhatsApp.
    - Growth user with WhatsApp enabled: should be BLOCKED with warning
    - Ultimate user with WhatsApp enabled: should work
    """
    print_test_header("Ultimate Plan Restriction for WhatsApp")
    create_db_and_tables()

    with Session(engine) as session:
        # 1. Setup Growth user (should be BLOCKED from WhatsApp)
        growth_user = User(
            email="growth@example.com",
            hashed_password=get_password_hash("password"),
            plan_type=PlanType.GROWTH,
            is_verified=True
        )
        session.add(growth_user)
        session.commit()
        session.refresh(growth_user)

        project = Project(
            user_id=growth_user.id,
            url="https://test.com",
            description="Test project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        competitor = Competitor(
            project_id=project.id,
            name="Test Competitor",
            url="https://comp.com"
        )
        session.add(competitor)
        session.commit()
        session.refresh(competitor)

        # Enable WhatsApp for Growth user (should be blocked)
        setting_whatsapp_growth = NotificationSettings(
            user_id=growth_user.id,
            channel=NotificationChannel.WHATSAPP,
            min_score=50,
            enabled=True
        )
        session.add(setting_whatsapp_growth)
        session.commit()

        # Create event
        event = Event(
            competitor_id=competitor.id,
            event_type=EventType.PRICE,
            description="Price dropped!",
            score=8  # normalized to 80
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        print("\nExpected: RESTRICTION warning for Growth user\n")
        notify_subscribers(event, session)

    # Now test Ultimate user (should work)
    with Session(engine) as session:
        create_db_and_tables()

        # 2. Setup Ultimate user (should get WhatsApp notification)
        ultimate_user = User(
            email="ultimate@example.com",
            hashed_password=get_password_hash("password"),
            plan_type=PlanType.ULTIMATE,
            is_verified=True
        )
        session.add(ultimate_user)
        session.commit()
        session.refresh(ultimate_user)

        project = Project(
            user_id=ultimate_user.id,
            url="https://test.com",
            description="Test project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        competitor = Competitor(
            project_id=project.id,
            name="Test Competitor",
            url="https://comp.com"
        )
        session.add(competitor)
        session.commit()
        session.refresh(competitor)

        # Enable WhatsApp for Ultimate user (should work)
        setting_whatsapp_ultimate = NotificationSettings(
            user_id=ultimate_user.id,
            channel=NotificationChannel.WHATSAPP,
            min_score=50,
            enabled=True
        )
        session.add(setting_whatsapp_ultimate)
        session.commit()

        # Create event
        event = Event(
            competitor_id=competitor.id,
            event_type=EventType.PRICE,
            description="Price dropped!",
            score=9  # normalized to 90
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        print("\nExpected: WhatsApp notification for Ultimate user\n")
        notify_subscribers(event, session)


def test_all_channels_ultimate():
    """
    Test 3: All channels working for Ultimate user.
    """
    print_test_header("All Channels for Ultimate User")
    create_db_and_tables()

    with Session(engine) as session:
        user = User(
            email="ultimate_all@example.com",
            hashed_password=get_password_hash("password"),
            plan_type=PlanType.ULTIMATE,
            is_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        project = Project(
            user_id=user.id,
            url="https://test.com",
            description="Test project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)

        competitor = Competitor(
            project_id=project.id,
            name="Test Competitor",
            url="https://comp.com"
        )
        session.add(competitor)
        session.commit()
        session.refresh(competitor)

        # Enable all channels
        for channel in NotificationChannel:
            setting = NotificationSettings(
                user_id=user.id,
                channel=channel,
                min_score=30,  # Low threshold to ensure all trigger
                enabled=True
            )
            session.add(setting)
        session.commit()

        # Create event with high score
        event = Event(
            competitor_id=competitor.id,
            event_type=EventType.FEATURE,
            description="New feature launched!",
            score=10  # normalized to 100
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        print("\nExpected: All 4 channel notifications (Email, Slack, Discord, WhatsApp)\n")
        notify_subscribers(event, session)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  NOTIFICATION SERVICE VERIFICATION TESTS")
    print("  Task 5.3 - Multi-Channel Integration (Mock)")
    print("=" * 60)

    test_basic_provider_dispatch()
    test_ultimate_plan_restriction()
    test_all_channels_ultimate()

    print("\n" + "=" * 60)
    print("  ALL TESTS COMPLETE")
    print("=" * 60 + "\n")
