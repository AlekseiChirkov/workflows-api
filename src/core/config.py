from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    API_KEY: str

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    INSTANCE_CONNECTION_NAME: str | None = None

    ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    GCP_PROJECT_ID: str
    PUBSUB_TOPIC_WORKFLOW_EVENTS: str

    @cached_property
    def DATABASE_URL(self):
        if self.ENV == "local":
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@/{self.DB_NAME}?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"
        )


settings = Settings()  # type: ignore
