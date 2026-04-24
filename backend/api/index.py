from app.main import app

# Export recognized entrypoint names for Vercel Python runtime.
application = app
handler = app
