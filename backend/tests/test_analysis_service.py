from unittest.mock import AsyncMock, patch

import pytest

from app.clients.n8n_client import N8nWebhookError
from app.models.analysis import CreateAnalysisRequest
from app.repositories.analysis_repository import AnalysisNotFoundError
from app.services.analysis_service import AnalysisService, DuplicateAnalysisError
from tests.conftest import FAKE_ANALYSIS, FAKE_ANALYSIS_COMPLETED, FAKE_USER_ID


@pytest.fixture()
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    return repo


@pytest.fixture()
def service(mock_repo: AsyncMock) -> AnalysisService:
    return AnalysisService(repository=mock_repo)


class TestCreateAnalysis:
    async def test_create_analysis_success(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.check_duplicate.return_value = False
        mock_repo.create.return_value = FAKE_ANALYSIS

        with patch(
            "app.services.analysis_service.trigger_sunarp_analysis",
            new_callable=AsyncMock,
            return_value=True,
        ):
            result = await service.create_analysis(
                request=CreateAnalysisRequest(oficina="LIMA", partida="12345678"),
                user_id=FAKE_USER_ID,
            )

        assert str(result.id) == FAKE_ANALYSIS["id"]
        assert result.status == "pending"
        mock_repo.create.assert_called_once()

    async def test_create_analysis_raises_on_duplicate(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.check_duplicate.return_value = True

        with pytest.raises(DuplicateAnalysisError):
            await service.create_analysis(
                request=CreateAnalysisRequest(oficina="LIMA", partida="12345678"),
                user_id=FAKE_USER_ID,
            )

        mock_repo.create.assert_not_called()

    async def test_create_analysis_marks_failed_on_n8n_error(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.check_duplicate.return_value = False
        mock_repo.create.return_value = FAKE_ANALYSIS
        mock_repo.update_status.return_value = {**FAKE_ANALYSIS, "status": "failed"}

        with (
            patch(
                "app.services.analysis_service.trigger_sunarp_analysis",
                new_callable=AsyncMock,
                side_effect=N8nWebhookError("timeout"),
            ),
            pytest.raises(N8nWebhookError),
        ):
            await service.create_analysis(
                request=CreateAnalysisRequest(oficina="LIMA", partida="12345678"),
                user_id=FAKE_USER_ID,
            )

        mock_repo.update_status.assert_called_once_with(
            analysis_id=FAKE_ANALYSIS["id"],
            status="failed",
            error_message="Failed to trigger analysis workflow: timeout",
        )


class TestGetAnalysis:
    async def test_get_analysis_returns_detail(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_by_id.return_value = FAKE_ANALYSIS_COMPLETED

        result = await service.get_analysis(
            analysis_id=FAKE_ANALYSIS_COMPLETED["id"],
            user_id=FAKE_USER_ID,
        )

        assert result.status == "completed"
        assert result.total_asientos == 23
        assert len(result.cargas_encontradas) == 1
        mock_repo.get_by_id.assert_called_once_with(
            analysis_id=FAKE_ANALYSIS_COMPLETED["id"],
            user_id=FAKE_USER_ID,
        )

    async def test_get_analysis_raises_not_found(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_by_id.side_effect = AnalysisNotFoundError("Not found")

        with pytest.raises(AnalysisNotFoundError):
            await service.get_analysis(analysis_id="bad-id", user_id=FAKE_USER_ID)


class TestListAnalyses:
    async def test_list_analyses_returns_paginated_response(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.list_by_user.return_value = ([FAKE_ANALYSIS], 1)

        summaries, pagination = await service.list_analyses(
            user_id=FAKE_USER_ID, page=1, per_page=20
        )

        assert len(summaries) == 1
        assert pagination.total == 1
        assert pagination.page == 1
        assert pagination.per_page == 20

    async def test_list_analyses_empty_returns_empty_list(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.list_by_user.return_value = ([], 0)

        summaries, pagination = await service.list_analyses(
            user_id=FAKE_USER_ID, page=1, per_page=20
        )

        assert summaries == []
        assert pagination.total == 0

    async def test_list_analyses_passes_status_filter(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.list_by_user.return_value = ([], 0)

        await service.list_analyses(
            user_id=FAKE_USER_ID, page=1, per_page=20, status="completed"
        )

        mock_repo.list_by_user.assert_called_once_with(
            user_id=FAKE_USER_ID,
            page=1,
            per_page=20,
            status="completed",
        )


class TestGetPdfStoragePath:
    async def test_returns_path_when_pdf_exists(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_by_id.return_value = FAKE_ANALYSIS_COMPLETED

        path = await service.get_pdf_storage_path(
            analysis_id=FAKE_ANALYSIS_COMPLETED["id"],
            user_id=FAKE_USER_ID,
        )

        assert path == FAKE_ANALYSIS_COMPLETED["pdf_path"]

    async def test_returns_none_when_no_pdf(
        self, service: AnalysisService, mock_repo: AsyncMock
    ) -> None:
        mock_repo.get_by_id.return_value = FAKE_ANALYSIS  # no pdf_path

        path = await service.get_pdf_storage_path(
            analysis_id=FAKE_ANALYSIS["id"],
            user_id=FAKE_USER_ID,
        )

        assert path is None
