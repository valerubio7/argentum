"""Unit tests for Authentication DTOs."""

import pytest
from datetime import datetime

from app.application.dtos.auth_dtos import (
    LoginDTO,
    RegisterUserDTO,
    TokenDTO,
    UserResponseDTO,
)


class TestRegisterUserDTO:
    """Tests for RegisterUserDTO."""

    def test_create_valid_register_dto(self):
        """Test creating a valid registration DTO."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        assert dto.email == "user@example.com"
        assert dto.password == "SecurePassword123"
        assert dto.username == "john_doe"

    def test_register_dto_is_immutable(self):
        """Test that RegisterUserDTO is immutable."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        with pytest.raises(AttributeError):
            dto.email = "new@example.com"

    def test_register_dto_empty_email_raises_error(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email is required"):
            RegisterUserDTO(
                email="",
                password="SecurePassword123",
                username="john_doe",
            )

    def test_register_dto_empty_password_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password is required"):
            RegisterUserDTO(
                email="user@example.com",
                password="",
                username="john_doe",
            )

    def test_register_dto_empty_username_raises_error(self):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Username is required"):
            RegisterUserDTO(
                email="user@example.com",
                password="SecurePassword123",
                username="",
            )


class TestLoginDTO:
    """Tests for LoginDTO."""

    def test_create_valid_login_dto(self):
        """Test creating a valid login DTO."""
        dto = LoginDTO(
            email="user@example.com",
            password="SecurePassword123",
        )

        assert dto.email == "user@example.com"
        assert dto.password == "SecurePassword123"

    def test_login_dto_is_immutable(self):
        """Test that LoginDTO is immutable."""
        dto = LoginDTO(
            email="user@example.com",
            password="SecurePassword123",
        )

        with pytest.raises(AttributeError):
            dto.email = "new@example.com"

    def test_login_dto_empty_email_raises_error(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email is required"):
            LoginDTO(email="", password="SecurePassword123")

    def test_login_dto_empty_password_raises_error(self):
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password is required"):
            LoginDTO(email="user@example.com", password="")


class TestTokenDTO:
    """Tests for TokenDTO."""

    def test_create_valid_token_dto(self):
        """Test creating a valid token DTO."""
        expires_at = datetime.now()
        dto = TokenDTO(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer",
            expires_at=expires_at,
        )

        assert dto.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert dto.token_type == "bearer"
        assert dto.expires_at == expires_at

    def test_token_dto_default_token_type(self):
        """Test that token_type defaults to 'bearer'."""
        dto = TokenDTO(access_token="some_token")

        assert dto.token_type == "bearer"

    def test_token_dto_is_immutable(self):
        """Test that TokenDTO is immutable."""
        dto = TokenDTO(access_token="some_token")

        with pytest.raises(AttributeError):
            dto.access_token = "new_token"

    def test_token_dto_empty_access_token_raises_error(self):
        """Test that empty access_token raises ValueError."""
        with pytest.raises(ValueError, match="Access token is required"):
            TokenDTO(access_token="")

    def test_token_dto_empty_token_type_raises_error(self):
        """Test that empty token_type raises ValueError."""
        with pytest.raises(ValueError, match="Token type is required"):
            TokenDTO(access_token="some_token", token_type="")

    def test_token_dto_without_expiration(self):
        """Test creating token DTO without expiration."""
        dto = TokenDTO(access_token="some_token")

        assert dto.expires_at is None


class TestUserResponseDTO:
    """Tests for UserResponseDTO."""

    def test_create_valid_user_response_dto(self):
        """Test creating a valid user response DTO."""
        created_at = datetime.now()
        dto = UserResponseDTO(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="user@example.com",
            username="john_doe",
            is_active=True,
            is_verified=False,
            created_at=created_at,
        )

        assert dto.id == "550e8400-e29b-41d4-a716-446655440000"
        assert dto.email == "user@example.com"
        assert dto.username == "john_doe"
        assert dto.is_active is True
        assert dto.is_verified is False
        assert dto.created_at == created_at

    def test_user_response_dto_is_immutable(self):
        """Test that UserResponseDTO is immutable."""
        dto = UserResponseDTO(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="user@example.com",
            username="john_doe",
            is_active=True,
            is_verified=False,
            created_at=datetime.now(),
        )

        with pytest.raises(AttributeError):
            dto.email = "new@example.com"

    def test_user_response_dto_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="User ID is required"):
            UserResponseDTO(
                id="",
                email="user@example.com",
                username="john_doe",
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
            )

    def test_user_response_dto_empty_email_raises_error(self):
        """Test that empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email is required"):
            UserResponseDTO(
                id="550e8400-e29b-41d4-a716-446655440000",
                email="",
                username="john_doe",
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
            )

    def test_user_response_dto_empty_username_raises_error(self):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Username is required"):
            UserResponseDTO(
                id="550e8400-e29b-41d4-a716-446655440000",
                email="user@example.com",
                username="",
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
            )
