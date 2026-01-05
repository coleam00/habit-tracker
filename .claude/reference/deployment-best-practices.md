# Deployment Best Practices Reference

A concise reference guide for deploying Python/FastAPI + React applications.

---

## Table of Contents

1. [Local Development](#1-local-development)
2. [Production Builds](#2-production-builds)
3. [Backend Deployment](#3-backend-deployment)
4. [Frontend Deployment](#4-frontend-deployment)
5. [Docker](#5-docker)
6. [Reverse Proxy (Nginx)](#6-reverse-proxy-nginx)
7. [Environment & Configuration](#7-environment--configuration)
8. [Database in Production](#8-database-in-production)
9. [Monitoring & Logging](#9-monitoring--logging)
10. [Cloud Platforms](#10-cloud-platforms)
11. [Security](#11-security)
12. [Single Binary Deployment](#12-single-binary-deployment)

---

## 1. Local Development

### Running Frontend and Backend

**Two Terminal Approach:**

```bash
# Terminal 1: Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev  # Runs on port 5173
```

### Vite Proxy Configuration

Avoid CORS issues by proxying API requests through Vite:

```javascript
// frontend/vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

Now frontend code can use relative paths:
```javascript
fetch('/api/habits')  // Proxied to http://localhost:8000/api/habits
```

### Hot Reloading

- **Backend**: `uvicorn --reload` watches for file changes
- **Frontend**: Vite HMR (Hot Module Replacement) built-in

### Environment Variables

```bash
# backend/.env
DATABASE_URL=sqlite:///./habits.db
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]

# frontend/.env
VITE_API_URL=/api
```

---

## 2. Production Builds

### Frontend Build (Vite)

```bash
cd frontend
npm run build  # Creates dist/ folder
```

**Output:**
```
dist/
├── index.html
├── assets/
│   ├── index-abc123.js
│   └── index-def456.css
```

### Build Optimization

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
});
```

### Bundle Analysis

```bash
npm install rollup-plugin-visualizer --save-dev
```

```javascript
// vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true }),
  ],
});
```

---

## 3. Backend Deployment

### Uvicorn (Recommended for Most Cases)

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (with multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Worker count**: Number of CPU cores for async workers.

### Gunicorn + Uvicorn Workers

```bash
# Install
pip install gunicorn uvicorn

# Run
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**Gunicorn config file:**

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count()
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 30
keepalive = 5
max_requests = 10000
max_requests_jitter = 1000
```

```bash
gunicorn app.main:app -c gunicorn.conf.py
```

### Systemd Service

```ini
# /etc/systemd/system/habittracker.service
[Unit]
Description=Habit Tracker API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/habit-tracker/backend
Environment="PATH=/var/www/habit-tracker/backend/.venv/bin"
ExecStart=/var/www/habit-tracker/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable habittracker
sudo systemctl start habittracker
sudo systemctl status habittracker
```

---

## 4. Frontend Deployment

### Option 1: FastAPI Serves Static Files

```python
# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

app = FastAPI()

# API routes first
@app.get("/api/habits")
async def list_habits():
    pass

# Serve React app
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")

@app.get("/")
async def serve_react_app():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Handle client-side routing
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    if not request.url.path.startswith("/api"):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    raise exc

# Mount static files AFTER routes
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")
```

**Benefits**: Single deployment, no CORS issues, simpler infrastructure.

### Option 2: Nginx Serves Static Files

Better performance for static assets:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/habit-tracker/frontend/dist;

    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to FastAPI
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 3: CDN/Static Hosting

Deploy frontend to Vercel, Netlify, or Cloudflare Pages:

```bash
# Vercel
npm install -g vercel
vercel --prod

# Netlify
npm install -g netlify-cli
netlify deploy --prod
```

Configure API URL for separate backend:
```javascript
// frontend/.env.production
VITE_API_URL=https://api.yourdomain.com
```

---

## 5. Docker

### Dockerfile (Multi-Stage Build)

```dockerfile
# backend/Dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/habits.db
    volumes:
      - ./data:/app/data  # Persist SQLite database
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Docker Commands

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild single service
docker-compose up --build backend
```

### Image Optimization Tips

| Tip | Impact |
|-----|--------|
| Use slim base images | `python:3.11-slim` is 45MB vs 125MB |
| Multi-stage builds | 70%+ smaller images |
| Use `.dockerignore` | Faster builds |
| Order layers by change frequency | Better caching |
| Combine RUN commands | Fewer layers |

**.dockerignore:**
```
__pycache__
*.pyc
.git
.env
.venv
node_modules
dist
*.md
```

---

## 6. Reverse Proxy (Nginx)

### Basic Configuration

```nginx
# /etc/nginx/sites-available/habittracker
server {
    listen 80;
    server_name yourdomain.com;

    # Serve React static files
    root /var/www/habit-tracker/frontend/dist;
    index index.html;

    # Handle React Router (client-side routing)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to FastAPI
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/habittracker /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

**Result** (auto-generated by certbot):

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... rest of config
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}
```

---

## 7. Environment & Configuration

### 12-Factor App Principles

| Factor | Application |
|--------|-------------|
| Config | Environment variables |
| Dependencies | requirements.txt / package.json |
| Processes | Stateless app |
| Port binding | App binds to port |
| Logs | Stream to stdout |
| Dev/prod parity | Use Docker |

### Pydantic Settings

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Habit Tracker"
    database_url: str = "sqlite:///./habits.db"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Environment Files

```bash
# .env.development
DATABASE_URL=sqlite:///./habits.db
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]

# .env.production
DATABASE_URL=sqlite:///./data/habits.db
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

### Secrets Management (Production)

| Environment | Solution |
|-------------|----------|
| Local | `.env` files (gitignored) |
| Docker | Environment variables / secrets |
| Cloud | Platform secrets (Railway, Fly.io) |
| Enterprise | HashiCorp Vault, AWS Secrets Manager |

---

## 8. Database in Production

### SQLite Considerations

**When SQLite works**:
- Single server deployment
- Low write concurrency
- Database < 1TB
- Local/personal applications

**When to migrate to PostgreSQL**:
- Multiple servers/load balancing
- High write concurrency
- Need for replication/HA

### Database File Location

```python
# Don't store in application directory
# BAD
DATABASE_URL = "sqlite:///./habits.db"

# GOOD - absolute path outside app
DATABASE_URL = "sqlite:////var/data/habit-tracker/habits.db"
```

### Docker Volume for Persistence

```yaml
# docker-compose.yml
services:
  backend:
    volumes:
      - db-data:/app/data

volumes:
  db-data:
```

### Backup with Litestream

```yaml
# litestream.yml
dbs:
  - path: /data/habits.db
    replicas:
      - url: s3://bucket-name/habits
        sync-interval: 1s
        retention: 24h
```

```bash
# Run with litestream
litestream replicate -config litestream.yml
```

### Manual Backup

```bash
# Safe backup using SQLite CLI
sqlite3 /data/habits.db "VACUUM INTO '/backups/habits-$(date +%Y%m%d).db'"

# Or using Python
python -c "import sqlite3; src=sqlite3.connect('/data/habits.db'); dst=sqlite3.connect('/backups/backup.db'); src.backup(dst)"
```

### Migrations with Alembic

```bash
# Generate migration
alembic revision --autogenerate -m "Add description column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Production deployment:**
1. Create backup
2. Run migrations: `alembic upgrade head`
3. Start application
4. Verify health checks

---

## 9. Monitoring & Logging

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        return json.dumps(log_data)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Request Logging Middleware

```python
import time
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s"
    )
    return response
```

### Health Check Endpoints

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "error": str(e)},
        )
```

### Monitoring Stack (Optional)

| Tool | Purpose |
|------|---------|
| Prometheus | Metrics collection |
| Grafana | Visualization |
| Sentry | Error tracking |
| Loki | Log aggregation |

---

## 10. Cloud Platforms

### Platform Comparison

| Platform | Pricing | Best For | SQLite Support |
|----------|---------|----------|----------------|
| **Railway** | Usage-based | Fast deploys | Limited |
| **Render** | $7+/mo | Managed services | Limited |
| **Fly.io** | $2+/mo | Global, SQLite | Yes (volumes) |
| **DigitalOcean** | $4+/mo | VPS control | Yes |
| **Hetzner** | $4+/mo | Europe, budget | Yes |

### Fly.io Deployment

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy

# Create volume for SQLite
fly volumes create data --size 1

# Check status
fly status
```

**fly.toml:**
```toml
app = "habit-tracker"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true

[mounts]
  source = "data"
  destination = "/data"
```

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

### VPS Deployment Checklist

1. **Server setup**
   ```bash
   sudo apt update && sudo apt upgrade
   sudo apt install nginx python3-pip python3-venv
   ```

2. **Clone repository**
   ```bash
   git clone https://github.com/user/habit-tracker /var/www/habit-tracker
   ```

3. **Setup backend**
   ```bash
   cd /var/www/habit-tracker/backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Build frontend**
   ```bash
   cd /var/www/habit-tracker/frontend
   npm install && npm run build
   ```

5. **Configure systemd service**

6. **Configure Nginx**

7. **Setup SSL with Certbot**

8. **Configure firewall**
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

---

## 11. Security

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Security Headers (Nginx)

```nginx
# Add to server block
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
```

### Docker Security

```dockerfile
# Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

# Use specific versions
FROM python:3.11.7-slim

# Don't store secrets in image
# Use runtime environment variables
```

### HTTPS Everywhere

- Use Let's Encrypt for free SSL certificates
- Redirect HTTP to HTTPS
- Enable HSTS

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Environment Security

```bash
# Never commit .env files
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore

# Set restrictive permissions
chmod 600 .env
```

---

## 12. Single Binary Deployment

### PyInstaller

```bash
pip install pyinstaller

# Create spec file
pyi-makespec --onefile --name habittracker backend/app/main.py
```

**entrypoint.py:**
```python
import multiprocessing
import uvicorn

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Required for Windows
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
```

**Build:**
```bash
pyinstaller --onefile --add-data "frontend/dist:frontend/dist" entrypoint.py
```

### Tauri (Desktop App)

For a native desktop wrapper:

```bash
# Install Tauri CLI
cargo install tauri-cli

# Initialize
cargo tauri init

# Build
cargo tauri build
```

**Benefits**:
- Native WebView (not bundled browser)
- Small binary (~10-50MB)
- Cross-platform

---

## Deployment Scenarios

### Scenario 1: Local/Personal Use

```
┌─────────────────────────────────┐
│  uvicorn + embedded React       │
│  SQLite file in ./data          │
└─────────────────────────────────┘
```

**Commands:**
```bash
cd backend && uvicorn app.main:app --port 8000
# Access at http://localhost:8000
```

### Scenario 2: Self-Hosted VPS

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│  Nginx   │──────│  FastAPI │──────│  SQLite  │
│  (SSL)   │      │ (systemd)│      │  (file)  │
└──────────┘      └──────────┘      └──────────┘
```

**Cost**: ~$4-5/month

### Scenario 3: Docker Compose

```
┌──────────────────────────────────────────┐
│  docker-compose                          │
│  ┌────────────┐    ┌────────────┐        │
│  │  frontend  │    │  backend   │        │
│  │  (nginx)   │────│  (uvicorn) │        │
│  └────────────┘    └─────┬──────┘        │
│                          │               │
│                    ┌─────▼──────┐        │
│                    │   volume   │        │
│                    │  (sqlite)  │        │
│                    └────────────┘        │
└──────────────────────────────────────────┘
```

### Scenario 4: Cloud PaaS (Fly.io)

```
┌──────────────────────────────────────────┐
│  Fly.io                                  │
│  ┌────────────────────────┐              │
│  │  Docker container      │              │
│  │  FastAPI + React       │              │
│  └───────────┬────────────┘              │
│              │                           │
│        ┌─────▼─────┐                     │
│        │  Volume   │                     │
│        │  (SQLite) │                     │
│        └───────────┘                     │
└──────────────────────────────────────────┘
```

**Cost**: ~$2-5/month

---

## Quick Reference

### Essential Commands

```bash
# Development
uvicorn app.main:app --reload
npm run dev

# Production build
npm run build
pip install -r requirements.txt

# Docker
docker-compose up --build
docker-compose logs -f

# Deployment
fly deploy
railway up

# SSL
sudo certbot --nginx -d yourdomain.com

# Database backup
sqlite3 db.db "VACUUM INTO 'backup.db'"
```

### Port Reference

| Service | Default Port |
|---------|--------------|
| Vite dev server | 5173 |
| FastAPI/Uvicorn | 8000 |
| Nginx HTTP | 80 |
| Nginx HTTPS | 443 |
| PostgreSQL | 5432 |

---

## Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Static Deploy](https://vitejs.dev/guide/static-deploy.html)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Litestream](https://litestream.io/)
