"""Unit tests for JWTTokenService."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.infrastructure.services.jwt_token_service import (
    InvalidTokenError,
    JWTTokenService,
)


class TestJWTTokenService:
    """Tests for JWT token service implementation."""

    @pytest.fixture
    def token_service(self):
        """Fixture providing a token service instance."""
        return JWTTokenService(
            secret_key="test_secret_key_12345",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )

    @pytest.fixture
    def user_data(self):
        """Fixture providing sample user data."""
        return {"user_id": uuid4(), "email": "user@example.com"}

    def test_generate_token(self, token_service, user_data):
        """Test generating a token."""
        token, expires_at = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        assert isinstance(expires_at, datetime)
        assert expires_at > datetime.now(timezone.utc)

    def test_generate_token_expiration_time(self, token_service, user_data):
        """Test that token expires at correct time."""
        token, expires_at = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        # Should expire in approximately 30 minutes
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
        time_diff = abs((expires_at - expected_expiry).total_seconds())

        assert time_diff < 2  # Within 2 seconds

    def test_generate_token_empty_user_id_raises_error(self, token_service):
        """Test that generating token with empty user_id raises error."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            token_service.generate_token(None, "user@example.com")  # type: ignore

    def test_generate_token_empty_email_raises_error(self, token_service, user_data):
        """Test that generating token with empty email raises error."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            token_service.generate_token(user_data["user_id"], "")

    def test_validate_token(self, token_service, user_data):
        """Test validating a valid token."""
        token, _ = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        payload = token_service.validate_token(token)

        assert payload is not None
        assert payload["user_id"] == str(user_data["user_id"])
        assert payload["email"] == user_data["email"]

    def test_validate_token_empty_raises_error(self, token_service):
        """Test that validating empty token raises error."""
        with pytest.raises(InvalidTokenError, match="Token cannot be empty"):
            token_service.validate_token("")

    def test_validate_token_invalid_raises_error(self, token_service):
        """Test that validating invalid token raises error."""
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            token_service.validate_token("invalid.token.here")

    def test_validate_token_expired_raises_error(self):
        """Test that validating expired token raises error."""
        # Create service with very short expiration
        service = JWTTokenService(
            secret_key="test_secret",
            access_token_expire_minutes=-1,  # Already expired
        )
        user_id = uuid4()
        token, _ = service.generate_token(user_id, "user@example.com")

        with pytest.raises(InvalidTokenError, match="Token has expired"):
            service.validate_token(token)

    def test_validate_token_wrong_secret_raises_error(self, user_data):
        """Test that validating token with wrong secret raises error."""
        service1 = JWTTokenService(secret_key="secret1")
        service2 = JWTTokenService(secret_key="secret2")

        token, _ = service1.generate_token(user_data["user_id"], user_data["email"])

        with pytest.raises(InvalidTokenError, match="Invalid token"):
            service2.validate_token(token)

    def test_get_token_expiration(self, token_service, user_data):
        """Test getting token expiration."""
        token, original_expiry = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        expiry = token_service.get_token_expiration(token)

        assert isinstance(expiry, datetime)
        # Should be very close to original expiry (within 1 second)
        time_diff = abs((expiry - original_expiry).total_seconds())
        assert time_diff < 1

    def test_get_token_expiration_empty_raises_error(self, token_service):
        """Test that getting expiration of empty token raises error."""
        with pytest.raises(InvalidTokenError, match="Token cannot be empty"):
            token_service.get_token_expiration("")

    def test_get_token_expiration_invalid_raises_error(self, token_service):
        """Test that getting expiration of invalid token raises error."""
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            token_service.get_token_expiration("invalid.token")

    def test_token_service_custom_algorithm(self, user_data):
        """Test creating token service with custom algorithm."""
        service = JWTTokenService(secret_key="test_secret", algorithm="HS512")

        token, _ = service.generate_token(user_data["user_id"], user_data["email"])
        payload = service.validate_token(token)

        assert payload["user_id"] == str(user_data["user_id"])

    def test_token_service_custom_expiration(self, user_data):
        """Test creating token service with custom expiration."""
        service = JWTTokenService(
            secret_key="test_secret", access_token_expire_minutes=60
        )

        token, expires_at = service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=60)
        time_diff = abs((expires_at - expected_expiry).total_seconds())

        assert time_diff < 2

    def test_token_service_empty_secret_raises_error(self):
        """Test that creating service with empty secret raises error."""
        with pytest.raises(ValueError, match="Secret key cannot be empty"):
            JWTTokenService(secret_key="")

    def test_token_contains_issued_at(self, token_service, user_data):
        """Test that token contains issued at timestamp."""
        import jwt

        token, _ = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        # Decode without verification to inspect payload
        payload = jwt.decode(token, options={"verify_signature": False})

        assert "iat" in payload
        assert isinstance(payload["iat"], int)

        # Issued at should be recent (within last 5 seconds)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        time_since_issued = (datetime.now(timezone.utc) - iat_time).total_seconds()
        assert time_since_issued < 5

    def test_token_subject_is_user_id(self, token_service, user_data):
        """Test that token subject (sub) is the user ID."""
        import jwt

        token, _ = token_service.generate_token(
            user_data["user_id"], user_data["email"]
        )

        # Decode without verification to inspect payload
        payload = jwt.decode(token, options={"verify_signature": False})

        assert payload["sub"] == str(user_data["user_id"])

    def test_multiple_users_different_tokens(self, token_service):
        """Test that different users get different tokens."""
        user1_id = uuid4()
        user2_id = uuid4()

        token1, _ = token_service.generate_token(user1_id, "user1@example.com")
        token2, _ = token_service.generate_token(user2_id, "user2@example.com")

        assert token1 != token2

        payload1 = token_service.validate_token(token1)
        payload2 = token_service.validate_token(token2)

        assert payload1["user_id"] != payload2["user_id"]
        assert payload1["email"] != payload2["email"]
