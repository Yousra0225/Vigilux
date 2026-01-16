from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core import security
from app.core.db import get_session
from app.models.auth import Token
from app.models.user import User, UserCreate, UserRead, PlanType
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register_user(
    user_in: UserCreate,
    session: Session = Depends(get_session),
) -> User:
    """
    Create new user.
    """
    # Check if user exists
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        plan_type=PlanType.GROWTH,
        trial_start_date=datetime.now(timezone.utc),
        is_verified=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token_expires = None
    access_token = security.create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current user.
    """
    return current_user
