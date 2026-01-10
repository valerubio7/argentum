"""API schemas package."""

from presentation.api.schemas.auth_schemas import (
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    "ErrorResponse",
]
