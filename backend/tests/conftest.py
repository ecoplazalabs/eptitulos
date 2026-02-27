import os
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock

# Set test environment variables BEFORE any app imports so pydantic-settings
# does not fail validation when there is no real .env file present.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_MINUTES", "60")
os.environ.setdefault("STORAGE_PATH", "./test_storage")
os.environ.setdefault("N8N_WEBHOOK_URL", "https://test-n8n.railway.app/webhook")
os.environ.setdefault("N8N_API_KEY", "test-api-key")
os.environ.setdefault("APP_ENV", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.dependencies import get_current_user, get_storage  # noqa: E402
from app.main import app  # noqa: E402
from app.services.storage_service import StorageService  # noqa: E402

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

FAKE_USER_ID = "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa"
FAKE_USER_EMAIL = "test@example.com"
FAKE_USER_CREATED_AT = datetime(2026, 2, 25, 10, 0, 0, tzinfo=UTC)

FAKE_USER_DICT = {
    "id": FAKE_USER_ID,
    "email": FAKE_USER_EMAIL,
    "created_at": FAKE_USER_CREATED_AT,
}

FAKE_ANALYSIS = {
    "id": "bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb",
    "requested_by": FAKE_USER_ID,
    "oficina": "LIMA",
    "partida": "12345678",
    "area_registral": "Propiedad Inmueble Predial",
    "status": "pending",
    "total_asientos": None,
    "pdf_path": None,
    "informe": None,
    "cargas_encontradas": [],
    "error_message": None,
    "started_at": None,
    "completed_at": None,
    "duration_seconds": None,
    "claude_cost_usd": None,
    "created_at": datetime(2026, 2, 25, 10, 30, 0, tzinfo=UTC),
    "updated_at": datetime(2026, 2, 25, 10, 30, 0, tzinfo=UTC),
}

FAKE_ANALYSIS_COMPLETED = {
    **FAKE_ANALYSIS,
    "status": "completed",
    "total_asientos": 23,
    "pdf_path": f"{FAKE_USER_ID}/bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb/copia_literal.pdf",
    "informe": "Se encontraron 2 cargas vigentes.",
    "cargas_encontradas": [
        {
            "tipo": "Hipoteca",
            "detalle": "Hipoteca BCP",
            "vigente": True,
            "fecha": "2019-03-15",
        }
    ],
    "duration_seconds": 263,
    "claude_cost_usd": "4.2500",
    "completed_at": datetime(2026, 2, 25, 10, 34, 23, tzinfo=UTC),
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_storage() -> StorageService:
    service = MagicMock(spec=StorageService)
    return service


@pytest.fixture()
def client(mock_storage: StorageService) -> Generator[TestClient, None, None]:
    """Test client with auth and storage overridden."""
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_DICT
    app.dependency_overrides[get_storage] = lambda: mock_storage

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def client_unauthenticated() -> Generator[TestClient, None, None]:
    """Test client without auth override - used for auth failure tests."""
    with TestClient(app) as test_client:
        yield test_client
