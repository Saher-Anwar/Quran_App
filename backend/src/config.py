"""Global configuration and environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://admin:admin@localhost:5432/quran_db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://admin:admin@localhost:5432/quran_db"

    # Application
    APP_NAME: str = "Quran App API"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
