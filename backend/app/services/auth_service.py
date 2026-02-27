from datetime import UTC, datetime, timedelta

import structlog
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.db import User
from app.repositories.user_repository import UserAlreadyExistsError, UserRepository

logger = structlog.get_logger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthError(Exception):
    """Generic authentication error."""


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    """Create a signed JWT with sub=user_id and expiry configured in settings."""
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiration_minutes)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    """
    Decode and validate a JWT.

    Returns the user_id (sub claim).
    Raises HTTPException 401 on any JWT error.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError as exc:
        logger.warning("jwt_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def register(self, email: str, password: str) -> tuple[User, str]:
        """
        Register a new user.

        Returns (user, token).
        Raises HTTPException 409 if email already exists.
        """
        existing = await self._user_repo.get_by_email(email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        hashed = hash_password(password)
        try:
            user = await self._user_repo.create(email=email, hashed_password=hashed)
        except UserAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            ) from None

        token = create_access_token(str(user.id))
        logger.info("user_registered", user_id=str(user.id))
        return user, token

    async def login(self, email: str, password: str) -> str:
        """
        Authenticate a user.

        Returns a JWT token string.
        Raises HTTPException 401 if credentials are invalid.
        """
        user = await self._user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            logger.warning("login_failed", email=email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = create_access_token(str(user.id))
        logger.info("user_logged_in", user_id=str(user.id))
        return token
