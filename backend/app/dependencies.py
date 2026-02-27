from typing import Any

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import extract_bearer_token, get_user_id_from_token
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.user_repository import UserRepository
from app.services.analysis_service import AnalysisService
from app.services.auth_service import AuthService
from app.services.storage_service import StorageService, get_storage_service_singleton


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    FastAPI dependency that verifies the JWT and returns the user dict.

    Raises HTTPException 401 if the token is missing or invalid.
    Raises HTTPException 401 if the user no longer exists.
    """
    from fastapi import HTTPException, status

    token = extract_bearer_token(request)
    user_id = get_user_id_from_token(token)

    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": user.created_at,
    }


def get_analysis_repository(
    session: AsyncSession = Depends(get_db),
) -> AnalysisRepository:
    """Provide an AnalysisRepository backed by the current DB session."""
    return AnalysisRepository(session)


def get_analysis_service(
    repository: AnalysisRepository = Depends(get_analysis_repository),
) -> AnalysisService:
    """Provide an AnalysisService instance."""
    return AnalysisService(repository)


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Provide a UserRepository backed by the current DB session."""
    return UserRepository(session)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Provide an AuthService instance."""
    return AuthService(user_repo)


def get_storage() -> StorageService:
    """Provide the singleton StorageService."""
    return get_storage_service_singleton()
