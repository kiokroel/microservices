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



class APISettings(BaseSettings):
    """API configuration"""

    api_title: str = "Blog API"
    api_description: str = "RESTful API для упрощённой блог-платформы"
    api_version: str = "1.0.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="BACKEND_API_",
    )



class QueueSettings(BaseSettings):
    """Queue (RabbitMQ) configuration"""

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    post_queue_name: str = "post_events"

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="BACKEND_QUEUE_",
    )


class JWTSettings(BaseSettings):
    """JWT configuration"""

    secret_key: str = ""
    algorithm: str = "HS256"
    expiration_hours: int = 24

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="USERS_JWT_",
    )


class Settings(BaseSettings):
    env: str = "development"
    database_settings: DatabaseSettings = DatabaseSettings()
    api_settings: APISettings = APISettings()
    queue_settings: QueueSettings = QueueSettings()
    jwt_settings: JWTSettings = JWTSettings()


    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self.database_settings.database_url


    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )



settings = Settings()



if __name__ == "__main__":
    print(f"Env file path: {env_file_path}")
    print(f"Database settings: {settings.database_settings.model_dump()}")
    print(f"API settings: {settings.api_settings.model_dump()}")
    print(f"Database URL: {settings.database_url}")