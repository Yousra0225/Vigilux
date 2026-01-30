import uuid
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from app.models.competitor import TrackingStatus

class CompetitorBase(BaseModel):
    name: str
    url: str

class CompetitorCreate(CompetitorBase):
    project_id: uuid.UUID
    status: Optional[TrackingStatus] = TrackingStatus.ACTIVE

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    status: Optional[TrackingStatus] = None
    score: Optional[float] = None

class CompetitorRead(CompetitorBase):
    id: uuid.UUID
    project_id: uuid.UUID
    status: TrackingStatus
    score: Optional[float] = None

    class Config:
        from_attributes = True

class CompetitorDetail(CompetitorRead):
    pitch: str
    estimated_revenue: str
    strengths: List[str]
    weaknesses: List[str]
    market_sentiment: str

class RadarResult(BaseModel):
    name: str
    url: str
    threat_score: int
    market_presence: str  # e.g., "High", "Medium", "Low"
    pitch: str
    strengths: List[str]
    weaknesses: List[str]
