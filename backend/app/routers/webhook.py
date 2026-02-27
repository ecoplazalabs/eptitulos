import base64
from datetime import datetime
from typing import Literal

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.repositories.analysis_repository import AnalysisNotFoundError, AnalysisRepository
from app.services.storage_service import StorageService, get_storage_service_singleton

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/internal", tags=["internal"])


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


def verify_api_key(x_api_key: str = Header(...)) -> None:
    """
    Validate the X-Api-Key header against the configured n8n_api_key.

    Raises HTTP 401 if missing or incorrect.
    """
    if x_api_key != settings.n8n_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class CargaItem(BaseModel):
    tipo: str
    detalle: str
    vigente: bool | None = None
    fecha: str | None = None


class AnalysisCallbackRequest(BaseModel):
    analysis_id: str
    status: Literal["completed", "failed"]
    total_asientos: int | None = None
    cargas_encontradas: list[CargaItem] | None = None
    informe: str | None = None
    error_message: str | None = None
    started_at: str | None = None   # ISO 8601 datetime string
    completed_at: str | None = None # ISO 8601 datetime string
    pdf_base64: str | None = None   # base64-encoded PDF bytes


class CallbackResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse an ISO 8601 datetime string to a timezone-aware datetime object."""
    if value is None:
        return None
    # Replace trailing 'Z' to satisfy Python's fromisoformat before 3.11
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/analysis-callback",
    response_model=CallbackResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_api_key)],
)
async def analysis_callback(
    body: AnalysisCallbackRequest,
    session: AsyncSession = Depends(get_db),
    storage: StorageService = Depends(get_storage_service_singleton),
) -> CallbackResponse:
    """
    Internal endpoint called by n8n to report the result of a SUNARP analysis.

    Authentication is via the X-Api-Key header (service-to-service).
    No JWT user authentication is required.
    """
    logger.info(
        "analysis_callback_received",
        analysis_id=body.analysis_id,
        status=body.status,
    )

    repo = AnalysisRepository(session)

    # Resolve the analysis and get the owner user_id for storage paths
    try:
        record = await repo.get_by_id_internal(body.analysis_id)
    except AnalysisNotFoundError:
        logger.warning("analysis_callback_not_found", analysis_id=body.analysis_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {body.analysis_id} not found",
        ) from None

    user_id: str = record["requested_by"]

    # Decode and persist the PDF if provided
    pdf_path: str | None = None
    if body.pdf_base64:
        try:
            pdf_bytes = base64.b64decode(body.pdf_base64)
            pdf_path = storage.save_pdf(
                user_id=user_id,
                analysis_id=body.analysis_id,
                file_bytes=pdf_bytes,
            )
            logger.info(
                "analysis_callback_pdf_saved",
                analysis_id=body.analysis_id,
                pdf_path=pdf_path,
            )
        except Exception as exc:
            # Log but do not abort the callback — results matter more than the PDF
            logger.error(
                "analysis_callback_pdf_save_failed",
                analysis_id=body.analysis_id,
                error=str(exc),
            )

    started_at = _parse_iso_datetime(body.started_at)
    completed_at = _parse_iso_datetime(body.completed_at)

    cargas_dicts: list[dict] | None = (
        [c.model_dump() for c in body.cargas_encontradas]
        if body.cargas_encontradas is not None
        else None
    )

    await repo.update_result(
        analysis_id=body.analysis_id,
        status=body.status,
        total_asientos=body.total_asientos,
        cargas_encontradas=cargas_dicts,
        informe=body.informe,
        error_message=body.error_message,
        started_at=started_at,
        completed_at=completed_at,
        pdf_path=pdf_path,
    )

    logger.info(
        "analysis_callback_processed",
        analysis_id=body.analysis_id,
        status=body.status,
    )
    return CallbackResponse(status="ok")
