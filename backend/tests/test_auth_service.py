"""Tests for AuthService: register, login, token verification."""
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.services.auth_service import (
    AuthService,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from tests.conftest import FAKE_USER_EMAIL, FAKE_USER_ID


def _make_user(user_id: str = FAKE_USER_ID, email: str = FAKE_USER_EMAIL) -> MagicMock:
    user = MagicMock()
    user.id = UUID(user_id)
    user.email = email
    user.hashed_password = hash_password("correctpassword")
    user.created_at = datetime(2026, 2, 25, 10, 0, 0, tzinfo=UTC)
    return user


@pytest.fixture()
def mock_user_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture()
def auth_service(mock_user_repo: AsyncMock) -> AuthService:
    return AuthService(user_repo=mock_user_repo)


class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self) -> None:
        plain = "MySuperSecret123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_wrong_password_fails_verification(self) -> None:
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False


class TestJwtTokens:
    def test_create_and_decode_token(self) -> None:
        token = create_access_token(FAKE_USER_ID)
        assert isinstance(token, str)
        decoded_id = decode_access_token(token)
        assert decoded_id == FAKE_USER_ID

    def test_decode_invalid_token_raises_401(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("this.is.not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_decode_tampered_token_raises_401(self) -> None:
        token = create_access_token(FAKE_USER_ID)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered)
        assert exc_info.value.status_code == 401


class TestRegister:
    async def test_register_new_user_returns_user_and_token(
        self, auth_service: AuthService, mock_user_repo: AsyncMock
    ) -> None:
        user = _make_user()
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = user

        result_user, token = await auth_service.register(
            email=FAKE_USER_EMAIL, password="correctpassword"
        )

        assert result_user.email == FAKE_USER_EMAIL
        assert isinstance(token, str)
        mock_user_repo.create.assert_called_once()

    async def test_register_duplicate_email_raises_409(
        self, auth_service: AuthService, mock_user_repo: AsyncMock
    ) -> None:
        existing = _make_user()
        mock_user_repo.get_by_email.return_value = existing

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register(email=FAKE_USER_EMAIL, password="anypassword")

        assert exc_info.value.status_code == 409
        mock_user_repo.create.assert_not_called()


class TestLogin:
    async def test_login_valid_credentials_returns_token(
        self, auth_service: AuthService, mock_user_repo: AsyncMock
    ) -> None:
        user = _make_user()
        mock_user_repo.get_by_email.return_value = user

        token = await auth_service.login(
            email=FAKE_USER_EMAIL, password="correctpassword"
        )

        assert isinstance(token, str)
        decoded_id = decode_access_token(token)
        assert decoded_id == FAKE_USER_ID

    async def test_login_wrong_password_raises_401(
        self, auth_service: AuthService, mock_user_repo: AsyncMock
    ) -> None:
        user = _make_user()
        mock_user_repo.get_by_email.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                email=FAKE_USER_EMAIL, password="wrongpassword"
            )

        assert exc_info.value.status_code == 401

    async def test_login_unknown_email_raises_401(
        self, auth_service: AuthService, mock_user_repo: AsyncMock
    ) -> None:
        mock_user_repo.get_by_email.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login(
                email="nobody@example.com", password="somepassword"
            )

        assert exc_info.value.status_code == 401


class TestAuthRouter:
    def test_register_endpoint_success(self, client_unauthenticated) -> None:
        from datetime import datetime
        from unittest.mock import AsyncMock, patch
        from uuid import UUID

        user_mock = MagicMock()
        user_mock.id = UUID(FAKE_USER_ID)
        user_mock.email = FAKE_USER_EMAIL
        user_mock.created_at = datetime(2026, 2, 25, tzinfo=UTC)

        with patch(
            "app.services.auth_service.AuthService.register",
            new_callable=AsyncMock,
            return_value=(user_mock, "fake.jwt.token"),
        ):
            response = client_unauthenticated.post(
                "/api/auth/register",
                json={"email": FAKE_USER_EMAIL, "password": "strongpassword"},
            )

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["token"] == "fake.jwt.token"
        assert body["data"]["user"]["email"] == FAKE_USER_EMAIL

    def test_register_short_password_returns_400(
        self, client_unauthenticated
    ) -> None:
        response = client_unauthenticated.post(
            "/api/auth/register",
            json={"email": FAKE_USER_EMAIL, "password": "short"},
        )
        assert response.status_code == 400

    def test_login_endpoint_success(self, client_unauthenticated) -> None:
        with patch(
            "app.services.auth_service.AuthService.login",
            new_callable=AsyncMock,
            return_value="fake.jwt.token",
        ):
            response = client_unauthenticated.post(
                "/api/auth/login",
                json={"email": FAKE_USER_EMAIL, "password": "correctpassword"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["token"] == "fake.jwt.token"

    def test_me_endpoint_returns_user(self, client) -> None:
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == FAKE_USER_ID
        assert body["data"]["email"] == FAKE_USER_EMAIL
