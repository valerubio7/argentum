"""Hash service interface for password hashing."""

from abc import ABC, abstractmethod


class HashService(ABC):
    """Abstract interface for password hashing service.

    This interface defines the contract for any password hashing
    implementation (e.g., bcrypt, argon2, scrypt).
    """

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass
