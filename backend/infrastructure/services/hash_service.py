"""Bcrypt implementation of HashService."""

import logging

import bcrypt

from application.interfaces.hash_service import HashService

logger = logging.getLogger(__name__)


class BcryptHashService(HashService):
    """Bcrypt implementation of password hashing service.

    Uses bcrypt algorithm for secure password hashing.
    """

    def __init__(self, rounds: int = 12):
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
            Returns False for bcrypt-specific errors (invalid hash format).
            Logs and re-raises unexpected exceptions.
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except (ValueError, AttributeError) as e:
            # Invalid hash format or encoding issues - expected errors
            logger.debug(f"Password verification failed due to invalid hash: {e}")
            return False
        except Exception as e:
            # Unexpected errors should be logged and re-raised
            logger.error(f"Unexpected error during password verification: {e}")
            raise
