from datetime import date

from pydantic import BaseModel


class EventCount(BaseModel):
    date: date
    count: int

class DashboardStats(BaseModel):
    total_competitors: int
    breakthroughs_today: int
    avg_threat_score: float
    chart_data: list[EventCount]
