"""
Pydantic schemas for competitive intelligence data.

Defines the structure for parsed AI responses from Gemini,
including SWOT analysis, threat scoring, and key events.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class MarketSentiment(str, Enum):
    """Market sentiment classification."""
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class EventType(str, Enum):
    """Types of competitive events."""
    PRICE = "PRICE"
    FEATURE = "FEATURE"
    HEALTH = "HEALTH"
    NEW_ENTRANT = "NEW_ENTRANT"


class SWOTAnalysis(BaseModel):
    """
    Strengths, Weaknesses, Opportunities, and Threats analysis.
    """
    strengths: List[str] = Field(default_factory=list, description="Key strengths of the competitor")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses of the competitor")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities for the competitor")
    threats: List[str] = Field(default_factory=list, description="Threats posed by the competitor")

    @field_validator("*", mode="before")
    @classmethod
    def ensure_list(cls, v):
        """Ensure all fields are lists, even if AI returns a string."""
        if isinstance(v, str):
            return [v]
        return v if v is not None else []


class KeyEvent(BaseModel):
    """
    A detected competitive event (price change, feature launch, etc.).
    """
    type: EventType = Field(description="Type of the event")
    description: str = Field(description="Description of the event")
    score: float = Field(default=50.0, ge=0, le=100, description="Confidence score for this event (0-100)")

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v):
        """Normalize event type string to enum."""
        if isinstance(v, str):
            v_upper = v.upper()
            # Try exact match first
            try:
                return EventType(v_upper)
            except ValueError:
                # Fuzzy match for common variations
                if "PRICE" in v_upper or "PRICING" in v_upper:
                    return EventType.PRICE
                elif "FEATURE" in v_upper or "PRODUCT" in v_upper:
                    return EventType.FEATURE
                elif "HEALTH" in v_upper or "FINANCIAL" in v_upper or "FUNDING" in v_upper:
                    return EventType.HEALTH
                elif "ENTRANT" in v_upper or "EXPANSION" in v_upper or "MARKET" in v_upper:
                    return EventType.NEW_ENTRANT
        return v


class IntelligenceReport(BaseModel):
    """
    Complete competitive intelligence report from AI analysis.

    This schema matches the expected JSON output from Gemini's
    competitive intelligence analysis.
    """
    swot_analysis: SWOTAnalysis = Field(description="Complete SWOT analysis")
    sentinel_score: int = Field(default=50, ge=0, le=100, description="Competitive threat score (0-100)")
    market_sentiment: MarketSentiment = Field(default=MarketSentiment.NEUTRAL, description="Overall market sentiment")
    pitch: str = Field(default="", description="Brief 1-2 sentence summary of the competitor")
    key_events: List[KeyEvent] = Field(default_factory=list, description="Detected competitive events")

    @field_validator("sentinel_score", mode="before")
    @classmethod
    def normalize_score(cls, v):
        """Ensure score is an integer between 0-100."""
        if isinstance(v, float):
            v = int(v)
        if v < 0:
            return 0
        if v > 100:
            return 100
        return v

    @field_validator("market_sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, v):
        """Normalize sentiment string to enum."""
        if isinstance(v, str):
            v_lower = v.lower()
            if "positive" in v_lower:
                return MarketSentiment.POSITIVE
            elif "negative" in v_lower:
                return MarketSentiment.NEGATIVE
            return MarketSentiment.NEUTRAL
        return v

    @field_validator("key_events", mode="before")
    @classmethod
    def ensure_events_list(cls, v):
        """Ensure events is always a list."""
        if v is None:
            return []
        if isinstance(v, dict):
            # Single event as dict
            return [v]
        return v


class IntelligenceParseError(BaseModel):
    """
    Schema for tracking parsing errors when AI output is malformed.
    """
    raw_response: str = Field(description="The raw AI response that failed to parse")
    error_message: str = Field(description="Error description")
    partial_data: Optional[dict] = Field(default=None, description="Any partial data that could be extracted")


def parse_intelligence_response(ai_response: str) -> IntelligenceReport:
    """
    Parse and validate an AI response into an IntelligenceReport.

    Cleans the response (removes markdown code blocks if present),
    parses as JSON, and validates against the schema.

    Args:
        ai_response: Raw text response from Gemini AI

    Returns:
        Validated IntelligenceReport object

    Raises:
        ValueError: If the response is malformed or cannot be parsed
    """
    import json
    import re

    if not ai_response or not ai_response.strip():
        raise ValueError("Empty AI response")

    # Clean the response - remove markdown code blocks
    cleaned = ai_response.strip()

    # Remove ```json and ``` markers
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)

    # Try to extract JSON if there's surrounding text
    json_match = re.search(r'\{[\s\S]*\}', cleaned)
    if json_match:
        cleaned = json_match.group(0)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to fix common JSON issues
        # Remove trailing commas
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        # Fix unquoted keys
        cleaned = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', cleaned)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e2:
            raise ValueError(f"Failed to parse AI response as JSON: {e2}") from e2

    # Validate and create the report
    try:
        return IntelligenceReport(**data)
    except Exception as e:
        raise ValueError(f"AI response does not match IntelligenceReport schema: {e}") from e


def safe_parse_intelligence_response(ai_response: str) -> tuple[IntelligenceReport | None, IntelligenceParseError | None]:
    """
    Safely parse an AI response with comprehensive error handling.

    Unlike parse_intelligence_response, this function does not raise exceptions.
    Instead, it returns a tuple of (report, error) where one is always None.

    Args:
        ai_response: Raw text response from Gemini AI

    Returns:
        Tuple of (IntelligenceReport or None, IntelligenceParseError or None)
    """
    try:
        report = parse_intelligence_response(ai_response)
        return report, None
    except Exception as e:
        error = IntelligenceParseError(
            raw_response=ai_response[:1000],  # Truncate for storage
            error_message=str(e)
        )
        return None, error
