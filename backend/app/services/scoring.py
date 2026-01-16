import random
from typing import Dict, Any, Optional

def score_event(event_data: Dict[str, Any]) -> int:
    """
    Simulates an AI algorithm that assigns a score from 1 to 10 to an event.
    Events of type 'price' or 'new_entrant' have a higher probability of receiving a high score (>7).
    """
    event_type = event_data.get("event_type")
    
    # Base probability distribution: usually lower scores
    # If high impact type, skew towards higher scores
    if event_type in ["price", "new_entrant"]:
        # 70% chance of being 8, 9, or 10
        # 30% chance of being 1-7
        if random.random() < 0.7:
            return random.randint(8, 10)
        else:
            return random.randint(4, 7) # Still likely significant
    
    # Normal distribution logic for other events (feature, health, etc.)
    # Weighted slightly towards mid-range
    return random.choices(
        population=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        weights=[5, 10, 15, 20, 20, 15, 10, 3, 1, 1],
        k=1
    )[0]

def is_breakthrough_signal(score: int) -> bool:
    """
    Returns True if the score implies a breakthrough signal (score > 7).
    """
    return score > 7

def categorize_event_by_description(description: str) -> Optional[str]:
    """
    Categorizes events based on keywords in the description.
    Returns a string category (e.g., 'pricing', 'feature', 'hiring') or None if no match.
    """
    desc_lower = description.lower()
    
    if any(keyword in desc_lower for keyword in ["price", "pricing", "cost", "subscription", "plan", "discount"]):
        return "pricing"
    if any(keyword in desc_lower for keyword in ["feature", "launch", "release", "update", "beta", "module"]):
        return "feature"
    if any(keyword in desc_lower for keyword in ["hiring", "job", "career", "team", "recruit"]):
        return "hiring"
    if any(keyword in desc_lower for keyword in ["funding", "invest", "raise", "capital"]):
        return "funding"
    
    return None

def generate_competitor_insights(competitor_name: str) -> Dict[str, Any]:
    """
    Generates mock insights for a given competitor.
    """
    # Deterministic randomness based on name hash for consistent mock data
    random.seed(competitor_name)
    
    est_revenue = f"${random.randint(1, 100)}M"
    strengths = [
        "Strong market presence", "Innovative R&D", "Loyal customer base", 
        "Aggressive pricing", "High brand value"
    ]
    weaknesses = [
        "High churn rate", "Legacy technology", "Poor support", 
        "Limited global reach", "Slow feature rollout"
    ]
    
    # Reset seed to avoid side effects
    random.seed()
    
    return {
        "competitor": competitor_name,
        "pitch": f"{competitor_name} aims to revolutionize the industry with AI-driven solutions.",
        "estimated_revenue": est_revenue,
        "strengths": random.sample(strengths, 2),
        "weaknesses": random.sample(weaknesses, 2),
        "market_sentiment": random.choice(["Bullish", "Neutral", "Bearish"])
    }
