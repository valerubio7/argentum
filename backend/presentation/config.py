"""Configuration and settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Argentum"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/argentum"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Security
    bcrypt_rounds: int = 12

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # API
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields from .env
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str, info) -> str:
        """Validate JWT secret key strength in production."""
        environment = info.data.get("environment", "development")

        # In production, enforce strong secret key
        if environment == "production":
            if not v or len(v) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must be at least 32 characters in production. "
                    "Generate a strong key with: openssl rand -hex 32"
                )

            # Check for weak/default values
            weak_patterns = ["secret", "change", "example", "test", "password", "your-"]
            if any(pattern in v.lower() for pattern in weak_patterns):
                raise ValueError(
                    "JWT_SECRET_KEY appears to be a default/weak value. "
                    "Generate a strong key with: openssl rand -hex 32"
                )

        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
