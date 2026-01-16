import random
from typing import List, Dict, Any, Annotated

from fastapi import APIRouter, Depends
from sqlmodel import SQLModel

from app.api.deps import get_current_user
from app.models.user import User
from app.services.scoring import generate_competitor_insights

router = APIRouter()

class RadarCompetitor(SQLModel):
    name: str
    url: str
    threat_score: int
    insights: Dict[str, Any]

@router.get("/", response_model=List[RadarCompetitor])
def search_market_opportunities(
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[RadarCompetitor]:
    """
    Simulate a market search to find potential competitors (Radar).
    Returns a list of untracked entities with AI-generated insights and threat scores.
    """
    
    # Mock potential competitors
    candidates = [
        {"name": "Vortex AI", "url": "https://vortex.ai"},
        {"name": "NebulaSoft", "url": "https://nebulasoft.io"},
        {"name": "Quantum Leap", "url": "https://quantumleap.tech"},
        {"name": "Echo Systems", "url": "https://echosystems.com"},
        {"name": "Stratosphere", "url": "https://stratosphere.net"},
    ]
    
    results = []
    
    # Randomly select 3-5 candidates to show
    selected_candidates = random.sample(candidates, k=random.randint(3, 5))
    
    for candidate in selected_candidates:
        # Generate insights
        insights = generate_competitor_insights(candidate["name"])
        
        # Generate a mock threat score (1-100)
        # In a real app, this would be based on the insights analysis
        threat_score = random.randint(30, 95)
        
        results.append(
            RadarCompetitor(
                name=candidate["name"],
                url=candidate["url"],
                threat_score=threat_score,
                insights=insights
            )
        )
        
    # Sort by threat score descending
    results.sort(key=lambda x: x.threat_score, reverse=True)
    
    return results
