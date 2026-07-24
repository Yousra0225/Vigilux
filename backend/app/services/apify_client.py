import logging
from typing import Any

from apify_client import ApifyClient

from app.core.config import settings

logger = logging.getLogger(__name__)


class ApifyServiceError(Exception):
    """Raised when an Apify actor run fails."""


class ApifyService:
    def __init__(self) -> None:
        self.client = ApifyClient(token=settings.APIFY_API_TOKEN)
        if not settings.APIFY_API_TOKEN:
            logger.warning("APIFY_API_TOKEN is not set. Apify services will not function correctly.")

    def run_actor(
        self,
        actor_id: str,
        run_input: dict[str, Any] | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Runs a specified Apify actor and returns the dataset items.

        Args:
            actor_id: The ID of the actor to run (e.g. 'apify/google-maps-scraper').
            run_input: The input dictionary for the actor.
            memory_mbytes: Optional memory limit.
            timeout_secs: Optional timeout for the run.

        Returns:
            A list of dictionary items representing the dataset results.

        Raises:
            ApifyServiceError: If the actor run fails or does not complete successfully.
        """
        try:
            logger.info(f"Starting actor {actor_id}...")
            run = self.client.actor(actor_id).call(
                run_input=run_input,
                memory_mbytes=memory_mbytes,
                timeout_secs=timeout_secs,
            )

            if not run:
                raise ApifyServiceError("Failed to start actor run (no response).")

            status = run.get("status")
            logger.info(f"Actor {actor_id} finished with status: {status}")

            if status != "SUCCEEDED":
                raise ApifyServiceError(f"Actor run failed with status: {status}")

            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                logger.warning("No default dataset ID returned.")
                return []

            dataset_items = self.client.dataset(dataset_id).list_items().items
            logger.info(f"Retrieved {len(dataset_items)} items from dataset {dataset_id}")

            return dataset_items

        except ApifyServiceError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError, KeyError) as exc:
            logger.error(f"Error running actor {actor_id}: {exc!s}")
            raise ApifyServiceError(str(exc)) from exc

    def scrape_google_maps(self, name: str, location: str) -> list[dict[str, Any]]:
        """
        Scrapes Google Maps for a specific competitor by name and location.

        Args:
            name: The name of the competitor.
            location: The geographic location or address.

        Returns:
            A list of dictionary items representing the scraped data.
        """
        run_input = {
            "searchStringsArray": [f"{name} {location}"],
            "maxReviews": 20,
        }

        logger.info(f"Scraping Google Maps for: {name} in {location}")

        results = self.run_actor(
            actor_id="compass/crawler-google-places",
            run_input=run_input,
        )
        return results


apify_service = ApifyService()
