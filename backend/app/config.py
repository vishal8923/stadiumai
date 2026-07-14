import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field(default="", env="GEMINI_MODEL")
    DATABASE_URL: str = Field(default="sqlite:///./stadium_ai.db", env="DATABASE_URL")
    SECRET_KEY: str = Field(default="stadium_ai_secret_key_change_me_in_prod", env="SECRET_KEY")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
