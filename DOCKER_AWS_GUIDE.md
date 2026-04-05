# Docker Compose + EC2 Deployment Guide (Compulysis)

This guide is for your assignment requirement: deploy to AWS EC2 using Dockerfiles and Docker Compose.

The stack in this repository runs:
- frontend container (Nginx serving React)
- backend container (FastAPI)
- postgres container

## 1) What was configured in this repo

- Backend Dockerfile: `backend/Dockerfile`
- Frontend Dockerfile: `frontend/Dockerfile`
- Compose orchestration: `docker-compose.yml`
- Frontend now proxies `/api/*` to backend internally, so the app can run on one public origin

With this setup, users access only port 80 (or 443 with TLS). Backend port 8000 is bound to localhost on EC2.

## 2) Create EC2 instance

1. Launch an Ubuntu Server 22.04 or 24.04 EC2 instance (t3.small or higher recommended).
2. Attach a key pair.
3. Security Group inbound rules:
	 - TCP 22 from your IP only
	 - TCP 80 from 0.0.0.0/0
	 - TCP 443 from 0.0.0.0/0 (if using TLS)
4. (Optional but recommended) Allocate and attach an Elastic IP.

## 3) SSH into EC2 and install Docker + Compose plugin

```bash
ssh -i /path/to/key.pem ubuntu@<EC2_PUBLIC_IP>

sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
	"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
	$(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
```

## 4) Pull your project on EC2

```bash
git clone <YOUR_REPO_URL>.git
cd compulysis-webapp
```

## 5) Set production environment values

Create a `.env` file at repository root (same level as `docker-compose.yml`):

```bash
cat > .env << 'EOF'
SECRET_KEY=replace-with-a-long-random-secret-at-least-32-chars
ENVIRONMENT=production

# Keep empty when using fixed allowed origins list.
CORS_ALLOW_ORIGIN_REGEX=

# Set to EC2 URL or your domain.
BACKEND_CORS_ORIGINS=http://<EC2_PUBLIC_IP>,https://<YOUR_DOMAIN>

# Frontend build-time API URL. Using same-origin proxy is recommended.
VITE_API_URL=/api/v1
EOF
```

Notes:
- Compose already defines `DATABASE_URL` for the internal postgres service.
- If you move to RDS later, override `DATABASE_URL` in `.env`.

## 6) Build and run with Docker Compose

```bash
docker compose up -d --build
docker compose ps
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

## 7) Validate deployment

From EC2:

```bash
curl http://localhost/
curl http://localhost/api/v1/docs
curl http://localhost:8000/health
```

From your laptop/browser:
- `http://<EC2_PUBLIC_IP>/`
- `http://<EC2_PUBLIC_IP>/api/v1/docs`

## 8) Useful operations

Restart services:

```bash
docker compose restart
```

Pull latest code and redeploy:

```bash
git pull
docker compose up -d --build
```

Stop stack:

```bash
docker compose down
```

Stop and remove DB data volume:

```bash
docker compose down -v
```

## 9) Optional: add HTTPS with domain + Nginx Proxy Manager or Caddy

For class assignment, HTTP on EC2 IP is often acceptable.
For production, attach a domain and terminate TLS (Let's Encrypt).

## 10) Production recommendations (after assignment)

1. Use AWS RDS Postgres instead of containerized Postgres.
2. Store secrets in AWS Systems Manager Parameter Store or AWS Secrets Manager.
3. Add CloudWatch log shipping.
4. Add automated backups and monitoring alarms.
