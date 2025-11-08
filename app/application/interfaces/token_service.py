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
        """Generate an authentication token for a user.

        Args:
            user_id: The user's unique identifier
            email: The user's email address

        Returns:
            A tuple containing:
                - The generated token as a string
                - The expiration datetime

        Raises:
            ValueError: If user_id or email is invalid
        """
        pass

    @abstractmethod
    def validate_token(self, token: str) -> dict[str, str]:
        """Validate and decode an authentication token.

        Args:
            token: The JWT token to validate

        Returns:
            A dictionary containing the token payload with at least:
                - user_id: str (UUID as string)
                - email: str

        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        pass

    @abstractmethod
    def get_token_expiration(self, token: str) -> datetime:
        """Get the expiration datetime of a token.

        Args:
            token: The JWT token

        Returns:
            The expiration datetime

        Raises:
            InvalidTokenError: If token is invalid
        """
        pass
