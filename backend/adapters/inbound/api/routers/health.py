from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: datetime
    service: str
    version: str


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health check response with status and timestamp.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC),
        service="review-genie-backend",
        version="0.1.0",
    )
