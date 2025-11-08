"""Email value object."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Email value object with validation.

    Value objects are immutable and are defined by their values,
    not by an identity.
    """

    value: str

    # Simple email regex pattern
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    def __post_init__(self):
        """Validate email format after initialization."""
        if not self.value:
            raise ValueError("Email cannot be empty")

        if not isinstance(self.value, str):
            raise ValueError("Email must be a string")

        # Normalize email to lowercase
        object.__setattr__(self, "value", self.value.lower().strip())

        if len(self.value) > 255:
            raise ValueError("Email is too long (max 255 characters)")

        if not self.EMAIL_PATTERN.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def __str__(self) -> str:
        """String representation of the email."""
        return self.value

    def __repr__(self) -> str:
        """Representation of the email."""
        return f"Email('{self.value}')"
