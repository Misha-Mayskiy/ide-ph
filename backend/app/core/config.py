from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IDE Builder MVP"
    env: str = "dev"
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/ide_builder"
    )
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173"

    worker_poll_interval_seconds: float = 1.0
    rate_limit_requests_per_minute: int = 120

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    auto_create_tables: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
