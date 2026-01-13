"""User entity."""

from datetime import datetime
from uuid import UUID

from domain.entities.base import BaseEntity
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword


class User(BaseEntity):
    """User domain entity.

    Represents a user in the system with authentication capabilities.
    """

    def __init__(
        self,
        email: Email,
        hashed_password: HashedPassword,
        username: str,
        is_active: bool = True,
        is_verified: bool = False,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)

        self._email = email
        self._hashed_password = hashed_password
        self._username = self._validate_username(username)
        self._is_active = is_active
        self._is_verified = is_verified

    @staticmethod
    def _validate_username(username: str) -> str:
        """Validate username format.

        Args:
            username: The username to validate

        Returns:
            The validated username

        Raises:
            ValueError: If username is invalid
        """
        if not username:
            raise ValueError("Username cannot be empty")

        if not isinstance(username, str):
            raise ValueError("Username must be a string")

        username = username.strip()

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")

        if len(username) > 50:
            raise ValueError("Username must be at most 50 characters")

        return username

    @property
    def email(self) -> Email:
        return self._email

    @property
    def hashed_password(self) -> HashedPassword:
        return self._hashed_password

    @property
    def username(self) -> str:
        return self._username

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_verified(self) -> bool:
        return self._is_verified

    def update_email(self, new_email: Email) -> None:
        """Require email re-verification after change."""
        self._email = new_email
        self._is_verified = False  # Require re-verification
        self._update_timestamp()

    def update_password(self, new_hashed_password: HashedPassword) -> None:
        self._hashed_password = new_hashed_password
        self._update_timestamp()

    def update_username(self, new_username: str) -> None:
        self._username = self._validate_username(new_username)
        self._update_timestamp()

    def activate(self) -> None:
        self._is_active = True
        self._update_timestamp()

    def deactivate(self) -> None:
        self._is_active = False
        self._update_timestamp()

    def verify_email(self) -> None:
        self._is_verified = True
        self._update_timestamp()

    def __str__(self) -> str:
        return f"User({self.username}, {self.email})"

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', is_active={self.is_active}, "
            f"is_verified={self.is_verified})"
        )
