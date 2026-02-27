from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from tests.conftest import FAKE_ANALYSIS, FAKE_ANALYSIS_COMPLETED


class TestCreateAnalysis:
    def test_create_analysis_success(self, client: TestClient) -> None:
        with (
            patch(
                "app.repositories.analysis_repository.AnalysisRepository.check_duplicate",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.repositories.analysis_repository.AnalysisRepository.create",
                new_callable=AsyncMock,
                return_value=FAKE_ANALYSIS,
            ),
            patch(
                "app.services.analysis_service.trigger_sunarp_analysis",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            response = client.post(
                "/api/sunarp/analyze",
                json={
                    "oficina": "LIMA",
                    "partida": "12345678",
                    "area_registral": "Propiedad Inmueble Predial",
                },
            )

        assert response.status_code == 201
        body = response.json()
        assert body["error"] is None
        assert body["data"]["status"] == "pending"
        assert body["data"]["oficina"] == "LIMA"
        assert body["data"]["partida"] == "12345678"

    def test_create_analysis_duplicate_returns_409(self, client: TestClient) -> None:
        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.check_duplicate",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.post(
                "/api/sunarp/analyze",
                json={"oficina": "LIMA", "partida": "12345678"},
            )

        assert response.status_code == 409
        body = response.json()
        assert body["error"]["code"] == "DUPLICATE_ANALYSIS"

    def test_create_analysis_invalid_oficina_returns_400(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/sunarp/analyze",
            json={"oficina": "INVALID_CITY", "partida": "12345678"},
        )
        assert response.status_code == 400
        body = response.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_create_analysis_invalid_partida_returns_400(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/api/sunarp/analyze",
            json={"oficina": "LIMA", "partida": "ABC123"},
        )
        assert response.status_code == 400

    def test_create_analysis_n8n_failure_returns_502(
        self, client: TestClient
    ) -> None:
        from app.clients.n8n_client import N8nWebhookError

        with (
            patch(
                "app.repositories.analysis_repository.AnalysisRepository.check_duplicate",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "app.repositories.analysis_repository.AnalysisRepository.create",
                new_callable=AsyncMock,
                return_value=FAKE_ANALYSIS,
            ),
            patch(
                "app.clients.n8n_client.trigger_sunarp_analysis",
                new_callable=AsyncMock,
                side_effect=N8nWebhookError("Connection refused"),
            ),
            patch(
                "app.repositories.analysis_repository.AnalysisRepository.update_status",
                new_callable=AsyncMock,
                return_value={**FAKE_ANALYSIS, "status": "failed"},
            ),
        ):
            response = client.post(
                "/api/sunarp/analyze",
                json={"oficina": "LIMA", "partida": "12345678"},
            )

        assert response.status_code == 502
        body = response.json()
        assert body["error"]["code"] == "UPSTREAM_ERROR"


class TestGetAnalysis:
    def test_get_analysis_success(self, client: TestClient) -> None:
        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.get_by_id",
            new_callable=AsyncMock,
            return_value=FAKE_ANALYSIS_COMPLETED,
        ):
            response = client.get(f"/api/sunarp/analyses/{FAKE_ANALYSIS_COMPLETED['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["error"] is None
        assert body["data"]["status"] == "completed"
        assert body["data"]["total_asientos"] == 23
        assert len(body["data"]["cargas_encontradas"]) == 1

    def test_get_analysis_not_found_returns_404(self, client: TestClient) -> None:
        from app.repositories.analysis_repository import AnalysisNotFoundError

        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.get_by_id",
            new_callable=AsyncMock,
            side_effect=AnalysisNotFoundError("Analysis not-existing-id not found"),
        ):
            response = client.get("/api/sunarp/analyses/not-existing-id")

        assert response.status_code == 404
        body = response.json()
        assert body["error"]["code"] == "NOT_FOUND"


class TestListAnalyses:
    def test_list_analyses_success(self, client: TestClient) -> None:
        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.list_by_user",
            new_callable=AsyncMock,
            return_value=([FAKE_ANALYSIS], 1),
        ):
            response = client.get("/api/sunarp/analyses")

        assert response.status_code == 200
        body = response.json()
        assert body["error"] is None
        assert len(body["data"]) == 1
        assert body["pagination"]["total"] == 1
        assert body["pagination"]["page"] == 1

    def test_list_analyses_pagination_params(self, client: TestClient) -> None:
        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.list_by_user",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            response = client.get("/api/sunarp/analyses?page=2&per_page=10")

        assert response.status_code == 200
        body = response.json()
        assert body["pagination"]["page"] == 2
        assert body["pagination"]["per_page"] == 10

    def test_list_analyses_per_page_max_enforced(self, client: TestClient) -> None:
        response = client.get("/api/sunarp/analyses?per_page=9999")
        assert response.status_code == 400


class TestGetPdf:
    def test_get_pdf_success(self, client: TestClient, mock_storage) -> None:
        fake_path = Path("/tmp/test_copia_literal.pdf")
        fake_path.write_bytes(b"%PDF-1.4 test content")
        mock_storage.get_pdf_path.return_value = fake_path

        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.get_by_id",
            new_callable=AsyncMock,
            return_value=FAKE_ANALYSIS_COMPLETED,
        ):
            response = client.get(
                f"/api/sunarp/analyses/{FAKE_ANALYSIS_COMPLETED['id']}/pdf"
            )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        fake_path.unlink(missing_ok=True)

    def test_get_pdf_no_pdf_returns_404(self, client: TestClient) -> None:
        with patch(
            "app.repositories.analysis_repository.AnalysisRepository.get_by_id",
            new_callable=AsyncMock,
            return_value=FAKE_ANALYSIS,  # pending, no pdf_path
        ):
            response = client.get(
                f"/api/sunarp/analyses/{FAKE_ANALYSIS['id']}/pdf"
            )

        assert response.status_code == 404


class TestHealthEndpoint:
    def test_health_check(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert "version" in body
        assert "timestamp" in body
