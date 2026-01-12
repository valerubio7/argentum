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
            plain_password: The plain text password to hash (assumed validated)

        Returns:
            The hashed password as a string

        Note:
            Input validation is handled by PlainPassword value object.
            This service assumes valid input.
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password.

        Args:
            plain_password: The plain text password to verify (assumed validated)
            hashed_password: The hashed password to compare against

        Returns:
            True if password matches, False otherwise

        Note:
            Returns False for any bcrypt errors (invalid hash format, etc.)
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception:
            # If bcrypt raises any exception (invalid hash format, etc.)
            return False
