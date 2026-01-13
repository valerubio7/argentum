"""Pydantic schemas for authentication API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: str = Field(..., min_length=3, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "username": "john_doe",
            }
        }
    )


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com", "password": "SecurePassword123"}
        }
    )


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-11-08T10:30:00Z",
            }
        }
    )


class TokenResponse(BaseModel):
    """Response schema for authentication token."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_at": "2025-11-08T11:00:00Z",
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Invalid credentials"}}
    )
