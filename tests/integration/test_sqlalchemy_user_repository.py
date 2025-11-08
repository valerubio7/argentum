"""Integration tests for SQLAlchemyUserRepository."""

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import UserNotFoundError
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword
from app.infrastructure.database.models import Base, UserModel
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


@pytest.fixture
async def engine():
    """Create an async SQLite in-memory engine for testing."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, future=True
    )

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def session(engine):
    """Create a new database session for a test."""
    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as test_session:
        yield test_session
        await test_session.rollback()


@pytest.fixture
def repository(session):
    """Create a repository instance."""
    return SQLAlchemyUserRepository(session)


@pytest.fixture
def sample_user():
    """Create a sample user entity."""
    return User(
        email=Email("user@example.com"),
        hashed_password=HashedPassword(
            "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
        ),
        username="john_doe",
    )


class TestSQLAlchemyUserRepository:
    """Integration tests for SQLAlchemy user repository."""

    @pytest.mark.asyncio
    async def test_save_user(self, repository, session, sample_user):
        """Test saving a user to the database."""
        saved_user = await repository.save(sample_user)

        assert saved_user.id == sample_user.id
        assert saved_user.email == sample_user.email
        assert saved_user.username == sample_user.username

        await session.commit()

        # Verify user exists in database
        result = await session.get(UserModel, sample_user.id)
        assert result is not None
        assert result.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_find_by_id(self, repository, session, sample_user):
        """Test finding a user by ID."""
        await repository.save(sample_user)
        await session.commit()

        found_user = await repository.find_by_id(sample_user.id)

        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Test finding a non-existent user returns None."""
        non_existent_id = uuid4()
        found_user = await repository.find_by_id(non_existent_id)

        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_email(self, repository, session, sample_user):
        """Test finding a user by email."""
        await repository.save(sample_user)
        await session.commit()

        found_user = await repository.find_by_email(Email("user@example.com"))

        assert found_user is not None
        assert found_user.email.value == "user@example.com"
        assert found_user.username == "john_doe"

    @pytest.mark.asyncio
    async def test_find_by_email_not_found(self, repository):
        """Test finding a non-existent email returns None."""
        found_user = await repository.find_by_email(Email("nonexistent@example.com"))

        assert found_user is None

    @pytest.mark.asyncio
    async def test_find_by_username(self, repository, session, sample_user):
        """Test finding a user by username."""
        await repository.save(sample_user)
        await session.commit()

        found_user = await repository.find_by_username("john_doe")

        assert found_user is not None
        assert found_user.username == "john_doe"
        assert found_user.email.value == "user@example.com"

    @pytest.mark.asyncio
    async def test_find_by_username_not_found(self, repository):
        """Test finding a non-existent username returns None."""
        found_user = await repository.find_by_username("nonexistent")

        assert found_user is None

    @pytest.mark.asyncio
    async def test_update_user(self, repository, session, sample_user):
        """Test updating a user."""
        await repository.save(sample_user)
        await session.commit()

        # Update username
        sample_user.update_username("new_username")
        updated_user = await repository.update(sample_user)

        assert updated_user.username == "new_username"

        await session.commit()

        # Verify update persisted
        found_user = await repository.find_by_id(sample_user.id)
        assert found_user is not None
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
    async def test_delete_user(self, repository, session, sample_user):
        """Test deleting a user."""
        await repository.save(sample_user)
        await session.commit()

        result = await repository.delete(sample_user.id)

        assert result is True

        await session.commit()

        # Verify user no longer exists
        found_user = await repository.find_by_id(sample_user.id)
        assert found_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, repository):
        """Test deleting a non-existent user returns False."""
        non_existent_id = uuid4()
        result = await repository.delete(non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_by_email(self, repository, session, sample_user):
        """Test checking if user exists by email."""
        exists_before = await repository.exists_by_email(Email("user@example.com"))
        assert exists_before is False

        await repository.save(sample_user)
        await session.commit()

        exists_after = await repository.exists_by_email(Email("user@example.com"))
        assert exists_after is True

    @pytest.mark.asyncio
    async def test_exists_by_username(self, repository, session, sample_user):
        """Test checking if user exists by username."""
        exists_before = await repository.exists_by_username("john_doe")
        assert exists_before is False

        await repository.save(sample_user)
        await session.commit()

        exists_after = await repository.exists_by_username("john_doe")
        assert exists_after is True

    @pytest.mark.asyncio
    async def test_list_all_users(self, repository, session):
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

        await session.commit()

        users = await repository.list_all()

        assert len(users) == 5
        assert all(isinstance(user, User) for user in users)

    @pytest.mark.asyncio
    async def test_list_all_with_pagination(self, repository, session):
        """Test listing users with pagination."""
        # Create 10 users
        for i in range(10):
            user = User(
                email=Email(f"user{i}@example.com"),
                hashed_password=HashedPassword(
                    "$2b$12$KIXqBwFLpBOjhsqkXjKl3OZpR7gTqZvP8LkKJHF9qB3zB8vF5QYXK"
                ),
                username=f"user_{i}",
            )
            await repository.save(user)

        await session.commit()

        # Get first page
        page1 = await repository.list_all(limit=5, offset=0)
        assert len(page1) == 5

        # Get second page
        page2 = await repository.list_all(limit=5, offset=5)
        assert len(page2) == 5

        # Verify pages don't overlap
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    @pytest.mark.asyncio
    async def test_count_users(self, repository, session):
        """Test counting users."""
        count_before = await repository.count()
        assert count_before == 0

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

        await session.commit()

        count_after = await repository.count()
        assert count_after == 3

    @pytest.mark.asyncio
    async def test_entity_to_model_conversion(self, repository, session, sample_user):
        """Test that entity is correctly converted to model."""
        await repository.save(sample_user)
        await session.commit()

        # Get model directly from database
        model = await session.get(UserModel, sample_user.id)

        assert model is not None
        assert model.id == sample_user.id
        assert model.email == sample_user.email.value
        assert model.hashed_password == sample_user.hashed_password.value
        assert model.username == sample_user.username
        assert model.is_active == sample_user.is_active
        assert model.is_verified == sample_user.is_verified

    @pytest.mark.asyncio
    async def test_model_to_entity_conversion(self, repository, session, sample_user):
        """Test that model is correctly converted to entity."""
        await repository.save(sample_user)
        await session.commit()

        found_user = await repository.find_by_id(sample_user.id)

        assert found_user is not None
        assert isinstance(found_user, User)
        assert isinstance(found_user.email, Email)
        assert isinstance(found_user.hashed_password, HashedPassword)
        assert found_user.id == sample_user.id
        assert found_user.email.value == sample_user.email.value
