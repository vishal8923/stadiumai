"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Pydantic settings model loaded from environment variables and .env file."""

    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="", env="GEMINI_MODEL")
    DATABASE_URL: str = Field(default="sqlite:///./stadium_ai.db", env="DATABASE_URL")
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173,https://stadiumai-six.vercel.app", env="CORS_ORIGINS")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")

    class Config:
        """Pydantic configuration: load from .env and ignore extra fields."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
