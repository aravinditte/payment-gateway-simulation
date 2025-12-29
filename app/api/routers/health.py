"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness")
async def readiness_check() -> dict:
    """Readiness check endpoint.

    Returns:
        dict: Readiness status
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }
