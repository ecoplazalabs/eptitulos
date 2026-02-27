from fastapi import HTTPException, Request, status

from app.services.auth_service import decode_access_token


def extract_bearer_token(request: Request) -> str:
    """
    Extract the Bearer token from the Authorization header.

    Raises HTTPException 401 if the header is missing or malformed.
    """
    authorization: str | None = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


def get_user_id_from_token(token: str) -> str:
    """Decode the JWT and extract the user ID from the 'sub' claim."""
    return decode_access_token(token)
