import uuid
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import SunarpAnalysis

logger = structlog.get_logger(__name__)


class AnalysisRepositoryError(Exception):
    """Base error for repository operations."""


class AnalysisNotFoundError(AnalysisRepositoryError):
    """Raised when the requested analysis does not exist."""


class AnalysisRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new analysis record and return it as a dict."""
        analysis = SunarpAnalysis(**data)
        self._session.add(analysis)
        await self._session.flush()
        await self._session.refresh(analysis)
        logger.info("analysis_created", analysis_id=str(analysis.id))
        return _to_dict(analysis)

    async def get_by_id(self, analysis_id: uuid.UUID | str, user_id: str) -> dict[str, Any]:
        """
        Fetch a single analysis by ID, scoped to the given user.

        Raises AnalysisNotFoundError if not found or if it belongs to another user.
        """
        try:
            aid = analysis_id if isinstance(analysis_id, uuid.UUID) else uuid.UUID(str(analysis_id))
            uid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except ValueError as exc:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found") from exc

        result = await self._session.execute(
            select(SunarpAnalysis).where(
                SunarpAnalysis.id == aid,
                SunarpAnalysis.requested_by == uid,
            )
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        return _to_dict(analysis)

    async def list_by_user(
        self,
        user_id: str,
        page: int,
        per_page: int,
        status: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Return a paginated list of analyses for a user.

        Returns (rows, total_count).
        """
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
        offset = (page - 1) * per_page

        base_where = [SunarpAnalysis.requested_by == uid]
        if status is not None:
            base_where.append(SunarpAnalysis.status == status)

        count_result = await self._session.execute(
            select(func.count()).select_from(SunarpAnalysis).where(*base_where)
        )
        total: int = count_result.scalar_one()

        rows_result = await self._session.execute(
            select(SunarpAnalysis)
            .where(*base_where)
            .order_by(SunarpAnalysis.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        rows = [_to_dict(r) for r in rows_result.scalars().all()]
        return rows, total

    async def update_status(
        self,
        analysis_id: uuid.UUID | str,
        status: str,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        """Update the status (and optional error_message) of an analysis."""
        aid = uuid.UUID(str(analysis_id)) if not isinstance(analysis_id, uuid.UUID) else analysis_id

        values: dict[str, Any] = {"status": status}
        if error_message is not None:
            values["error_message"] = error_message

        await self._session.execute(
            update(SunarpAnalysis).where(SunarpAnalysis.id == aid).values(**values)
        )
        await self._session.flush()

        result = await self._session.execute(
            select(SunarpAnalysis).where(SunarpAnalysis.id == aid)
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisRepositoryError(
                f"Failed to update status for analysis {analysis_id}"
            )
        logger.info(
            "analysis_status_updated",
            analysis_id=str(analysis_id),
            status=status,
        )
        return _to_dict(analysis)

    async def get_by_id_internal(self, analysis_id: uuid.UUID | str) -> dict[str, Any]:
        """
        Fetch a single analysis by ID without user scoping.

        Used by internal service-to-service endpoints.
        Raises AnalysisNotFoundError if not found.
        """
        try:
            aid = analysis_id if isinstance(analysis_id, uuid.UUID) else uuid.UUID(str(analysis_id))
        except ValueError as exc:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found") from exc

        result = await self._session.execute(
            select(SunarpAnalysis).where(SunarpAnalysis.id == aid)
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")
        return _to_dict(analysis)

    async def update_result(
        self,
        analysis_id: uuid.UUID | str,
        status: str,
        total_asientos: int | None = None,
        cargas_encontradas: list[dict] | None = None,
        informe: str | None = None,
        error_message: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        pdf_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Update all result fields of an analysis at once.

        Calculates duration_seconds automatically from started_at and completed_at
        when both are provided.
        """
        aid = analysis_id if isinstance(analysis_id, uuid.UUID) else uuid.UUID(str(analysis_id))

        values: dict[str, Any] = {"status": status}

        if total_asientos is not None:
            values["total_asientos"] = total_asientos
        if cargas_encontradas is not None:
            values["cargas_encontradas"] = cargas_encontradas
        if informe is not None:
            values["informe"] = informe
        if error_message is not None:
            values["error_message"] = error_message
        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if pdf_path is not None:
            values["pdf_path"] = pdf_path

        if started_at is not None and completed_at is not None:
            delta = completed_at - started_at
            values["duration_seconds"] = max(0, int(delta.total_seconds()))

        await self._session.execute(
            update(SunarpAnalysis).where(SunarpAnalysis.id == aid).values(**values)
        )
        await self._session.flush()

        result = await self._session.execute(
            select(SunarpAnalysis).where(SunarpAnalysis.id == aid)
        )
        analysis = result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisRepositoryError(
                f"Failed to update result for analysis {analysis_id}"
            )
        logger.info(
            "analysis_result_updated",
            analysis_id=str(analysis_id),
            status=status,
            duration_seconds=values.get("duration_seconds"),
        )
        return _to_dict(analysis)

    async def delete_analysis(
        self,
        analysis_id: uuid.UUID | str,
        user_id: str,
    ) -> None:
        """
        Hard-delete an analysis scoped to the given user.

        Raises AnalysisNotFoundError if not found or not owned by user_id.
        """
        try:
            aid = analysis_id if isinstance(analysis_id, uuid.UUID) else uuid.UUID(str(analysis_id))
            uid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except ValueError as exc:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found") from exc

        result = await self._session.execute(
            delete(SunarpAnalysis).where(
                SunarpAnalysis.id == aid,
                SunarpAnalysis.requested_by == uid,
            )
        )
        if result.rowcount == 0:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")

        logger.info("analysis_deleted", analysis_id=str(analysis_id))

    async def cancel_analysis(
        self,
        analysis_id: uuid.UUID | str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        Set an analysis status to 'failed' with error_message 'Cancelled by user'.

        Only updates if the current status is 'pending' or 'processing' and the
        record belongs to user_id.

        Raises AnalysisNotFoundError if not found or not owned by user_id.
        Raises AnalysisRepositoryError if the status is not cancellable.
        """
        try:
            aid = analysis_id if isinstance(analysis_id, uuid.UUID) else uuid.UUID(str(analysis_id))
            uid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(str(user_id))
        except ValueError as exc:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found") from exc

        existing_result = await self._session.execute(
            select(SunarpAnalysis).where(
                SunarpAnalysis.id == aid,
                SunarpAnalysis.requested_by == uid,
            )
        )
        analysis = existing_result.scalar_one_or_none()
        if analysis is None:
            raise AnalysisNotFoundError(f"Analysis {analysis_id} not found")

        if analysis.status not in ("pending", "processing"):
            raise AnalysisRepositoryError(
                f"Analysis {analysis_id} cannot be cancelled: current status is '{analysis.status}'"
            )

        await self._session.execute(
            update(SunarpAnalysis)
            .where(SunarpAnalysis.id == aid)
            .values(status="failed", error_message="Cancelled by user")
        )
        await self._session.flush()
        await self._session.refresh(analysis)

        logger.info("analysis_cancelled", analysis_id=str(analysis_id))
        return _to_dict(analysis)

    async def check_duplicate(self, user_id: str, oficina: str, partida: str) -> bool:
        """
        Return True if there is already a pending or processing analysis
        for the given user + oficina + partida combination.
        """
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id

        result = await self._session.execute(
            select(func.count())
            .select_from(SunarpAnalysis)
            .where(
                SunarpAnalysis.requested_by == uid,
                SunarpAnalysis.oficina == oficina,
                SunarpAnalysis.partida == partida,
                SunarpAnalysis.status.in_(["pending", "processing"]),
            )
        )
        count: int = result.scalar_one()
        return count > 0


def _to_dict(analysis: SunarpAnalysis) -> dict[str, Any]:
    """Convert a SunarpAnalysis ORM instance to a plain dict."""
    return {
        "id": str(analysis.id),
        "requested_by": str(analysis.requested_by),
        "oficina": analysis.oficina,
        "partida": analysis.partida,
        "area_registral": analysis.area_registral,
        "status": analysis.status,
        "total_asientos": analysis.total_asientos,
        "pdf_path": analysis.pdf_path,
        "informe": analysis.informe,
        "cargas_encontradas": analysis.cargas_encontradas or [],
        "error_message": analysis.error_message,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "duration_seconds": analysis.duration_seconds,
        "claude_cost_usd": analysis.claude_cost_usd,
        "created_at": analysis.created_at,
        "updated_at": analysis.updated_at,
    }
