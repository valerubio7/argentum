"""Hash service interface for password hashing."""

from abc import ABC, abstractmethod


class HashService(ABC):
    """Abstract interface for password hashing service.

    This interface defines the contract for any password hashing
    implementation (e.g., bcrypt, argon2, scrypt).
    """

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password.

        Args:
            plain_password: The plain text password to hash

        Returns:
            The hashed password as a string

        Raises:
            ValueError: If password is invalid or empty
        """
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password.

        Args:
            plain_password: The plain text password to verify
            hashed_password: The hashed password to compare against

        Returns:
            True if password matches, False otherwise

        Raises:
            ValueError: If inputs are invalid
        """
        pass
