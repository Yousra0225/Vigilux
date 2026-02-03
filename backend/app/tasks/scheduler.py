import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from sqlmodel import select

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor, TrackingStatus
from app.models.project import Project
from app.models.user import User, PlanType
from app.tasks.base import BaseTask
from app.tasks.scraping import scrape_competitor_task

logger = logging.getLogger(__name__)


@celery_app.task(base=BaseTask, bind=True, name="app.tasks.scheduler.run_tiered_scheduler")
def run_tiered_scheduler(self) -> Dict[str, Any]:
    """
    Periodic task that triggers competitor scans based on user plan tier.

    Scheduling rules:
    - Ultimate users: Daily scans (trigger if last_scanned_at > 24 hours ago or None)
    - Growth users: Weekly scans (trigger if last_scanned_at > 7 days ago or None)
    - Starter users: Manual only (no automatic scans)

    This task is typically run by Celery Beat every hour to check and
    trigger scans for competitors that are due for refresh.

    Returns:
        Dictionary with summary of triggered tasks
    """
    logger.info("Running tiered scheduler - checking for competitors to scan")

    triggered_count = 0
    skipped_count = 0
    errors = []

    try:
        with next(get_session()) as session:
            # Efficient query: join Competitor -> Project -> User
            # Get all active competitors with their associated user's plan type
            statement = (
                select(Competitor, User)
                .join(Project, Competitor.project_id == Project.id)
                .join(User, Project.user_id == User.id)
                .where(Competitor.status == TrackingStatus.ACTIVE)
            )

            results = session.exec(statement).all()

            logger.info(f"Found {len(results)} active competitors to evaluate")

            for competitor, user in results:
                try:
                    # Get effective plan (handles trial expiration)
                    from app.services.quota import QuotaService
                    effective_plan = QuotaService.get_effective_plan(user)

                    # Starter users: manual refresh only
                    if effective_plan == PlanType.STARTER:
                        skipped_count += 1
                        continue

                    # Determine if scan is due based on plan
                    should_scan = False
                    reason = ""

                    if competitor.last_scanned_at is None:
                        # Never scanned - trigger for Growth/Ultimate
                        should_scan = True
                        reason = "never scanned"
                    else:
                        time_since_scan = datetime.utcnow() - competitor.last_scanned_at

                        if effective_plan == PlanType.ULTIMATE:
                            # Daily: trigger if > 24 hours
                            if time_since_scan >= timedelta(hours=24):
                                should_scan = True
                                reason = f"last scan {time_since_scan.days} days ago (Ultimate: daily)"
                        elif effective_plan == PlanType.GROWTH:
                            # Weekly: trigger if > 7 days
                            if time_since_scan >= timedelta(days=7):
                                should_scan = True
                                reason = f"last scan {time_since_scan.days} days ago (Growth: weekly)"

                    if should_scan:
                        logger.info(
                            f"Triggering scan for competitor {competitor.name} "
                            f"(user: {user.email}, plan: {effective_plan.value}, reason: {reason})"
                        )
                        # Trigger the async scrape task
                        scrape_competitor_task.delay(str(competitor.id))
                        triggered_count += 1
                    else:
                        skipped_count += 1

                except Exception as e:
                    logger.error(f"Error processing competitor {competitor.id}: {e}")
                    errors.append({
                        "competitor_id": str(competitor.id),
                        "error": str(e)
                    })

    except Exception as e:
        logger.error(f"Error in tiered scheduler: {e}")
        return {
            "success": False,
            "error": str(e),
            "triggered": 0,
            "skipped": 0
        }

    result = {
        "success": True,
        "triggered": triggered_count,
        "skipped": skipped_count,
        "errors": len(errors),
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info(
        f"Tiered scheduler completed: {triggered_count} triggered, "
        f"{skipped_count} skipped, {len(errors)} errors"
    )

    return result


@celery_app.task(base=BaseTask, bind=True, name="app.tasks.scheduler.trigger_project_scan")
def trigger_project_scan(self, project_id: str) -> Dict[str, Any]:
    """
    Trigger scans for all competitors in a specific project.

    This is useful for manual project-wide refresh operations.

    Args:
        project_id: UUID of the project

    Returns:
        Dictionary with results summary
    """
    logger.info(f"Triggering project-wide scan for: {project_id}")

    try:
        proj_id = uuid.UUID(project_id)
    except ValueError:
        logger.error(f"Invalid project ID: {project_id}")
        return {"success": False, "error": "Invalid project ID"}

    with next(get_session()) as session:
        project = session.get(Project, proj_id)
        if not project:
            logger.warning(f"Project {project_id} not found")
            return {"success": False, "error": "Project not found"}

        statement = select(Competitor).where(
            Competitor.project_id == proj_id,
            Competitor.status == TrackingStatus.ACTIVE
        )
        competitors = session.exec(statement).all()

        results = []
        for competitor in competitors:
            # Trigger async scraping for each competitor
            task = scrape_competitor_task.delay(str(competitor.id))
            results.append({
                "competitor_id": str(competitor.id),
                "competitor_name": competitor.name,
                "task_id": task.id
            })

        logger.info(f"Triggered scraping for {len(results)} competitors in project {project_id}")

        return {
            "success": True,
            "project_id": project_id,
            "tasks_triggered": len(results),
            "results": results
        }


__all__ = ['run_tiered_scheduler', 'trigger_project_scan']
