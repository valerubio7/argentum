"""Tests for PostgresUserRepository."""

import pytest
import pytest_asyncio
from uuid import uuid4

from domain.entities.user import User
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword
from infrastructure.repositories.postgres_user_repository import PostgresUserRepository


@pytest_asyncio.fixture
async def repository(async_session) -> PostgresUserRepository:
    """Create repository instance with test session."""
    return PostgresUserRepository(async_session)


def create_user(
    email: str | None = None,
    username: str | None = None,
    hashed_password: str = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.M7",
) -> User:
    """Helper to create a User entity with unique values."""
    unique_id = uuid4().hex[:8]
    return User(
        email=Email(email or f"user_{unique_id}@example.com"),
        hashed_password=HashedPassword(hashed_password),
        username=username or f"user_{unique_id}",
    )


class TestSaveUser:
    """Tests for saving users."""

    @pytest.mark.asyncio
    async def test_save_new_user(self, repository):
        """Test saving a new user."""
        user = create_user()

        saved_user = await repository.save(user)

        assert saved_user.id == user.id
        assert saved_user.email.value == user.email.value
        assert saved_user.username == user.username
        assert saved_user.is_active is True
        assert saved_user.is_verified is False

    @pytest.mark.asyncio
    async def test_save_user_with_custom_flags(self, repository):
        """Test saving a user with custom is_active and is_verified flags."""
        user = User(
            email=Email(f"custom_{uuid4().hex[:8]}@example.com"),
            hashed_password=HashedPassword(
                "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.M7"
            ),
            username=f"custom_{uuid4().hex[:8]}",
            is_active=False,
            is_verified=True,
        )

        saved_user = await repository.save(user)

        assert saved_user.is_active is False
        assert saved_user.is_verified is True


class TestFindByEmail:
    """Tests for finding users by email."""

    @pytest.mark.asyncio
    async def test_find_by_email_existing_user(self, repository):
        """Test finding an existing user by email."""
        user = create_user()
        await repository.save(user)

        found_user = await repository.find_by_email(user.email)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email.value == user.email.value

    @pytest.mark.asyncio
    async def test_find_by_email_nonexistent_user(self, repository):
        """Test finding a nonexistent user by email returns None."""
        email = Email("nonexistent@example.com")

        found_user = await repository.find_by_email(email)

        assert found_user is None


class TestFindById:
    """Tests for finding users by ID."""

    @pytest.mark.asyncio
    async def test_find_by_id_existing_user(self, repository):
        """Test finding an existing user by ID."""
        user = create_user()
        await repository.save(user)

        found_user = await repository.find_by_id(user.id)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == user.username

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent_user(self, repository):
        """Test finding a nonexistent user by ID returns None."""
        random_id = uuid4()

        found_user = await repository.find_by_id(random_id)

        assert found_user is None


class TestFindByUsername:
    """Tests for finding users by username."""

    @pytest.mark.asyncio
    async def test_find_by_username_existing_user(self, repository):
        """Test finding an existing user by username."""
        user = create_user()
        await repository.save(user)

        found_user = await repository.find_by_username(user.username)

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == user.username

    @pytest.mark.asyncio
    async def test_find_by_username_nonexistent_user(self, repository):
        """Test finding a nonexistent user by username returns None."""
        found_user = await repository.find_by_username("nonexistent_user")

        assert found_user is None


class TestDeleteUser:
    """Tests for deleting users."""

    @pytest.mark.asyncio
    async def test_delete_existing_user(self, repository):
        """Test deleting an existing user."""
        user = create_user()
        await repository.save(user)

        result = await repository.delete(user.id)

        assert result is True
        assert await repository.find_by_id(user.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, repository):
        """Test deleting a nonexistent user returns False."""
        random_id = uuid4()

        result = await repository.delete(random_id)

        assert result is False


class TestExistsMethods:
    """Tests for exists methods."""

    @pytest.mark.asyncio
    async def test_exists_by_email_true(self, repository):
        """Test exists_by_email returns True for existing email."""
        user = create_user()
        await repository.save(user)

        exists = await repository.exists_by_email(user.email)

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_email_false(self, repository):
        """Test exists_by_email returns False for nonexistent email."""
        email = Email("nonexistent@example.com")

        exists = await repository.exists_by_email(email)

        assert exists is False

    @pytest.mark.asyncio
    async def test_exists_by_username_true(self, repository):
        """Test exists_by_username returns True for existing username."""
        user = create_user()
        await repository.save(user)

        exists = await repository.exists_by_username(user.username)

        assert exists is True

    @pytest.mark.asyncio
    async def test_exists_by_username_false(self, repository):
        """Test exists_by_username returns False for nonexistent username."""
        exists = await repository.exists_by_username("nonexistent_user")

        assert exists is False


class TestUpdateUser:
    """Tests for updating users."""

    @pytest.mark.asyncio
    async def test_update_user(self, repository):
        """Test updating an existing user."""
        user = create_user()
        await repository.save(user)

        # Update user properties
        user.update_username("updated_username")
        user.verify_email()

        updated_user = await repository.update(user)

        assert updated_user.username == "updated_username"
        assert updated_user.is_verified is True


class TestListAndCount:
    """Tests for listing and counting users."""

    @pytest.mark.asyncio
    async def test_list_all_users(self, repository):
        """Test listing all users with pagination."""
        # Create multiple users
        users = [create_user() for _ in range(3)]
        for user in users:
            await repository.save(user)

        result = await repository.list_all(limit=10, offset=0)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_count_users(self, repository):
        """Test counting total users."""
        # Create multiple users
        users = [create_user() for _ in range(3)]
        for user in users:
            await repository.save(user)

        count = await repository.count()

        assert count == 3
