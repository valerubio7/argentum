"""Tests for JWTTokenService."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import time

from infrastructure.services.jwt_token_service import JWTTokenService
from domain.exceptions.token_exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    InvalidTokenFormatError,
)


class TestGenerateToken:
    """Tests for token generation."""

    def test_generate_token_with_valid_data(self):
        """Test generating a token with valid user data."""
        service = JWTTokenService(secret_key="test_secret_key")
        user_id = uuid4()
        email = "test@example.com"

        token, expires_at = service.generate_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(expires_at, datetime)
        assert expires_at > datetime.now(timezone.utc)

    def test_generate_token_with_custom_expiration(self):
        """Test token generation with custom expiration time."""
        service = JWTTokenService(
            secret_key="test_secret_key", access_token_expire_minutes=60
        )
        user_id = uuid4()
        email = "test@example.com"

        token, expires_at = service.generate_token(user_id, email)

        # Check expiration is approximately 60 minutes from now
        expected_expiration = datetime.now(timezone.utc) + timedelta(minutes=60)
        time_diff = abs((expires_at - expected_expiration).total_seconds())
        assert time_diff < 2  # Within 2 seconds

    def test_generate_token_creates_different_tokens(self):
        """Test that generating tokens at different times creates different tokens."""
        service = JWTTokenService(secret_key="test_secret_key")
        user_id = uuid4()
        email = "test@example.com"

        token1, _ = service.generate_token(user_id, email)
        time.sleep(1.1)  # Delay to ensure different 'iat' (JWT uses seconds)
        token2, _ = service.generate_token(user_id, email)

        assert token1 != token2

    def test_generate_token_with_empty_user_id_raises_error(self):
        """Test that empty user_id raises ValueError."""
        service = JWTTokenService(secret_key="test_secret_key")

        with pytest.raises(ValueError, match="User ID cannot be empty"):
            service.generate_token(None, "test@example.com")  # type: ignore

    def test_generate_token_with_empty_email_raises_error(self):
        """Test that empty email raises ValueError."""
        service = JWTTokenService(secret_key="test_secret_key")
        user_id = uuid4()

        with pytest.raises(ValueError, match="Email cannot be empty"):
            service.generate_token(user_id, "")

    def test_generate_token_with_none_email_raises_error(self):
        """Test that None email raises ValueError."""
        service = JWTTokenService(secret_key="test_secret_key")
        user_id = uuid4()

        with pytest.raises(ValueError, match="Email cannot be empty"):
            service.generate_token(user_id, None)  # type: ignore


class TestValidateToken:
    """Tests for token validation."""

    def test_validate_token_with_valid_token(self):
        """Test validating a valid token returns correct data."""
        service = JWTTokenService(secret_key="test_secret_key")
        user_id = uuid4()
        email = "test@example.com"

        token, _ = service.generate_token(user_id, email)
        result = service.validate_token(token)

        assert result["user_id"] == str(user_id)
        assert result["email"] == email

    def test_validate_token_with_expired_token_raises_error(self):
        """Test that expired token raises ExpiredTokenError."""
        service = JWTTokenService(
            secret_key="test_secret_key", access_token_expire_minutes=0
        )
        user_id = uuid4()
        email = "test@example.com"

        token, _ = service.generate_token(user_id, email)
        time.sleep(1)  # Wait for token to expire

        with pytest.raises(ExpiredTokenError):
            service.validate_token(token)

    def test_validate_token_with_invalid_format_raises_error(self):
        """Test that invalid token format raises InvalidTokenFormatError."""
        service = JWTTokenService(secret_key="test_secret_key")

        with pytest.raises(InvalidTokenFormatError, match="Token cannot be empty"):
            service.validate_token("")

    def test_validate_token_with_malformed_token_raises_error(self):
        """Test that malformed token raises InvalidTokenError."""
        service = JWTTokenService(secret_key="test_secret_key")
        malformed_token = "not.a.jwt"

        with pytest.raises(InvalidTokenError):
            service.validate_token(malformed_token)

    def test_validate_token_with_wrong_secret_raises_error(self):
        """Test that token signed with different secret raises InvalidTokenError."""
        service1 = JWTTokenService(secret_key="secret1")
        service2 = JWTTokenService(secret_key="secret2")
        user_id = uuid4()
        email = "test@example.com"

        token, _ = service1.generate_token(user_id, email)

        with pytest.raises(InvalidTokenError):
            service2.validate_token(token)

    def test_validate_token_with_none_raises_error(self):
        """Test that None token raises InvalidTokenFormatError."""
        service = JWTTokenService(secret_key="test_secret_key")

        with pytest.raises(InvalidTokenFormatError, match="Token cannot be empty"):
            service.validate_token(None)  # type: ignore


class TestGetTokenExpiration:
    """Tests for getting token expiration."""

    def test_get_token_expiration_returns_correct_datetime(self):
        """Test getting expiration datetime from a valid token."""
        service = JWTTokenService(
            secret_key="test_secret_key", access_token_expire_minutes=30
        )
        user_id = uuid4()
        email = "test@example.com"

        token, expected_expiration = service.generate_token(user_id, email)
        actual_expiration = service.get_token_expiration(token)

        # Compare timestamps (should be very close)
        time_diff = abs((actual_expiration - expected_expiration).total_seconds())
        assert time_diff < 1  # Within 1 second

    def test_get_token_expiration_with_empty_token_raises_error(self):
        """Test that empty token raises InvalidTokenFormatError."""
        service = JWTTokenService(secret_key="test_secret_key")

        with pytest.raises(InvalidTokenFormatError, match="Token cannot be empty"):
            service.get_token_expiration("")

    def test_get_token_expiration_with_invalid_token_raises_error(self):
        """Test that invalid token raises InvalidTokenError."""
        service = JWTTokenService(secret_key="test_secret_key")

        with pytest.raises(InvalidTokenError):
            service.get_token_expiration("invalid.token.here")

    def test_get_token_expiration_works_with_expired_token(self):
        """Test that expiration can be retrieved even from expired token."""
        service = JWTTokenService(
            secret_key="test_secret_key", access_token_expire_minutes=0
        )
        user_id = uuid4()
        email = "test@example.com"

        token, expected_expiration = service.generate_token(user_id, email)
        time.sleep(1)  # Wait for token to expire

        # Should still be able to get expiration
        actual_expiration = service.get_token_expiration(token)
        time_diff = abs((actual_expiration - expected_expiration).total_seconds())
        assert time_diff < 1


class TestJWTServiceInitialization:
    """Tests for service initialization."""

    def test_initialize_with_valid_secret_key(self):
        """Test successful initialization with valid secret key."""
        service = JWTTokenService(secret_key="my_secret_key")
        assert service is not None

    def test_initialize_with_empty_secret_key_raises_error(self):
        """Test that empty secret key raises ValueError."""
        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            JWTTokenService(secret_key="")

    def test_initialize_with_custom_algorithm(self):
        """Test initialization with custom algorithm."""
        service = JWTTokenService(secret_key="test_secret", algorithm="HS512")
        user_id = uuid4()
        email = "test@example.com"

        token, _ = service.generate_token(user_id, email)
        result = service.validate_token(token)

        assert result["user_id"] == str(user_id)
        assert result["email"] == email


class TestJWTServiceIntegration:
    """Integration tests for complete workflows."""

    def test_full_token_lifecycle(self):
        """Test the complete lifecycle: generate, validate, get expiration."""
        service = JWTTokenService(
            secret_key="test_secret_key", access_token_expire_minutes=30
        )
        user_id = uuid4()
        email = "test@example.com"

        # Generate token
        token, expected_expiration = service.generate_token(user_id, email)
        assert token is not None

        # Validate token
        result = service.validate_token(token)
        assert result["user_id"] == str(user_id)
        assert result["email"] == email

        # Get expiration
        actual_expiration = service.get_token_expiration(token)
        time_diff = abs((actual_expiration - expected_expiration).total_seconds())
        assert time_diff < 1

    def test_tokens_from_different_services_incompatible(self):
        """Test that tokens from different services are incompatible."""
        service1 = JWTTokenService(secret_key="secret1")
        service2 = JWTTokenService(secret_key="secret2")
        user_id = uuid4()
        email = "test@example.com"

        token1, _ = service1.generate_token(user_id, email)
        token2, _ = service2.generate_token(user_id, email)

        # Tokens should be different
        assert token1 != token2

        # Each service can validate its own token
        assert service1.validate_token(token1)["user_id"] == str(user_id)
        assert service2.validate_token(token2)["user_id"] == str(user_id)

        # But cannot validate the other's token
        with pytest.raises(InvalidTokenError):
            service1.validate_token(token2)
        with pytest.raises(InvalidTokenError):
            service2.validate_token(token1)
