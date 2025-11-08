"""FastAPI dependencies for dependency injection."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.hash_service import HashService
from app.application.interfaces.token_service import TokenService
from app.application.use_cases.auth.login_user import LoginUser
from app.application.use_cases.auth.register_user import RegisterUser
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.config import DatabaseConfig
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.hash_service import BcryptHashService
from app.infrastructure.services.jwt_token_service import (
    InvalidTokenError,
    JWTTokenService,
)
from app.presentation.config import settings

# Global instances
_db_config: DatabaseConfig | None = None
_hash_service: HashService | None = None
_token_service: TokenService | None = None

# Security
security = HTTPBearer()


def get_database_config() -> DatabaseConfig:
    """Get database configuration singleton."""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig(
            database_url=settings.database_url, echo=settings.debug
        )
    return _db_config


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    db_config = get_database_config()
    async for session in db_config.get_session():
        yield session


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Get user repository dependency."""
    return SQLAlchemyUserRepository(session)


def get_hash_service() -> HashService:
    """Get hash service dependency."""
    global _hash_service
    if _hash_service is None:
        _hash_service = BcryptHashService(rounds=settings.bcrypt_rounds)
    return _hash_service


def get_token_service() -> TokenService:
    """Get token service dependency."""
    global _token_service
    if _token_service is None:
        _token_service = JWTTokenService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        )
    return _token_service


async def get_register_user_use_case(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    hash_service: Annotated[HashService, Depends(get_hash_service)],
) -> RegisterUser:
    """Get register user use case dependency."""
    return RegisterUser(user_repository=repository, hash_service=hash_service)


async def get_login_user_use_case(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    hash_service: Annotated[HashService, Depends(get_hash_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> LoginUser:
    """Get login user use case dependency."""
    return LoginUser(
        user_repository=repository,
        hash_service=hash_service,
        token_service=token_service,
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        repository: User repository
        token_service: Token service

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Validate and decode token
        payload = token_service.validate_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find user
        from uuid import UUID

        user = await repository.find_by_id(UUID(user_id))

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is not active",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
