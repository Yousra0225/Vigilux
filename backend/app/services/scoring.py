import random
from typing import Dict, Any, List

from app.models.event import Event, EventType

class ScoringService:
    @staticmethod
    def calculate_score(event_type: EventType, description: str) -> int:
        """
        Mock scoring engine.
        Assigns a score between 1-100 based on event type and randomness.
        """
        base_score = 50
        variance = random.randint(-20, 20)
        
        if event_type == EventType.PRICE:
            if "decreased" in description.lower() or "deal" in description.lower():
                base_score = 80
            else:
                base_score = 60
        elif event_type == EventType.FEATURE:
            base_score = 70
        elif event_type == EventType.HEALTH:
            if "downtime" in description.lower() or "resigned" in description.lower() or "layoff" in description.lower():
                 base_score = 90 # High impact negative event
            else:
                 base_score = 40
        elif event_type == EventType.NEW_ENTRANT:
            base_score = 65

        final_score = max(1, min(100, base_score + variance))
        return final_score

    @staticmethod
    def analyze_event(event: Event) -> Dict[str, Any]:
        """
        Analyze an event and return insights.
        """
        is_breakthrough = event.score is not None and event.score > 70
        
        category = "Standard Update"
        if is_breakthrough:
            if event.type == EventType.PRICE:
                category = "Major Price Shift"
            elif event.type == EventType.FEATURE:
                category = "Feature Breakthrough"
            elif event.type == EventType.HEALTH:
                category = "Critical Health Signal"
            elif event.type == EventType.NEW_ENTRANT:
                category = "Disruptive Entrant"

        return {
            "score": event.score,
            "is_breakthrough": is_breakthrough,
            "category": category
        }
