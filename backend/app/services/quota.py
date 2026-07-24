from datetime import UTC, datetime, timedelta

from app.models.user import PlanType, User

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
            if datetime.now(UTC) > expiration_date:
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

    @staticmethod
    def can_refresh_competitor(user: User, last_refresh: datetime | None = None) -> bool:
        """
        Check if user can refresh a competitor based on their plan.

        Starter: 1 refresh per 24 hours
        Growth: 10 refreshes per 24 hours
        Ultimate: No limit (basic throttle only - 1 per minute)

        Args:
            user: The user attempting to refresh
            last_refresh: Last time this competitor was refreshed (optional)

        Returns:
            True if refresh is allowed, False otherwise
        """
        effective_plan = QuotaService.get_effective_plan(user)

        # Ultimate users: no daily limit, just basic throttle (1 per minute)
        if effective_plan == PlanType.ULTIMATE:
            if last_refresh:
                time_since_last = datetime.now(UTC) - last_refresh
                # Allow refresh if at least 1 minute has passed
                return time_since_last >= timedelta(minutes=1)
            return True

        # Growth users: 10 per 24 hours
        if effective_plan == PlanType.GROWTH:
            if last_refresh:
                time_since_last = datetime.now(UTC) - last_refresh
                # Allow refresh if at least 2.4 hours has passed (24h / 10)
                return time_since_last >= timedelta(hours=2.4)
            return True

        # Starter users: 1 per 24 hours
        if effective_plan == PlanType.STARTER:
            if last_refresh:
                time_since_last = datetime.now(UTC) - last_refresh
                # Allow refresh if at least 24 hours have passed
                return time_since_last >= timedelta(hours=24)
            return True

        return True
