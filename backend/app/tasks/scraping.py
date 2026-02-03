import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from sqlmodel import Session, select

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor
from app.models.project import Project
from app.tasks.base import ScanningTask
from app.services.apify_client import apify_service
from app.services.normalization import normalization_service
from app.services.websocket_manager import notify_user

logger = logging.getLogger(__name__)


@celery_app.task(base=ScanningTask, bind=True, name="app.tasks.scraping.scrape_competitor")
def scrape_competitor_task(
    self,
    competitor_id: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scrape competitor data from Google Maps and update the competitor record.

    This task:
    1. Retrieves the competitor from the database
    2. Scrapes Google Maps for the competitor's name and location
    3. Normalizes the scraped data
    4. Updates the competitor record with scraped information
    5. Triggers the analysis task for further processing

    Args:
        self: Celery task instance (bind=True)
        competitor_id: UUID of the competitor to scrape
        location: Geographic location for the search (optional, defaults to "United States")

    Returns:
        Dictionary containing:
        - success: Boolean indicating if the scrape was successful
        - competitor_id: UUID of the competitor
        - data_found: Boolean if Google Maps data was found
        - message: Status message
        - normalized_data: The normalized data (if found)
    """
    logger.info(f"Starting scrape for competitor: {competitor_id}")

    # Default location if not provided
    if not location:
        location = "United States"

    try:
        # Validate competitor_id
        comp_id = uuid.UUID(competitor_id)
    except ValueError:
        logger.error(f"Invalid competitor ID: {competitor_id}")
        return {
            "success": False,
            "competitor_id": competitor_id,
            "message": "Invalid competitor ID format"
        }

    # Retrieve competitor from database
    with next(get_session()) as session:
        competitor = session.get(Competitor, comp_id)

        if not competitor:
            logger.warning(f"Competitor {competitor_id} not found")
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": "Competitor not found"
            }

        # Fetch project to get user_id for notifications
        project = session.get(Project, competitor.project_id)
        user_id = project.user_id if project else None

        logger.info(f"Scraping data for: {competitor.name}")

        # Emit: Scraping started
        if user_id:
            try:
                notify_user(
                    user_id=user_id,
                    notification_type="TASK_UPDATE",
                    data={
                        "status": "scraping_started",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send scraping started notification: {e}")

        # Step 1: Scrape Google Maps for competitor data
        try:
            raw_results = apify_service.scrape_google_maps(
                name=competitor.name,
                location=location
            )

            if not raw_results:
                logger.warning(f"No Google Maps results found for {competitor.name}")
                # Emit: Scraping complete but no data
                if user_id:
                    try:
                        notify_user(
                            user_id=user_id,
                            notification_type="TASK_UPDATE",
                            data={
                                "status": "scraping_complete_no_data",
                                "competitor_id": competitor_id,
                                "competitor_name": competitor.name,
                                "message": "No Google Maps data found",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send scraping notification: {e}")
                return {
                    "success": True,
                    "competitor_id": competitor_id,
                    "data_found": False,
                    "message": "No Google Maps data found"
                }

            logger.info(f"Found {len(raw_results)} raw results for {competitor.name}")

        except Exception as e:
            logger.error(f"Google Maps scraping failed for {competitor.name}: {e}")
            # Emit: Scraping failed
            if user_id:
                try:
                    notify_user(
                        user_id=user_id,
                        notification_type="TASK_UPDATE",
                        data={
                            "status": "scraping_failed",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "error": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as notify_error:
                    logger.warning(f"Failed to send scraping failed notification: {notify_error}")
            # Return without raising - ScanningTask will handle retries for HTTP exceptions
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Scraping failed: {str(e)}"
            }

        # Step 2: Normalize the scraped data
        try:
            normalized_data = normalization_service.normalize_google_maps_data(raw_results)

            if not normalized_data.get("matched"):
                logger.warning(f"Normalization failed for {competitor.name}")
                return {
                    "success": True,
                    "competitor_id": competitor_id,
                    "data_found": False,
                    "message": "Normalization returned no match"
                }

            logger.info(f"Normalized data for {competitor.name}: score={normalized_data.get('score')}")

        except Exception as e:
            logger.error(f"Normalization failed for {competitor.name}: {e}")
            # Emit: Normalization failed
            if user_id:
                try:
                    notify_user(
                        user_id=user_id,
                        notification_type="TASK_UPDATE",
                        data={
                            "status": "scraping_failed",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "error": f"Normalization failed: {str(e)}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as notify_error:
                    logger.warning(f"Failed to send scraping failed notification: {notify_error}")
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Normalization failed: {str(e)}"
            }

        # Step 3: Update competitor with scraped data
        try:
            # Update existing fields
            if normalized_data.get("website"):
                competitor.url = normalized_data["website"]

            if normalized_data.get("score") is not None:
                competitor.score = normalized_data["score"]

            # Update last_scanned_at timestamp
            competitor.last_scanned_at = datetime.utcnow()

            # Note: Additional fields like address, phone
            # would need to be added to the Competitor model schema
            # For now, we log them

            # Update competitor if there's additional info
            # (Since Competitor model is limited, we keep what we can update)
            session.add(competitor)
            session.commit()
            session.refresh(competitor)

            logger.info(f"Updated competitor {competitor_id} with scraped data (last_scanned_at: {competitor.last_scanned_at})")

        except Exception as e:
            logger.error(f"Failed to update competitor {competitor_id}: {e}")
            # Emit: Database update failed
            if user_id:
                try:
                    notify_user(
                        user_id=user_id,
                        notification_type="TASK_UPDATE",
                        data={
                            "status": "scraping_failed",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "error": f"Database update failed: {str(e)}",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as notify_error:
                    logger.warning(f"Failed to send scraping failed notification: {notify_error}")
            session.rollback()
            return {
                "success": False,
                "competitor_id": competitor_id,
                "message": f"Database update failed: {str(e)}"
            }

        # Step 4: Trigger the analysis task (placeholder for Phase 7C)
        # This will chain the scraping task to the AI analysis task
        try:
            # Import here to avoid circular dependencies
            from app.tasks.analysis import analyze_competitor_task
            
            logger.info(f"Triggering analysis task for {competitor_id}")
            analyze_competitor_task.delay(str(competitor.id), normalized_data)

        except Exception as e:
            logger.warning(f"Could not trigger analysis task: {e}")
            # Don't fail the scrape task if analysis trigger fails

    # Return success result
    # Emit: Scraping complete successfully
    if user_id:
        try:
            notify_user(
                user_id=user_id,
                notification_type="TASK_UPDATE",
                data={
                    "status": "scraping_complete",
                    "competitor_id": competitor_id,
                    "competitor_name": normalized_data.get("name", competitor.name),
                    "score": normalized_data.get("score"),
                    "reviews_count": len(normalized_data.get("reviews", [])),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to send scraping complete notification: {e}")

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
        }
    }

    logger.info(f"Scrape task completed for competitor {competitor_id}")
    return result


@celery_app.task(base=ScanningTask, bind=True, name="app.tasks.scraping.scrape_all_competitors")
def scrape_all_competitors_task(
    self,
    project_id: str,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scrape all competitors in a project.

    This is a batch task that triggers individual scrape tasks for each
    competitor in the specified project.

    Args:
        self: Celery task instance
        project_id: UUID of the project
        location: Geographic location for the search (optional)

    Returns:
        Dictionary with results summary
    """
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

        from app.models.competitor import Competitor
        statement = select(Competitor).where(Competitor.project_id == proj_id)
        competitors = session.exec(statement).all()

        results = []
        for competitor in competitors:
            # Trigger async scraping for each competitor
            task = scrape_competitor_task.delay(str(competitor.id), location)
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


__all__ = ['scrape_competitor_task', 'scrape_all_competitors_task']
