from typing import List
from pydantic import BaseModel
from datetime import date

class EventCount(BaseModel):
    date: date
    count: int

class DashboardStats(BaseModel):
    total_competitors: int
    breakthroughs_today: int
    avg_threat_score: float
    chart_data: List[EventCount]
