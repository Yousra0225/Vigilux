from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import get_session
from app.models.user import User
from app.models.notification_setting import NotificationSetting, NotificationChannel
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead, UserUpdate

from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Get current user.
    """
    return current_user

@router.patch("/me", response_model=UserRead)
def update_user_me(
    *,
    session: Annotated[Session, Depends(get_session)],
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Update own user.
    """
    if user_in.niche is not None:
        current_user.niche = user_in.niche
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/login", response_model=Token)
def login_access_token(
    session: Annotated[Session, Depends(get_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Case-insensitive email lookup
    statement = select(User).where(User.email == form_data.username.lower())
    user = session.exec(statement).first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=UserRead)
def register_user(
    user_in: UserCreate,
    session: Annotated[Session, Depends(get_session)]
) -> UserRead:
    """
    Create new user with default notification settings.
    """
    # Ensure email is stored in lowercase
    user_email = user_in.email.lower()
    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user = User(
        email=user_email,
        hashed_password=security.get_password_hash(user_in.password),
        is_verified=False
    )
    session.add(user)
    session.flush()  # Flush to get the user ID before creating notification settings

    # Create default notification settings
    default_settings = [
        NotificationSetting(
            user_id=user.id,
            channel=NotificationChannel.EMAIL,
            min_score=70,
            enabled=True
        ),
        NotificationSetting(
            user_id=user.id,
            channel=NotificationChannel.SMS,
            min_score=85,
            enabled=False
        ),
        NotificationSetting(
            user_id=user.id,
            channel=NotificationChannel.WEBHOOK,
            min_score=75,
            enabled=False
        ),
        NotificationSetting(
            user_id=user.id,
            channel=NotificationChannel.IN_APP,
            min_score=60,
            enabled=True
        ),
    ]

    for setting in default_settings:
        session.add(setting)

    session.commit()
    session.refresh(user)
    return user
