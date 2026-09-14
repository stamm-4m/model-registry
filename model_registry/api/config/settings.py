import os

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Settings(BaseSettings):
    # --- API ---
    R_API_URL: str = Field(..., description="URL of the R API")

    # --- Security ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Database ---
    DATABASE_URL: str

    # --- Airflow (workflow-orchestrator) — POST /api/v1/experiments/{id}/trigger-prediction
    # is the only place these credentials are read. Optional: if unset, the
    # trigger is skipped (logged) instead of blocking the request.
    AIRFLOW_API_BASE: str = Field(default="")
    AIRFLOW_TRIGGER_USERNAME: str = Field(default="")
    AIRFLOW_TRIGGER_PASSWORD: str = Field(default="")

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")
        env_file_encoding = "utf-8"


# instance of settings to be used across the application
settings = Settings()
