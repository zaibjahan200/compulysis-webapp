import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Define a concrete top-level ASGI app so Vercel's static detector always finds it.
app = FastAPI(title="Compulysis API - Bootstrap")

_startup_exc = None
_startup_trace = None

try:
    from app.main import app as real_app
    app = real_app
except Exception as exc:
    _startup_exc = exc
    _startup_trace = traceback.format_exc()
    print("[STARTUP_ERROR] Failed to import app.main")
    print(_startup_trace)

    @app.get("/")
    @app.get("/health")
    async def root():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "startup_import_failed",
                "message": str(_startup_exc),
                "details": _startup_trace,
            },
        )

    @app.get("/{path:path}")
    async def catch_all(path: str):
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "startup_import_failed",
                "message": str(_startup_exc),
                "path": f"/{path}",
                "details": _startup_trace,
            },
        )

# Export all recognized names as ASGI app objects.
application = app
handler = app
