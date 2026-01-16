"""Vigilux Backend - Health Check API."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        A dictionary with status information.
    """
    return {"status": "ok"}
