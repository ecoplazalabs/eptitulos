from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, field_validator

from app.dependencies import get_auth_service, get_current_user
from app.models.common import ApiResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserData(BaseModel):
    id: str
    email: str
    created_at: datetime


class AuthTokenResponse(BaseModel):
    user: UserData
    token: str


class TokenResponse(BaseModel):
    token: str


@router.post(
    "/register",
    response_model=ApiResponse[AuthTokenResponse],
    status_code=201,
)
async def register(
    body: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[AuthTokenResponse]:
    """
    Register a new user account.

    Returns the created user and a JWT access token.
    """
    user, token = await auth_service.register(email=body.email, password=body.password)
    return ApiResponse(
        data=AuthTokenResponse(
            user=UserData(
                id=str(user.id),
                email=user.email,
                created_at=user.created_at,
            ),
            token=token,
        )
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[TokenResponse]:
    """
    Authenticate with email and password.

    Returns a JWT access token.
    """
    token = await auth_service.login(email=body.email, password=body.password)
    return ApiResponse(data=TokenResponse(token=token))


@router.get("/me", response_model=ApiResponse[UserData])
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> ApiResponse[UserData]:
    """Return the authenticated user's profile data."""
    return ApiResponse(
        data=UserData(
            id=current_user["id"],
            email=current_user["email"],
            created_at=current_user["created_at"],
        )
    )
