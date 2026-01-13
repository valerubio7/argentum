"""Tests for Request ID middleware."""

import uuid

import pytest
from httpx import AsyncClient

from presentation.api.middleware.request_id import get_request_id, request_id_var


class TestRequestIDMiddleware:
    """Tests for RequestIDMiddleware functionality."""

    @pytest.mark.asyncio
    async def test_automatic_request_id_generation(self, client: AsyncClient):
        """Test that Request ID is automatically generated when not provided."""
        response = await client.get("/health")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers

        # Verify it's a valid UUID
        request_id = response.headers["X-Request-ID"]
        assert uuid.UUID(request_id)  # Should not raise ValueError

    @pytest.mark.asyncio
    async def test_custom_request_id_propagation(self, client: AsyncClient):
        """Test that custom Request ID from client is preserved."""
        custom_id = "my-custom-trace-12345"
        headers = {"X-Request-ID": custom_id}

        response = await client.get("/health", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_unique_request_ids_across_requests(self, client: AsyncClient):
        """Test that each request without custom ID gets a unique Request ID."""
        request_ids = []

        for _ in range(5):
            response = await client.get("/health")
            request_id = response.headers["X-Request-ID"]
            request_ids.append(request_id)

        # All IDs should be unique
        assert len(request_ids) == len(set(request_ids))

        # All should be valid UUIDs
        for request_id in request_ids:
            assert uuid.UUID(request_id)

    @pytest.mark.asyncio
    async def test_request_id_with_error_responses(self, client: AsyncClient):
        """Test that Request ID is included even in error responses."""
        custom_id = "error-test-123"
        headers = {"X-Request-ID": custom_id}

        # Test with 404
        response_404 = await client.get("/nonexistent", headers=headers)
        assert response_404.status_code == 404
        assert response_404.headers["X-Request-ID"] == custom_id

        # Test with validation error (422)
        response_422 = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "username": "test",
                "password": "password123",
            },
            headers=headers,
        )
        assert response_422.status_code == 422
        assert response_422.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_concurrent_requests_have_different_ids(self, client: AsyncClient):
        """Test that concurrent requests have different Request IDs."""
        import asyncio

        # Make 10 concurrent requests
        tasks = [client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        request_ids = [r.headers["X-Request-ID"] for r in responses]

        # All should be unique
        assert len(request_ids) == len(set(request_ids))

        # All should be valid UUIDs
        for request_id in request_ids:
            assert uuid.UUID(request_id)


class TestRequestIDContext:
    """Tests for Request ID context variable functionality."""

    @pytest.mark.asyncio
    async def test_get_request_id_function(self):
        """Test the get_request_id() function directly."""
        # Initially should be empty
        assert get_request_id() == ""

        # Set a value
        test_id = "test-direct-access"
        token = request_id_var.set(test_id)

        try:
            # Should retrieve the value
            assert get_request_id() == test_id
        finally:
            # Clean up
            request_id_var.reset(token)

        # Should be empty again
        assert get_request_id() == ""


class TestRequestIDIntegration:
    """Integration tests for Request ID with other features."""

    @pytest.mark.asyncio
    async def test_request_id_persists_through_authentication(
        self, client: AsyncClient, test_user_token: str
    ):
        """Test that Request ID persists through authenticated requests."""
        custom_id = "auth-persist-test"
        headers = {
            "X-Request-ID": custom_id,
            "Authorization": f"Bearer {test_user_token}",
        }

        response = await client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
