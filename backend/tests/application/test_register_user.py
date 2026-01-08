"""Tests for RegisterUser use case."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from application.dtos.auth_dtos import RegisterUserDTO, UserResponseDTO
from application.use_cases.register_user import RegisterUser
from domain.entities.user import User
from domain.exceptions.user_exceptions import UserAlreadyExistsError
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword


class TestRegisterUser:
    """Tests for the RegisterUser use case."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock UserRepository."""
        repository = AsyncMock()
        repository.exists_by_email = AsyncMock(return_value=False)
        repository.exists_by_username = AsyncMock(return_value=False)
        return repository

    @pytest.fixture
    def mock_hash_service(self):
        """Create a mock HashService."""
        service = Mock()
        service.hash_password = Mock(return_value="$2b$12$hashed_password_value_here")
        return service

    @pytest.fixture
    def register_user_use_case(self, mock_user_repository, mock_hash_service):
        """Create a RegisterUser use case with mocked dependencies."""
        return RegisterUser(
            user_repository=mock_user_repository,
            hash_service=mock_hash_service,
        )

    @pytest.fixture
    def valid_register_dto(self):
        """Create a valid RegisterUserDTO."""
        return RegisterUserDTO(
            email="test@example.com",
            password="SecurePassword123!",
            username="testuser",
        )

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        register_user_use_case,
        mock_user_repository,
        mock_hash_service,
        valid_register_dto,
    ):
        """Test successful user registration (happy path)."""
        # Arrange
        user_id = uuid4()
        created_at = datetime.now(timezone.utc)

        saved_user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=True,
            is_verified=False,
        )
        saved_user._id = user_id
        saved_user._created_at = created_at

        mock_user_repository.save = AsyncMock(return_value=saved_user)

        # Act
        result = await register_user_use_case.execute(valid_register_dto)

        # Assert
        assert isinstance(result, UserResponseDTO)
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.is_active is True
        assert result.is_verified is False
        mock_user_repository.exists_by_email.assert_called_once()
        mock_user_repository.exists_by_username.assert_called_once()
        mock_hash_service.hash_password.assert_called_once_with("SecurePassword123!")
        mock_user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(
        self,
        register_user_use_case,
        mock_user_repository,
        valid_register_dto,
    ):
        """Test that registering with an existing email raises UserAlreadyExistsError."""
        # Arrange
        mock_user_repository.exists_by_email = AsyncMock(return_value=True)

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await register_user_use_case.execute(valid_register_dto)

        assert "email" in str(exc_info.value)
        mock_user_repository.exists_by_email.assert_called_once()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_username_already_exists(
        self,
        register_user_use_case,
        mock_user_repository,
        valid_register_dto,
    ):
        """Test that registering with an existing username raises UserAlreadyExistsError."""
        # Arrange
        mock_user_repository.exists_by_username = AsyncMock(return_value=True)

        # Act & Assert
        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await register_user_use_case.execute(valid_register_dto)

        assert "username" in str(exc_info.value)
        mock_user_repository.exists_by_username.assert_called_once()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        register_user_use_case,
        mock_user_repository,
    ):
        """Test that registering with an invalid email raises ValueError."""
        # Arrange
        invalid_dto = RegisterUserDTO(
            email="not-an-email",
            password="SecurePassword123!",
            username="testuser",
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await register_user_use_case.execute(invalid_dto)

        assert "email" in str(exc_info.value).lower()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_weak_password(
        self,
        register_user_use_case,
        mock_user_repository,
    ):
        """Test that registering with a weak password (< 8 chars) raises ValueError."""
        # Arrange
        weak_password_dto = RegisterUserDTO(
            email="test@example.com",
            password="weak",  # Less than 8 characters
            username="testuser",
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await register_user_use_case.execute(weak_password_dto)

        assert "password" in str(exc_info.value).lower()
        mock_user_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_user_password_is_hashed(
        self,
        register_user_use_case,
        mock_user_repository,
        mock_hash_service,
        valid_register_dto,
    ):
        """Test that the password is hashed before saving."""
        # Arrange
        user_id = uuid4()
        created_at = datetime.now(timezone.utc)

        saved_user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=True,
            is_verified=False,
        )
        saved_user._id = user_id
        saved_user._created_at = created_at

        mock_user_repository.save = AsyncMock(return_value=saved_user)

        # Act
        await register_user_use_case.execute(valid_register_dto)

        # Assert
        mock_hash_service.hash_password.assert_called_once_with("SecurePassword123!")

        # Verify save was called with a user that has hashed password
        save_call_args = mock_user_repository.save.call_args
        saved_user_arg = save_call_args[0][0]
        assert isinstance(saved_user_arg, User)
        assert (
            saved_user_arg.hashed_password.value == "$2b$12$hashed_password_value_here"
        )

    @pytest.mark.asyncio
    async def test_register_user_returns_correct_dto(
        self,
        register_user_use_case,
        mock_user_repository,
        valid_register_dto,
    ):
        """Test that the use case returns a UserResponseDTO with correct data."""
        # Arrange
        user_id = uuid4()
        created_at = datetime.now(timezone.utc)

        saved_user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=True,
            is_verified=False,
        )
        saved_user._id = user_id
        saved_user._created_at = created_at

        mock_user_repository.save = AsyncMock(return_value=saved_user)

        # Act
        result = await register_user_use_case.execute(valid_register_dto)

        # Assert
        assert isinstance(result, UserResponseDTO)
        assert result.id == str(user_id)
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.is_active is True
        assert result.is_verified is False
        assert result.created_at == created_at

    @pytest.mark.asyncio
    async def test_register_user_sets_verified_false(
        self,
        register_user_use_case,
        mock_user_repository,
        valid_register_dto,
    ):
        """Test that a newly registered user has is_verified set to False."""
        # Arrange
        user_id = uuid4()
        created_at = datetime.now(timezone.utc)

        saved_user = User(
            email=Email("test@example.com"),
            hashed_password=HashedPassword("$2b$12$hashed_password_value_here"),
            username="testuser",
            is_active=True,
            is_verified=False,
        )
        saved_user._id = user_id
        saved_user._created_at = created_at

        mock_user_repository.save = AsyncMock(return_value=saved_user)

        # Act
        result = await register_user_use_case.execute(valid_register_dto)

        # Assert
        assert result.is_verified is False

        # Verify the User entity was created with is_verified=False
        save_call_args = mock_user_repository.save.call_args
        saved_user_arg = save_call_args[0][0]
        assert saved_user_arg.is_verified is False
