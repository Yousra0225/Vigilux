"""
Prompt templates for competitive intelligence extraction using Gemini AI.

Provides structured prompts to extract SWOT analysis, threat scoring,
and key events from raw competitor data.
"""

from typing import Dict, Any, List


class IntelligencePrompts:
    """
    Prompt templates for generating competitive intelligence analysis.

    All prompts are designed to return valid JSON that can be parsed
    into Pydantic schemas for structured data extraction.
    """

    # JSON schema description for the AI to follow
    RESPONSE_SCHEMA = """
You must respond with a valid JSON object following this exact structure:
{
  "swot_analysis": {
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "opportunities": ["opportunity1", "opportunity2", ...],
    "threats": ["threat1", "threat2", ...]
  },
  "sentinel_score": <integer 0-100>,
  "market_sentiment": "Positive | Neutral | Negative",
  "pitch": "<brief 1-2 sentence summary>",
  "key_events": [
    {
      "type": "PRICE | FEATURE | HEALTH | NEW_ENTRANT",
      "description": "<event description>",
      "score": <float 0-100, confidence score>
    }
  ]
}
"""

    BASE_ANALYSIS_PROMPT = """You are a competitive intelligence analyst. Analyze the following competitor data and extract key insights.

COMPETITOR DATA:
{competitor_data}

ANALYSIS INSTRUCTIONS:
1. Perform a SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
2. Calculate a "Sentinel Score" (0-100) representing the competitive threat level
3. Determine overall market sentiment (Positive/Neutral/Negative)
4. Create a brief 1-2 sentence pitch summarizing this competitor
5. Identify key events such as price changes, new features, business health changes, or market entry

{response_schema}

IMPORTANT: Respond ONLY with valid JSON. Do not include markdown formatting, explanations, or any text outside the JSON structure.
"""

    @staticmethod
    def build_analysis_prompt(
        competitor_name: str,
        raw_data: str,
        additional_context: Dict[str, Any] | None = None
    ) -> str:
        """
        Build a complete analysis prompt from raw competitor data.

        Args:
            competitor_name: Name of the competitor being analyzed
            raw_data: Raw text data (reviews, descriptions, scraped content)
            additional_context: Optional dict with url, location, categories, etc.

        Returns:
            Formatted prompt string ready for Gemini API
        """
        # Build context section
        context_parts = [f"Name: {competitor_name}"]

        if additional_context:
            if "url" in additional_context:
                context_parts.append(f"Website: {additional_context['url']}")
            if "location" in additional_context:
                context_parts.append(f"Location: {additional_context['location']}")
            if "categories" in additional_context and additional_context["categories"]:
                categories = ", ".join(additional_context["categories"])
                context_parts.append(f"Categories: {categories}")
            if "rating" in additional_context:
                context_parts.append(f"Rating: {additional_context['rating']}")
            if "review_count" in additional_context:
                context_parts.append(f"Review Count: {additional_context['review_count']}")

        # Combine context with raw data
        competitor_data = "\n".join(context_parts) + "\n\n" + raw_data

        # Build the full prompt
        return IntelligencePrompts.BASE_ANALYSIS_PROMPT.format(
            competitor_data=competitor_data,
            response_schema=IntelligencePrompts.RESPONSE_SCHEMA
        )

    @staticmethod
    def build_swot_only_prompt(raw_data: str) -> str:
        """
        Build a simplified prompt focused only on SWOT analysis.

        Args:
            raw_data: Raw text data to analyze

        Returns:
            Formatted prompt string for SWOT extraction
        """
        return f"""Analyze the following data and provide a SWOT analysis.

DATA:
{raw_data}

{IntelligencePrompts.RESPONSE_SCHEMA}

Respond ONLY with valid JSON. Include swot_analysis and set sentinel_score to 50 (neutral) if not applicable.
"""

    @staticmethod
    def build_events_detection_prompt(
        competitor_name: str,
        recent_data: str,
        previous_data: str | None = None
    ) -> str:
        """
        Build a prompt focused on detecting competitive events.

        Args:
            competitor_name: Name of the competitor
            recent_data: Recent competitor data
            previous_data: Optional previous data for comparison

        Returns:
            Formatted prompt string for event detection
        """
        comparison = ""
        if previous_data:
            comparison = f"\nPREVIOUS DATA (for comparison):\n{previous_data}\n"

        return f"""Detect key competitive events for this competitor.

COMPETITOR: {competitor_name}
{comparison}
RECENT DATA:
{recent_data}

Identify events of these types:
- PRICE: Price changes, discount offers, pricing strategy shifts
- FEATURE: New product launches, feature additions, product updates
- HEALTH: Business health changes, funding announcements, leadership changes
- NEW_ENTRANT: Market expansion, new geographic entry, partnerships

{IntelligencePrompts.RESPONSE_SCHEMA}

Respond ONLY with valid JSON. Focus on key_events array and provide relevant swot_analysis.
"""


class PromptBuilder:
    """
    Utility class for building intelligence prompts with various configurations.
    """

    @staticmethod
    def from_scraped_data(
        name: str,
        description: str,
        reviews: List[str] | None = None,
        **kwargs
    ) -> str:
        """
        Build prompt from structured scraped data.

        Args:
            name: Competitor name
            description: Business description
            reviews: List of review strings
            **kwargs: Additional context (url, location, categories, etc.)

        Returns:
            Formatted analysis prompt
        """
        raw_parts = [f"Description: {description}"]

        if reviews:
            raw_parts.append("\nReviews:")
            raw_parts.extend(f"- {r}" for r in reviews[:20])  # Limit to 20 reviews

        raw_data = "\n".join(raw_parts)
        return IntelligencePrompts.build_analysis_prompt(name, raw_data, kwargs)

    @staticmethod
    def from_apify_result(result: Dict[str, Any]) -> str:
        """
        Build prompt directly from Apify scraper result.

        Args:
            result: Raw Apify result dict

        Returns:
            Formatted analysis prompt
        """
        name = result.get("title") or result.get("name", "Unknown")

        # Extract description from categories and other metadata
        parts = []
        if "categories" in result and result["categories"]:
            parts.append(f"Categories: {', '.join(result['categories'][:5])}")

        # Add reviews if available
        if "reviews" in result and result["reviews"]:
            parts.append("\nRecent Reviews:")
            for review in result["reviews"][:10]:
                text = review.get("text") or review.get("comment", "")
                if text:
                    parts.append(f"- {text}")

        raw_data = "\n".join(parts)

        # Build additional context
        context = {
            "url": result.get("website") or result.get("dataUri"),
            "location": result.get("address", {}).get("city") if isinstance(result.get("address"), dict) else None,
            "categories": result.get("categories", []),
            "rating": result.get("totalScore"),
            "review_count": result.get("reviewsCount"),
        }

        return IntelligencePrompts.build_analysis_prompt(name, raw_data, context)
