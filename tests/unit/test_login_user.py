"""Unit tests for LoginUser use case."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID

from app.application.dtos.auth_dtos import LoginDTO
from app.application.interfaces.hash_service import HashService
from app.application.interfaces.token_service import TokenService
from app.application.use_cases.auth.login_user import LoginUser
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword


class MockHashService(HashService):
    """Mock implementation of HashService for testing."""

    def hash_password(self, plain_password: str) -> str:
        """Mock hash - simulates a bcrypt-like hash (60 chars)."""
        # Create a hash that's long enough to pass HashedPassword validation
        return f"$2b$12${'x' * 40}{plain_password[:10]}"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Mock verify - checks if hash contains the password."""
        return plain_password[:10] in hashed_password


class MockTokenService(TokenService):
    """Mock implementation of TokenService for testing."""

    def generate_token(self, user_id: UUID, email: str) -> tuple[str, datetime]:
        """Mock token generation."""
        expires_at = datetime.now() + timedelta(hours=24)
        token = f"mock_token_{user_id}_{email}"
        return token, expires_at

    def validate_token(self, token: str) -> dict[str, str]:
        """Mock token validation."""
        return {"user_id": "some-uuid", "email": "user@example.com"}

    def get_token_expiration(self, token: str) -> datetime:
        """Mock get expiration."""
        return datetime.now() + timedelta(hours=24)


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing."""

    def __init__(self):
        self._users: dict[str, User] = {}

    async def save(self, user: User) -> User:
        """Save user to mock storage."""
        self._users[str(user.id)] = user
        return user

    async def find_by_id(self, user_id) -> User | None:
        """Find user by ID."""
        return self._users.get(str(user_id))

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def update(self, user: User) -> User:
        """Update user."""
        self._users[str(user.id)] = user
        return user

    async def delete(self, user_id) -> bool:
        """Delete user."""
        user_id_str = str(user_id)
        if user_id_str in self._users:
            del self._users[user_id_str]
            return True
        return False

    async def exists_by_email(self, email: Email) -> bool:
        """Check if email exists."""
        return await self.find_by_email(email) is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists."""
        return await self.find_by_username(username) is not None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users."""
        return list(self._users.values())[offset : offset + limit]

    async def count(self) -> int:
        """Count users."""
        return len(self._users)


class TestLoginUser:
    """Tests for LoginUser use case."""

    @pytest.fixture
    def hash_service(self):
        """Fixture providing mock hash service."""
        return MockHashService()

    @pytest.fixture
    def token_service(self):
        """Fixture providing mock token service."""
        return MockTokenService()

    @pytest.fixture
    def user_repository(self):
        """Fixture providing mock user repository."""
        return MockUserRepository()

    @pytest.fixture
    async def existing_user(self, user_repository, hash_service):
        """Fixture providing an existing user in the repository."""
        user = User(
            email=Email("user@example.com"),
            hashed_password=HashedPassword(hash_service.hash_password("Password123")),
            username="john_doe",
            is_active=True,
            is_verified=True,
        )
        await user_repository.save(user)
        return user

    @pytest.fixture
    def login_user_use_case(self, user_repository, hash_service, token_service):
        """Fixture providing the LoginUser use case."""
        return LoginUser(
            user_repository=user_repository,
            hash_service=hash_service,
            token_service=token_service,
        )

    @pytest.mark.asyncio
    async def test_login_user_success(self, login_user_use_case, existing_user):
        """Test successful user login."""
        dto = LoginDTO(
            email="user@example.com",
            password="Password123",
        )

        result = await login_user_use_case.execute(dto)

        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.expires_at is not None
        assert "mock_token_" in result.access_token

    @pytest.mark.asyncio
    async def test_login_user_generates_token_with_correct_data(
        self, login_user_use_case, existing_user, token_service
    ):
        """Test that token is generated with correct user data."""
        dto = LoginDTO(
            email="user@example.com",
            password="Password123",
        )

        result = await login_user_use_case.execute(dto)

        # Token should contain user id and email
        assert str(existing_user.id) in result.access_token
        assert "user@example.com" in result.access_token

    @pytest.mark.asyncio
    async def test_login_user_invalid_email_raises_error(self, login_user_use_case):
        """Test that login with non-existent email raises InvalidCredentialsError."""
        dto = LoginDTO(
            email="nonexistent@example.com",
            password="Password123",
        )

        with pytest.raises(InvalidCredentialsError):
            await login_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_user_invalid_password_raises_error(
        self, login_user_use_case, existing_user
    ):
        """Test that login with wrong password raises InvalidCredentialsError."""
        dto = LoginDTO(
            email="user@example.com",
            password="WrongPassword",
        )

        with pytest.raises(InvalidCredentialsError):
            await login_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises_error(
        self, login_user_use_case, user_repository, hash_service
    ):
        """Test that login with inactive user raises UserNotActiveError."""
        # Create inactive user
        inactive_user = User(
            email=Email("inactive@example.com"),
            hashed_password=HashedPassword(hash_service.hash_password("Password123")),
            username="inactive_user",
            is_active=False,  # Inactive
            is_verified=True,
        )
        await user_repository.save(inactive_user)

        dto = LoginDTO(
            email="inactive@example.com",
            password="Password123",
        )

        with pytest.raises(UserNotActiveError) as exc_info:
            await login_user_use_case.execute(dto)

        assert exc_info.value.email == "inactive@example.com"

    @pytest.mark.asyncio
    async def test_login_user_verifies_password(
        self, login_user_use_case, existing_user, hash_service
    ):
        """Test that password verification is performed."""
        dto = LoginDTO(
            email="user@example.com",
            password="Password123",
        )

        result = await login_user_use_case.execute(dto)

        # Should succeed because hash_service.verify_password works correctly
        assert result is not None

    @pytest.mark.asyncio
    async def test_login_user_returns_correct_token_dto(
        self, login_user_use_case, existing_user
    ):
        """Test that the returned TokenDTO has correct structure."""
        dto = LoginDTO(
            email="user@example.com",
            password="Password123",
        )

        result = await login_user_use_case.execute(dto)

        # Verify DTO structure
        assert hasattr(result, "access_token")
        assert hasattr(result, "token_type")
        assert hasattr(result, "expires_at")
        assert isinstance(result.access_token, str)
        assert isinstance(result.token_type, str)
        assert isinstance(result.expires_at, datetime)

    @pytest.mark.asyncio
    async def test_login_user_invalid_email_format_raises_error(
        self, login_user_use_case
    ):
        """Test that invalid email format raises ValueError."""
        dto = LoginDTO(
            email="invalid-email",
            password="Password123",
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            await login_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_user_case_insensitive_email(
        self, login_user_use_case, existing_user
    ):
        """Test that email matching is case-insensitive."""
        dto = LoginDTO(
            email="USER@EXAMPLE.COM",  # Uppercase
            password="Password123",
        )

        result = await login_user_use_case.execute(dto)

        # Should succeed because Email value object normalizes to lowercase
        assert result is not None
        assert result.access_token is not None
