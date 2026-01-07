"""Bcrypt implementation of HashService."""

import bcrypt

from application.interfaces.hash_service import HashService


class BcryptHashService(HashService):
    """Bcrypt implementation of password hashing service.

    Uses bcrypt algorithm for secure password hashing.
    """

    def __init__(self, rounds: int = 12):
        """Initialize the hash service.

        Args:
            rounds: Number of rounds for bcrypt (default: 12)
                   Higher is more secure but slower
        """
        self._rounds = rounds

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            plain_password: The plain text password to hash

        Returns:
            The hashed password as a string

        Raises:
            ValueError: If password is invalid or empty
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")

        if not isinstance(plain_password, str):
            raise ValueError("Password must be a string")

        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)

        return hashed.decode("utf-8")

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
        if not plain_password:
            raise ValueError("Password cannot be empty")

        if not hashed_password:
            raise ValueError("Hashed password cannot be empty")

        if not isinstance(plain_password, str):
            raise ValueError("Password must be a string")

        if not isinstance(hashed_password, str):
            raise ValueError("Hashed password must be a string")

        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            # If bcrypt raises any exception (invalid hash format, etc.)
            return False
