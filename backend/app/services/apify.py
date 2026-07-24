import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class ApifyService:
    """
    Service for interacting with Apify actors to fetch real market data.

    Uses Apify's Google Maps Scraper actor to find businesses/competitors
    based on search queries.
    """

    # Apify Actor IDs
    GOOGLE_MAPS_SCRAPER = "apify/google-maps-scraper"
    # Alternative actors for different use cases:
    # - Web scraper: apify/web-scraper
    # - Website content extractor: apify/website-content-extractor

    @staticmethod
    def _get_client() -> Any | None:
        """
        Get an initialized ApifyClient instance.

        Returns None if APIFY_API_TOKEN is not configured.
        """
        if not settings.APIFY_API_TOKEN:
            logger.warning("APIFY_API_TOKEN not configured - Apify features disabled")
            return None

        try:
            from apify_client import ApifyClient
            return ApifyClient(token=settings.APIFY_API_TOKEN)
        except ImportError:
            logger.error("apify-client not installed. Run: pip install apify-client")
            return None
        except (OSError, RuntimeError, ValueError, TypeError) as exc:
            logger.error(f"Failed to initialize ApifyClient: {exc}")
            return None

    @staticmethod
    def search_competitors(
        query: str,
        location: str | None = None,
        max_results: int = 20,
        language: str = "en"
    ) -> list[dict[str, Any]]:
        """
        Search for competitors using Apify's Google Maps Scraper.

        Args:
            query: Search query (e.g., "saas companies", "crm software")
            location: Geographic location to search (e.g., "United States", "New York")
            max_results: Maximum number of results to return
            language: Language code for results

        Returns:
            List of standardized competitor dicts with keys:
            - name: Business name
            - url: Website URL
            - score: Calculated threat score (0-100)
            - description: Business description (from categories/reviews)
            - address: Business address
            - phone: Phone number
            - rating: Average rating (if available)
            - review_count: Number of reviews
            - categories: List of business categories

        Returns empty list if Apify is not configured or fails.
        """
        client = ApifyService._get_client()
        if not client:
            logger.info("Apify client not available - would return empty list")
            return []

        try:
            logger.info(f"Starting Apify search: query='{query}', location={location}")

            # Prepare the actor input
            actor_input = {
                "searchString": query,
                "maxCrawledPlaces": max_results,
                "language": language,
            }

            # Add location if provided
            if location:
                actor_input["locationString"] = location

            # Run the actor
            actor = client.actor(ApifyService.GOOGLE_MAPS_SCRAPER)
            run = actor.call(run_input=actor_input)

            # Fetch results from the dataset
            dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

            # Transform and standardize results
            results = []
            for item in dataset_items:
                competitor = ApifyService._transform_apify_result(item)
                if competitor:
                    results.append(competitor)

            logger.info(f"Apify search completed: found {len(results)} results")
            return results

        except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
            logger.error(f"Apify search failed: {exc}")
            return []

    @staticmethod
    def _transform_apify_result(item: dict[str, Any]) -> dict[str, Any] | None:
        """
        Transform raw Apify result into standardized competitor dict.

        Args:
            item: Raw item from Apify dataset

        Returns:
            Standardized competitor dict or None if required fields missing
        """
        # Extract basic fields
        name = item.get("title") or item.get("name")
        if not name:
            return None

        # Build URL from website or direct link
        url = None
        if item.get("website"):
            url = item["website"]
        elif item.get("dataUri"):
            url = item["dataUri"]

        # Build description from categories and other metadata
        description_parts = []
        if item.get("categories"):
            if isinstance(item["categories"], list):
                description_parts.extend(item["categories"][:3])
            else:
                description_parts.append(str(item["categories"]))

        if item.get("address") and isinstance(item["address"], dict):
            address_parts = [
                item["address"].get("street"),
                item["address"].get("city"),
                item["address"].get("state"),
                item["address"].get("country"),
            ]
            address_str = ", ".join([p for p in address_parts if p])
            if address_str:
                description_parts.append(f"Located in {address_str}")

        description = " | ".join(description_parts) if description_parts else "Business listing"

        # Calculate a base score from rating and review count
        score = 50  # Base score
        if item.get("totalScore"):
            # Google ratings are typically 1-5, normalize to 0-100
            rating = float(item["totalScore"])
            score += int((rating / 5.0) * 30)  # Max 30 points for rating

        if item.get("reviewsCount"):
            # More reviews = more established business
            review_count = int(item["reviewsCount"])
            if review_count > 1000:
                score += 20
            elif review_count > 100:
                score += 10
            elif review_count > 10:
                score += 5

        score = min(100, max(0, score))  # Clamp to 0-100

        return {
            "name": name,
            "url": url or "",
            "score": score,
            "description": description,
            "address": item.get("address", ""),
            "phone": item.get("phone", ""),
            "rating": item.get("totalScore"),
            "review_count": item.get("reviewsCount"),
            "categories": item.get("categories", []),
        }

    @staticmethod
    def scrape_website(url: str) -> dict[str, Any] | None:
        """
        Scrape a website for additional competitor information.

        Uses Apify's Website Content Extractor to get structured data
        from a competitor's website.

        Args:
            url: Website URL to scrape

        Returns:
            Dict with scraped content (title, description, keywords, etc.)
            or None if scraping fails.
        """
        client = ApifyService._get_client()
        if not client:
            return None

        try:
            logger.info(f"Scraping website: {url}")

            actor = client.actor("apify/website-content-extractor")
            run = actor.call(run_input={"url": url})

            dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

            if dataset_items and len(dataset_items) > 0:
                result = dataset_items[0]
                logger.info(f"Successfully scraped {url}")
                return {
                    "title": result.get("title", ""),
                    "description": result.get("description", ""),
                    "keywords": result.get("keywords", []),
                    "text": result.get("text", "")[:5000],  # Limit text length
                }

            return None

        except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
            logger.error(f"Website scraping failed for {url}: {exc}")
            return None

    @staticmethod
    def is_configured() -> bool:
        """Check if Apify is properly configured with an API token."""
        return bool(settings.APIFY_API_TOKEN)
