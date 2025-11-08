"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.auth_dtos import LoginDTO, RegisterUserDTO
from app.application.use_cases.auth.login_user import LoginUser
from app.application.use_cases.auth.register_user import RegisterUser
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotActiveError,
)
from app.presentation.api.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
    get_session,
)
from app.presentation.api.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, password, and username.",
    responses={
        201: {
            "description": "User successfully registered",
            "model": UserResponse,
        },
        400: {
            "description": "Invalid input or user already exists",
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def register(
    request: RegisterRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user_use_case)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    """Register a new user.

    Args:
        request: Registration request data
        use_case: Register user use case
        session: Database session

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        # Convert Pydantic model to DTO
        dto = RegisterUserDTO(
            email=request.email, password=request.password, username=request.username
        )

        # Execute use case
        user_dto = await use_case.execute(dto)

        # Commit transaction
        await session.commit()

        # Convert DTO to response
        return UserResponse(
            id=user_dto.id,
            email=user_dto.email,
            username=user_dto.username,
            is_active=user_dto.is_active,
            is_verified=user_dto.is_verified,
            created_at=user_dto.created_at,
        )

    except UserAlreadyExistsError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and receive a JWT access token.",
    responses={
        200: {
            "description": "Login successful",
            "model": TokenResponse,
        },
        401: {
            "description": "Invalid credentials or inactive user",
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def login(
    request: LoginRequest,
    use_case: Annotated[LoginUser, Depends(get_login_user_use_case)],
) -> TokenResponse:
    """Login user and get access token.

    Args:
        request: Login request data
        use_case: Login user use case

    Returns:
        TokenResponse: JWT access token

    Raises:
        HTTPException: If credentials are invalid or user is not active
    """
    try:
        # Convert Pydantic model to DTO
        dto = LoginDTO(email=request.email, password=request.password)

        # Execute use case
        token_dto = await use_case.execute(dto)

        # Convert DTO to response
        return TokenResponse(
            access_token=token_dto.access_token,
            token_type=token_dto.token_type,
            expires_at=token_dto.expires_at,
        )

    except (InvalidCredentialsError, UserNotActiveError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
    responses={
        200: {
            "description": "Current user information",
            "model": UserResponse,
        },
        401: {
            "description": "Not authenticated or invalid token",
        },
    },
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current authenticated user.

    Args:
        current_user: Currently authenticated user from JWT token

    Returns:
        UserResponse: Current user data
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email.value,
        username=current_user.username,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )
