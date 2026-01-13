"""PostgreSQL implementation of UserRepository."""

import logging
from uuid import UUID

from sqlalchemy import select, func, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword
from infrastructure.database.models import UserModel

logger = logging.getLogger(__name__)


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
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

        Raises:
            UserAlreadyExistsError: If email or username already exists.
        """
        logger.info(
            f"User save initiated - user_id: {str(user.id)}, "
            f"email: {user.email.value}, username: {user.username}"
        )
        model = self._to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        logger.info(
            f"User save success - user_id: {str(user.id)}, "
            f"email: {user.email.value}, username: {user.username}"
        )
        return self._to_entity(model)

    async def find_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: Email) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        """Update existing user.

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
        stmt = sql_delete(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def exists_by_email(self, email: Email) -> bool:
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = select(UserModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def count(self) -> int:
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar_one()
