"""
Tests for AnalysisRepository using mocked AsyncSession.

The repository methods are all async, so we mock AsyncSession and
SQLAlchemy execute results.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.analysis_repository import (
    AnalysisNotFoundError,
    AnalysisRepository,
)
from tests.conftest import FAKE_ANALYSIS, FAKE_USER_ID


@pytest.fixture()
def mock_session() -> AsyncMock:
    """Return a mock AsyncSession."""
    session = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture()
def repo(mock_session: AsyncMock) -> AnalysisRepository:
    return AnalysisRepository(mock_session)


def _make_scalar_result(value):
    """Helper: mock an execute() result whose scalar_one_or_none() returns value."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _make_scalar_one_result(value):
    """Helper: mock an execute() result whose scalar_one() returns value."""
    result = MagicMock()
    result.scalar_one.return_value = value
    return result


def _make_scalars_result(values: list):
    """Helper: mock an execute() result whose scalars().all() returns values."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


def _make_orm_analysis():
    """Build a minimal ORM-like analysis object with all expected attributes."""
    import uuid

    obj = MagicMock()
    obj.id = uuid.UUID(FAKE_ANALYSIS["id"])
    obj.requested_by = uuid.UUID(FAKE_ANALYSIS["requested_by"])
    obj.oficina = FAKE_ANALYSIS["oficina"]
    obj.partida = FAKE_ANALYSIS["partida"]
    obj.area_registral = FAKE_ANALYSIS["area_registral"]
    obj.status = FAKE_ANALYSIS["status"]
    obj.total_asientos = FAKE_ANALYSIS["total_asientos"]
    obj.pdf_path = FAKE_ANALYSIS["pdf_path"]
    obj.informe = FAKE_ANALYSIS["informe"]
    obj.cargas_encontradas = FAKE_ANALYSIS["cargas_encontradas"]
    obj.error_message = FAKE_ANALYSIS["error_message"]
    obj.started_at = FAKE_ANALYSIS["started_at"]
    obj.completed_at = FAKE_ANALYSIS["completed_at"]
    obj.duration_seconds = FAKE_ANALYSIS["duration_seconds"]
    obj.claude_cost_usd = FAKE_ANALYSIS["claude_cost_usd"]
    obj.created_at = FAKE_ANALYSIS["created_at"]
    obj.updated_at = FAKE_ANALYSIS["updated_at"]
    return obj


class TestCreate:
    async def test_create_returns_dict(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        _make_orm_analysis()
        mock_session.refresh = AsyncMock(return_value=None)

        # After add+flush+refresh, the ORM object is already set up via _make_orm_analysis.
        # We simulate that mock_session.add stores the object, then refresh populates it.
        # We capture what was added so we can check it.
        added_objects = []
        mock_session.add.side_effect = lambda obj: added_objects.append(obj)

        # Patch _to_dict directly since refresh is a no-op mock
        with patch(
            "app.repositories.analysis_repository._to_dict",
            return_value=FAKE_ANALYSIS,
        ):
            async def fake_refresh(obj):
                pass

            mock_session.refresh.side_effect = fake_refresh
            mock_session.add = MagicMock()

            result = await repo.create(
                {
                    "requested_by": FAKE_USER_ID,
                    "oficina": "LIMA",
                    "partida": "12345678",
                    "status": "pending",
                }
            )

        assert result["id"] == FAKE_ANALYSIS["id"]
        assert result["status"] == "pending"


class TestGetById:
    async def test_get_by_id_returns_dict(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        orm_obj = _make_orm_analysis()
        mock_session.execute = AsyncMock(return_value=_make_scalar_result(orm_obj))

        result = await repo.get_by_id(
            analysis_id=FAKE_ANALYSIS["id"], user_id=FAKE_USER_ID
        )

        assert result["id"] == FAKE_ANALYSIS["id"]
        assert result["oficina"] == "LIMA"

    async def test_get_by_id_raises_not_found_when_none(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        mock_session.execute = AsyncMock(return_value=_make_scalar_result(None))

        with pytest.raises(AnalysisNotFoundError):
            await repo.get_by_id(analysis_id="bad-id", user_id=FAKE_USER_ID)


class TestListByUser:
    async def test_list_by_user_returns_rows_and_count(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        count_result = _make_scalar_one_result(1)
        orm_obj = _make_orm_analysis()
        rows_result = _make_scalars_result([orm_obj])

        mock_session.execute = AsyncMock(side_effect=[count_result, rows_result])

        rows, total = await repo.list_by_user(
            user_id=FAKE_USER_ID, page=1, per_page=20
        )

        assert len(rows) == 1
        assert total == 1

    async def test_list_by_user_empty_returns_zero(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        count_result = _make_scalar_one_result(0)
        rows_result = _make_scalars_result([])

        mock_session.execute = AsyncMock(side_effect=[count_result, rows_result])

        rows, total = await repo.list_by_user(
            user_id=FAKE_USER_ID, page=1, per_page=20
        )

        assert rows == []
        assert total == 0


class TestCheckDuplicate:
    async def test_check_duplicate_returns_true_when_exists(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        mock_session.execute = AsyncMock(return_value=_make_scalar_one_result(1))

        assert await repo.check_duplicate(FAKE_USER_ID, "LIMA", "12345678") is True

    async def test_check_duplicate_returns_false_when_none(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        mock_session.execute = AsyncMock(return_value=_make_scalar_one_result(0))

        assert await repo.check_duplicate(FAKE_USER_ID, "LIMA", "99999999") is False


class TestUpdateStatus:
    async def test_update_status_success(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        orm_obj = _make_orm_analysis()
        orm_obj.status = "processing"

        # First execute is the UPDATE, second is the SELECT to re-fetch
        update_result = MagicMock()
        select_result = _make_scalar_result(orm_obj)

        mock_session.execute = AsyncMock(side_effect=[update_result, select_result])

        result = await repo.update_status(
            analysis_id=FAKE_ANALYSIS["id"], status="processing"
        )

        assert result["status"] == "processing"

    async def test_update_status_with_error_message(
        self, repo: AnalysisRepository, mock_session: AsyncMock
    ) -> None:
        orm_obj = _make_orm_analysis()
        orm_obj.status = "failed"
        orm_obj.error_message = "Timeout"

        update_result = MagicMock()
        select_result = _make_scalar_result(orm_obj)

        mock_session.execute = AsyncMock(side_effect=[update_result, select_result])

        result = await repo.update_status(
            analysis_id=FAKE_ANALYSIS["id"],
            status="failed",
            error_message="Timeout",
        )

        assert result["status"] == "failed"
        assert result["error_message"] == "Timeout"
