from typing import Any, Dict, List, Optional
from apify_client import ApifyClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ApifyService:
    def __init__(self) -> None:
        self.client = ApifyClient(token=settings.APIFY_API_TOKEN)
        if not settings.APIFY_API_TOKEN:
            logger.warning("APIFY_API_TOKEN is not set. Apify services will not function correctly.")

    def run_actor(
        self, 
        actor_id: str, 
        run_input: Optional[Dict[str, Any]] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None
    ) -> List[Dict[str, Any]]:
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
            Exception: If the actor run fails or does not complete successfully.
        """
        try:
            logger.info(f"Starting actor {actor_id}...")
            # call() starts the actor and waits for it to finish
            run = self.client.actor(actor_id).call(
                run_input=run_input,
                memory_mbytes=memory_mbytes,
                timeout_secs=timeout_secs
            )
            
            if not run:
                raise Exception("Failed to start actor run (no response).")
            
            status = run.get('status')
            logger.info(f"Actor {actor_id} finished with status: {status}")

            if status != 'SUCCEEDED':
                 raise Exception(f"Actor run failed with status: {status}")

            dataset_id = run.get('defaultDatasetId')
            if not dataset_id:
                logger.warning("No default dataset ID returned.")
                return []

            # Fetch items from the dataset
            # list_items returns a pagination object, .items gives the list
            dataset_items = self.client.dataset(dataset_id).list_items().items
            logger.info(f"Retrieved {len(dataset_items)} items from dataset {dataset_id}")
            
            return dataset_items
            
        except Exception as e:
            logger.error(f"Error running actor {actor_id}: {str(e)}")
            raise

    def scrape_google_maps(self, name: str, location: str) -> List[Dict[str, Any]]:
        """
        Scrapes Google Maps for a specific competitor by name and location.
        
        Args:
            name: The name of the competitor.
            location: The geographic location or address.
            
        Returns:
            A list of dictionary items representing the scraped data.
        """
        run_input = {
            "searchStrings": [f"{name} {location}"],
            "maxReviews": 20,
            "exportPlaceUrls": True,
        }
        
        logger.info(f"Scraping Google Maps for: {name} in {location}")
        
        try:
            # Using compass/crawler-google-places (correct actor ID)
            results = self.run_actor(
                actor_id="compass/crawler-google-places",
                run_input=run_input
            )
            return results
        except Exception as e:
            logger.error(f"Google Maps scraping failed for {name}: {str(e)}")
            # Re-raise to allow ScanningTask retry logic to handle transient failures
            raise

apify_service = ApifyService()
