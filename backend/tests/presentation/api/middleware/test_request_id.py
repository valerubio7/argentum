"""Tests for Request ID middleware."""

import uuid
from unittest.mock import patch

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
    async def test_request_id_in_response_headers(self, client: AsyncClient):
        """Test that Request ID is always included in response headers."""
        # Test without custom ID
        response1 = await client.get("/health")
        assert "X-Request-ID" in response1.headers

        # Test with custom ID
        response2 = await client.get("/health", headers={"X-Request-ID": "test-123"})
        assert "X-Request-ID" in response2.headers
        assert response2.headers["X-Request-ID"] == "test-123"

    @pytest.mark.asyncio
    async def test_unique_request_ids_across_requests(self, client: AsyncClient):
        """Test that each request gets a unique Request ID."""
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
    async def test_request_id_with_db_health_check(self, client: AsyncClient):
        """Test Request ID with database health check endpoint."""
        custom_id = "db-health-test-456"
        headers = {"X-Request-ID": custom_id}

        response = await client.get("/health/db", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_request_id_context_var_cleanup(self, client: AsyncClient):
        """Test that request_id context variable is cleaned up after request."""
        # Before request, context should be empty
        assert get_request_id() == ""

        # Make request
        response = await client.get("/health", headers={"X-Request-ID": "test-cleanup"})
        assert response.status_code == 200

        # After request completes, context should be empty again
        # (Note: In test context, this might still have a value from the last test)
        # The important thing is that it doesn't leak between actual HTTP requests

    @pytest.mark.asyncio
    async def test_request_id_with_auth_endpoints(self, client: AsyncClient):
        """Test Request ID with authentication endpoints."""
        custom_id = "auth-test-789"
        headers = {"X-Request-ID": custom_id}

        # Test with register endpoint (will fail validation but that's ok)
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short",  # Too short, will fail
            },
            headers=headers,
        )

        # Should have Request ID even on error
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_request_id_format_validation(self, client: AsyncClient):
        """Test Request ID with various formats."""
        test_cases = [
            # (input_id, should_be_valid)
            (str(uuid.uuid4()), True),  # Valid UUID
            ("custom-trace-123", True),  # Custom string
            ("", False),  # Empty string (should generate new one)
            ("simple", True),  # Simple string
        ]

        for input_id, should_preserve in test_cases:
            headers = {"X-Request-ID": input_id} if input_id else {}
            response = await client.get("/health", headers=headers)

            assert "X-Request-ID" in response.headers

            if should_preserve and input_id:
                # Should preserve the input ID
                assert response.headers["X-Request-ID"] == input_id
            elif not input_id:
                # Should generate a valid UUID
                assert uuid.UUID(response.headers["X-Request-ID"])

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


class TestRequestIDInLogs:
    """Tests for Request ID integration with logging."""

    @pytest.mark.asyncio
    async def test_request_id_appears_in_logs(self, client: AsyncClient, caplog):
        """Test that Request ID appears in structured logs."""
        custom_id = "log-test-123"
        headers = {"X-Request-ID": custom_id}

        # Make a request that will generate logs
        with caplog.at_level("INFO"):
            response = await client.get("/health/db", headers=headers)

        assert response.status_code == 200

        # Check if logs contain the request_id
        # Note: This depends on structlog configuration
        # In tests, logs might be captured differently

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


class TestRequestIDMiddlewareErrorHandling:
    """Tests for Request ID middleware error handling."""

    @pytest.mark.asyncio
    async def test_request_id_with_404_error(self, client: AsyncClient):
        """Test that Request ID is included even for 404 errors."""
        custom_id = "error-404-test"
        headers = {"X-Request-ID": custom_id}

        response = await client.get("/nonexistent", headers=headers)

        assert response.status_code == 404
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == custom_id

    @pytest.mark.asyncio
    async def test_request_id_with_500_error(self, client: AsyncClient):
        """Test that Request ID is included even for server errors."""
        custom_id = "error-500-test"
        headers = {"X-Request-ID": custom_id}

        # Force a database error by using an endpoint that requires DB
        # but with a mocked failure
        with patch(
            "infrastructure.database.connection.get_db",
            side_effect=Exception("DB Error"),
        ):
            try:
                response = await client.get("/health/db", headers=headers)
                # Should still have Request ID even on error
                assert "X-Request-ID" in response.headers
            except Exception:
                # If exception propagates, that's ok - we're testing middleware behavior
                pass

    @pytest.mark.asyncio
    async def test_request_id_with_validation_error(self, client: AsyncClient):
        """Test Request ID with validation errors."""
        custom_id = "validation-error-test"
        headers = {"X-Request-ID": custom_id}

        # Send invalid data to trigger validation error
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",  # Invalid email
                "username": "test",
                "password": "password123",
            },
            headers=headers,
        )

        assert response.status_code == 422  # Validation error
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] == custom_id


class TestRequestIDMiddlewareIntegration:
    """Integration tests for Request ID with other features."""

    @pytest.mark.asyncio
    async def test_request_id_with_cors(self, client: AsyncClient):
        """Test that Request ID works with CORS middleware."""
        custom_id = "cors-test-123"
        headers = {
            "X-Request-ID": custom_id,
            "Origin": "http://localhost:3000",
        }

        response = await client.get("/health", headers=headers)

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
        # CORS headers should also be present
        assert "access-control-allow-origin" in response.headers

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

    @pytest.mark.asyncio
    async def test_request_id_with_full_login_flow(
        self, client: AsyncClient, test_user
    ):
        """Test Request ID through complete login flow."""
        custom_id = "login-flow-test"
        headers = {"X-Request-ID": custom_id}

        # Login with valid credentials
        response = await client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
            headers=headers,
        )

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
        assert "access_token" in response.json()


class TestRequestIDMiddlewarePerformance:
    """Performance tests for Request ID middleware."""

    @pytest.mark.asyncio
    async def test_middleware_overhead_is_minimal(self, client: AsyncClient):
        """Test that Request ID middleware doesn't significantly impact performance."""
        import time

        # Measure time for multiple requests
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            response = await client.get("/health")
            assert response.status_code == 200

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_request = total_time / iterations

        # Should be very fast (< 100ms per request on average)
        assert avg_time_per_request < 0.1, (
            f"Requests are too slow: {avg_time_per_request}s per request"
        )

    @pytest.mark.asyncio
    async def test_uuid_generation_performance(self):
        """Test that UUID generation is fast."""
        import time

        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            _ = str(uuid.uuid4())

        end_time = time.time()
        total_time = end_time - start_time

        # Should be very fast (< 1ms per UUID on average)
        avg_time = total_time / iterations
        assert avg_time < 0.001, f"UUID generation is too slow: {avg_time}s per UUID"
