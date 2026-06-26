import os

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Settings(BaseSettings):
    # --- API ML---
    API_BASE_URL: str = Field(..., description="Base URL of the API")

    @field_validator("API_BASE_URL")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    # --   - IBISBA HUB config ---
    MODEL2SEEK_API_TOKEN: str = Field(
        ..., description="API token for the MODEL2SEEK API"
    )
    MODEL2SEEK_BASE_URL: str = Field(..., description="Base URL of the MODEL2SEEK API")

    class Config:
        env_file = (os.path.join(BASE_DIR, ".env"),)
        env_file_encoding = "utf-8"


# instance of settings to be used across the application
settings = Settings()
