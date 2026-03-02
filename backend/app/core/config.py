from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator
import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import json

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

fallback_env = dotenv_values(BASE_DIR / "app" / ".env")
for key, value in fallback_env.items():
    if value in (None, ""):
        continue

    current = os.getenv(key)
    if current is None or current == "":
        os.environ[key] = str(value)


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Compulysis OCD Risk Analyzer"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/compulysis_db")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    CORS_ALLOW_ORIGIN_REGEX: str = r"https?://(localhost|127\.0\.0\.1|([a-zA-Z0-9-]+\.)*ngrok-free\.dev)(:\d+)?$"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None or value == "":
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return []

            if trimmed.startswith("["):
                try:
                    parsed = json.loads(trimmed)
                    if isinstance(parsed, list):
                        return [item.strip() for item in parsed if isinstance(item, str) and item.strip()]
                except json.JSONDecodeError:
                    pass

            return [origin.strip() for origin in trimmed.split(",") if origin.strip()]

        return value
    
    class Config:
        env_file = str(BASE_DIR / ".env")
        case_sensitive = True


settings = Settings()