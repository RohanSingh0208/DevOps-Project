"""Application configuration via environment variables."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://campus_admin:changeme@localhost:5432/campus_resource_hub"
    database_url_sync: str = "postgresql+psycopg2://campus_admin:changeme@localhost:5432/campus_resource_hub"

    # App
    app_name: str = "Campus Resource Hub"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "changeme_generate_with_openssl_rand_hex_32"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
