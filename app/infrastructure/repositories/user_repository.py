"""SQLAlchemy implementation of UserRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword
from app.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository.

    This repository implements the domain repository interface using
    SQLAlchemy and PostgreSQL.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity.

        Args:
            model: SQLAlchemy UserModel

        Returns:
            User domain entity
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
        """Convert User entity to UserModel.

        Args:
            entity: User domain entity

        Returns:
            SQLAlchemy UserModel
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
        """Save a user entity."""
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by their ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by their email address."""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_username(self, username: str) -> User | None:
        """Find a user by their username."""
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            from app.domain.exceptions.user_exceptions import UserNotFoundError

            raise UserNotFoundError(user.id)

        # Update model fields
        model.email = user.email.value
        model.hashed_password = user.hashed_password.value
        model.username = user.username
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        model.updated_at = user.updated_at

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by their ID."""
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return False

        await self._session.delete(model)
        await self._session.flush()
        return True

    async def exists_by_email(self, email: Email) -> bool:
        """Check if a user with the given email exists."""
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        """Check if a user with the given username exists."""
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """List all users with pagination."""
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count(self) -> int:
        """Count total number of users."""
        stmt = select(UserModel)
        result = await self._session.execute(stmt)
        return len(result.scalars().all())
