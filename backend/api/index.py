import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse


try:
	from app.main import app
except Exception as exc:
	app = FastAPI(title="Compulysis API (Startup Error)")
	startup_trace = traceback.format_exc()

	@app.get("/{path:path}")
	async def startup_error(path: str):
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
