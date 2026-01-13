"""User-specific domain exceptions."""

from uuid import UUID


class UserDomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(UserDomainError):
    def __init__(self, identifier: str | UUID):
        self.identifier = identifier
        super().__init__(f"User not found: {identifier}")


class UserAlreadyExistsError(UserDomainError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"User with {field} '{value}' already exists")


class InvalidCredentialsError(UserDomainError):
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotActiveError(UserDomainError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User account '{email}' is not active")


class UserNotVerifiedError(UserDomainError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"User '{email}' has not verified their email")


class InvalidPasswordError(UserDomainError):
    def __init__(self, message: str = "Invalid password"):
        super().__init__(message)


class InvalidUsernameError(UserDomainError):
    def __init__(self, message: str = "Invalid username"):
        super().__init__(message)


class InvalidEmailError(UserDomainError):
    def __init__(self, message: str = "Invalid email"):
        super().__init__(message)
