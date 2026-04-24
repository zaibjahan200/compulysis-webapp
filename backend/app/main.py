from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
import app.models
import logging
import time
import os

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
Base = None
db_startup_error = None

try:
    from app.db.session import engine as _engine, SessionLocal as _SessionLocal
    from app.db.base_class import Base as _Base
    from app.services.seed_service import seed_initial_data
    from sqlalchemy import text
except Exception as exc:
    db_startup_error = exc
    logger.exception("Database modules failed to import: %s", exc)
else:
    engine = _engine
    SessionLocal = _SessionLocal
    Base = _Base


def _is_serverless_runtime() -> bool:
    return bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def ensure_database_ready(max_attempts: int = 10, delay_seconds: int = 2) -> bool:
    if not engine or not Base:
        logger.error("Database engine/base unavailable at startup: %s", db_startup_error)
        return False

    if _is_serverless_runtime():
        # Avoid long cold-start delays on serverless platforms.
        max_attempts = 1
        delay_seconds = 0

    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return True
        except Exception as exc:
            logger.warning(
                "Database initialization attempt %s/%s failed: %s",
                attempt,
                max_attempts,
                exc,
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)
    return False

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configure CORS
cors_kwargs = {
    "allow_origins": settings.get_cors_origins(),
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

if settings.CORS_ALLOW_ORIGIN_REGEX:
    cors_kwargs["allow_origin_regex"] = settings.CORS_ALLOW_ORIGIN_REGEX

app.add_middleware(CORSMiddleware, **cors_kwargs)

# Include routers (guarded to keep base health endpoints available)
try:
    from app.api.endpoints import auth
    app.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["Authentication"]
    )
except Exception as exc:
    logger.exception("Failed to include auth router: %s", exc)

try:
    from app.api.endpoints import clinical
    app.include_router(
        clinical.router,
        prefix=f"{settings.API_V1_STR}",
        tags=["Clinical"]
    )
except Exception as exc:
    logger.exception("Failed to include clinical router: %s", exc)


@app.on_event("startup")
def startup_seed_data():
    db_ready = ensure_database_ready()
    if not db_ready:
        logger.error("Database is not ready after retries; API will start but DB-dependent routes may fail.")
        return

    if SessionLocal is None:
        logger.error("SessionLocal unavailable; skipping seed initialization")
        return

    db = SessionLocal()
    try:
        seed_initial_data(db)
    except Exception as exc:
        # Keep API available even when seed data cannot be inserted.
        logger.exception("Seed initialization failed: %s", exc)
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Compulysis API",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/db")
async def health_db_check():
    """Database connectivity health endpoint"""
    if engine is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": "database_module_import_failed",
                "details": str(db_startup_error) if db_startup_error else "unknown",
            },
        )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as exc:
        logger.exception("Database health check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": "database_connection_failed",
                "details": str(exc),
            },
        )