import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.clients.n8n_client import N8nWebhookError
from app.repositories.analysis_repository import (
    AnalysisNotFoundError,
    AnalysisRepositoryError,
)
from app.services.analysis_service import DuplicateAnalysisError
from app.services.storage_service import StorageError

logger = structlog.get_logger(__name__)


def _error_response(message: str, code: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {"message": message, "code": code},
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    first = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first.get("loc", []))
    msg = first.get("msg", "Validation error")
    logger.warning("request_validation_error", path=request.url.path, errors=errors)
    return _error_response(
        message=f"Validation error on '{field}': {msg}",
        code="VALIDATION_ERROR",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


async def analysis_not_found_handler(
    request: Request, exc: AnalysisNotFoundError
) -> JSONResponse:
    logger.info("analysis_not_found", path=request.url.path, error=str(exc))
    return _error_response(
        message=str(exc),
        code="NOT_FOUND",
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def duplicate_analysis_handler(
    request: Request, exc: DuplicateAnalysisError
) -> JSONResponse:
    logger.info("duplicate_analysis", path=request.url.path, error=str(exc))
    return _error_response(
        message=str(exc),
        code="DUPLICATE_ANALYSIS",
        status_code=status.HTTP_409_CONFLICT,
    )


async def n8n_webhook_error_handler(
    request: Request, exc: N8nWebhookError
) -> JSONResponse:
    logger.error("n8n_webhook_error", path=request.url.path, error=str(exc))
    return _error_response(
        message="Failed to trigger analysis workflow. Please try again later.",
        code="UPSTREAM_ERROR",
        status_code=status.HTTP_502_BAD_GATEWAY,
    )


async def storage_error_handler(
    request: Request, exc: StorageError
) -> JSONResponse:
    logger.error("storage_error", path=request.url.path, error=str(exc))
    return _error_response(
        message="Storage operation failed. Please try again later.",
        code="STORAGE_ERROR",
        status_code=status.HTTP_502_BAD_GATEWAY,
    )


async def repository_error_handler(
    request: Request, exc: AnalysisRepositoryError
) -> JSONResponse:
    logger.error("repository_error", path=request.url.path, error=str(exc))
    return _error_response(
        message="Database operation failed. Please try again later.",
        code="DATABASE_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    return _error_response(
        message="An unexpected error occurred",
        code="INTERNAL_ERROR",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app) -> None:  # noqa: ANN001
    """Register all exception handlers on the FastAPI application."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(AnalysisNotFoundError, analysis_not_found_handler)
    app.add_exception_handler(DuplicateAnalysisError, duplicate_analysis_handler)
    app.add_exception_handler(N8nWebhookError, n8n_webhook_error_handler)
    app.add_exception_handler(StorageError, storage_error_handler)
    app.add_exception_handler(AnalysisRepositoryError, repository_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
