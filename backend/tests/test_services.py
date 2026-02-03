from datetime import datetime, timedelta
from app.services.quota import QuotaService
from app.services.scoring import ScoringService
from app.services.notifications import NotificationService
from app.models.user import User, PlanType
from app.models.event import Event, EventType
from app.models.notification_setting import NotificationSetting, NotificationChannel

def test_quota_service_effective_plan():
    # Test Growth plan not expired
    user_growth = User(
        email="growth@test.com",
        hashed_password="...",
        plan_type=PlanType.GROWTH,
        trial_start_date=datetime.utcnow()
    )
    assert QuotaService.get_effective_plan(user_growth) == PlanType.GROWTH

    # Test Growth plan expired
    user_expired = User(
        email="expired@test.com",
        hashed_password="...",
        plan_type=PlanType.GROWTH,
        trial_start_date=datetime.utcnow() - timedelta(days=8)
    )
    assert QuotaService.get_effective_plan(user_expired) == PlanType.STARTER

    # Test Ultimate plan
    user_ultimate = User(
        email="ultimate@test.com",
        hashed_password="...",
        plan_type=PlanType.ULTIMATE,
        trial_start_date=None
    )
    assert QuotaService.get_effective_plan(user_ultimate) == PlanType.ULTIMATE

def test_quota_service_can_add_competitor():
    user_starter = User(email="s@t.com", hashed_password=".", plan_type=PlanType.STARTER)
    assert QuotaService.can_add_competitor(user_starter, 2) is True
    assert QuotaService.can_add_competitor(user_starter, 3) is False

    user_ultimate = User(email="u@t.com", hashed_password=".", plan_type=PlanType.ULTIMATE)
    assert QuotaService.can_add_competitor(user_ultimate, 49) is True
    assert QuotaService.can_add_competitor(user_ultimate, 50) is False

def test_scoring_service():
    score = ScoringService.calculate_score(EventType.PRICE, "Significant price decrease")
    assert 1 <= score <= 100
    
    # Check breakthrough categorization
    event = Event(type=EventType.PRICE, description="Big deal", score=85, competitor_id=None)
    analysis = ScoringService.analyze_event(event)
    assert analysis["is_breakthrough"] is True
    assert analysis["category"] == "Major Price Shift"

    event_low = Event(type=EventType.FEATURE, description="Small update", score=30, competitor_id=None)
    analysis_low = ScoringService.analyze_event(event_low)
    assert analysis_low["is_breakthrough"] is False
    assert analysis_low["category"] == "Standard Update"

def test_notification_service_plan_check(session, caplog):
    import uuid
    user_id = uuid.uuid4()
    user_starter = User(
        id=user_id,
        email="starter@test.com",
        hashed_password=".",
        plan_type=PlanType.STARTER
    )
    session.add(user_starter)
    session.commit()

    # Create an event
    event = Event(
        id=uuid.uuid4(),
        type=EventType.HEALTH,
        description="CEO Resigned",
        score=95,
        competitor_id=uuid.uuid4(),
        timestamp=datetime.utcnow()
    )

    # Enable SMS (which is restricted)
    setting = NotificationSetting(
        user_id=user_id,
        channel=NotificationChannel.SMS,
        min_score=70,
        enabled=True,
        destination="+123456789"
    )
    session.add(setting)
    session.commit()

    # Dispatch should block SMS for Starter
    NotificationService.dispatch_notification(session, user_id, event)
    
    assert "Blocking sms notification" in caplog.text
