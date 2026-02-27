import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db import User

logger = structlog.get_logger(__name__)


class UserRepositoryError(Exception):
    """Base error for user repository operations."""


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when trying to create a user with a duplicate email."""


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, email: str, hashed_password: str) -> User:
        """Insert a new user and return the created instance."""
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        logger.info("user_created", user_id=str(user.id), email=email)
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email. Returns None if not found."""
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        """Fetch a user by ID. Returns None if not found."""
        uid = uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
        result = await self._session.execute(select(User).where(User.id == uid))
        return result.scalar_one_or_none()
