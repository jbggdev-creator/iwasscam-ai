# IwasScam AI

AI-powered scam detection and trust verification platform built for the Philippine market.

Users can paste suspicious URLs, upload screenshots, describe scam scenarios, and analyze QR codes. The system responds with an explainable risk score, specific red flags, and concrete advice — in plain language any Filipino internet user can act on immediately.

**Live demo:** https://frontend-six-kappa-31.vercel.app  
**API health:** https://iwasscam-api.onrender.com/api/v1/health

---

## What it detects

| Input | Detection capabilities |
|-------|----------------------|
| **URL** | Homograph attacks (`faceb0ok.com` → impersonates `facebook`), brand impersonation via character substitution, domain age, SSL validity, suspicious TLDs, redirect chains, URL entropy |
| **Screenshot** | Fake GCash / Maya receipts, prize & lottery scams, credential phishing screens, social engineering language |
| **QR Code** | Decodes QR content and runs full URL + social engineering analysis on the destination |
| **Text / Scenario** | Urgency manipulation, fake authority, impersonation, advance-fee patterns, job scam scripts |

---

## Tech stack

### Frontend
- **Next.js 15** (App Router) — React 19, TypeScript
- **Tailwind CSS v4** + **Radix UI** — accessible component primitives
- **Better Auth** — self-hosted auth, email/password
- **Zod** — runtime input validation
- **Vitest** + Testing Library — component unit tests
- **Vercel** — hosting and CI/CD

### Backend
- **FastAPI** + **Uvicorn** — async Python API
- **LangGraph** — stateful AI workflow orchestration
- **LangChain** — LLM tooling, prompt templates, RAG retrieval
- **PaddleOCR / Tesseract** — screenshot text extraction
- **pyzbar** — QR code decoding
- **pgvector** — vector similarity search for RAG knowledge base
- **Celery** + **Redis** — async job queue for heavy scans
- **Alembic** — database migrations
- **Sentry** — error tracking
- **Render** — Docker hosting

### Database
- **PostgreSQL 16** via Supabase — scans, findings, RAG documents
- **Redis** via Upstash — caching, rate limiting, Celery broker

---

## Project structure

```
iwasscam-ai/
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── (public)/           # Landing, features, pricing, education
│   │   ├── (auth)/             # Login and register
│   │   ├── (dashboard)/        # Scanner, history, settings
│   │   └── api/auth/           # Better Auth catch-all route
│   ├── components/
│   │   ├── scanner/            # Scan forms and result display
│   │   ├── shared/             # Nav, layout components
│   │   └── ui/                 # Radix-based UI primitives
│   ├── lib/                    # Auth client, API client, validators
│   └── middleware.ts           # Edge middleware
│
└── backend/                    # FastAPI application
    ├── app/
    │   ├── agents/             # LangGraph AI pipelines
    │   │   ├── url_agent.py        — URL risk scoring + brand impersonation
    │   │   ├── image_agent.py      — OCR + receipt/prize/phishing detection
    │   │   ├── qr_agent.py         — QR decode + URL analysis
    │   │   ├── text_agent.py       — Scenario analysis
    │   │   ├── social_engineering_agent.py
    │   │   └── prompts.py          — LLM system prompts
    │   ├── services/           # URL intelligence, OCR, QR, RAG, ClamAV
    │   ├── api/v1/             # FastAPI routers
    │   ├── db/                 # Models, migrations, repositories
    │   ├── core/               # Config, rate limiting, logging, guardrails
    │   ├── middleware/         # Request ID, size limits, security headers
    │   └── workers/            # Celery async tasks
    ├── eval/                   # DeepEval + Ragas evaluation harness
    ├── tests/                  # pytest suite (80% coverage enforced)
    ├── Dockerfile
    ├── start.sh                # Entrypoint: migrations → uvicorn
    └── render.yaml             # Render Blueprint
```

---

## Local development

### Prerequisites

- Node.js 20+
- Python 3.11+
- Docker (for local Postgres + Redis)
- Tesseract OCR — `brew install tesseract` (macOS) or `apt install tesseract-ocr` (Linux)

### Backend

```bash
cd backend

# Start Postgres and Redis locally
docker-compose up -d

# Create virtualenv and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Copy env template and fill in values
cp .env.example .env

# Run migrations
alembic upgrade head

# Start dev server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

npm install

# Copy env template and fill in values
cp .env.example .env.local

npm run dev
```

