"""Domain exceptions package."""

from domain.exceptions.user_exceptions import (
    UserDomainError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotActiveError,
    UserNotVerifiedError,
    InvalidPasswordError,
    InvalidUsernameError,
    InvalidEmailError,
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
