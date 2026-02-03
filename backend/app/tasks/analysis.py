import logging
import uuid
from datetime import datetime
from typing import Any, Dict


from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor
from app.models.event import Event, EventType
from app.models.project import Project
from app.tasks.base import AnalysisTask
from app.services.gemini import GeminiService
from app.services.websocket_manager import notify_user

logger = logging.getLogger(__name__)


@celery_app.task(base=AnalysisTask, bind=True, name="app.tasks.analysis.analyze_competitor")
def analyze_competitor_task(
    self,
    competitor_id: str,
    raw_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze competitor data using Gemini AI to generate insights.

    This task:
    1. Retrieves the competitor from the database.
    2. Uses GeminiService to analyze the raw data (reviews, description).
    3. Returns the structured intelligence report.

    Args:
        self: Celery task instance.
        competitor_id: UUID of the competitor.
        raw_data: dictionary containing normalized data from scraping 
                  (e.g., reviews, website, description).

    Returns:
        Dictionary containing the generated intelligence report.
    """
    logger.info(f"Starting analysis for competitor: {competitor_id}")

    try:
        comp_id = uuid.UUID(competitor_id)
    except ValueError:
        logger.error(f"Invalid competitor ID: {competitor_id}")
        return {"success": False, "message": "Invalid competitor ID format"}

    with next(get_session()) as session:
        competitor = session.get(Competitor, comp_id)
        if not competitor:
            logger.warning(f"Competitor {competitor_id} not found")
            return {"success": False, "message": "Competitor not found"}

        # Fetch project to get user_id for notifications
        project = session.get(Project, competitor.project_id)
        user_id = project.user_id if project else None

        # Emit: Analysis started
        if user_id:
            try:
                notify_user(
                    user_id=user_id,
                    notification_type="TASK_UPDATE",
                    data={
                        "status": "analysis_started",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to send analysis started notification: {e}")

        # Extract context for analysis
        # raw_data comes from the normalization service
        name = raw_data.get("name") or competitor.name
        reviews = raw_data.get("reviews", [])
        description = raw_data.get("description", "") # Normalization might not provide this yet, but good to have
        website = raw_data.get("website") or competitor.url
        
        # Prepare additional context
        context = {
            "website": website,
            "address": raw_data.get("address"),
            "phone": raw_data.get("phone")
        }

        # Use the convenience method from GeminiService that formats the prompt
        # directly from these fields
        try:
            report = GeminiService.analyze_from_scraped_data(
                name=name,
                description=description,
                reviews=reviews,
                **context
            )

            if not report:
                logger.warning(f"Analysis yielded no report for {competitor.name}")
                # Emit: Analysis failed (no result)
                if user_id:
                    try:
                        notify_user(
                            user_id=user_id,
                            notification_type="TASK_UPDATE",
                            data={
                                "status": "analysis_failed",
                                "competitor_id": competitor_id,
                                "competitor_name": competitor.name,
                                "error": "AI analysis returned no result",
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send analysis failed notification: {e}")
                return {
                    "success": False,
                    "competitor_id": competitor_id,
                    "message": "AI analysis returned no result"
                }
            
            # Convert Pydantic model to dict for Celery serialization
            report_data = report.model_dump()

            logger.info(f"Analysis complete for {competitor.name}. Sentinel Score: {report.sentinel_score}")

            # Persist insights to database
            # Step 1: Update competitor score
            competitor.score = report.sentinel_score
            # Note: last_updated_at field does not exist in Competitor model yet
            # When added, uncomment: competitor.last_updated_at = datetime.utcnow()

            # Step 2: Create Event records for each key_event
            events_created = []
            for key_event in report.key_events:
                try:
                    # Map event type string to EventType enum
                    event_type = EventType(key_event.type.value) if hasattr(key_event.type, 'value') else EventType(key_event.type)

                    event = Event(
                        competitor_id=competitor.id,
                        type=event_type,
                        description=key_event.description,
                        score=key_event.score,
                        timestamp=datetime.utcnow()
                    )
                    session.add(event)
                    events_created.append({
                        "type": event_type,
                        "description": key_event.description,
                        "score": key_event.score
                    })
                    logger.info(f"Created event for {competitor.name}: {event_type} - {key_event.description}")
                except ValueError as e:
                    logger.warning(f"Could not create event for {key_event}: {e}")
                except Exception as e:
                    logger.error(f"Error creating event: {e}")

            # Commit all changes to database
            session.add(competitor)
            session.commit()
            session.refresh(competitor)

            logger.info(f"Persisted {len(events_created)} events and updated score for {competitor.name}")

            # Step 3: Notification dispatch (stub)
            # This would trigger notifications to users about significant events
            # To be implemented: integrate with notification service
            _notify_users_of_insights(competitor_id=str(competitor.id), events=events_created)

            # Emit: Analysis complete successfully
            if user_id:
                try:
                    notify_user(
                        user_id=user_id,
                        notification_type="TASK_UPDATE",
                        data={
                            "status": "analysis_complete",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "new_score": report.sentinel_score,
                            "events_created": len(events_created),
                            "market_sentiment": report.market_sentiment.value if hasattr(report.market_sentiment, 'value') else str(report.market_sentiment),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to send analysis complete notification: {e}")

            return {
                "success": True,
                "competitor_id": competitor_id,
                "report": report_data,
                "events_created": len(events_created),
                "score_updated": True
            }

        except Exception as e:
            logger.error(f"AI Analysis failed for {competitor.name}: {e}")
            # Emit: Analysis failed
            if user_id:
                try:
                    notify_user(
                        user_id=user_id,
                        notification_type="TASK_UPDATE",
                        data={
                            "status": "analysis_failed",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "error": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                except Exception as notify_error:
                    logger.warning(f"Failed to send analysis failed notification: {notify_error}")
            # AnalysisTask will handle retries according to policy
            raise e


def _notify_users_of_insights(competitor_id: str, events: list) -> None:
    """
    Stub function for notifying users about new competitor insights.

    This function is a placeholder for future notification integration.
    It would typically:
    - Send in-app notifications
    - Send email alerts for high-priority events
    - Push WebSocket updates to connected clients

    Args:
        competitor_id: UUID of the competitor
        events: List of event dictionaries that were created
    """
    # TODO: Implement notification service integration
    # - For high-score events (score > 75), send immediate alerts
    # - Batch notifications for medium-score events
    # - Aggregate low-score events for daily digest

    high_priority_events = [e for e in events if e.get("score", 0) > 75]
    if high_priority_events:
        logger.info(
            f"NOTIFICATION STUB: {len(high_priority_events)} high-priority events "
            f"for competitor {competitor_id} - would notify user immediately"
        )

    logger.debug(f"NOTIFICATION STUB: Would notify user about {len(events)} events for competitor {competitor_id}")


__all__ = ['analyze_competitor_task']
