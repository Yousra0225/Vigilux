import uuid

from pydantic import BaseModel

from app.models.competitor import TrackingStatus


class CompetitorBase(BaseModel):
    name: str
    url: str

class CompetitorCreate(CompetitorBase):
    project_id: uuid.UUID
    status: TrackingStatus | None = TrackingStatus.ACTIVE

class CompetitorUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    status: TrackingStatus | None = None
    score: float | None = None

class CompetitorRead(CompetitorBase):
    id: uuid.UUID
    project_id: uuid.UUID
    status: TrackingStatus
    score: float | None = None

    class Config:
        from_attributes = True

class CompetitorDetail(CompetitorRead):
    pitch: str
    estimated_revenue: str
    strengths: list[str]
    weaknesses: list[str]
    market_sentiment: str

class RadarResult(BaseModel):
    name: str
    url: str
    threat_score: int
    market_presence: str  # e.g., "High", "Medium", "Low"
    pitch: str
    strengths: list[str]
    weaknesses: list[str]
