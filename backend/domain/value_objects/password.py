"""Password value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HashedPassword:
    """Hashed password value object.

    This represents an already hashed password.
    The actual hashing should be done by a domain service.
    """

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Hashed password cannot be empty")

        if not isinstance(self.value, str):
            raise ValueError("Hashed password must be a string")

        # Typically a bcrypt hash is 60 characters
        if len(self.value) < 20:
            raise ValueError("Invalid hashed password format")

    def __str__(self) -> str:
        """Don't expose the hash in string representation."""
        return "***HASHED***"

    def __repr__(self) -> str:
        """Don't expose the hash in representation."""
        return "HashedPassword(***)"


@dataclass(frozen=True)
class PlainPassword:
    """Plain password value object for validation before hashing.

    This is used temporarily during registration/password change
    before being hashed.
    """

    value: str

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    def __post_init__(self):
        if not self.value:
            raise ValueError("Password cannot be empty")

        if not isinstance(self.value, str):
            raise ValueError("Password must be a string")

        if len(self.value) < self.MIN_LENGTH:
            raise ValueError(f"Password must be at least {self.MIN_LENGTH} characters")

        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Password must be at most {self.MAX_LENGTH} characters")

        # Check password complexity
        has_upper = any(c.isupper() for c in self.value)
        has_lower = any(c.islower() for c in self.value)
        has_digit = any(c.isdigit() for c in self.value)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )

    def __str__(self) -> str:
        """Don't expose the password in string representation."""
        return "***HIDDEN***"

    def __repr__(self) -> str:
        """Don't expose the password in representation."""
        return "PlainPassword(***)"
