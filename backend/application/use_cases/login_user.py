"""Use case for user login."""

import logging

from application.dtos.auth_dtos import LoginDTO, TokenDTO
from application.interfaces.hash_service import HashService
from application.interfaces.token_service import TokenService
from domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
)
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email

logger = logging.getLogger(__name__)


class LoginUser:
    """Use case for user authentication/login.

    This use case handles the business logic for user login:
    1. Validates input data
    2. Finds user by email
    3. Verifies password
    4. Checks user is active
    5. Generates authentication token
    """

    def __init__(
        self,
        user_repository: UserRepository,
        hash_service: HashService,
        token_service: TokenService,
    ):
        self._user_repository = user_repository
        self._hash_service = hash_service
        self._token_service = token_service

    async def execute(self, dto: LoginDTO) -> TokenDTO:
        """Execute the user login use case.

        Raises:
            InvalidCredentialsError: If email or password is incorrect
            UserNotActiveError: If user account is not active
            ValueError: If input validation fails
        """
        email = Email(dto.email)

        user = await self._user_repository.find_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        is_password_valid = self._hash_service.verify_password(
            dto.password, user.hashed_password.value
        )
        if not is_password_valid:
            logger.warning(f"Login failed - invalid password for email: {dto.email}")
            raise InvalidCredentialsError()

        if not user.is_active:
            logger.warning(
                f"Login failed - inactive user: {dto.email} (user_id: {str(user.id)})"
            )
            raise UserNotActiveError(user.email.value)

        token, expires_at = self._token_service.generate_token(
            user_id=user.id, email=user.email.value
        )

        logger.info(
            f"User login success - username: {user.username}, "
            f"email: {user.email.value}, user_id: {str(user.id)}"
        )

        return TokenDTO(
            access_token=token,
            token_type="bearer",
            expires_at=expires_at,
        )
