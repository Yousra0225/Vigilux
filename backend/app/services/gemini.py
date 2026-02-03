import logging
from typing import Optional, Dict, Any

from app.core.config import settings
from app.services.intelligence_prompts import IntelligencePrompts
from app.schemas.intelligence import IntelligenceReport, safe_parse_intelligence_response

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google's Generative AI (Gemini) API
    for intelligence analysis.

    Provides insight generation from raw text data such as reviews,
    descriptions, and other competitor information.
    """

    # Model configurations
    MODEL_NAME = "gemini-1.5-pro-latest"
    MODEL_FALLBACK = "gemini-pro"

    # Safety settings for business analysis use case
    # Use BLOCK_NONE to be permissive for legitimate business content
    SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    @staticmethod
    def _get_client():
        """
        Initialize and return the generative AI client.

        Returns None if GEMINI_API_KEY is not configured.

        Returns:
            genai.GenerativeModel or None
        """
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured - Gemini features disabled")
            return None

        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            return genai
        except ImportError:
            logger.error("google-generativeai not installed. Run: pip install google-generativeai")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            return None

    @staticmethod
    def _get_model():
        """
        Get a configured GenerativeModel instance.

        Attempts to use the preferred model, falls back to gemini-pro
        if the preferred model is unavailable.

        Returns:
            genai.GenerativeModel or None
        """
        genai = GeminiService._get_client()
        if not genai:
            return None

        try:
            model = genai.GenerativeModel(
                model_name=GeminiService.MODEL_NAME,
                safety_settings=GeminiService.SAFETY_SETTINGS,
            )
            logger.debug(f"Using Gemini model: {GeminiService.MODEL_NAME}")
            return model
        except Exception as e:
            logger.warning(f"Failed to initialize {GeminiService.MODEL_NAME}: {e}")
            try:
                model = genai.GenerativeModel(
                    model_name=GeminiService.MODEL_FALLBACK,
                    safety_settings=GeminiService.SAFETY_SETTINGS,
                )
                logger.debug(f"Using fallback Gemini model: {GeminiService.MODEL_FALLBACK}")
                return model
            except Exception as fallback_error:
                logger.error(f"Failed to initialize Gemini model: {fallback_error}")
                return None

    @staticmethod
    def generate_insight(text_data: str) -> Optional[str]:
        """
        Generate an insight from raw text data using Gemini.

        Takes raw text (reviews, descriptions, competitor information)
        and sends it to the model for analysis.

        Args:
            text_data: Raw text content to analyze

        Returns:
            str: Generated insight text, or None if generation fails

        Raises:
            Does not raise exceptions; logs errors and returns None
        """
        if not text_data or not text_data.strip():
            logger.warning("Empty text_data provided to generate_insight")
            return None

        model = GeminiService._get_model()
        if not model:
            logger.info("Gemini model not available - would return None")
            return None

        try:
            logger.info(f"Generating insight from {len(text_data)} characters of text")

            # Truncate input if too long (Gemini has token limits)
            max_input_length = 100000  # Conservative limit
            if len(text_data) > max_input_length:
                text_data = text_data[:max_input_length]
                logger.debug(f"Truncated input to {max_input_length} characters")

            response = model.generate_content(text_data)

            if response.parts:
                result = response.text
                logger.info(f"Successfully generated insight: {len(result)} characters")
                return result
            else:
                logger.warning("Gemini returned empty response")
                return None

        except Exception as e:
            logger.error(f"Gemini insight generation failed: {e}")
            return None

    @staticmethod
    def is_configured() -> bool:
        """Check if Gemini is properly configured with an API key."""
        return bool(settings.GEMINI_API_KEY)

    @staticmethod
    def analyze_competitor_intelligence(
        competitor_name: str,
        raw_data: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[IntelligenceReport]:
        """
        Generate structured competitive intelligence from raw data.

        Uses prompt templates to extract SWOT analysis, threat scoring,
        and key events from competitor data.

        Args:
            competitor_name: Name of the competitor
            raw_data: Raw text data (reviews, descriptions, scraped content)
            additional_context: Optional dict with url, location, categories, etc.

        Returns:
            IntelligenceReport with structured analysis, or None if generation fails
        """
        if not raw_data or not raw_data.strip():
            logger.warning("Empty raw_data provided to analyze_competitor_intelligence")
            return None

        model = GeminiService._get_model()
        if not model:
            logger.info("Gemini model not available - would return None")
            return None

        try:
            # Build the structured prompt
            prompt = IntelligencePrompts.build_analysis_prompt(
                competitor_name=competitor_name,
                raw_data=raw_data,
                additional_context=additional_context
            )

            logger.info(f"Analyzing intelligence for {competitor_name}")

            # Truncate input if too long
            max_input_length = 100000
            if len(prompt) > max_input_length:
                prompt = prompt[:max_input_length]
                logger.debug(f"Truncated prompt to {max_input_length} characters")

            # Generate the response
            response = model.generate_content(prompt)

            if not response.parts:
                logger.warning("Gemini returned empty response for intelligence analysis")
                return None

            raw_response = response.text
            logger.info(f"Received AI response: {len(raw_response)} characters")

            # Parse the JSON response into IntelligenceReport
            report, parse_error = safe_parse_intelligence_response(raw_response)

            if parse_error:
                logger.error(f"Failed to parse intelligence response: {parse_error.error_message}")
                logger.debug(f"Raw response: {raw_response[:500]}")
                return None

            logger.info(
                f"Successfully generated intelligence report: "
                f"score={report.sentinel_score}, "
                f"sentiment={report.market_sentiment}, "
                f"events={len(report.key_events)}"
            )
            return report

        except Exception as e:
            logger.error(f"Competitor intelligence analysis failed: {e}")
            return None

    @staticmethod
    def analyze_from_scraped_data(
        name: str,
        description: str,
        reviews: Optional[list[str]] = None,
        **kwargs
    ) -> Optional[IntelligenceReport]:
        """
        Analyze competitor from structured scraped data.

        Convenience method that builds prompt from structured data
        and returns structured intelligence report.

        Args:
            name: Competitor name
            description: Business description
            reviews: List of review strings
            **kwargs: Additional context (url, location, categories, etc.)

        Returns:
            IntelligenceReport with structured analysis, or None if generation fails
        """

        # Build raw data string
        raw_parts = [f"Description: {description}"]

        if reviews:
            raw_parts.append("\nReviews:")
            raw_parts.extend(f"- {r}" for r in reviews[:20])

        raw_data = "\n".join(raw_parts)

        return GeminiService.analyze_competitor_intelligence(
            competitor_name=name,
            raw_data=raw_data,
            additional_context=kwargs
        )
