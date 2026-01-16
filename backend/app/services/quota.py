from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.models.user import User, PlanType
from app.models.competitor import Competitor
from app.models.project import Project

# --- Pricing Constants ---
PLAN_PRICES = {
    PlanType.STARTER: 0,
    PlanType.GROWTH: 49,
    PlanType.ULTIMATE: 199,
}

PLAN_COMPETITOR_QUOTAS = {
    PlanType.STARTER: 3,
    PlanType.GROWTH: 15,
    PlanType.ULTIMATE: 50,
}

TRIAL_DURATION_DAYS = 7


def get_effective_plan(user: User) -> PlanType:
    """
    Determines the effective plan for a user.
    
    Logic:
    - If user is on GROWTH plan:
        - Check if trial has expired (> 7 days since trial_start_date).
        - Check if user has NOT paid (is_paid is False).
        - If both true, effective plan is STARTER.
    - Otherwise, return the user's actual plan_type.
    """
    if user.plan_type == PlanType.GROWTH:
        if user.is_paid:
            return PlanType.GROWTH
            
        if user.trial_start_date:
            # Calculate trial end date
            trial_end = user.trial_start_date + timedelta(days=TRIAL_DURATION_DAYS)
            if datetime.utcnow() > trial_end:
                return PlanType.STARTER
        
        # If no trial start date set, assuming trial hasn't started or handling as is. 
        # Or if within trial period.
        return PlanType.GROWTH
        
    return user.plan_type


def check_competitor_quota(user: User, db: Session) -> None:
    """
    Verifies if the user can add more competitors based on their effective plan.
    
    Raises HTTPException if quota is reached.
    """
    effective_plan = get_effective_plan(user)
    quota = PLAN_COMPETITOR_QUOTAS.get(effective_plan, 0)
    
    # Count current competitors across all user's projects
    # Join Project to filter by user_id
    statement = (
        select(func.count(Competitor.id))
        .join(Project)
        .where(Project.user_id == user.id)
    )
    current_count = db.exec(statement).one() or 0
    
    if current_count >= quota:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Competitor quota reached for {effective_plan.value} plan ({current_count}/{quota}). Upgrade to add more."
        )
