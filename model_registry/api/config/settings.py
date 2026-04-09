from pydantic_settings import BaseSettings
from pydantic import Field
import os
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

    class Config:
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding = "utf-8"


# instance of settings to be used across the application
settings = Settings()