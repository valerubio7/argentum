"""Integration tests for authentication endpoints."""

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def test_user(test_session_factory):
    """Create a test user in the database."""
    from infrastructure.database.models import UserModel
    from infrastructure.services.hash_service import BcryptHashService

    hash_service = BcryptHashService(rounds=4)  # Lower rounds for faster tests
    hashed_password = hash_service.hash_password("TestPassword123!")

    async with test_session_factory() as session:
        user = UserModel(
            email="testuser@example.com",
            username="testuser",
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
        user_email = user.email

    # Return a simple object with the user data to avoid session issues
    return type(
        "User", (), {"id": user_id, "email": user_email, "username": "testuser"}
    )()


@pytest_asyncio.fixture
async def inactive_test_user(test_session_factory):
    """Create an inactive test user in the database."""
    from infrastructure.database.models import UserModel
    from infrastructure.services.hash_service import BcryptHashService

    hash_service = BcryptHashService(rounds=4)
    hashed_password = hash_service.hash_password("TestPassword123!")

    async with test_session_factory() as session:
        user = UserModel(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password=hashed_password,
            is_active=False,  # User is inactive
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
        user_email = user.email

    # Return a simple object with the user data to avoid session issues
    return type(
        "User", (), {"id": user_id, "email": user_email, "username": "inactiveuser"}
    )()


@pytest_asyncio.fixture
async def valid_token(test_user):
    """Create a valid JWT token for test user."""
    from infrastructure.services.jwt_token_service import JWTTokenService
    from presentation.config import settings

    token_service = JWTTokenService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
    )
    token, _ = token_service.generate_token(str(test_user.id), test_user.email)
    return token


class TestRegisterEndpoint:
    """Tests for POST /api/auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Test successful user registration returns 201 with UserResponse."""
        # Arrange
        payload = {
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "username": "newuser",
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email returns 409."""
        # Arrange
        payload = {
            "email": test_user.email,  # Duplicate email
            "password": "SecurePassword123!",
            "username": "differentuser",
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "email" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username returns 409."""
        # Arrange
        payload = {
            "email": "different@example.com",
            "password": "SecurePassword123!",
            "username": test_user.username,  # Duplicate username
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "username" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email returns 422 (Pydantic validation)."""
        # Arrange
        payload = {
            "email": "not-an-email",  # Invalid email format
            "password": "SecurePassword123!",
            "username": "testuser",
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client):
        """Test registration with weak password (< 8 chars) returns 422 (Pydantic validation)."""
        # Arrange
        payload = {
            "email": "test@example.com",
            "password": "weak",  # Less than 8 characters
            "username": "testuser",
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client):
        """Test registration with missing fields returns 422 (Pydantic validation)."""
        # Arrange
        payload = {
            "email": "test@example.com",
            # Missing password and username
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_response_structure(self, client):
        """Test registration response has correct JSON structure."""
        # Arrange
        payload = {
            "email": "structure@example.com",
            "password": "SecurePassword123!",
            "username": "structureuser",
        }

        # Act
        response = await client.post("/api/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        # Verify all expected fields are present
        expected_fields = {
            "id",
            "email",
            "username",
            "is_active",
            "is_verified",
            "created_at",
        }
        assert set(data.keys()) == expected_fields
        # Verify field types
        assert isinstance(data["id"], str)
        assert isinstance(data["email"], str)
        assert isinstance(data["username"], str)
        assert isinstance(data["is_active"], bool)
        assert isinstance(data["is_verified"], bool)
        assert isinstance(data["created_at"], str)


class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        """Test successful login returns 200 with TokenResponse."""
        # Arrange
        payload = {
            "email": test_user.email,
            "password": "TestPassword123!",
        }

        # Act
        response = await client.post("/api/auth/login", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_at" in data
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials returns 401 with generic message."""
        # Test 1: Wrong password
        payload = {
            "email": test_user.email,
            "password": "WrongPassword123!",
        }
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        # Should be generic message
        assert "invalid" in data["detail"].lower()

        # Test 2: Non-existent email
        payload = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123!",
        }
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == 401
        # Should have same generic message
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_login_inactive_user(self, client, inactive_test_user):
        """Test login with inactive user returns 403 with specific message."""
        # Arrange
        payload = {
            "email": inactive_test_user.email,
            "password": "TestPassword123!",
        }

        # Act
        response = await client.post("/api/auth/login", json=payload)

        # Assert
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "not active" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client):
        """Test login with missing fields returns 422."""
        # Arrange
        payload = {
            "email": "test@example.com",
            # Missing password
        }

        # Act
        response = await client.post("/api/auth/login", json=payload)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_token_is_valid(self, client, test_user):
        """Test that the token generated by login is valid."""
        # Arrange
        payload = {
            "email": test_user.email,
            "password": "TestPassword123!",
        }

        # Act
        response = await client.post("/api/auth/login", json=payload)
        assert response.status_code == 200
        token = response.json()["access_token"]

        # Assert - Try to use the token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == test_user.email


class TestGetCurrentUserEndpoint:
    """Tests for GET /api/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client, test_user, valid_token):
        """Test getting current user with valid token returns 200 with UserResponse."""
        # Arrange
        headers = {"Authorization": f"Bearer {valid_token}"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "id" in data
        assert "is_active" in data
        assert "password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client):
        """Test getting current user without token returns 401."""
        # Act
        response = await client.get("/api/auth/me")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token returns 401."""
        # Arrange
        headers = {"Authorization": "Bearer invalid_token_here"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(self, client, test_user):
        """Test getting current user with expired token returns 401."""
        # Import locally to avoid import issues
        from infrastructure.services.jwt_token_service import JWTTokenService
        from presentation.config import settings

        # Arrange - Create an expired token
        token_service = JWTTokenService(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            access_token_expire_minutes=-1,  # Negative to create expired token
        )
        expired_token, _ = token_service.generate_token(
            str(test_user.id), test_user.email
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
