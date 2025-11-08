"""Authentication Data Transfer Objects."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RegisterUserDTO:
    """DTO for user registration request.

    This DTO carries registration data from the presentation layer
    to the application layer.
    """

    email: str
    password: str
    username: str

    def __post_init__(self):
        """Validate DTO fields."""
        if not self.email:
            raise ValueError("Email is required")
        if not self.password:
            raise ValueError("Password is required")
        if not self.username:
            raise ValueError("Username is required")


@dataclass(frozen=True)
class LoginDTO:
    """DTO for user login request.

    This DTO carries login credentials from the presentation layer
    to the application layer.
    """

    email: str
    password: str

    def __post_init__(self):
        """Validate DTO fields."""
        if not self.email:
            raise ValueError("Email is required")
        if not self.password:
            raise ValueError("Password is required")


@dataclass(frozen=True)
class TokenDTO:
    """DTO for authentication token response.

    This DTO carries token information from the application layer
    back to the presentation layer.
    """

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime | None = None

    def __post_init__(self):
        """Validate DTO fields."""
        if not self.access_token:
            raise ValueError("Access token is required")
        if not self.token_type:
            raise ValueError("Token type is required")


@dataclass(frozen=True)
class UserResponseDTO:
    """DTO for user information response.

    This DTO carries user information from the application layer
    back to the presentation layer, excluding sensitive data.
    """

    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    def __post_init__(self):
        """Validate DTO fields."""
        if not self.id:
            raise ValueError("User ID is required")
        if not self.email:
            raise ValueError("Email is required")
        if not self.username:
            raise ValueError("Username is required")
