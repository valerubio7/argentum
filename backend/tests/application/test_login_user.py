"""Tests for LoginUser use case."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from application.dtos.auth_dtos import LoginDTO, TokenDTO
from application.use_cases.login_user import LoginUser
from domain.entities.user import User
from domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
)
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword


class TestLoginUser:
    """Tests for the LoginUser use case."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock UserRepository."""
        return AsyncMock()

    @pytest.fixture
    def mock_hash_service(self):
        """Create a mock HashService."""
        service = Mock()
        service.verify_password = Mock(return_value=True)
        return service

    @pytest.fixture
    def mock_token_service(self):
        """Create a mock TokenService."""
        service = Mock()
        expires_at = datetime.now(timezone.utc)
        service.generate_token = Mock(return_value=("mock_jwt_token_here", expires_at))
        return service

    @pytest.fixture
    def login_user_use_case(
        self, mock_user_repository, mock_hash_service, mock_token_service
    ):
        """Create a LoginUser use case with mocked dependencies."""
        return LoginUser(
            user_repository=mock_user_repository,
            hash_service=mock_hash_service,
            token_service=mock_token_service,
        )

    @pytest.fixture
    def valid_login_dto(self):
        """Create a valid LoginDTO."""
        return LoginDTO(email="test@example.com", password="SecurePassword123!")

    @pytest.fixture
    def existing_user(self):
        """Create an existing active user."""
        user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=True,
            is_verified=True,
        )
        user._id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        login_user_use_case,
        mock_user_repository,
        mock_hash_service,
        mock_token_service,
        valid_login_dto,
        existing_user,
    ):
        """Test successful user login (happy path) returns valid TokenDTO."""
        # Arrange
        mock_user_repository.find_by_email = AsyncMock(return_value=existing_user)

        # Act
        result = await login_user_use_case.execute(valid_login_dto)

        # Assert
        assert isinstance(result, TokenDTO)
        assert result.access_token == "mock_jwt_token_here"
        assert result.token_type == "bearer"
        assert result.expires_at is not None
        mock_user_repository.find_by_email.assert_called_once()
        mock_hash_service.verify_password.assert_called_once_with(
            "SecurePassword123!", "$2b$12$hashed_password_value_here"
        )
        mock_token_service.generate_token.assert_called_once_with(
            user_id=existing_user.id, email="test@example.com"
        )

    @pytest.mark.asyncio
    async def test_login_invalid_email(
        self,
        login_user_use_case,
        mock_user_repository,
        valid_login_dto,
    ):
        """Test that login with non-existent email raises InvalidCredentialsError."""
        # Arrange
        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await login_user_use_case.execute(valid_login_dto)

        mock_user_repository.find_by_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_invalid_password(
        self,
        login_user_use_case,
        mock_user_repository,
        mock_hash_service,
        valid_login_dto,
        existing_user,
    ):
        """Test that login with incorrect password raises InvalidCredentialsError."""
        # Arrange
        mock_user_repository.find_by_email = AsyncMock(return_value=existing_user)
        mock_hash_service.verify_password = Mock(return_value=False)

        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            await login_user_use_case.execute(valid_login_dto)

        mock_user_repository.find_by_email.assert_called_once()
        mock_hash_service.verify_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self,
        login_user_use_case,
        mock_user_repository,
        valid_login_dto,
    ):
        """Test that login with inactive user raises UserNotActiveError."""
        # Arrange
        inactive_user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=False,  # User is not active
            is_verified=True,
        )
        inactive_user._id = uuid4()
        mock_user_repository.find_by_email = AsyncMock(return_value=inactive_user)

        # Act & Assert
        with pytest.raises(UserNotActiveError) as exc_info:
            await login_user_use_case.execute(valid_login_dto)

        assert "test@example.com" in str(exc_info.value)
        mock_user_repository.find_by_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_empty_email(
        self,
        login_user_use_case,
    ):
        """Test that login with empty email raises ValueError from DTO validation."""
        # Arrange & Act & Assert
        # LoginDTO validates in __post_init__ and raises ValueError
        with pytest.raises(ValueError, match="Email is required"):
            LoginDTO(email="", password="SecurePassword123!")

    @pytest.mark.asyncio
    async def test_login_empty_password(
        self,
        login_user_use_case,
    ):
        """Test that login with empty password raises ValueError from DTO validation."""
        # Arrange & Act & Assert
        # LoginDTO validates in __post_init__ and raises ValueError
        with pytest.raises(ValueError, match="Password is required"):
            LoginDTO(email="test@example.com", password="")

    @pytest.mark.asyncio
    async def test_login_token_contains_user_id(
        self,
        login_user_use_case,
        mock_user_repository,
        mock_token_service,
        valid_login_dto,
        existing_user,
    ):
        """Test that the generated token contains the correct user_id."""
        # Arrange
        mock_user_repository.find_by_email = AsyncMock(return_value=existing_user)

        # Act
        await login_user_use_case.execute(valid_login_dto)

        # Assert
        mock_token_service.generate_token.assert_called_once()
        call_args = mock_token_service.generate_token.call_args
        assert call_args.kwargs["user_id"] == existing_user.id
        assert call_args.kwargs["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_password_verification_called(
        self,
        login_user_use_case,
        mock_user_repository,
        mock_hash_service,
        valid_login_dto,
        existing_user,
    ):
        """Test that hash_service.verify_password is called with correct parameters."""
        # Arrange
        mock_user_repository.find_by_email = AsyncMock(return_value=existing_user)

        # Act
        await login_user_use_case.execute(valid_login_dto)

        # Assert
        mock_hash_service.verify_password.assert_called_once_with(
            "SecurePassword123!", "$2b$12$hashed_password_value_here"
        )

    @pytest.mark.asyncio
    async def test_login_generic_error_message(
        self,
        login_user_use_case,
        mock_user_repository,
        mock_hash_service,
        valid_login_dto,
        existing_user,
    ):
        """Test that InvalidCredentialsError doesn't reveal if email or password is wrong."""
        # Test 1: Email doesn't exist
        mock_user_repository.find_by_email = AsyncMock(return_value=None)

        with pytest.raises(InvalidCredentialsError) as exc_info_email:
            await login_user_use_case.execute(valid_login_dto)

        # Test 2: Password is wrong
        mock_user_repository.find_by_email = AsyncMock(return_value=existing_user)
        mock_hash_service.verify_password = Mock(return_value=False)

        with pytest.raises(InvalidCredentialsError) as exc_info_password:
            await login_user_use_case.execute(valid_login_dto)

        # Assert: Both should raise the same generic error
        assert isinstance(exc_info_email.value, type(exc_info_password.value))
        # Error messages should be generic and the same for both cases
        assert str(exc_info_email.value) == str(exc_info_password.value)
        assert str(exc_info_email.value) == "Invalid email or password"
