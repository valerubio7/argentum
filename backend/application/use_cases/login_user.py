"""Use case for user login."""

from application.dtos.auth_dtos import LoginDTO, TokenDTO
from application.interfaces.hash_service import HashService
from application.interfaces.token_service import TokenService
from domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
)
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from infrastructure.logging import get_logger

logger = get_logger(__name__)


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
        """Initialize the login user use case.

        Args:
            user_repository: Repository for user retrieval
            hash_service: Service for password verification
            token_service: Service for JWT token generation
        """
        self._user_repository = user_repository
        self._hash_service = hash_service
        self._token_service = token_service

    async def execute(self, dto: LoginDTO) -> TokenDTO:
        """Execute the user login use case.

        Args:
            dto: Login data transfer object

        Returns:
            TokenDTO with authentication token

        Raises:
            InvalidCredentialsError: If email or password is incorrect
            UserNotActiveError: If user account is not active
            ValueError: If input validation fails
        """
        # 1. Validate and create email value object
        email = Email(dto.email)

        # 2. Find user by email
        user = await self._user_repository.find_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        # 3. Verify password
        is_password_valid = self._hash_service.verify_password(
            dto.password, user.hashed_password.value
        )
        if not is_password_valid:
            logger.warning(
                "login_failed_invalid_password",
                email=dto.email,
                reason="invalid_password",
            )
            raise InvalidCredentialsError()

        # 4. Check if user is active
        if not user.is_active:
            logger.warning(
                "login_failed_inactive_user",
                email=dto.email,
                user_id=str(user.id),
                reason="inactive_user",
            )
            raise UserNotActiveError(user.email.value)

        # 5. Generate authentication token
        token, expires_at = self._token_service.generate_token(
            user_id=user.id, email=user.email.value
        )

        logger.info(
            "user_login_success",
            username=user.username,
            email=user.email.value,
            user_id=str(user.id),
        )

        # 6. Return token DTO
        return TokenDTO(
            access_token=token,
            token_type="bearer",
            expires_at=expires_at,
        )
