"""PostgreSQL implementation of UserRepository."""

from uuid import UUID

from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword
from infrastructure.database.models import UserModel
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of the UserRepository interface."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        """Map UserModel to User domain entity.

        Args:
            model: SQLAlchemy UserModel instance.

        Returns:
            User domain entity.
        """
        return User(
            id=model.id,
            email=Email(model.email),
            hashed_password=HashedPassword(model.hashed_password),
            username=model.username,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Map User domain entity to UserModel.

        Args:
            entity: User domain entity.

        Returns:
            SQLAlchemy UserModel instance.
        """
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            hashed_password=entity.hashed_password.value,
            username=entity.username,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def save(self, user: User) -> User:
        """Save a user to the database.

        Args:
            user: User entity to save.

        Returns:
            Saved User entity with updated timestamps.

        Raises:
            UserAlreadyExistsError: If email or username already exists.
        """
        logger.info(
            "user_save_initiated",
            user_id=str(user.id),
            email=user.email.value,
            username=user.username,
        )
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        logger.info(
            "user_save_success",
            user_id=str(user.id),
            email=user.email.value,
            username=user.username,
        )
        return self._to_entity(model)

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find user by ID.

        Args:
            user_id: UUID of the user to find.

        Returns:
            User entity if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        """Find user by email.

        Args:
            email: Email value object to search for.

        Returns:
            User entity if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_username(self, username: str) -> User | None:
        """Find user by username.

        Args:
            username: Username to search for.

        Returns:
            User entity if found, None otherwise.
        """
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update existing user.

        Args:
            user: User entity with updated data.

        Returns:
            Updated User entity.

        Raises:
            UserNotFoundError: If user doesn't exist.
        """
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            from domain.exceptions.user_exceptions import UserNotFoundError

            raise UserNotFoundError(f"User with id {user.id} not found")

        model.email = user.email.value
        model.hashed_password = user.hashed_password.value
        model.username = user.username
        model.is_active = user.is_active
        model.is_verified = user.is_verified

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete user by ID.

        Args:
            user_id: UUID of the user to delete.

        Returns:
            True if user was deleted, False if not found.
        """
        stmt = sql_delete(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists_by_email(self, email: Email) -> bool:
        """Check if email exists.

        Args:
            email: Email value object to check.

        Returns:
            True if email exists, False otherwise.
        """
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists.

        Args:
            username: Username to check.

        Returns:
            True if username exists, False otherwise.
        """
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            List of User entities.
        """
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count(self) -> int:
        """Count total users.

        Returns:
            Total number of users in the database.
        """
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar_one()
