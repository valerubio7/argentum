"""Request ID middleware for request tracing."""

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store request ID for the current request
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get the current request ID from context.

    Returns:
        Current request ID, or empty string if not set.
    """
    return request_id_var.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request ID to each request.

    This middleware:
    1. Generates or accepts a unique request ID for each request
    2. Stores it in a context variable for access in logs
    3. Adds it to response headers for client-side tracing
    4. Supports X-Request-ID header from clients (or generates new UUID)
    """

    def __init__(self, app, header_name: str = "X-Request-ID"):
        """Initialize middleware.

        Args:
            app: ASGI application
            header_name: Name of the header to use for request ID
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and inject request ID.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with X-Request-ID header
        """
        # Get request ID from header or generate new one
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())

        # Store in context variable for access in logs
        token = request_id_var.set(request_id)

        try:
            # Process request
            response = await call_next(request)

            # Add request ID to response headers
            response.headers[self.header_name] = request_id

            return response
        finally:
            # Clean up context variable
            request_id_var.reset(token)
