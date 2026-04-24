# Compulysis Vercel Deployment Guide

This guide deploys current setup as two Vercel projects:
- Frontend project from `frontend`
- Backend project from `backend`

## Do You Need Docker On Vercel?

No. For this setup, do not use Docker on Vercel.

Use Vercel native deployments:
- Frontend: Vite static build
- Backend: Python serverless function (already configured with `backend/vercel.json`)

Docker is still useful for local development, AWS, or other container-first platforms.

## 1. Backend Deployment (FastAPI)

1. In Vercel, create a new project from your GitHub repo.
2. Set Root Directory to `backend`.
3. Framework Preset: `Other`.
4. Keep default build settings (Vercel uses `vercel.json` + `requirements.txt`).

Backend files already prepared:
- `backend/vercel.json`
- `backend/api/index.py`
- `backend/requirements.txt` (references `app/requirements.txt`)

### Backend Environment Variables

Set these in Vercel Project Settings -> Environment Variables:

- `SECRET_KEY` = strong random secret
- `ENVIRONMENT` = `production`
- `BACKEND_CORS_ORIGINS` = your frontend Vercel URL (example: `https://compulysis.vercel.app`)
- `CORS_ALLOW_ORIGIN_REGEX` = empty

Database vars:
- Add Vercel Postgres from Storage and link it to backend project.
- Current code accepts `DATABASE_URL` or `POSTGRES_URL`.

### First-Time Database Setup (No Existing DB)

If you currently have no database, do this first:

1. Open Vercel Dashboard -> your backend project.
2. Go to Storage -> Create Database -> Postgres.
3. Choose region close to your users (and ideally same region as backend).
4. Link the new Postgres instance to your backend project.
5. Vercel will auto-inject Postgres environment variables into backend project.

Important vars typically added by Vercel Postgres:
- `POSTGRES_URL`
- `POSTGRES_PRISMA_URL`
- `POSTGRES_URL_NON_POOLING`
- `POSTGRES_USER`
- `POSTGRES_HOST`
- `POSTGRES_PASSWORD`
- `POSTGRES_DATABASE`

Your backend reads DB URL in this order:
1. `DATABASE_URL`
2. `POSTGRES_URL`
3. local fallback URL (localhost, only for local dev)

So for Vercel deployment, linking Postgres is enough. Optionally, set `DATABASE_URL` explicitly to the same value as `POSTGRES_URL`.

After linking DB:
1. Redeploy backend project.
2. Hit `https://<backend>.vercel.app/health/db`
3. Expect HTTP `200` with `database: connected`.

## 2. Frontend Deployment (React + Vite)

1. Create another Vercel project from the same repo.
2. Set Root Directory to `frontend`.
3. Framework Preset: `Vite`.
4. Add environment variable:
   - `VITE_API_URL` = `https://<your-backend-project>.vercel.app/api/v1`
5. Deploy.

## 3. Health Observation and Monitoring

## Backend Health Endpoints

Use these URLs after deployment:

- API liveness: `https://<backend>.vercel.app/health`
- API + DB connectivity: `https://<backend>.vercel.app/health/db`
- API docs: `https://<backend>.vercel.app/api/v1/docs`

`/health/db` returns:
- `200` when DB connection succeeds
- `503` when DB connection fails

## Frontend Health

Frontend is static, so health is usually availability of:
- `https://<frontend>.vercel.app/`

For stronger checks, monitor both:
- frontend URL (availability)
- backend `/health/db` URL (app + DB)

Recommended uptime tools:
- UptimeRobot
- Better Stack Uptime
- Pingdom

## Vercel Native Observability

In each Vercel project:
- Enable Observability / Runtime Logs
- Review Function logs (backend)
- Review deployment logs (frontend and backend)
- Optional: Enable Web Analytics and Speed Insights for frontend

## 4. Verify End-to-End

1. Open frontend URL.
2. Attempt login from UI.
3. Check backend logs for auth request.
4. Open backend `/health/db` and verify status is healthy.

## 5. Common Failure Cases

1. CORS errors
- Ensure `BACKEND_CORS_ORIGINS` exactly matches frontend origin.

2. 401 or auth issues
- Ensure frontend points to correct backend URL via `VITE_API_URL`.

3. DB connection failures
- Ensure Vercel Postgres is linked to backend project.
- Confirm DB env vars exist in backend environment.
- Check `/health/db` and backend runtime logs.

4. Import/build errors on backend
- Ensure all Python dependencies remain in `backend/app/requirements.txt`.

## 6. Optional Production Hardening

- Add a lightweight external synthetic check every 1 minute to `/health/db`.
- Configure alert notifications to Slack/Email.
- Rotate `SECRET_KEY` and DB credentials periodically.
