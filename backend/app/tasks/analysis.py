import logging
import uuid
from typing import Any, Dict

from sqlmodel import Session

from app.core.celery_app import celery_app
from app.core.db import get_session
from app.models.competitor import Competitor
from app.tasks.base import AnalysisTask
from app.services.gemini import GeminiService

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
                return {
                    "success": False,
                    "competitor_id": competitor_id,
                    "message": "AI analysis returned no result"
                }
            
            # Convert Pydantic model to dict for Celery serialization
            report_data = report.model_dump()
            
            logger.info(f"Analysis complete for {competitor.name}. Sentinel Score: {report.sentinel_score}")
            
            return {
                "success": True,
                "competitor_id": competitor_id,
                "report": report_data
            }

        except Exception as e:
            logger.error(f"AI Analysis failed for {competitor.name}: {e}")
            # AnalysisTask will handle retries according to policy
            raise e

__all__ = ['analyze_competitor_task']
