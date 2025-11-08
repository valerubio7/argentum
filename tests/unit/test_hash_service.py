"""Unit tests for BcryptHashService."""

import pytest

from app.infrastructure.services.hash_service import BcryptHashService


class TestBcryptHashService:
    """Tests for Bcrypt hash service implementation."""

    @pytest.fixture
    def hash_service(self):
        """Fixture providing a hash service instance."""
        return BcryptHashService(rounds=4)  # Lower rounds for faster tests

    def test_hash_password(self, hash_service):
        """Test hashing a password."""
        password = "SecurePassword123"
        hashed = hash_service.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 20
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_hash_password_different_each_time(self, hash_service):
        """Test that hashing the same password produces different hashes (due to salt)."""
        password = "SecurePassword123"
        hash1 = hash_service.hash_password(password)
        hash2 = hash_service.hash_password(password)

        assert hash1 != hash2  # Different salts produce different hashes

    def test_hash_password_empty_raises_error(self, hash_service):
        """Test that hashing empty password raises error."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_service.hash_password("")

    def test_hash_password_non_string_raises_error(self, hash_service):
        """Test that hashing non-string raises error."""
        with pytest.raises(ValueError, match="Password must be a string"):
            hash_service.hash_password(123)  # type: ignore

    def test_verify_password_correct(self, hash_service):
        """Test verifying a correct password."""
        password = "SecurePassword123"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, hash_service):
        """Test verifying an incorrect password."""
        password = "SecurePassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password_raises_error(self, hash_service):
        """Test that verifying empty password raises error."""
        hashed = hash_service.hash_password("password")

        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_service.verify_password("", hashed)

    def test_verify_password_empty_hash_raises_error(self, hash_service):
        """Test that verifying with empty hash raises error."""
        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            hash_service.verify_password("password", "")

    def test_verify_password_non_string_password_raises_error(self, hash_service):
        """Test that verifying non-string password raises error."""
        hashed = hash_service.hash_password("password")

        with pytest.raises(ValueError, match="Password must be a string"):
            hash_service.verify_password(123, hashed)  # type: ignore

    def test_verify_password_non_string_hash_raises_error(self, hash_service):
        """Test that verifying non-string hash raises error."""
        with pytest.raises(ValueError, match="Hashed password must be a string"):
            hash_service.verify_password("password", 123)  # type: ignore

    def test_verify_password_invalid_hash_format(self, hash_service):
        """Test that verifying with invalid hash format returns False."""
        result = hash_service.verify_password("password", "invalid_hash")

        assert result is False

    def test_hash_service_custom_rounds(self):
        """Test creating hash service with custom rounds."""
        service = BcryptHashService(rounds=6)
        password = "TestPassword"
        hashed = service.hash_password(password)

        assert hashed.startswith("$2b$06$")  # Verify rounds in hash
        assert service.verify_password(password, hashed) is True

    def test_hash_password_unicode(self, hash_service):
        """Test hashing password with unicode characters."""
        password = "Contraseña123!@#"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True

    def test_hash_password_special_characters(self, hash_service):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_service.hash_password(password)

        assert hash_service.verify_password(password, hashed) is True
        assert hash_service.verify_password("P@ssw0rd", hashed) is False
