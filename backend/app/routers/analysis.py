from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.dependencies import (
    get_analysis_service,
    get_current_user,
    get_storage,
)
from app.models.analysis import (
    AnalysisCreatedResponse,
    AnalysisDetailResponse,
    AnalysisSummaryResponse,
    CreateAnalysisRequest,
)
from app.models.common import ApiResponse, PaginatedResponse
from app.repositories.analysis_repository import AnalysisNotFoundError
from app.services.analysis_service import AnalysisNotCancellableError, AnalysisService
from app.services.storage_service import StorageError, StorageService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/sunarp", tags=["analysis"])

MAX_PER_PAGE = 100


@router.post(
    "/analyze",
    response_model=ApiResponse[AnalysisCreatedResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_analysis(
    body: CreateAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[AnalysisCreatedResponse]:
    """
    Create a new SUNARP analysis request.

    - Validates input (oficina, partida).
    - Rejects duplicate in-progress requests (409).
    - Inserts a pending record in the database.
    - Triggers the n8n workflow.
    - Returns the analysis ID for polling.
    """
    user_id: str = current_user["id"]
    logger.info(
        "create_analysis_request",
        user_id=user_id,
        oficina=body.oficina,
        partida=body.partida,
    )
    created = await service.create_analysis(request=body, user_id=user_id)
    return ApiResponse(data=created)


@router.get(
    "/analyses",
    response_model=PaginatedResponse[AnalysisSummaryResponse],
)
async def list_analyses(
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=MAX_PER_PAGE)] = 20,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> PaginatedResponse[AnalysisSummaryResponse]:
    """
    List analyses for the authenticated user, ordered by creation date descending.

    Supports pagination via `page` and `per_page` query params.
    Optionally filter by `status` (pending, processing, completed, failed).
    """
    user_id: str = current_user["id"]
    summaries, pagination = await service.list_analyses(
        user_id=user_id,
        page=page,
        per_page=per_page,
        status=status_filter,
    )
    return PaginatedResponse(data=summaries, pagination=pagination)


@router.get(
    "/analyses/{analysis_id}",
    response_model=ApiResponse[AnalysisDetailResponse],
)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[AnalysisDetailResponse]:
    """
    Get full detail for a single analysis.

    This endpoint is polled by the frontend every 5 seconds while the analysis
    is in 'pending' or 'processing' status.
    """
    user_id: str = current_user["id"]
    detail = await service.get_analysis(analysis_id=analysis_id, user_id=user_id)
    return ApiResponse(data=detail)


@router.get("/analyses/{analysis_id}/pdf")
async def get_pdf(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
    storage: StorageService = Depends(get_storage),
) -> FileResponse:
    """
    Stream the PDF copia literal for a completed analysis.

    Returns 404 if the analysis does not have an associated PDF yet.
    """
    user_id: str = current_user["id"]
    pdf_path = await service.get_pdf_storage_path(
        analysis_id=analysis_id, user_id=user_id
    )

    if not pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This analysis does not have an associated PDF yet",
        )

    try:
        full_path: Path = storage.get_pdf_path(pdf_path)
    except StorageError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found",
        ) from None

    return FileResponse(
        path=str(full_path),
        media_type="application/pdf",
        filename=f"copia_literal_{analysis_id}.pdf",
    )


@router.delete(
    "/analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> None:
    """
    Hard-delete an analysis owned by the authenticated user.

    Returns 404 if the analysis does not exist or belongs to another user.
    Returns 409 if the analysis is currently in 'processing' status.
    Returns 204 No Content on success.
    """
    user_id: str = current_user["id"]
    logger.info("delete_analysis_request", user_id=user_id, analysis_id=analysis_id)

    try:
        await service.delete_analysis(analysis_id=analysis_id, user_id=user_id)
    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        ) from None
    except AnalysisNotCancellableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None


@router.post(
    "/analyses/{analysis_id}/cancel",
    response_model=ApiResponse[AnalysisDetailResponse],
)
async def cancel_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    service: AnalysisService = Depends(get_analysis_service),
) -> ApiResponse[AnalysisDetailResponse]:
    """
    Cancel a pending or processing analysis.

    Sets status to 'failed' with error_message 'Cancelled by user'.
    Returns 404 if the analysis does not exist or belongs to another user.
    Returns 409 if the analysis status is not 'pending' or 'processing'.
    Returns the updated analysis on success.
    """
    user_id: str = current_user["id"]
    logger.info("cancel_analysis_request", user_id=user_id, analysis_id=analysis_id)

    try:
        updated = await service.cancel_analysis(analysis_id=analysis_id, user_id=user_id)
    except AnalysisNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        ) from None
    except AnalysisNotCancellableError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from None

    return ApiResponse(data=updated)
