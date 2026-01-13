"""Use case for user registration."""

import logging

from application.dtos.auth_dtos import RegisterUserDTO, UserResponseDTO
from application.interfaces.hash_service import HashService
from domain.entities.user import User
from domain.exceptions.user_exceptions import UserAlreadyExistsError
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.password import HashedPassword, PlainPassword

logger = logging.getLogger(__name__)


class RegisterUser:
    """Use case for registering a new user.

    This use case handles the business logic for user registration:
    1. Validates input data
    2. Checks if user already exists
    3. Hashes the password
    4. Creates the user entity
    5. Persists to repository
    """

    def __init__(
        self,
        user_repository: UserRepository,
        hash_service: HashService,
    ):
        self._user_repository = user_repository
        self._hash_service = hash_service

    async def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        """Execute the user registration use case.

        Raises:
            UserAlreadyExistsError: If user with email or username exists
            ValueError: If input validation fails
        """
        email = Email(dto.email)
        plain_password = PlainPassword(dto.password)

        if await self._user_repository.exists_by_email(email):
            raise UserAlreadyExistsError("email", dto.email)

        if await self._user_repository.exists_by_username(dto.username):
            raise UserAlreadyExistsError("username", dto.username)

        hashed_password_value = self._hash_service.hash_password(plain_password.value)
        hashed_password = HashedPassword(hashed_password_value)

        user = User(
            email=email,
            hashed_password=hashed_password,
            username=dto.username,
            is_active=True,
            is_verified=False,
        )

        saved_user = await self._user_repository.save(user)

        logger.info(
            f"User registered - username: {saved_user.username}, "
            f"email: {saved_user.email.value}, user_id: {str(saved_user.id)}"
        )

        return UserResponseDTO(
            id=str(saved_user.id),
            email=saved_user.email.value,
            username=saved_user.username,
            is_active=saved_user.is_active,
            is_verified=saved_user.is_verified,
            created_at=saved_user.created_at,
        )
