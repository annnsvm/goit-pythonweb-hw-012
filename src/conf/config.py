"""
Config Module
"""

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    MAIL_USERNAME: Optional[EmailStr] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[EmailStr] = None
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_SSL_TLS: Optional[bool] = None
    DB_URL: Optional[str] = None
    TEST_DB_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: Optional[str] = None
    JWT_ACCESS_EXPIRATION_MINUTES: Optional[int] = None
    JWT_REFRESH_EXPIRATION_MINUTES: Optional[int] = None
    CLOUDINARY_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[int] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    model_config = SettingsConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()