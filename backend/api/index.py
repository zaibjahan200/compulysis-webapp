import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

_resolved_app = None

try:
	from app.main import app as _resolved_app
except Exception as exc:
	_resolved_app = FastAPI(title="Compulysis API (Startup Error)")
	startup_trace = traceback.format_exc()
    print("[Compulysis Startup Error] Failed to import app.main")
    print(startup_trace)
		return JSONResponse(
			status_code=500,
			content={
				"status": "error",
				"error": "startup_import_failed",
				"message": str(exc),
				"path": f"/{path}" if path else "/",
				"trace": startup_trace,
			},
		)


# Vercel looks for one of these exact top-level callables.
app = _resolved_app
application = app
handler = app
