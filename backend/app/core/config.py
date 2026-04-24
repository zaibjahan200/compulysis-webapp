from typing import List
import os
from pathlib import Path
import json
from urllib.parse import quote_plus, urlparse, urlencode, parse_qs, urlunparse

try:
    from dotenv import load_dotenv, dotenv_values
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs):
        return False

    def dotenv_values(*_args, **_kwargs):
        return {}

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

fallback_env = dotenv_values(BASE_DIR / "app" / ".env")
for key, value in fallback_env.items():
    if value in (None, ""):
        continue

    current = os.getenv(key)
    if current is None or current == "":
        os.environ[key] = str(value)


# psycopg2 only accepts a known set of libpq connection parameters as query params.
# Providers like Supabase inject extras (e.g. supa=base-pooler.x) that make psycopg2
# raise "invalid connection option". We keep only the safe known set.
_PSYCOPG2_ALLOWED_PARAMS = {
    "sslmode", "sslcert", "sslkey", "sslrootcert", "sslcrl",
    "connect_timeout", "application_name", "fallback_application_name",
    "keepalives", "keepalives_idle", "keepalives_interval", "keepalives_count",
    "options", "service", "target_session_attrs",
}


def _sanitise_db_url(url: str) -> str:
    """Normalise scheme and strip provider-specific query params psycopg2 can't handle."""
    # SQLAlchemy 2.x dropped the short postgres:// alias.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    parsed = urlparse(url)
    if parsed.query:
        filtered = {
            k: v for k, v in parse_qs(parsed.query, keep_blank_values=True).items()
            if k in _PSYCOPG2_ALLOWED_PARAMS
        }
        clean_query = urlencode(filtered, doseq=True)
        parsed = parsed._replace(query=clean_query)

    return urlunparse(parsed)


def resolve_database_url() -> str:
    direct_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_POSTGRES_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("STORAGE_URL")
    )
    if direct_url:
        return _sanitise_db_url(direct_url)

    user = os.getenv("DATABASE_POSTGRES_USER") or os.getenv("POSTGRES_USER")
    password = os.getenv("DATABASE_POSTGRES_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("DATABASE_POSTGRES_HOST") or os.getenv("POSTGRES_HOST")
    database = os.getenv("DATABASE_POSTGRES_DATABASE") or os.getenv("POSTGRES_DATABASE")
    port = os.getenv("DATABASE_POSTGRES_PORT") or os.getenv("POSTGRES_PORT") or "5432"

    if user and password and host and database:
        encoded_password = quote_plus(password)
        sslmode = os.getenv("DATABASE_POSTGRES_SSLMODE") or os.getenv("POSTGRES_SSLMODE")
        if not sslmode:
            sslmode = "disable" if host in {"localhost", "127.0.0.1", "db"} else "require"
        return f"postgresql://{user}:{encoded_password}@{host}:{port}/{database}?sslmode={sslmode}"

    return "postgresql://postgres:postgres@localhost:5432/compulysis_db"


class Settings:
    def __init__(self) -> None:
        # Project Info
        self.PROJECT_NAME: str = "Compulysis OCD Risk Analyzer"
        self.API_V1_STR: str = "/api/v1"

        # Database
        self.DATABASE_URL: str = resolve_database_url()

        # JWT
        self.SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

        # CORS
        self.BACKEND_CORS_ORIGINS: str = os.getenv(
            "BACKEND_CORS_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000",
        )
        self.CORS_ALLOW_ORIGIN_REGEX: str = os.getenv(
            "CORS_ALLOW_ORIGIN_REGEX",
            r"https?://(localhost|127\.0\.0\.1|([a-zA-Z0-9-]+\.)*ngrok-free\.dev)(:\d+)?$",
        )

        # Email
        self.SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower().strip().strip("'\"") == "true"
        self.SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587").strip().strip("'\""))
        _smtp_host = os.getenv("SMTP_HOST", "").strip().strip("'\"")
        # Users sometimes paste "https://smtp.gmail.com" — strip the scheme.
        for prefix in ("https://", "http://"):
            if _smtp_host.startswith(prefix):
                _smtp_host = _smtp_host[len(prefix):]
        self.SMTP_HOST: str = _smtp_host.rstrip("/")
        self.SMTP_USER: str = os.getenv("SMTP_USER", "").strip().strip("'\"")
        self.SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "").strip().strip("'\"")

        # Environment
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    def get_cors_origins(self) -> List[str]:
        value = self.BACKEND_CORS_ORIGINS

        if value is None or value == "":
            return []

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

        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]

        return []
    
settings = Settings()