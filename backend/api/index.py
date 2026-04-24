import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Define at module scope first - Vercel requires these symbols to be defined
# at import time before any conditional logic
app = None
application = None
handler = None

# Try to import the real app from app.main
try:
    from app.main import app as _resolved_app
    app = _resolved_app
except Exception as exc:
    import sys
    startup_trace = traceback.format_exc()
    print("[STARTUP_ERROR] Failed to import app.main")
    print(startup_trace)
    
    # Create minimal fallback app that returns diagnostic info
    app = FastAPI(title="Compulysis API - Startup Failed")
    
    @app.get("/")
    @app.get("/health")
    async def root():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "startup_import_failed",
                "message": str(exc),
                "details": startup_trace,
            }
        )
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "startup_import_failed",
                "message": str(exc),
                "path": f"/{path}",
                "details": startup_trace,
            }
        )

# Vercel looks for one of these exact top-level callables
application = app

async def handler(scope, receive, send):
    """ASGI handler for Vercel"""
    await app(scope, receive, send)
