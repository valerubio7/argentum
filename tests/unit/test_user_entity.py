"""Unit tests for User entity."""

import pytest
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword, PlainPassword


class TestEmail:
    """Tests for Email value object."""

    def test_valid_email(self):
        """Test creating a valid email."""
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_email_lowercase_normalization(self):
        """Test email is normalized to lowercase."""
        email = Email("User@EXAMPLE.COM")
        assert email.value == "user@example.com"

    def test_email_trim_whitespace(self):
        """Test email trims whitespace."""
        email = Email("  user@example.com  ")
        assert email.value == "user@example.com"

    def test_invalid_email_format(self):
        """Test invalid email format raises error."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("invalid-email")

    def test_empty_email(self):
        """Test empty email raises error."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_email_too_long(self):
        """Test email that's too long raises error."""
        long_email = "a" * 256 + "@example.com"
        with pytest.raises(ValueError, match="Email is too long"):
            Email(long_email)

    def test_email_immutability(self):
        """Test email is immutable."""
        email = Email("user@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"


class TestPassword:
    """Tests for Password value objects."""

    def test_valid_plain_password(self):
        """Test creating a valid plain password."""
        password = PlainPassword("SecurePassword123")
        assert password.value == "SecurePassword123"

    def test_plain_password_too_short(self):
        """Test password that's too short raises error."""
        with pytest.raises(ValueError, match="must be at least"):
            PlainPassword("short")

    def test_plain_password_too_long(self):
        """Test password that's too long raises error."""
        long_password = "a" * 129
        with pytest.raises(ValueError, match="must be at most"):
            PlainPassword(long_password)

    def test_plain_password_not_exposed_in_str(self):
        """Test plain password is not exposed in string representation."""
        password = PlainPassword("SecurePassword123")
        assert str(password) == "***HIDDEN***"
        assert "SecurePassword123" not in repr(password)

    def test_valid_hashed_password(self):
        """Test creating a valid hashed password."""
        # Simulating a bcrypt hash
        hashed = "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
        password = HashedPassword(hashed)
        assert password.value == hashed

    def test_hashed_password_too_short(self):
        """Test hashed password that's too short raises error."""
        with pytest.raises(ValueError, match="Invalid hashed password"):
            HashedPassword("tooshort")

    def test_hashed_password_not_exposed(self):
        """Test hashed password is not exposed in string representation."""
        hashed = "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
        password = HashedPassword(hashed)
        assert str(password) == "***HASHED***"
        assert hashed not in repr(password)


class TestUser:
    """Tests for User entity."""

    @pytest.fixture
    def valid_user_data(self):
        """Fixture providing valid user data."""
        return {
            "email": Email("user@example.com"),
            "hashed_password": HashedPassword(
                "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
            ),
            "username": "john_doe",
        }

    def test_create_user(self, valid_user_data):
        """Test creating a user with valid data."""
        user = User(**valid_user_data)

        assert user.email.value == "user@example.com"
        assert user.username == "john_doe"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_with_custom_id(self, valid_user_data):
        """Test creating a user with a custom ID."""
        custom_id = uuid4()
        user = User(**valid_user_data, id=custom_id)

        assert user.id == custom_id

    def test_user_equality_by_id(self, valid_user_data):
        """Test users are equal if they have the same ID."""
        user_id = uuid4()
        user1 = User(**valid_user_data, id=user_id)
        user2 = User(**valid_user_data, id=user_id)

        assert user1 == user2

    def test_user_inequality_by_id(self, valid_user_data):
        """Test users are not equal if they have different IDs."""
        user1 = User(**valid_user_data)
        user2 = User(**valid_user_data)

        assert user1 != user2

    def test_invalid_username_too_short(self, valid_user_data):
        """Test username that's too short raises error."""
        valid_user_data["username"] = "ab"
        with pytest.raises(ValueError, match="at least 3 characters"):
            User(**valid_user_data)

    def test_invalid_username_too_long(self, valid_user_data):
        """Test username that's too long raises error."""
        valid_user_data["username"] = "a" * 51
        with pytest.raises(ValueError, match="at most 50 characters"):
            User(**valid_user_data)

    def test_empty_username(self, valid_user_data):
        """Test empty username raises error."""
        valid_user_data["username"] = ""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(**valid_user_data)

    def test_update_email(self, valid_user_data):
        """Test updating user's email."""
        user = User(**valid_user_data)
        original_updated_at = user.updated_at

        new_email = Email("newemail@example.com")
        user.update_email(new_email)

        assert user.email == new_email
        assert user.is_verified is False  # Email change requires re-verification
        assert user.updated_at > original_updated_at

    def test_update_password(self, valid_user_data):
        """Test updating user's password."""
        user = User(**valid_user_data)
        original_updated_at = user.updated_at

        new_password = HashedPassword(
            "$2b$12$NEWKIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5"
        )
        user.update_password(new_password)

        assert user.hashed_password == new_password
        assert user.updated_at > original_updated_at

    def test_update_username(self, valid_user_data):
        """Test updating user's username."""
        user = User(**valid_user_data)
        original_updated_at = user.updated_at

        user.update_username("new_username")

        assert user.username == "new_username"
        assert user.updated_at > original_updated_at

    def test_activate_user(self, valid_user_data):
        """Test activating a user."""
        user = User(**valid_user_data, is_active=False)
        original_updated_at = user.updated_at

        user.activate()

        assert user.is_active is True
        assert user.updated_at > original_updated_at

    def test_deactivate_user(self, valid_user_data):
        """Test deactivating a user."""
        user = User(**valid_user_data)
        original_updated_at = user.updated_at

        user.deactivate()

        assert user.is_active is False
        assert user.updated_at > original_updated_at

    def test_verify_email(self, valid_user_data):
        """Test verifying user's email."""
        user = User(**valid_user_data)
        original_updated_at = user.updated_at

        user.verify_email()

        assert user.is_verified is True
        assert user.updated_at > original_updated_at

    def test_user_str_representation(self, valid_user_data):
        """Test user string representation."""
        user = User(**valid_user_data)
        assert str(user) == "User(john_doe, user@example.com)"

    def test_user_repr_representation(self, valid_user_data):
        """Test user detailed representation."""
        user = User(**valid_user_data)
        repr_str = repr(user)

        assert "john_doe" in repr_str
        assert "user@example.com" in repr_str
        assert str(user.id) in repr_str