App available at `http://localhost:3000`

---

## Environment variables

### Backend (`.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | Random secret for session signing | `openssl rand -hex 32` |
| `FRONTEND_URL` | Allowed CORS origin(s), comma-separated | `https://yourapp.vercel.app` |
| `ENVIRONMENT` | `development` or `production` | `production` |
| `DEBUG` | Enable SQLAlchemy query logging | `false` |
| `USE_LLM` | Enable Ollama LLM for richer explanations | `false` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Qwen model name | `qwen3` |
| `CLAMAV_ENABLED` | Enable ClamAV malware scanning on uploads | `false` |
| `SENTRY_DSN` | Sentry DSN for error tracking (optional) | — |

### Frontend (`.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL |
| `NEXT_PUBLIC_APP_URL` | Frontend canonical URL |
| `BETTER_AUTH_SECRET` | Secret for Better Auth session signing |
| `BETTER_AUTH_URL` | Better Auth base URL (same as `NEXT_PUBLIC_APP_URL`) |
| `DATABASE_URL` | PostgreSQL URL for Better Auth session storage |

---

## API reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/scan/url` | Optional | Analyze a suspicious URL |
| `POST` | `/api/v1/scan/image` | Optional | Analyze a screenshot (multipart) |
| `POST` | `/api/v1/scan/text` | Optional | Analyze a text scenario |
| `POST` | `/api/v1/scan/qr` | Optional | Analyze a QR code image (multipart) |
| `GET` | `/api/v1/scan` | Required | List your past scans |
| `GET` | `/api/v1/scan/{id}` | Optional | Get a single scan result |
| `GET` | `/api/v1/health` | None | Service health check |

### Example — URL scan

```bash
curl -X POST https://iwasscam-api.onrender.com/api/v1/scan/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.faceb0ok.com/"}'
```

```json
{
  "id": "uuid",
  "input_type": "url",
  "risk_level": "critical",
  "confidence_score": 0.95,
  "explanation": "WARNING: This URL is impersonating facebook by substituting '0' for 'o'. This is a phishing site — do NOT visit it.",
  "findings": [
    {
      "finding_type": "brand_impersonation",
      "description": "This domain impersonates 'facebook' using character substitution.",
      "severity": "critical"
    }
  ]
}
```

---

## AI pipeline

Each scan type runs a dedicated **LangGraph** state machine:

```
User Input
    ↓
Input Validation (Zod / Pydantic)
    ↓
Appropriate LangGraph Agent
    ├── URL Agent:   WHOIS → SSL → redirects → entropy → homograph check → score → explain
    ├── Image Agent: OCR → prize/receipt/phishing signals → social engineering → score → explain
    ├── QR Agent:    decode → URL/text analysis → score → explain
    └── Text Agent:  social engineering signals → RAG retrieval → score → explain
    ↓
Risk Score (0–100) → Level (low / medium / high / critical)
    ↓
RAG retrieval from Philippine fraud knowledge base
    ↓
LLM explanation (Qwen 3 via Ollama, with rule-based fallback)
    ↓
Response to frontend
```

The scoring engine is **deterministic and rules-based first** — the LLM only writes the human-readable explanation. This prevents hallucination from affecting risk levels.

---

## Access model

| Route | Without account | With account |
|-------|----------------|--------------|
| `/scanner` | Free scans, no login needed | Same + scans saved to history |
| `/history` | Locked overlay with Sign In prompt | Your personal scan history |
| `/settings` | Locked overlay with Sign In prompt | Account management |

---

## Security highlights

- Uploaded images are re-encoded to strip metadata before processing
- SSRF protection blocks requests to internal IPs and cloud metadata endpoints
- Rate limiting on all scan endpoints (per-IP via SlowAPI + Redis)
- Request size limits at middleware level
- No uploaded content is logged — only scan metadata
- Security headers middleware (HSTS, X-Frame-Options, CSP)
- ClamAV malware scanning on uploads (configurable)
- Better Auth uses httpOnly cookies + CSRF protection

---

## Running tests

### Backend
```bash
cd backend
pytest                               # all tests + coverage report
pytest tests/agents/                 # agent tests only
pytest --cov=app --cov-report=html   # HTML coverage report
```

Coverage threshold is enforced at **80%** — the build fails below this.

### Frontend
```bash
cd frontend
npm test                  # run all tests
npm run test:coverage     # with coverage report
```

---

## License

MIT
