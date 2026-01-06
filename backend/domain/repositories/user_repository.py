"""User repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User
from domain.value_objects.email import Email


class UserRepository(ABC):
    """Repository interface for User entity following DDD Repository pattern."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save a user.

        Raises:
            UserAlreadyExistsError: If email or username already exists.
        """

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find user by ID."""

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email."""

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user.

        Raises:
            UserNotFoundError: If user doesn't exist.
        """

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user. Returns True if deleted, False if not found."""

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """Check if email exists."""

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists."""

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List users with pagination."""

    @abstractmethod
    async def count(self) -> int:
        """Count total users."""
