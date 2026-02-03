from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class NormalizationService:
    def normalize_google_maps_data(self, raw_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalizes the raw output from the Google Maps scraper into a structured format.
        
        Args:
            raw_items: The list of raw items returned by the scraper.
            
        Returns:
            A dictionary containing normalized data:
            - matched: Boolean indicating if a valid result was found.
            - name: The name of the place.
            - score: Normalized score (0-100).
            - address: The address of the place.
            - website: The website URL.
            - phone: The phone number.
            - reviews: A list of review texts.
            - raw_data: The selected raw item (for reference).
        """
        if not raw_items:
            logger.warning("No raw items to normalize.")
            return {"matched": False}

        # We assume the first result is the most relevant one since we search by specific name + location
        item = raw_items[0]
        
        try:
            name = item.get("title") or item.get("name")
            
            # Normalize score from 0-5 to 0-100
            raw_score = item.get("totalScore")
            normalized_score = None
            if raw_score is not None:
                try:
                    normalized_score = float(raw_score) * 20.0
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse score: {raw_score}")

            address = item.get("address")
            website = item.get("website")
            phone = item.get("phone")
            
            # Extract reviews
            reviews_data = item.get("reviews", [])
            reviews_texts = []
            if isinstance(reviews_data, list):
                for review in reviews_data:
                    text = review.get("text")
                    if text:
                        reviews_texts.append(text)
            
            normalized_data = {
                "matched": True,
                "name": name,
                "score": normalized_score,
                "address": address,
                "website": website,
                "phone": phone,
                "reviews": reviews_texts,
                "url": item.get("url"), # Google Maps URL
                # "raw_data": item # Optional: keep raw data if needed for debugging
            }
            
            logger.info(f"Successfully normalized data for: {name}")
            return normalized_data

        except Exception as e:
            logger.error(f"Error normalizing Google Maps data: {str(e)}")
            return {"matched": False, "error": str(e)}

normalization_service = NormalizationService()
