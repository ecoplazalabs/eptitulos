from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    message: str
    code: str


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    error: ErrorDetail | None = None


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T] | None = None
    pagination: PaginationMeta | None = None
    error: ErrorDetail | None = None


class ErrorResponse(BaseModel):
    data: None = None
    error: ErrorDetail
