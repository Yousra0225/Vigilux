import logging
from typing import Optional
from celery import shared_task

from app.services.scoring import ScoringService

logger = logging.getLogger(__name__)


@shared_task(
    name="app.tasks.scoring.calculate_competitor_score",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def calculate_competitor_score(self, competitor_id: str) -> Optional[dict]:
    """
    Calculate and update the V-Score for a competitor asynchronously.

    This task analyzes a competitor's recent events and calculates their
    overall threat score (V-Score).

    Args:
        self: Celery task instance
        competitor_id: ID of the competitor to score

    Returns:
        Dictionary with score details or None if competitor not found
    """
    import uuid
    from sqlmodel import Session, select
    from app.core.db import get_session
    from app.models.competitor import Competitor
    from app.models.event import Event

    logger.info(f"Calculating score for competitor: {competitor_id}")

    try:
        comp_id = uuid.UUID(competitor_id)
    except ValueError:
        logger.error(f"Invalid competitor ID: {competitor_id}")
        return None

    with next(get_session()) as session:
        competitor = session.get(Competitor, comp_id)
        if not competitor:
            logger.warning(f"Competitor {competitor_id} not found")
            return None

        # Get recent events for this competitor
        statement = (
            select(Event)
            .where(Event.competitor_id == comp_id)
            .order_by(Event.timestamp.desc())
            .limit(10)
        )
        events = session.exec(statement).all()

        if not events:
            logger.info(f"No events found for competitor {competitor_id}")
            return {
                "competitor_id": competitor_id,
                "score": None,
                "events_count": 0
            }

        # Calculate score based on recent events
        # For now, we'll use the average of event scores
        # In production, this would be more sophisticated
        total_score = 0
        scored_events = 0

        for event in events:
            if event.score is not None:
                total_score += event.score
                scored_events += 1

        if scored_events > 0:
            avg_score = total_score / scored_events
            competitor.score = avg_score
            session.add(competitor)
            session.commit()
            session.refresh(competitor)

            logger.info(f"Score calculated for competitor {competitor_id}: {avg_score:.2f}")

            return {
                "competitor_id": competitor_id,
                "score": avg_score,
                "events_count": scored_events
            }

        return {
            "competitor_id": competitor_id,
            "score": None,
            "events_count": 0
        }


@shared_task(
    name="app.tasks.scoring.score_all_competitors",
    bind=True,
)
def score_all_competitors(self, project_id: str) -> dict:
    """
    Calculate scores for all competitors in a project.

    Args:
        self: Celery task instance
        project_id: ID of the project

    Returns:
        Dictionary with results summary
    """
    import uuid
    from sqlmodel import Session, select
    from app.core.db import get_session
    from app.models.competitor import Competitor
    from app.models.project import Project

    logger.info(f"Scoring all competitors for project: {project_id}")

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
            # Trigger async scoring for each competitor
            task = calculate_competitor_score.delay(str(competitor.id))
            results.append({
                "competitor_id": str(competitor.id),
                "task_id": task.id
            })

        logger.info(f"Triggered scoring for {len(results)} competitors")

        return {
            "success": True,
            "project_id": project_id,
            "tasks_triggered": len(results),
            "results": results
        }


@shared_task(
    name="app.tasks.scoring.process_event_and_score",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_event_and_score(
    self,
    competitor_id: str,
    event_type: str,
    description: str
) -> dict:
    """
    Create an event, calculate its score, and update the competitor's V-Score.

    This is a compound task that:
    1. Creates a new event for the competitor
    2. Calculates the event's score using ScoringService
    3. Triggers a re-calculation of the competitor's overall V-Score

    Args:
        self: Celery task instance
        competitor_id: ID of the competitor
        event_type: Type of event (PRICE, FEATURE, HEALTH, NEW_ENTRANT)
        description: Event description

    Returns:
        Dictionary with event details and updated competitor score
    """
    import uuid
    from sqlmodel import Session, select
    from app.core.db import get_session
    from app.models.competitor import Competitor
    from app.models.event import Event, EventType

    logger.info(f"Processing event for competitor {competitor_id}: {event_type} - {description}")

    try:
        comp_id = uuid.UUID(competitor_id)
        event_type_enum = EventType(event_type)
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid input: {e}")
        return {"success": False, "error": str(e)}

    with next(get_session()) as session:
        competitor = session.get(Competitor, comp_id)
        if not competitor:
            logger.warning(f"Competitor {competitor_id} not found")
            return {"success": False, "error": "Competitor not found"}

        # Calculate event score
        event_score = ScoringService.calculate_score(event_type_enum, description)

        # Create event
        event = Event(
            competitor_id=comp_id,
            type=event_type_enum,
            description=description,
            score=event_score
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        # Trigger competitor score recalculation
        score_task = calculate_competitor_score.delay(str(competitor.id))

        logger.info(
            f"Event created with score {event_score}, "
            f"score recalculation task: {score_task.id}"
        )

        return {
            "success": True,
            "event_id": str(event.id),
            "event_score": event_score,
            "score_task_id": score_task.id
        }
