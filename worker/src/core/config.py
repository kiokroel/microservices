from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging
import os

base_path = Path(__file__).resolve().parent.parent.parent
env_file_path = str(base_path / ".env")

class DatabaseSettings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_address: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "blog_db"
    db_pool_size: int = 10

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_address}:{self.postgres_port}/{self.postgres_db}"


class BackendAPISettings(DatabaseSettings):

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="BACKEND_",
    )


class UsersAPISettings(DatabaseSettings):

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="USERS_",
    )


class WorkerDBSettings(DatabaseSettings):

    model_config = SettingsConfigDict(
        env_file=env_file_path,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="WORKER_",
    )


class Settings(BaseSettings):
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    post_queue_name: str = "post_events"
    push_notificator_url: str = "http://push-notificator:8000/api/v1/notify"
    worker_concurrency: int = 10

    backend_api_settings: BackendAPISettings = BackendAPISettings()
    users_api_settings: UsersAPISettings = UsersAPISettings()
    worker_db_settings: WorkerDBSettings = WorkerDBSettings()

settings = Settings()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)