"""Unit tests for UserRepository interface using a mock implementation."""

import pytest
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for testing.

    This is a simple implementation that stores users in a dictionary
    to test the repository interface contract.
    """

    def __init__(self):
        self._users: dict[str, User] = {}  # Using user_id as key

    async def save(self, user: User) -> User:
        """Save a user entity."""
        # Check for duplicates
        if await self.exists_by_email(user.email):
            raise UserAlreadyExistsError("email", str(user.email))

        if await self.exists_by_username(user.username):
            raise UserAlreadyExistsError("username", user.username)

        self._users[str(user.id)] = user
        return user

    async def find_by_id(self, user_id) -> User | None:
        """Find a user by their ID."""
        return self._users.get(str(user_id))

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by their email address."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_by_username(self, username: str) -> User | None:
        """Find a user by their username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        if str(user.id) not in self._users:
            raise UserNotFoundError(user.id)

        self._users[str(user.id)] = user
        return user

    async def delete(self, user_id) -> bool:
        """Delete a user by their ID."""
        user_id_str = str(user_id)
        if user_id_str in self._users:
            del self._users[user_id_str]
            return True
        return False

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        return await self.find_by_email(email) is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if a user with the given username exists."""
        return await self.find_by_username(username) is not None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users with pagination."""
        users = list(self._users.values())
        return users[offset : offset + limit]

    async def count(self) -> int:
        """Count total number of users."""
        return len(self._users)


