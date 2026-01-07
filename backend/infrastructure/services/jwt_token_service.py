"""JWT implementation of TokenService."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from application.interfaces.token_service import TokenService
from domain.exceptions.token_exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    InvalidTokenFormatError,
)


class JWTTokenService(TokenService):
    """JWT implementation of token service.

    Uses PyJWT library for token generation and validation.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
    ):
        """Initialize the JWT token service.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            access_token_expire_minutes: Token expiration time in minutes (default: 30)
        """
        if not secret_key:
            raise ValueError("Secret key cannot be empty")

        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes

    def generate_token(self, user_id: UUID, email: str) -> tuple[str, datetime]:
        """Generate an authentication token for a user.

        Args:
            user_id: The user's unique identifier
            email: The user's email address

        Returns:
            A tuple containing:
                - The generated token as a string
                - The expiration datetime

        Raises:
            ValueError: If user_id or email is invalid
        """
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not email:
            raise ValueError("Email cannot be empty")

        # Calculate expiration time
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._access_token_expire_minutes
        )

        # Create token payload
        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "exp": expires_at,  # Expiration time
            "iat": datetime.now(timezone.utc),  # Issued at
        }

        # Generate token
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        return token, expires_at

    def validate_token(self, token: str) -> dict[str, str]:
        """Validate and decode an authentication token.

        Args:
            token: The JWT token to validate

        Returns:
            A dictionary containing the token payload with:
                - user_id: str (UUID as string)
                - email: str

        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        if not token:
            raise InvalidTokenFormatError("Token cannot be empty")

        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])

            return {
                "user_id": payload.get("sub", ""),
                "email": payload.get("email", ""),
            }

        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")

    def get_token_expiration(self, token: str) -> datetime:
        """Get the expiration datetime of a token.

        Args:
            token: The JWT token

        Returns:
            The expiration datetime

        Raises:
            InvalidTokenError: If token is invalid
        """
        if not token:
            raise InvalidTokenFormatError("Token cannot be empty")

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={"verify_exp": False},
            )

            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                raise InvalidTokenFormatError("Token does not have expiration")

            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
