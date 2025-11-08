"""Unit tests for User domain exceptions."""

import pytest
from uuid import uuid4

from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    InvalidEmailError,
    InvalidPasswordError,
    InvalidUsernameError,
    UserAlreadyExistsError,
    UserDomainError,
    UserNotActiveError,
    UserNotFoundError,
    UserNotVerifiedError,
)


class TestUserDomainError:
    """Tests for base UserDomainError exception."""

    def test_user_domain_error_message(self):
        """Test UserDomainError stores and displays message correctly."""
        error = UserDomainError("Test error message")
        assert error.message == "Test error message"
        assert str(error) == "Test error message"

    def test_user_domain_error_is_exception(self):
        """Test UserDomainError is an Exception."""
        error = UserDomainError("Test error")
        assert isinstance(error, Exception)


class TestUserNotFoundError:
    """Tests for UserNotFoundError exception."""

    def test_user_not_found_with_string_identifier(self):
        """Test UserNotFoundError with string identifier."""
        error = UserNotFoundError("user@example.com")
        assert error.identifier == "user@example.com"
        assert "User not found: user@example.com" in str(error)

    def test_user_not_found_with_uuid_identifier(self):
        """Test UserNotFoundError with UUID identifier."""
        user_id = uuid4()
        error = UserNotFoundError(user_id)
        assert error.identifier == user_id
        assert f"User not found: {user_id}" in str(error)

    def test_user_not_found_inherits_from_user_domain_error(self):
        """Test UserNotFoundError inherits from UserDomainError."""
        error = UserNotFoundError("test")
        assert isinstance(error, UserDomainError)


class TestUserAlreadyExistsError:
    """Tests for UserAlreadyExistsError exception."""

    def test_user_already_exists_with_email(self):
        """Test UserAlreadyExistsError for email conflict."""
        error = UserAlreadyExistsError("email", "user@example.com")
        assert error.field == "email"
        assert error.value == "user@example.com"
        assert "User with email 'user@example.com' already exists" in str(error)

    def test_user_already_exists_with_username(self):
        """Test UserAlreadyExistsError for username conflict."""
        error = UserAlreadyExistsError("username", "john_doe")
        assert error.field == "username"
        assert error.value == "john_doe"
        assert "User with username 'john_doe' already exists" in str(error)

    def test_user_already_exists_inherits_from_user_domain_error(self):
        """Test UserAlreadyExistsError inherits from UserDomainError."""
        error = UserAlreadyExistsError("email", "test@example.com")
        assert isinstance(error, UserDomainError)


class TestInvalidCredentialsError:
    """Tests for InvalidCredentialsError exception."""

    def test_invalid_credentials_message(self):
        """Test InvalidCredentialsError has correct message."""
        error = InvalidCredentialsError()
        assert "Invalid email or password" in str(error)

    def test_invalid_credentials_inherits_from_user_domain_error(self):
        """Test InvalidCredentialsError inherits from UserDomainError."""
        error = InvalidCredentialsError()
        assert isinstance(error, UserDomainError)


class TestUserNotActiveError:
    """Tests for UserNotActiveError exception."""

    def test_user_not_active_message(self):
        """Test UserNotActiveError stores email and displays message."""
        error = UserNotActiveError("user@example.com")
        assert error.email == "user@example.com"
        assert "User account 'user@example.com' is not active" in str(error)

    def test_user_not_active_inherits_from_user_domain_error(self):
        """Test UserNotActiveError inherits from UserDomainError."""
        error = UserNotActiveError("user@example.com")
        assert isinstance(error, UserDomainError)


class TestUserNotVerifiedError:
    """Tests for UserNotVerifiedError exception."""

    def test_user_not_verified_message(self):
        """Test UserNotVerifiedError stores email and displays message."""
        error = UserNotVerifiedError("user@example.com")
        assert error.email == "user@example.com"
        assert "User 'user@example.com' has not verified their email" in str(error)

    def test_user_not_verified_inherits_from_user_domain_error(self):
        """Test UserNotVerifiedError inherits from UserDomainError."""
        error = UserNotVerifiedError("user@example.com")
        assert isinstance(error, UserDomainError)


class TestInvalidPasswordError:
    """Tests for InvalidPasswordError exception."""

    def test_invalid_password_default_message(self):
        """Test InvalidPasswordError with default message."""
        error = InvalidPasswordError()
        assert "Invalid password" in str(error)

    def test_invalid_password_custom_message(self):
        """Test InvalidPasswordError with custom message."""
        error = InvalidPasswordError("Password must contain uppercase letters")
        assert "Password must contain uppercase letters" in str(error)

    def test_invalid_password_inherits_from_user_domain_error(self):
        """Test InvalidPasswordError inherits from UserDomainError."""
        error = InvalidPasswordError()
        assert isinstance(error, UserDomainError)


class TestInvalidUsernameError:
    """Tests for InvalidUsernameError exception."""

    def test_invalid_username_default_message(self):
        """Test InvalidUsernameError with default message."""
        error = InvalidUsernameError()
        assert "Invalid username" in str(error)

    def test_invalid_username_custom_message(self):
        """Test InvalidUsernameError with custom message."""
        error = InvalidUsernameError("Username contains invalid characters")
        assert "Username contains invalid characters" in str(error)

    def test_invalid_username_inherits_from_user_domain_error(self):
        """Test InvalidUsernameError inherits from UserDomainError."""
        error = InvalidUsernameError()
        assert isinstance(error, UserDomainError)


class TestInvalidEmailError:
    """Tests for InvalidEmailError exception."""

    def test_invalid_email_default_message(self):
        """Test InvalidEmailError with default message."""
        error = InvalidEmailError()
        assert "Invalid email" in str(error)

    def test_invalid_email_custom_message(self):
        """Test InvalidEmailError with custom message."""
        error = InvalidEmailError("Email domain not allowed")
        assert "Email domain not allowed" in str(error)

    def test_invalid_email_inherits_from_user_domain_error(self):
        """Test InvalidEmailError inherits from UserDomainError."""
        error = InvalidEmailError()
        assert isinstance(error, UserDomainError)


class TestExceptionHierarchy:
    """Tests for exception hierarchy and catching."""

    def test_catch_all_user_domain_errors(self):
        """Test that all user exceptions can be caught as UserDomainError."""
        exceptions = [
            UserNotFoundError("test"),
            UserAlreadyExistsError("email", "test@example.com"),
            InvalidCredentialsError(),
            UserNotActiveError("test@example.com"),
            UserNotVerifiedError("test@example.com"),
            InvalidPasswordError(),
            InvalidUsernameError(),
            InvalidEmailError(),
        ]

        for exc in exceptions:
            try:
                raise exc
            except UserDomainError as e:
                assert e.message is not None
            else:
                pytest.fail(f"{exc.__class__.__name__} not caught as UserDomainError")
