import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor
from app.models.event import Event, EventType
from app.models.project import Project
from app.services.gemini import GeminiService
from app.services.websocket_manager import emit_task_update
from app.tasks.base import AnalysisTask

logger = logging.getLogger(__name__)


@celery_app.task(base=AnalysisTask, bind=True, name="app.tasks.analysis.analyze_competitor")
def analyze_competitor_task(
    self,
    competitor_id: str,
    raw_data: dict[str, Any],
) -> dict[str, Any]:
    """Analyze competitor data using Gemini AI to generate insights."""
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

        project = session.get(Project, competitor.project_id)
        user_id = project.user_id if project else None

        if user_id:
            emit_task_update(
                user_id=user_id,
                data={
                    "status": "analysis_started",
                    "competitor_id": competitor_id,
                    "competitor_name": competitor.name,
                },
            )

        name = raw_data.get("name") or competitor.name
        reviews = raw_data.get("reviews", [])
        description = raw_data.get("description", "")
        website = raw_data.get("website") or competitor.url

        context = {
            "website": website,
            "address": raw_data.get("address"),
            "phone": raw_data.get("phone"),
        }

        try:
            report = GeminiService.analyze_from_scraped_data(
                name=name,
                description=description,
                reviews=reviews,
                **context,
            )

            if not report:
                logger.warning(f"Analysis yielded no report for {competitor.name}")
                if user_id:
                    emit_task_update(
                        user_id=user_id,
                        data={
                            "status": "analysis_failed",
                            "competitor_id": competitor_id,
                            "competitor_name": competitor.name,
                            "error": "AI analysis returned no result",
                        },
                    )
                return {
                    "success": False,
                    "competitor_id": competitor_id,
                    "message": "AI analysis returned no result",
                }

            report_data = report.model_dump()

            logger.info(
                f"Analysis complete for {competitor.name}. "
                f"Sentinel Score: {report.sentinel_score}"
            )

            competitor.score = report.sentinel_score

            events_created = []
            for key_event in report.key_events:
                try:
                    event_type = (
                        EventType(key_event.type.value)
                        if hasattr(key_event.type, "value")
                        else EventType(key_event.type)
                    )

                    event = Event(
                        competitor_id=competitor.id,
                        type=event_type,
                        description=key_event.description,
                        score=key_event.score,
                        timestamp=datetime.now(UTC),
                    )
                    session.add(event)
                    events_created.append({
                        "type": event_type,
                        "description": key_event.description,
                        "score": key_event.score,
                    })
                    logger.info(
                        f"Created event for {competitor.name}: "
                        f"{event_type} - {key_event.description}"
                    )
                except ValueError as exc:
                    logger.warning(f"Could not create event for {key_event}: {exc}")
                except (SQLAlchemyError, TypeError, AttributeError) as exc:
                    logger.error(f"Error creating event: {exc}")

            session.add(competitor)
            session.commit()
            session.refresh(competitor)

            logger.info(
                f"Persisted {len(events_created)} events and updated score for "
                f"{competitor.name}"
            )

            _notify_users_of_insights(
                competitor_id=str(competitor.id),
                events=events_created,
            )

            if user_id:
                emit_task_update(
                    user_id=user_id,
                    data={
                        "status": "analysis_complete",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "new_score": report.sentinel_score,
                        "events_created": len(events_created),
                        "market_sentiment": (
                            report.market_sentiment.value
                            if hasattr(report.market_sentiment, "value")
                            else str(report.market_sentiment)
                        ),
                    },
                )

            return {
                "success": True,
                "competitor_id": competitor_id,
                "report": report_data,
                "events_created": len(events_created),
                "score_updated": True,
            }

        except SQLAlchemyError as exc:
            logger.error(f"AI Analysis failed for {competitor.name}: {exc}")
            session.rollback()
            if user_id:
                emit_task_update(
                    user_id=user_id,
                    data={
                        "status": "analysis_failed",
                        "competitor_id": competitor_id,
                        "competitor_name": competitor.name,
                        "error": str(exc),
                    },
                )
            raise


def _notify_users_of_insights(competitor_id: str, events: list) -> None:
    """Stub function for notifying users about new competitor insights."""
    high_priority_events = [event for event in events if event.get("score", 0) > 75]
    if high_priority_events:
        logger.info(
            f"NOTIFICATION STUB: {len(high_priority_events)} high-priority events "
            f"for competitor {competitor_id} - would notify user immediately"
        )

    logger.debug(
        f"NOTIFICATION STUB: Would notify user about {len(events)} events "
        f"for competitor {competitor_id}"
    )


__all__ = ["analyze_competitor_task"]
