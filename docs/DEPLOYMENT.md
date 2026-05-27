# Deployment Guide

## Architecture

| Service | Platform | Region |
|---------|----------|--------|
| Frontend | Vercel | Auto (Edge) |
| Backend API | Render (Docker) | Singapore |
| Database | Supabase PostgreSQL | Southeast Asia |
| Redis | Upstash | Singapore |

---

## Backend — Render

### First-time setup

1. Create a [Render](https://render.com) account and connect your GitHub repository.

2. In the Render dashboard, click **New → Blueprint** and point it at the repo root. Render reads `render.yaml` and creates the `iwasscam-api` web service automatically.

3. Set the required environment variables under your service → **Environment**:

| Variable | Where to get it |
|----------|----------------|
| `DATABASE_URL` | Supabase → Settings → Database → **Session pooler** string. Change `postgresql://` to `postgresql+asyncpg://` |
| `REDIS_URL` | Upstash console → your Redis instance → connection string |
| `SECRET_KEY` | Run `openssl rand -hex 32` |
| `FRONTEND_URL` | Your Vercel deployment URL |

The following are pre-set in `render.yaml`:
```
ENVIRONMENT=production
DEBUG=false
LOG_FORMAT=json
CLAMAV_ENABLED=false
USE_LLM=false
```

4. Click **Deploy**. The container builds, then `start.sh` runs Alembic migrations and starts Uvicorn.

### Verify

```bash
curl https://iwasscam-api.onrender.com/api/v1/health
# {"status":"ok","version":"0.1.0","db":true,"redis":true}
```

### Free tier notes

- Service spins down after 15 minutes of inactivity; first request after spin-down takes ~30 s.
- No persistent disk — all file processing must be in-memory (already the case).

---

## Database — Supabase

1. Create a [Supabase](https://supabase.com) project in `ap-southeast-1`.

2. Go to **Settings → Database → Connection string** and copy the **Session pooler** URL (port 5432).

3. The URL format:
   ```
   postgresql+asyncpg://postgres.PROJECTREF:PASSWORD@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
   ```

4. Migrations run automatically on deploy. To run manually:
   ```bash
   cd backend
   DATABASE_URL="your-url" alembic upgrade head
   ```

5. Seed the RAG knowledge base:
   ```bash
   cd backend
   python -m app.data.seed_knowledge
   ```

---

## Redis — Upstash

1. Create an [Upstash](https://upstash.com) Redis database in the Singapore region.

2. Copy the connection string — it looks like:
   ```
   rediss://default:TOKEN@hostname.upstash.io:6379
   ```
   Note: `rediss://` (double-s) means TLS-enabled.

3. Set this as `REDIS_URL` on Render.

---

## Frontend — Vercel

### First-time setup

```bash
cd frontend
npm i -g vercel
vercel link     # connect to your Vercel project
```

Set environment variables via the Vercel dashboard (Settings → Environment Variables):

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://iwasscam-api.onrender.com` |
| `NEXT_PUBLIC_APP_URL` | `https://your-app.vercel.app` |
| `BETTER_AUTH_SECRET` | `openssl rand -hex 32` |
| `BETTER_AUTH_URL` | `https://your-app.vercel.app` |
| `DATABASE_URL` | Supabase connection string (standard `postgresql://`) |

Deploy:
```bash
vercel --prod
```

### Subsequent deploys

Push to `main` — Vercel auto-deploys if Git integration is connected. Otherwise:
```bash
cd frontend && vercel --prod
```

### CORS after a URL change

If your Vercel URL changes, update `FRONTEND_URL` on Render. Preview deployments matching `*-jb-s-projects14.vercel.app` are already whitelisted via `allow_origin_regex`.

---

## Enabling the LLM (optional)

By default `USE_LLM=false` — the backend generates deterministic rule-based explanations. To enable Qwen 3 AI explanations:

1. Run [Ollama](https://ollama.ai) on a server reachable by Render:
   ```bash
   ollama pull qwen3
   ```

2. Set on Render:
   ```
   USE_LLM=true
   OLLAMA_BASE_URL=https://your-ollama-host
   OLLAMA_MODEL=qwen3
   ```

3. Redeploy.

---

## Health monitoring

`GET /api/v1/health` returns:
```json
{"status": "ok", "version": "0.1.0", "db": true, "redis": true}
```

`status` becomes `"degraded"` (not `"error"`) if DB or Redis is unreachable — scans still work with rule-based analysis.

Set up a free uptime monitor at [UptimeRobot](https://uptimerobot.com) pointing at this endpoint.
