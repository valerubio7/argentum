"""User repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.user import User
from domain.value_objects.email import Email


class UserRepository(ABC):
    """Repository interface for User entity following DDD Repository pattern."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Raises: UserAlreadyExistsError if email or username already exists."""

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> User | None:
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Raises: UserNotFoundError if user doesn't exist."""

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Returns True if deleted."""

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        pass

    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
