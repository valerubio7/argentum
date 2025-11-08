"""Unit tests for RegisterUser use case."""

import pytest
from datetime import datetime

from app.application.dtos.auth_dtos import RegisterUserDTO
from app.application.interfaces.hash_service import HashService
from app.application.use_cases.auth.register_user import RegisterUser
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email


class MockHashService(HashService):
    """Mock implementation of HashService for testing."""

    def hash_password(self, plain_password: str) -> str:
        """Mock hash - simulates a bcrypt-like hash (60 chars)."""
        # Create a hash that's long enough to pass HashedPassword validation
        return f"$2b$12${'x' * 40}{plain_password[:10]}"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Mock verify - checks if hash contains the password."""
        return plain_password[:10] in hashed_password


class MockUserRepository(UserRepository):
    """Mock implementation of UserRepository for testing."""

    def __init__(self):
        self._users: dict[str, User] = {}
        self._emails: set[str] = set()
        self._usernames: set[str] = set()

    async def save(self, user: User) -> User:
        """Save user to mock storage."""
        self._users[str(user.id)] = user
        self._emails.add(user.email.value)
        self._usernames.add(user.username)
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
        return email.value in self._emails

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists."""
        return username in self._usernames

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users."""
        return list(self._users.values())[offset : offset + limit]

    async def count(self) -> int:
        """Count users."""
        return len(self._users)


class TestRegisterUser:
    """Tests for RegisterUser use case."""

    @pytest.fixture
    def hash_service(self):
        """Fixture providing mock hash service."""
        return MockHashService()

    @pytest.fixture
    def user_repository(self):
        """Fixture providing mock user repository."""
        return MockUserRepository()

    @pytest.fixture
    def register_user_use_case(self, user_repository, hash_service):
        """Fixture providing the RegisterUser use case."""
        return RegisterUser(
            user_repository=user_repository,
            hash_service=hash_service,
        )

    @pytest.mark.asyncio
    async def test_register_user_success(self, register_user_use_case):
        """Test successful user registration."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        result = await register_user_use_case.execute(dto)

        assert result.email == "user@example.com"
        assert result.username == "john_doe"
        assert result.is_active is True
        assert result.is_verified is False
        assert result.id is not None
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_register_user_hashes_password(
        self, register_user_use_case, user_repository
    ):
        """Test that password is hashed during registration."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        await register_user_use_case.execute(dto)

        # Verify the user was saved with hashed password
        saved_user = await user_repository.find_by_email(Email("user@example.com"))
        assert saved_user is not None
        assert saved_user.hashed_password.value.startswith("$2b$12$")
        assert "SecurePas" in saved_user.hashed_password.value

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email_raises_error(
        self, register_user_use_case, user_repository
    ):
        """Test that registering with duplicate email raises error."""
        # Create first user
        dto1 = RegisterUserDTO(
            email="user@example.com",
            password="Password123",
            username="user1",
        )
        await register_user_use_case.execute(dto1)

        # Try to register with same email
        dto2 = RegisterUserDTO(
            email="user@example.com",
            password="Password456",
            username="user2",
        )

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await register_user_use_case.execute(dto2)

        assert exc_info.value.field == "email"
        assert exc_info.value.value == "user@example.com"

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username_raises_error(
        self, register_user_use_case, user_repository
    ):
        """Test that registering with duplicate username raises error."""
        # Create first user
        dto1 = RegisterUserDTO(
            email="user1@example.com",
            password="Password123",
            username="john_doe",
        )
        await register_user_use_case.execute(dto1)

        # Try to register with same username
        dto2 = RegisterUserDTO(
            email="user2@example.com",
            password="Password456",
            username="john_doe",
        )

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await register_user_use_case.execute(dto2)

        assert exc_info.value.field == "username"
        assert exc_info.value.value == "john_doe"

    @pytest.mark.asyncio
    async def test_register_user_invalid_email_raises_error(
        self, register_user_use_case
    ):
        """Test that invalid email format raises ValueError."""
        dto = RegisterUserDTO(
            email="invalid-email",
            password="SecurePassword123",
            username="john_doe",
        )

        with pytest.raises(ValueError, match="Invalid email format"):
            await register_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_invalid_password_raises_error(
        self, register_user_use_case
    ):
        """Test that invalid password raises ValueError."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="short",  # Too short
            username="john_doe",
        )

        with pytest.raises(ValueError, match="at least"):
            await register_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_invalid_username_raises_error(
        self, register_user_use_case
    ):
        """Test that invalid username raises ValueError."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="ab",  # Too short
        )

        with pytest.raises(ValueError, match="at least 3 characters"):
            await register_user_use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_saves_to_repository(
        self, register_user_use_case, user_repository
    ):
        """Test that user is persisted to repository."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        await register_user_use_case.execute(dto)

        # Verify user exists in repository
        assert await user_repository.exists_by_email(Email("user@example.com"))
        assert await user_repository.exists_by_username("john_doe")

    @pytest.mark.asyncio
    async def test_register_user_returns_correct_dto(self, register_user_use_case):
        """Test that the returned DTO has correct structure."""
        dto = RegisterUserDTO(
            email="user@example.com",
            password="SecurePassword123",
            username="john_doe",
        )

        result = await register_user_use_case.execute(dto)

        # Verify DTO structure
        assert hasattr(result, "id")
        assert hasattr(result, "email")
        assert hasattr(result, "username")
        assert hasattr(result, "is_active")
        assert hasattr(result, "is_verified")
        assert hasattr(result, "created_at")
        assert isinstance(result.created_at, datetime)
