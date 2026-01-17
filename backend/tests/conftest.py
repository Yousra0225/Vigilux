"""
Shared pytest fixtures for backend testing.

Provides database isolation and common test utilities.
"""

import uuid
from datetime import datetime, timezone
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, StaticPool

from app.main import app
from app.core.db import get_session
from app.models.user import User, PlanType
from app.models.project import Project
from app.models.competitor import Competitor
from app.models.event import Event, EventType
from app.models.notification import NotificationSettings, NotificationChannel
from app.core.security import get_password_hash, create_access_token


# In-memory SQLite database for isolated testing
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Creates a fresh database session for each test function.
    All tables are created at the start and dropped at the end.
    """
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    """
    Provides a TestClient with database session override.
    """
    def get_session_override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Creates a test user with Growth plan."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        plan_type=PlanType.GROWTH,
        trial_start_date=datetime.now(timezone.utc),
        is_verified=True,
        is_paid=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_starter(db_session: Session) -> User:
    """Creates a test user with Starter plan."""
    user = User(
        email="starter@example.com",
        hashed_password=get_password_hash("testpassword123"),
        plan_type=PlanType.STARTER,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_ultimate(db_session: Session) -> User:
    """Creates a test user with Ultimate plan."""
    user = User(
        email="ultimate@example.com",
        hashed_password=get_password_hash("testpassword123"),
        plan_type=PlanType.ULTIMATE,
        is_verified=True,
        is_paid=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_project(db_session: Session, test_user: User) -> Project:
    """Creates a test project for the test user."""
    project = Project(
        user_id=test_user.id,
        url="https://myproject.com",
        description="Test Project"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_competitor(db_session: Session, test_project: Project) -> Competitor:
    """Creates a test competitor for the test project."""
    competitor = Competitor(
        project_id=test_project.id,
        name="Test Competitor",
        url="https://competitor.com"
    )
    db_session.add(competitor)
    db_session.commit()
    db_session.refresh(competitor)
    return competitor


@pytest.fixture
def test_event(db_session: Session, test_competitor: Competitor) -> Event:
    """Creates a test event for the test competitor."""
    event = Event(
        competitor_id=test_competitor.id,
        event_type=EventType.PRICE,
        description="Test price change event",
        score=7
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Returns HTTP headers with Bearer token for the test user."""
    access_token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_starter(test_user_starter: User) -> dict:
    """Returns HTTP headers with Bearer token for Starter user."""
    access_token = create_access_token(subject=test_user_starter.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def auth_headers_ultimate(test_user_ultimate: User) -> dict:
    """Returns HTTP headers with Bearer token for Ultimate user."""
    access_token = create_access_token(subject=test_user_ultimate.id)
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def notification_settings(db_session: Session, test_user: User) -> list[NotificationSettings]:
    """Creates notification settings for the test user."""
    settings = [
        NotificationSettings(
            user_id=test_user.id,
            channel=NotificationChannel.EMAIL,
            min_score=50,
            enabled=True
        ),
        NotificationSettings(
            user_id=test_user.id,
            channel=NotificationChannel.SLACK,
            min_score=70,
            enabled=True
        ),
        NotificationSettings(
            user_id=test_user.id,
            channel=NotificationChannel.DISCORD,
            min_score=60,
            enabled=True
        ),
    ]
    for setting in settings:
        db_session.add(setting)
    db_session.commit()
    return settings
