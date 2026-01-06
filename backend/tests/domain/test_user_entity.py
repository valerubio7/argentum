"""Tests for User entity."""

import pytest
from uuid import UUID
from datetime import datetime

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword


class TestUserEntityCreation:
    """Tests for User entity creation."""

    def test_create_user_with_valid_data(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test creating a user with valid data."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
        )

        assert user.email == valid_email
        assert user.hashed_password == valid_hashed_password
        assert user.username == valid_username
        assert user.is_active is True
        assert user.is_verified is False
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_create_user_with_custom_id(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test creating a user with a custom UUID."""
        from uuid import uuid4

        custom_id = uuid4()
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
            id=custom_id,
        )

        assert user.id == custom_id

    def test_create_user_with_inactive_status(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test creating an inactive user."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
            is_active=False,
        )

        assert user.is_active is False

    def test_create_user_with_verified_status(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test creating a verified user."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
            is_verified=True,
        )

        assert user.is_verified is True


class TestUsernameValidation:
    """Tests for username validation."""

    def test_username_cannot_be_empty(self, valid_email, valid_hashed_password):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(
                email=valid_email,
                hashed_password=valid_hashed_password,
                username="",
            )

    def test_username_too_short(self, valid_email, valid_hashed_password):
        """Test that username with less than 3 characters raises ValueError."""
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            User(
                email=valid_email,
                hashed_password=valid_hashed_password,
                username="ab",
            )

    def test_username_too_long(self, valid_email, valid_hashed_password):
        """Test that username with more than 50 characters raises ValueError."""
        long_username = "a" * 51
        with pytest.raises(ValueError, match="Username must be at most 50 characters"):
            User(
                email=valid_email,
                hashed_password=valid_hashed_password,
                username=long_username,
            )

    def test_username_strips_whitespace(self, valid_email, valid_hashed_password):
        """Test that username whitespace is stripped."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username="  testuser  ",
        )

        assert user.username == "testuser"

    def test_username_minimum_length(self, valid_email, valid_hashed_password):
        """Test username with exactly 3 characters is valid."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username="abc",
        )

        assert user.username == "abc"

    def test_username_maximum_length(self, valid_email, valid_hashed_password):
        """Test username with exactly 50 characters is valid."""
        username = "a" * 50
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=username,
        )

        assert user.username == username


class TestEmailValidation:
    """Tests for Email value object validation."""

    def test_valid_email(self):
        """Test creating a valid email."""
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_email_normalized_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        email = Email("User@EXAMPLE.COM")
        assert email.value == "user@example.com"

    def test_email_cannot_be_empty(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_invalid_email_format(self):
        """Test that invalid email format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("invalid-email")

    def test_email_without_domain(self):
        """Test email without domain raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("user@")

    def test_email_without_at_symbol(self):
        """Test email without @ symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("userexample.com")

    def test_email_too_long(self):
        """Test that email over 255 characters raises ValueError."""
        long_email = "a" * 250 + "@b.com"
        with pytest.raises(ValueError, match="Email is too long"):
            Email(long_email)


class TestUserMethods:
    """Tests for User entity methods."""

    def test_update_email(self, user_entity):
        """Test updating user email."""
        new_email = Email("newemail@example.com")
        old_updated_at = user_entity.updated_at

        user_entity.update_email(new_email)

        assert user_entity.email == new_email
        assert user_entity.is_verified is False  # Should require re-verification
        assert user_entity.updated_at >= old_updated_at

    def test_update_password(self, user_entity):
        """Test updating user password."""
        new_password = HashedPassword("$2b$12$NewHashedPasswordValue1234567890123456")
        old_updated_at = user_entity.updated_at

        user_entity.update_password(new_password)

        assert user_entity.hashed_password == new_password
        assert user_entity.updated_at >= old_updated_at

    def test_update_username(self, user_entity):
        """Test updating username."""
        new_username = "newusername"
        old_updated_at = user_entity.updated_at

        user_entity.update_username(new_username)

        assert user_entity.username == new_username
        assert user_entity.updated_at >= old_updated_at

    def test_activate_user(self, valid_email, valid_hashed_password, valid_username):
        """Test activating a user."""
        user = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
            is_active=False,
        )

        user.activate()

        assert user.is_active is True

    def test_deactivate_user(self, user_entity):
        """Test deactivating a user."""
        user_entity.deactivate()

        assert user_entity.is_active is False

    def test_verify_email(self, user_entity):
        """Test verifying user email."""
        user_entity.verify_email()

        assert user_entity.is_verified is True


class TestUserEquality:
    """Tests for User entity equality."""

    def test_users_with_same_id_are_equal(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test that users with the same ID are equal."""
        from uuid import uuid4

        shared_id = uuid4()
        user1 = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
            id=shared_id,
        )
        user2 = User(
            email=Email("other@example.com"),
            hashed_password=valid_hashed_password,
            username="otherusername",
            id=shared_id,
        )

        assert user1 == user2

    def test_users_with_different_id_are_not_equal(
        self, valid_email, valid_hashed_password, valid_username
    ):
        """Test that users with different IDs are not equal."""
        user1 = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
        )
        user2 = User(
            email=valid_email,
            hashed_password=valid_hashed_password,
            username=valid_username,
        )

        assert user1 != user2
