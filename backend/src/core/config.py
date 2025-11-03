from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


base_path = Path(__file__).resolve().parent.parent.parent
env_file_path = str(base_path / ".env")


class DatabaseSettings(BaseSettings):
    """Database configuration"""

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_address: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "blog_db"
    db_pool_size: int = 10

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="BACKEND_",
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_address}:{self.postgres_port}/{self.postgres_db}"


class JWTSettings(BaseSettings):
    """JWT configuration"""

    secret_key: str = ""
    algorithm: str = "HS256"
    expiration_hours: int = 24

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_JWT_",
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class APISettings(BaseSettings):
    """API configuration"""

    api_title: str = "Blog API"
    api_description: str = "RESTful API для упрощённой блог-платформы"
    api_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_API_",
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class Settings(BaseSettings):
    env: str = "development"
    database_settings: DatabaseSettings = Field(default_factory=DatabaseSettings)
    jwt_settings: JWTSettings = Field(default_factory=JWTSettings)
    api_settings: APISettings = Field(default_factory=APISettings)

    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self.database_settings.database_url

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_",
        extra="ignore",
        env_file=env_file_path,
        env_file_encoding="utf-8",
    )


settings = Settings()


if __name__ == "__main__":
    print(f"Env file path: {env_file_path}")
    print(f"Database settings: {settings.database_settings.model_dump()}")
    print(f"JWT settings: {settings.jwt_settings.model_dump()}")
    print(f"API settings: {settings.api_settings.model_dump()}")
    print(f"Database URL: {settings.database_url}")