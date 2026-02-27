from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint. No authentication required."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(tz=UTC),
    )
