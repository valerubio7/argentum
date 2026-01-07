"""Tests for BcryptHashService."""

import pytest
import re

from infrastructure.services.hash_service import BcryptHashService


class TestHashPassword:
    """Tests for password hashing."""

    def test_hash_password_generates_different_hashes_for_same_password(self):
        """Test that hashing the same password twice produces different hashes.

        This is expected because bcrypt generates a random salt for each hash.
        """
        service = BcryptHashService()
        password = "my_secure_password"

        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)

        assert hash1 != hash2

    def test_hash_password_produces_valid_bcrypt_format(self):
        """Test that the hash follows bcrypt format ($2b$rounds$salt+hash)."""
        service = BcryptHashService(rounds=10)
        password = "test_password"

        hashed = service.hash_password(password)

        # Bcrypt hash format: $2b$rounds$22-char-salt+31-char-hash
        # Total length is typically 60 characters
        assert len(hashed) == 60
        assert hashed.startswith("$2b$10$")

        # Validate full bcrypt format with regex
        bcrypt_pattern = re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")
        assert bcrypt_pattern.match(hashed)

    def test_hash_password_with_different_rounds(self):
        """Test hashing with different complexity rounds."""
        service_low = BcryptHashService(rounds=4)
        service_high = BcryptHashService(rounds=12)
        password = "test_password"

        hash_low = service_low.hash_password(password)
        hash_high = service_high.hash_password(password)

        assert hash_low.startswith("$2b$04$")
        assert hash_high.startswith("$2b$12$")

    def test_hash_password_with_empty_string_raises_error(self):
        """Test that empty password raises ValueError."""
        service = BcryptHashService()

        with pytest.raises(ValueError, match="Password cannot be empty"):
            service.hash_password("")

    def test_hash_password_with_none_raises_error(self):
        """Test that None password raises ValueError."""
        service = BcryptHashService()

        with pytest.raises(ValueError, match="Password cannot be empty"):
            service.hash_password(None)  # type: ignore

    def test_hash_password_with_non_string_raises_error(self):
        """Test that non-string password raises ValueError."""
        service = BcryptHashService()

        with pytest.raises(ValueError, match="Password must be a string"):
            service.hash_password(12345)  # type: ignore


class TestVerifyPassword:
    """Tests for password verification."""

    def test_verify_password_returns_true_with_correct_password(self):
        """Test that verification succeeds with correct password."""
        service = BcryptHashService()
        password = "my_secure_password"

        hashed = service.hash_password(password)
        result = service.verify_password(password, hashed)

        assert result is True

    def test_verify_password_returns_false_with_incorrect_password(self):
        """Test that verification fails with incorrect password."""
        service = BcryptHashService()
        correct_password = "correct_password"
        wrong_password = "wrong_password"

        hashed = service.hash_password(correct_password)
        result = service.verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_with_different_case(self):
        """Test that password verification is case-sensitive."""
        service = BcryptHashService()
        password = "MyPassword"

        hashed = service.hash_password(password)
        result_lowercase = service.verify_password("mypassword", hashed)
        result_uppercase = service.verify_password("MYPASSWORD", hashed)

        assert result_lowercase is False
        assert result_uppercase is False

    def test_verify_password_handles_invalid_hash_format(self):
        """Test that invalid hash format returns False instead of raising."""
        service = BcryptHashService()
        password = "test_password"
        invalid_hash = "not_a_valid_bcrypt_hash"

        result = service.verify_password(password, invalid_hash)

        assert result is False

    def test_verify_password_handles_malformed_hash(self):
        """Test various malformed hash formats."""
        service = BcryptHashService()
        password = "test_password"

        malformed_hashes = [
            "short",
            "$2b$invalid",
            "random_string_60_chars_long_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "$2b$12$",  # Too short
        ]

        for bad_hash in malformed_hashes:
            result = service.verify_password(password, bad_hash)
            assert result is False

    def test_verify_password_with_empty_password_raises_error(self):
        """Test that empty password raises ValueError."""
        service = BcryptHashService()
        hashed = service.hash_password("valid_password")

        with pytest.raises(ValueError, match="Password cannot be empty"):
            service.verify_password("", hashed)

    def test_verify_password_with_empty_hash_raises_error(self):
        """Test that empty hash raises ValueError."""
        service = BcryptHashService()

        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            service.verify_password("password", "")

    def test_verify_password_with_none_inputs_raises_error(self):
        """Test that None inputs raise ValueError."""
        service = BcryptHashService()

        with pytest.raises(ValueError, match="Password cannot be empty"):
            service.verify_password(None, "hash")  # type: ignore

        with pytest.raises(ValueError, match="Hashed password cannot be empty"):
            service.verify_password("password", None)  # type: ignore


class TestBcryptServiceIntegration:
    """Integration tests for the complete hash and verify workflow."""

    def test_hash_and_verify_workflow(self):
        """Test the complete workflow of hashing and verifying."""
        service = BcryptHashService()
        passwords = [
            "simple",
            "with spaces",
            "with$pecial!chars@123",
            "unicode_emoji_🔒",
            "medium_length_password_that_is_within_72_bytes",
        ]

        for password in passwords:
            hashed = service.hash_password(password)
            assert service.verify_password(password, hashed) is True
            assert service.verify_password(password + "wrong", hashed) is False

    def test_multiple_services_can_verify_same_hash(self):
        """Test that different service instances can verify the same hash."""
        service1 = BcryptHashService()
        service2 = BcryptHashService()
        password = "shared_password"

        hashed = service1.hash_password(password)
        result = service2.verify_password(password, hashed)

        assert result is True
