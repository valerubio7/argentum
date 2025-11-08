"""End-to-end tests for authentication endpoints."""

from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import HashedPassword
from app.infrastructure.database.models import Base
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.hash_service import BcryptHashService
from app.infrastructure.services.jwt_token_service import JWTTokenService
from app.presentation.api.dependencies.auth import (
    get_hash_service,
    get_session,
    get_token_service,
    get_user_repository,
)
from app.presentation.api.routes.auth import router as auth_router
from app.presentation.config import Settings


@pytest.fixture
async def test_db() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create a test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    yield session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(
    test_db: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session."""
    async with test_db() as session:
        yield session


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test-secret-key-for-testing-only",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=30,
        bcrypt_rounds=4,
        api_prefix="/api/v1",
        debug=True,
    )


@pytest.fixture
def hash_service() -> BcryptHashService:
    """Create a hash service."""
    return BcryptHashService(rounds=4)


@pytest.fixture
def token_service() -> JWTTokenService:
    """Create a token service."""
    return JWTTokenService(
        secret_key="test-secret-key-for-testing-only",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )


@pytest.fixture
async def user_repository(test_session: AsyncSession) -> SQLAlchemyUserRepository:
    """Create a user repository."""
    return SQLAlchemyUserRepository(test_session)


@pytest.fixture
async def app(
    test_session: AsyncSession,
    user_repository: SQLAlchemyUserRepository,
    hash_service: BcryptHashService,
    token_service: JWTTokenService,
) -> FastAPI:
    """Create a FastAPI test app."""
    test_app = FastAPI()

    # Override dependencies
    test_app.dependency_overrides[get_session] = lambda: test_session
    test_app.dependency_overrides[get_user_repository] = lambda: user_repository
    test_app.dependency_overrides[get_hash_service] = lambda: hash_service
    test_app.dependency_overrides[get_token_service] = lambda: token_service

    # Include router
    test_app.include_router(auth_router, prefix="/api/v1")

    return test_app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for testing."""
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def registered_user(
    user_repository: SQLAlchemyUserRepository, hash_service: BcryptHashService
) -> User:
    """Create a registered user for testing."""
    hashed = hash_service.hash_password("SecurePass123!")
    user = User(
        email=Email("existing@example.com"),
        hashed_password=HashedPassword(hashed),
        username="existinguser",
    )
    await user_repository.save(user)
    return user


class TestRegisterEndpoint:
    """Tests for the /register endpoint."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "username": "newuser",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True
        assert data["is_verified"] is False

    async def test_register_duplicate_email(
        self, client: AsyncClient, registered_user: User
    ):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "SecurePass123!",
                "username": "differentuser",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower()

    async def test_register_duplicate_username(
        self, client: AsyncClient, registered_user: User
    ):
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "password": "SecurePass123!",
                "username": "existinguser",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "username" in data["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
                "username": "testuser",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
                "username": "testuser",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_long_password(self, client: AsyncClient):
        """Test registration with too long password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "a" * 129,
                "username": "testuser",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_short_username(self, client: AsyncClient):
        """Test registration with short username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "username": "ab",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_long_username(self, client: AsyncClient):
        """Test registration with too long username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "username": "a" * 51,
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing fields."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestLoginEndpoint:
    """Tests for the /login endpoint."""

    async def test_login_success(self, client: AsyncClient, registered_user: User):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_at" in data

    async def test_login_wrong_password(
        self, client: AsyncClient, registered_user: User
    ):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_login_invalid_email_format(self, client: AsyncClient):
        """Test login with invalid email format."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing fields."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"},
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        user_repository: SQLAlchemyUserRepository,
        hash_service: BcryptHashService,
    ):
        """Test login with inactive user."""
        hashed = hash_service.hash_password("SecurePass123!")
        user = User(
            email=Email("inactive@example.com"),
            hashed_password=HashedPassword(hashed),
            username="inactiveuser",
        )
        user.deactivate()
        await user_repository.save(user)

        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "inactive@example.com",
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestGetMeEndpoint:
    """Tests for the /me endpoint."""

    async def test_get_me_success(self, client: AsyncClient, registered_user: User):
        """Test getting current user information."""
        # First login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "existing@example.com",
                "password": "SecurePass123!",
            },
        )
        token = login_response.json()["access_token"]

        # Then get user info
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "existing@example.com"
        assert data["username"] == "existinguser"
        assert "id" in data
        assert "created_at" in data

    async def test_get_me_no_token(self, client: AsyncClient):
        """Test getting user info without token."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting user info with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_me_expired_token(
        self, client: AsyncClient, registered_user: User
    ):
        """Test getting user info with expired token."""
        # Create a token service with very short expiration
        expired_token_service = JWTTokenService(
            secret_key="test-secret-key-for-testing-only",
            algorithm="HS256",
            access_token_expire_minutes=-1,  # Already expired
        )

        token = expired_token_service.generate_token(
            user_id=str(registered_user.id),
            email=registered_user.email.value,
        )

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_me_deleted_user(
        self,
        client: AsyncClient,
        registered_user: User,
        user_repository: SQLAlchemyUserRepository,
        token_service: JWTTokenService,
    ):
        """Test getting user info when user has been deleted."""
        # Generate token first
        token = token_service.generate_token(
            user_id=str(registered_user.id),
            email=registered_user.email.value,
        )

        # Delete the user
        await user_repository.delete(registered_user.id)

        # Try to get user info
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    async def test_get_me_malformed_authorization_header(self, client: AsyncClient):
        """Test getting user info with malformed authorization header."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "InvalidFormat token"},
        )

        assert response.status_code == 403
        data = response.json()
        assert "detail" in data


class TestEndToEndFlow:
    """End-to-end tests for complete authentication flow."""

    async def test_register_login_get_me_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> get user info."""
        # Step 1: Register a new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "flowtest@example.com",
                "password": "FlowTest123!",
                "username": "flowtest",
            },
        )
        assert register_response.status_code == 201
        registered_user_data = register_response.json()

        # Step 2: Login with the new user
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "flowtest@example.com",
                "password": "FlowTest123!",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 3: Get user info with the token
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        user_data = me_response.json()

        # Verify data consistency
        assert user_data["id"] == registered_user_data["id"]
        assert user_data["email"] == "flowtest@example.com"
        assert user_data["username"] == "flowtest"

    async def test_multiple_users_independent(self, client: AsyncClient):
        """Test that multiple users can register and authenticate independently."""
        # Register first user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user1@example.com",
                "password": "User1Pass123!",
                "username": "user1",
            },
        )

        # Register second user
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "password": "User2Pass123!",
                "username": "user2",
            },
        )

        # Login first user
        login1 = await client.post(
            "/api/v1/auth/login",
            json={"email": "user1@example.com", "password": "User1Pass123!"},
        )
        token1 = login1.json()["access_token"]

        # Login second user
        login2 = await client.post(
            "/api/v1/auth/login",
            json={"email": "user2@example.com", "password": "User2Pass123!"},
        )
        token2 = login2.json()["access_token"]

        # Get info for first user
        me1 = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token1}"}
        )
        assert me1.json()["email"] == "user1@example.com"

        # Get info for second user
        me2 = await client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token2}"}
        )
        assert me2.json()["email"] == "user2@example.com"

        # Verify tokens are different
        assert token1 != token2
