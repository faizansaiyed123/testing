from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Fieldline CRM"
    environment: str = "development"
    debug: bool = False
    database_url: str = "postgresql+psycopg://fieldline:fieldline@localhost:5432/fieldline"
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FIELDLINE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
