from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str
    ENVIRONMENT: str
    SERVICE_SECRET: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
