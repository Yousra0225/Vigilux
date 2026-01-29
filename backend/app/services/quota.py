from datetime import datetime, timedelta
from typing import Optional

from app.models.user import User, PlanType

PLAN_LIMITS = {
    PlanType.STARTER: 3,
    PlanType.GROWTH: 15,
    PlanType.ULTIMATE: 50
}

TRIAL_DURATION_DAYS = 7

class QuotaService:
    @staticmethod
    def get_effective_plan(user: User) -> PlanType:
        """
        Determine the effective plan based on trial status.
        If Growth trial expired, revert to Starter (logic to be handled by caller or here?).
        For now, if trial expired, we report STARTER unless they upgraded.
        """
        if user.plan_type == PlanType.GROWTH and user.trial_start_date:
            expiration_date = user.trial_start_date + timedelta(days=TRIAL_DURATION_DAYS)
            if datetime.utcnow() > expiration_date:
                # Trial expired, effectively Starter
                return PlanType.STARTER
        
        return user.plan_type

    @staticmethod
    def get_competitor_limit(plan: PlanType) -> int:
        return PLAN_LIMITS.get(plan, 3)

    @staticmethod
    def can_add_competitor(user: User, current_count: int) -> bool:
        effective_plan = QuotaService.get_effective_plan(user)
        limit = QuotaService.get_competitor_limit(effective_plan)
        return current_count < limit
