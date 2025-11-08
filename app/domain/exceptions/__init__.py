"""Domain exceptions."""

from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidPasswordError,
    InvalidUsernameError,
    UserAlreadyExistsError,
    UserDomainError,
    UserNotActiveError,
    UserNotFoundError,
    UserNotVerifiedError,
)

__all__ = [
    "UserDomainError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "UserNotActiveError",
    "UserNotVerifiedError",
    "InvalidPasswordError",
    "InvalidUsernameError",
    "InvalidEmailError",
]
