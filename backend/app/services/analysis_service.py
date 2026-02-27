import structlog

from app.clients.n8n_client import N8nWebhookError, trigger_sunarp_analysis
from app.models.analysis import (
    AnalysisCreatedResponse,
    AnalysisDetailResponse,
    AnalysisSummaryResponse,
    Carga,
    CreateAnalysisRequest,
)
from app.models.common import PaginationMeta
from app.repositories.analysis_repository import AnalysisRepository

logger = structlog.get_logger(__name__)


class DuplicateAnalysisError(Exception):
    """Raised when a pending/processing analysis already exists for this partida."""


class AnalysisService:
    def __init__(self, repository: AnalysisRepository) -> None:
        self._repo = repository

    async def create_analysis(
        self,
        request: CreateAnalysisRequest,
        user_id: str,
    ) -> AnalysisCreatedResponse:
        """
        Create a new SUNARP analysis request.

        1. Check for in-progress duplicate.
        2. Insert record with status='pending'.
        3. Trigger n8n webhook.
        4. On n8n failure: mark record as 'failed' and raise N8nWebhookError.
        """
        log = logger.bind(
            user_id=user_id,
            oficina=request.oficina,
            partida=request.partida,
        )

        is_duplicate = await self._repo.check_duplicate(
            user_id=user_id,
            oficina=request.oficina,
            partida=request.partida,
        )
        if is_duplicate:
            log.warning("analysis_duplicate_rejected")
            raise DuplicateAnalysisError(
                f"An analysis for partida '{request.partida}' in oficina "
                f"'{request.oficina}' is already in progress"
            )

        record = await self._repo.create(
            {
                "requested_by": user_id,
                "oficina": request.oficina,
                "partida": request.partida,
                "area_registral": request.area_registral,
                "status": "pending",
            }
        )

        analysis_id: str = record["id"]
        log = log.bind(analysis_id=analysis_id)
        log.info("analysis_record_created")

        try:
            await trigger_sunarp_analysis(
                analysis_id=analysis_id,
                oficina=request.oficina,
                partida=request.partida,
                area_registral=request.area_registral,
            )
        except N8nWebhookError as exc:
            log.error("n8n_trigger_failed", error=str(exc))
            await self._repo.update_status(
                analysis_id=analysis_id,
                status="failed",
                error_message=f"Failed to trigger analysis workflow: {exc}",
            )
            raise

        return AnalysisCreatedResponse(
            id=record["id"],
            status=record["status"],
            oficina=record["oficina"],
            partida=record["partida"],
            created_at=record["created_at"],
        )

    async def get_analysis(
        self,
        analysis_id: str,
        user_id: str,
    ) -> AnalysisDetailResponse:
        """
        Retrieve full detail for a single analysis.

        Raises AnalysisNotFoundError if not found or not owned by user_id.
        """
        record = await self._repo.get_by_id(analysis_id=analysis_id, user_id=user_id)
        return _map_to_detail(record)

    async def list_analyses(
        self,
        user_id: str,
        page: int,
        per_page: int,
        status: str | None = None,
    ) -> tuple[list[AnalysisSummaryResponse], PaginationMeta]:
        """Return a paginated list of analyses for the authenticated user."""
        rows, total = await self._repo.list_by_user(
            user_id=user_id,
            page=page,
            per_page=per_page,
            status=status,
        )
        summaries = [_map_to_summary(row) for row in rows]
        pagination = PaginationMeta(page=page, per_page=per_page, total=total)
        return summaries, pagination

    async def get_pdf_storage_path(self, analysis_id: str, user_id: str) -> str | None:
        """
        Return the local storage path for the PDF of the given analysis.

        Returns None if the analysis has no associated PDF yet.
        Raises AnalysisNotFoundError if the analysis does not exist or is not owned by user_id.
        """
        record = await self._repo.get_by_id(analysis_id=analysis_id, user_id=user_id)
        return record.get("pdf_path")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _map_to_detail(record: dict) -> AnalysisDetailResponse:
    raw_cargas = record.get("cargas_encontradas") or []
    cargas = [Carga(**c) for c in raw_cargas]

    return AnalysisDetailResponse(
        id=record["id"],
        oficina=record["oficina"],
        partida=record["partida"],
        area_registral=record["area_registral"],
        status=record["status"],
        total_asientos=record.get("total_asientos"),
        informe=record.get("informe"),
        cargas_encontradas=cargas,
        error_message=record.get("error_message"),
        started_at=record.get("started_at"),
        completed_at=record.get("completed_at"),
        duration_seconds=record.get("duration_seconds"),
        claude_cost_usd=record.get("claude_cost_usd"),
        created_at=record["created_at"],
    )


def _map_to_summary(record: dict) -> AnalysisSummaryResponse:
    raw_cargas = record.get("cargas_encontradas") or []

    return AnalysisSummaryResponse(
        id=record["id"],
        oficina=record["oficina"],
        partida=record["partida"],
        status=record["status"],
        total_asientos=record.get("total_asientos"),
        cargas_count=len(raw_cargas),
        duration_seconds=record.get("duration_seconds"),
        created_at=record["created_at"],
        completed_at=record.get("completed_at"),
    )
