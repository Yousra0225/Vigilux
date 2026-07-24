import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor
from app.models.project import Project
from app.services.apify_client import ApifyServiceError, apify_service
from app.services.normalization import normalization_service
from app.services.websocket_manager import emit_task_update
from app.tasks.base import ScanningTask

logger = logging.getLogger(__name__)


@celery_app.task(base=ScanningTask, bind=True, name="app.tasks.scraping.scrape_competitor")
def scrape_competitor_task(
    self,
    competitor_id: str,
    location: str | None = None,
) -> dict[str, Any]:
    """
    Scrape competitor data from Google Maps and update the competitor record.

    This task:
    1. Retrieves the competitor from the database
    2. Scrapes Google Maps for the competitor's name and location
    3. Normalizes the scraped data
    4. Updates the competitor record with scraped information
    5. Triggers the analysis task for further processing
    """
    logger.info(f"Starting scrape for competitor: {competitor_id}")

    if not location:
        location = "United States"

    try:
        comp_id = uuid.UUID(competitor_id)
    except ValueError:
        logger.error(f"Invalid competitor ID: {competitor_id}")
        return {
            "success": False,
            "competitor_id": competitor_id,
            "message": "Invalid competitor ID format",
        }

    with next(get_session()) as session:
        competitor = session.get(Competitor, comp_id)

        if not competitor:
            logger.warning(f"Competitor {competitor_id} not found")
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": "Competitor not found",
            }

        project = session.get(Project, competitor.project_id)
        user_id = project.user_id if project else None

        logger.info(f"Scraping data for: {competitor.name}")

        from app.models.user import User
        from app.services.quota import QuotaService

        if user_id:
            user = session.get(User, user_id)
            if not QuotaService.can_refresh_competitor(user, competitor.last_scanned_at):
                logger.warning(
                    f"Rate limit exceeded for {user.email}, competitor {competitor.name}. "
                    f"Last scanned: {competitor.last_scanned_at}"
                )
                return {
                    "success": False,
                    "competitor_id": competitor_id,
                    "message": "Rate limit exceeded. Please wait before refreshing again.",
                }

        if user_id:
            emit_task_update(
                user_id=user_id,
                data={
                    "status": "scraping_started",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor.name,
                },
            )

        try:
            raw_results = apify_service.scrape_google_maps(
                name=competitor.name,
                location=location,
            )

            if not raw_results:
                logger.warning(f"No Google Maps results found for {competitor.name}")
                if user_id:
                    emit_task_update(
                        user_id=user_id,
                        data={
                            "status": "scraping_complete_no_data",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "message": "No Google Maps data found",
                        },
                    )
                return {
                    "success": True,
                    "competitor_id": competitor_id,
                    "data_found": False,
                    "message": "No Google Maps data found",
                }

            logger.info(f"Found {len(raw_results)} raw results for {competitor.name}")

        except ApifyServiceError as exc:
            logger.error(f"Google Maps scraping failed for {competitor.name}: {exc}")
            if user_id:
                emit_task_update(
                    user_id=user_id,
                    data={
                        "status": "scraping_failed",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "error": str(exc),
                    },
                )
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Scraping failed: {exc!s}",
            }

        try:
            normalized_data = normalization_service.normalize_google_maps_data(raw_results)

            if not normalized_data.get("matched"):
                logger.warning(f"Normalization failed for {competitor.name}")
                return {
                    "success": True,
                    "competitor_id": competitor_id,
                    "data_found": False,
                    "message": "Normalization returned no match",
                }

            logger.info(
                f"Normalized data for {competitor.name}: score={normalized_data.get('score')}"
            )

        except (TypeError, ValueError, KeyError) as exc:
            logger.error(f"Normalization failed for {competitor.name}: {exc}")
            if user_id:
                emit_task_update(
                    user_id=user_id,
                    data={
                        "status": "scraping_failed",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "error": f"Normalization failed: {exc!s}",
                    },
                )
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Normalization failed: {exc!s}",
            }

        try:
            if normalized_data.get("website"):
                competitor.url = normalized_data["website"]

            if normalized_data.get("score") is not None:
                competitor.score = normalized_data["score"]

            competitor.last_scanned_at = datetime.now(UTC)

            session.add(competitor)
            session.commit()
            session.refresh(competitor)

            logger.info(
                f"Updated competitor {competitor_id} with scraped data "
                f"(last_scanned_at: {competitor.last_scanned_at})"
            )

        except SQLAlchemyError as exc:
            logger.error(f"Failed to update competitor {competitor_id}: {exc}")
            if user_id:
                emit_task_update(
                    user_id=user_id,
                    data={
                        "status": "scraping_failed",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "error": f"Database update failed: {exc!s}",
                    },
                )
            session.rollback()
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Database update failed: {exc!s}",
            }

        try:
            from app.tasks.analysis import analyze_competitor_task

            logger.info(f"Triggering analysis task for {competitor_id}")
            analyze_competitor_task.delay(str(competitor.id), normalized_data)

        except (ImportError, OSError, RuntimeError) as exc:
            logger.warning(f"Could not trigger analysis task: {exc}")

    if user_id:
        emit_task_update(
            user_id=user_id,
            data={
                "status": "scraping_complete",
                "competitor_id": competitor_id,
                "competitor_name": normalized_data.get("name", competitor.name),
                "score": normalized_data.get("score"),
                "reviews_count": len(normalized_data.get("reviews", [])),
            },
        )

    result = {
        "success": True,
        "competitor_id": competitor_id,
        "data_found": True,
        "message": "Scraping completed successfully",
        "normalized_data": {
            "name": normalized_data.get("name"),
            "score": normalized_data.get("score"),
            "address": normalized_data.get("address"),
            "website": normalized_data.get("website"),
            "phone": normalized_data.get("phone"),
            "reviews_count": len(normalized_data.get("reviews", [])),
        },
    }

    logger.info(f"Scrape task completed for competitor {competitor_id}")
    return result


@celery_app.task(base=ScanningTask, bind=True, name="app.tasks.scraping.scrape_all_competitors")
def scrape_all_competitors_task(
    self,
    project_id: str,
    location: str | None = None,
) -> dict[str, Any]:
    """Scrape all competitors in a project."""
    logger.info(f"Starting batch scrape for project: {project_id}")

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

        statement = select(Competitor).where(Competitor.project_id == proj_id)
        competitors = session.exec(statement).all()

        results = []
        for competitor in competitors:
            task = scrape_competitor_task.delay(str(competitor.id), location)
            results.append({
                "competitor_id": str(competitor.id),
                "competitor_name": competitor.name,
                "task_id": task.id,
            })

        logger.info(f"Triggered scraping for {len(results)} competitors in project {project_id}")

        return {
            "success": True,
            "project_id": project_id,
            "tasks_triggered": len(results),
            "results": results,
        }


__all__ = ["scrape_all_competitors_task", "scrape_competitor_task"]
