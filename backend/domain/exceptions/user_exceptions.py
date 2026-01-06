"""User-specific domain exceptions."""

from uuid import UUID


class UserDomainError(Exception):
    """Base exception for all user domain errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(UserDomainError):
    """Raised when a user cannot be found."""

    def __init__(self, identifier: str | UUID):
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")


class UserAlreadyExistsError(UserDomainError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"User with {field} '{value}' already exists")


class InvalidCredentialsError(UserDomainError):
    """Raised when user credentials are invalid."""

    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotActiveError(UserDomainError):
    """Raised when attempting to authenticate with an inactive user account."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User account '{email}' is not active")


class UserNotVerifiedError(UserDomainError):
    """Raised when a user has not verified their email."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User '{email}' has not verified their email")


class InvalidPasswordError(UserDomainError):
    """Raised when password validation fails."""

    def __init__(self, message: str = "Invalid password"):
        super().__init__(message)


class InvalidUsernameError(UserDomainError):
    """Raised when username validation fails."""

    def __init__(self, message: str = "Invalid username"):
        super().__init__(message)


class InvalidEmailError(UserDomainError):
    """Raised when email validation fails."""

    def __init__(self, message: str = "Invalid email"):
        super().__init__(message)