class TestUserRepository:
    """Tests for UserRepository interface using in-memory implementation."""

    @pytest.fixture
    def repository(self):
        """Fixture providing a fresh repository instance."""
        return InMemoryUserRepository()

    @pytest.fixture
    def sample_user(self):
        """Fixture providing a sample user."""
        return User(
            email=Email("user@example.com"),
            hashed_password=HashedPassword(
                "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
            ),
            username="john_doe",
        )

    @pytest.mark.asyncio
    async def test_save_user(self, repository, sample_user):
        """Test saving a user to the repository."""
        saved_user = await repository.save(sample_user)

        assert saved_user.id == sample_user.id
        assert saved_user.email == sample_user.email
        assert saved_user.username == sample_user.username

    @pytest.mark.asyncio
    async def test_save_duplicate_email_raises_error(self, repository, sample_user):
        """Test saving a user with duplicate email raises error."""
        await repository.save(sample_user)

        # Try to save another user with same email
        duplicate_user = User(
            email=Email("user@example.com"),  # Same email
            hashed_password=HashedPassword(
                "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
            ),
            username="different_username",
        )

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await repository.save(duplicate_user)

        assert exc_info.value.field == "email"
        assert exc_info.value.value == "user@example.com"

    @pytest.mark.asyncio
    async def test_save_duplicate_username_raises_error(self, repository, sample_user):
        """Test saving a user with duplicate username raises error."""
        await repository.save(sample_user)

        # Try to save another user with same username
        duplicate_user = User(
            email=Email("different@example.com"),
            hashed_password=HashedPassword(
                "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
            ),
            username="john_doe",  # Same username
        )

        with pytest.raises(UserAlreadyExistsError) as exc_info:
            await repository.save(duplicate_user)

        assert exc_info.value.field == "username"
        assert exc_info.value.value == "john_doe"

    @pytest.mark.asyncio
    async def test_find_by_id(self, repository, sample_user):
        """Test finding a user by ID."""
        await repository.save(sample_user)

        found_user = await repository.find_by_id(sample_user.id)

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Test finding a non-existent user by ID returns None."""
        non_existent_id = uuid4()
        found_user = await repository.find_by_id(non_existent_id)

        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_email(self, repository, sample_user):
        """Test finding a user by email."""
        await repository.save(sample_user)

        found_user = await repository.find_by_email(Email("user@example.com"))

        assert found_user is not None
        assert found_user.email.value == "user@example.com"

    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, repository):
        """Test finding a non-existent user by email returns None."""
        found_user = await repository.find_by_email(Email("nonexistent@example.com"))

        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_username(self, repository, sample_user):
        """Test finding a user by username."""
        await repository.save(sample_user)

        found_user = await repository.find_by_username("john_doe")

        assert found_user is not None
        assert found_user.username == "john_doe"

    @pytest.mark.asyncio
    async def test_find_by_username_not_found(self, repository):
        """Test finding a non-existent user by username returns None."""
        found_user = await repository.find_by_username("nonexistent")

        assert found_user is None

    @pytest.mark.asyncio
    async def test_update_user(self, repository, sample_user):
        """Test updating an existing user."""
        await repository.save(sample_user)

        # Update username
        sample_user.update_username("new_username")
        updated_user = await repository.update(sample_user)

        assert updated_user.username == "new_username"

        # Verify the update persisted
        found_user = await repository.find_by_id(sample_user.id)
        assert found_user.username == "new_username"

    @pytest.mark.asyncio
    async def test_update_nonexistent_user_raises_error(self, repository):
        """Test updating a non-existent user raises error."""
        user = User(
            email=Email("user@example.com"),
            hashed_password=HashedPassword(
                "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
            ),
            username="john_doe",
        )

        with pytest.raises(UserNotFoundError):
            await repository.update(user)

    @pytest.mark.asyncio
    async def test_delete_user(self, repository, sample_user):
        """Test deleting a user."""
        await repository.save(sample_user)

        result = await repository.delete(sample_user.id)

        assert result is True
        assert await repository.find_by_id(sample_user.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, repository):
        """Test deleting a non-existent user returns False."""
        non_existent_id = uuid4()
        result = await repository.delete(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_by_email(self, repository, sample_user):
        """Test checking if user exists by email."""
        assert await repository.exists_by_email(Email("user@example.com")) is False

        await repository.save(sample_user)

        assert await repository.exists_by_email(Email("user@example.com")) is True

    @pytest.mark.asyncio
    async def test_exists_by_username(self, repository, sample_user):
        """Test checking if user exists by username."""
        assert await repository.exists_by_username("john_doe") is False

        await repository.save(sample_user)

        assert await repository.exists_by_username("john_doe") is True

    @pytest.mark.asyncio
    async def test_list_all_users(self, repository):
        """Test listing all users."""
        # Create multiple users
        for i in range(5):
            user = User(
                email=Email(f"user{i}@example.com"),
                hashed_password=HashedPassword(
                    "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
                ),
                username=f"user_{i}",
            )
            await repository.save(user)

        users = await repository.list_all()

        assert len(users) == 5

    @pytest.mark.asyncio
    async def test_list_all_with_pagination(self, repository):
        """Test listing users with pagination."""
        # Create multiple users
        for i in range(10):
            user = User(
                email=Email(f"user{i}@example.com"),
                hashed_password=HashedPassword(
                    "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
                ),
                username=f"user_{i}",
            )
            await repository.save(user)

        # Get first page
        page1 = await repository.list_all(limit=5, offset=0)
        assert len(page1) == 5

        # Get second page
        page2 = await repository.list_all(limit=5, offset=5)
        assert len(page2) == 5

        # Ensure pages don't overlap
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    @pytest.mark.asyncio
    async def test_count_users(self, repository):
        """Test counting total users."""
        assert await repository.count() == 0

        # Add some users
        for i in range(3):
            user = User(
                email=Email(f"user{i}@example.com"),
                hashed_password=HashedPassword(
                    "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
                ),
                username=f"user_{i}",
            )
            await repository.save(user)

        assert await repository.count() == 3

    @pytest.mark.asyncio
    async def test_repository_interface_contract(self, repository):
        """Test that the repository implements all required methods."""
        assert isinstance(repository, UserRepository)
        assert hasattr(repository, "save")
        assert hasattr(repository, "find_by_id")
        assert hasattr(repository, "find_by_email")
        assert hasattr(repository, "find_by_username")
        assert hasattr(repository, "update")
        assert hasattr(repository, "delete")
        assert hasattr(repository, "exists_by_email")
        assert hasattr(repository, "exists_by_username")
        assert hasattr(repository, "list_all")
        assert hasattr(repository, "count")
