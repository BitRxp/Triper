from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    rapidapi_skyscanner_host: Optional[str] = Field(
        None,
        env="RAPIDAPI_SKYSCANNER_HOST",
        description="RapidAPI host for Skyscanner API",
    )
    rapidapi_skyscanner_key: Optional[str] = Field(
        None,
        env="RAPIDAPI_SKYSCANNER_KEY",
        description="RapidAPI key for Skyscanner API",
    )
    rapidapi_timeout_seconds: int = Field(
        10,
        env="RAPIDAPI_TIMEOUT_SECONDS",
        description="Timeout for RapidAPI requests in seconds",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
