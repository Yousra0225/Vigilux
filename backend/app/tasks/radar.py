import logging
import random
import uuid
from typing import List

from app.core.celery_app import celery_app
from app.tasks.base import ScanningTask
from app.services.apify import ApifyService

logger = logging.getLogger(__name__)


@celery_app.task(
    base=ScanningTask,
    name="app.tasks.radar.perform_market_scan",
    bind=True,
)
def perform_market_scan(
    self,
    query: str,
    user_id: str,
    num_results: int = 5,
    location: str = None
) -> List[dict]:
    """
    Perform an async market scan for competitors.

    Uses Apify's Google Maps Scraper when APIFY_API_TOKEN is configured.
    Falls back to mock data generation when token is not available.

    Args:
        self: Celery task instance (bind=True)
        query: Market keyword to scan for
        user_id: ID of the user requesting the scan
        num_results: Number of results to return (default: 5)
        location: Geographic location for search (default: None)

    Returns:
        List of dictionaries containing RadarResult data
    """
    logger.info(f"Starting market scan for query: '{query}', user: {user_id}, location: {location}")

    # Try to use Apify if configured
    if ApifyService.is_configured():
        logger.info("Using Apify for real market data")
        try:
            apify_results = ApifyService.search_competitors(
                query=query,
                location=location,
                max_results=num_results
            )

            if apify_results:
                # Transform Apify results to RadarResult format
                results = []
                mock_strengths = ["Strong community", "Rapid innovation", "User-friendly UI", "Low cost", "Global reach"]
                mock_weaknesses = ["Limited integration", "High complexity", "New player", "Fragmented support"]
                mock_pitches = [
                    "Disrupting the industry with AI-driven insights.",
                    "Next-generation automation for modern enterprises.",
                    "The complete toolkit for scaling digital infrastructure.",
                    "Revolutionizing customer engagement through predictive modeling."
                ]

                for item in apify_results:
                    threat_score = item["score"]

                    market_presence = "Medium"
                    if threat_score > 80:
                        market_presence = "High"
                    elif threat_score < 40:
                        market_presence = "Low"

                    results.append({
                        "name": item["name"],
                        "url": item["url"],
                        "threat_score": threat_score,
                        "market_presence": market_presence,
                        "pitch": random.choice(mock_pitches),
                        "strengths": random.sample(mock_strengths, 2),
                        "weaknesses": random.sample(mock_weaknesses, 2)
                    })

                logger.info(f"Apify scan completed: found {len(results)} results")
                return results

        except Exception as e:
            logger.warning(f"Apify scan failed, falling back to mock data: {e}")

    # Fallback to mock data generation
    logger.info("Using mock data generation for market scan")

    # Simulate processing time (in production, this would be actual web scraping)
    import time
    time.sleep(2)  # Simulate 2 seconds of "scanning"

    # Mock data generation (same logic as the original endpoint)
    mock_suffixes = ["Solutions", "Tech", "Systems", "AI", "Soft", "Hub", "Lab"]
    mock_pitches = [
        "Disrupting the industry with AI-driven insights.",
        "Next-generation automation for modern enterprises.",
        "The complete toolkit for scaling digital infrastructure.",
        "Revolutionizing customer engagement through predictive modeling."
    ]
    mock_strengths = ["Strong community", "Rapid innovation", "User-friendly UI", "Low cost", "Global reach"]
    mock_weaknesses = ["Limited integration", "High complexity", "New player", "Fragmented support"]

    results = []

    for _ in range(num_results):
        name = f"{query.capitalize()} {random.choice(mock_suffixes)}"
        threat_score = random.randint(30, 95)

        market_presence = "Medium"
        if threat_score > 80:
            market_presence = "High"
        elif threat_score < 40:
            market_presence = "Low"

        results.append({
            "name": name,
            "url": f"https://www.{name.lower().replace(' ', '')}.com",
            "threat_score": threat_score,
            "market_presence": market_presence,
            "pitch": random.choice(mock_pitches),
            "strengths": random.sample(mock_strengths, 2),
            "weaknesses": random.sample(mock_weaknesses, 2)
        })

    logger.info(f"Mock market scan completed for query: '{query}', found {len(results)} results")
    return results


@celery_app.task(
    base=ScanningTask,
    name="app.tasks.radar.add_competitors_from_scan",
    bind=True,
)
def add_competitors_from_scan(
    self,
    project_id: str,
    scan_results: List[dict],
    user_id: str
) -> dict:
    """
    Add competitors from a scan result to a project.

    Args:
        self: Celery task instance
        project_id: ID of the project to add competitors to
        scan_results: List of competitor data from scan
        user_id: ID of the user owning the project

    Returns:
        Dictionary with success status and added competitor IDs
    """
    from app.core.db import get_session
    from app.models.competitor import Competitor
    from app.models.project import Project

    logger.info(f"Adding {len(scan_results)} competitors to project {project_id}")

    added_count = 0
    competitor_ids = []

    with next(get_session()) as session:
        # Verify project ownership
        project = session.get(Project, uuid.UUID(project_id))
        if not project or str(project.user_id) != user_id:
            logger.error(f"Project {project_id} not found or access denied for user {user_id}")
            return {"success": False, "error": "Project not found"}

        # Add competitors
        for result in scan_results:
            competitor = Competitor(
                project_id=project.id,
                name=result["name"],
                url=result["url"],
                score=result["threat_score"],
            )
            session.add(competitor)
            competitor_ids.append(str(competitor.id))
            added_count += 1

        session.commit()

    logger.info(f"Successfully added {added_count} competitors to project {project_id}")
    return {
        "success": True,
        "added_count": added_count,
        "competitor_ids": competitor_ids
    }
