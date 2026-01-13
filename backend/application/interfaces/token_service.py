"""Token service interface for JWT token generation and validation."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class TokenService(ABC):
    """Abstract interface for JWT token service.

    This interface defines the contract for any token generation
    and validation implementation.
    """

    @abstractmethod
    def generate_token(self, user_id: UUID, email: str) -> tuple[str, datetime]:
        pass

    @abstractmethod
    def validate_token(self, token: str) -> dict[str, str]:
        pass

    @abstractmethod
    def get_token_expiration(self, token: str) -> datetime:
        pass
