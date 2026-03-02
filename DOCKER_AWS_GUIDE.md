# Docker + AWS Guide (Compulysis)

This setup gives you Dockerized frontend + backend + Postgres for local testing, and a clean path to AWS.

## 1) Local Docker run

From project root:

```bash
docker compose up --build
```

App URLs:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/v1`
- Backend docs: `http://localhost:8000/api/v1/docs`

Stop:

```bash
docker compose down
```

Reset DB volume:

```bash
docker compose down -v
```

## 2) Keep AWS and Vercel isolated

For AWS deployment, set:

- Frontend image build arg: `VITE_API_URL=https://<aws-backend-domain>/api/v1`
- Backend env: `BACKEND_CORS_ORIGINS=https://<aws-frontend-domain>`
- Backend env: `CORS_ALLOW_ORIGIN_REGEX=` (empty in production)

For Vercel deployment, use Vercel-native envs separately (do not point to AWS URLs).

## 3) Build images manually (optional)

Backend:

```bash
docker build -t compulysis-backend:latest ./backend
```

Frontend:

```bash
docker build -t compulysis-frontend:latest --build-arg VITE_API_URL=https://<aws-backend-domain>/api/v1 ./frontend
```

## 4) AWS deployment options

- ECS/Fargate (recommended for containers)
- EC2 with Docker + Compose (simpler for small teams)

Use managed Postgres (RDS) in production and set backend `DATABASE_URL` to the RDS endpoint.
