from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./local.db"
    APP_NAME: str = "CrackedInfo"
    ENVIRONMENT: str = "development"
    SERVICE_SECRET: str = ""
    GROQ_API_KEY: str = ""
    DRIVE_FOLDER_ID: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
