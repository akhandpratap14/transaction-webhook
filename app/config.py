import logging
import os
from random import randint
from typing import ClassVar, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = ""
    ALLOWED_ORIGINS: str = (
        "http://127.0.0.1:3000,http://localhost:3000"
    )

    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: str = "5432"
    DB_NAME: str = "transaction"
    DB_SCHEMA: str = "transaction"
    DATABASE_URL: Optional[str] = None
    ENCRYPTION_ALGORITHM: str = "HS256"

    APP_BASE_URL: str = os.environ.get("APP_BASE_URL", "http://localhost:3000")



class TestSettings(GlobalSettings):
    DB_SCHEMA: str = f"test_{randint(1, 100)}"


class DevelopmentSettings(GlobalSettings):
    APP_BASE_URL: str = os.environ.get("APP_BASE_URL", "https://api.transaction.com")
    pass


class ProductionSettings(GlobalSettings):

    APP_BASE_URL: str = os.environ.get("APP_BASE_URL", "https://api.transaction.com")


def get_settings():
    env = os.environ.get("ENVIRONMENT", "production")
    if env == "test":
        return TestSettings()
    elif env == "development":
        return DevelopmentSettings()
    elif env == "production":
        return ProductionSettings()

    return GlobalSettings()


settings = get_settings()
