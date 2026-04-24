import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Serverless platforms (Vercel) use ephemeral processes — a large connection
# pool wastes connections and can hit provider limits (Neon free tier = 5 conns).
# Use a minimal pool there; keep a proper pool for Docker/local.
_is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=1 if _is_serverless else 5,
    max_overflow=0 if _is_serverless else 10,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()