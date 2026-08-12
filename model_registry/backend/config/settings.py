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

    # --- Airflow (workflow-orchestrator) — triggers deployment_soft_sensors
    # when an experiment is created. Optional: if unset, the trigger is
    # skipped (logged) instead of blocking experiment creation.
    AIRFLOW_API_BASE: str = Field(default="", description="Base URL of the Airflow API server")
    AIRFLOW_TRIGGER_USERNAME: str = Field(default="", description="Airflow user (Op role) used to trigger DAG runs")
    AIRFLOW_TRIGGER_PASSWORD: str = Field(default="", description="Password for AIRFLOW_TRIGGER_USERNAME")

    class Config:
        env_file = (os.path.join(BASE_DIR, ".env"),)
        env_file_encoding = "utf-8"


# instance of settings to be used across the application
settings = Settings()
