from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str

    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
