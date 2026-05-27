# Architecture

## Overview

IwasScam AI is a full-stack web application with a stateless Next.js frontend and a Python AI backend. The backend runs stateful LangGraph pipelines for each scan type, backed by PostgreSQL for persistence and Redis for caching and async jobs.

```
┌─────────────────────────────────────────┐
│           Next.js Frontend               │
│  Vercel Edge Network (Singapore)         │
│                                          │
│  (public)   /scanner  /history           │
│  /login     /register /settings          │
│         │                                │
│  Better Auth (httpOnly cookies)          │
└────────────────┬─────────────────────────┘
                 │ HTTPS + CORS
┌────────────────▼─────────────────────────┐
│         FastAPI Backend                   │
│  Render Docker (Singapore)                │
│                                           │
│  Rate limiting → Request size guard       │
│  Security headers → Request ID            │
│                                           │
│  /scan/url  /scan/image                   │
│  /scan/text /scan/qr   /health            │
│          │                                │
│  LangGraph AI Pipelines                   │
│  UrlAgent  ImageAgent  QrAgent            │
│  TextAgent SocialEngineeringAgent         │
│          │                                │
│  Services: URL Intel, OCR, QR,            │
│  RAG, Embeddings, ClamAV, SafeFetch       │
└────────────────┬─────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────────┐  ┌───────▼──────────┐
│  PostgreSQL 16    │  │  Redis (Upstash) │
│  (Supabase)       │  │                  │
│                   │  │  Rate limiting   │
│  scans            │  │  Celery broker   │
│  findings         │  │  Result cache    │
│  rag_documents    │  └──────────────────┘
│  auth sessions    │
└───────────────────┘
```

---

## Design principle

The **risk score is always computed by deterministic rules**, not the LLM. The LLM only writes the human-readable explanation. This means:

- Risk levels cannot be hallucinated upward or downward
- Explanations are grounded in the specific signals that triggered the score
- If Ollama is unavailable the system generates a rule-based explanation instead — no silent failures

---

## URL Agent

```
extract_features → score_risk → generate_explanation
```

**extract_features** (`url_intelligence.py`)
- WHOIS lookup for domain age
- SSL check via HTTPS connect attempt
- HTTP redirect chain (max 5 hops)
- Shannon entropy on full URL string
- TLD lookup against suspicious-TLD set
- **Homograph detection**: normalises `0→o`, `1→l`, `3→e`, `rn→m`, `vv→w`, etc., then checks Levenshtein distance ≤ 1 against 30+ known brand domains

**Score table**

| Signal | Points |
|--------|--------|
| Brand impersonation (homograph) | +60 |
| Domain < 7 days old | +40 |
| No valid SSL | +25 |
| Domain < 30 days old | +25 |
| Suspicious TLD | +20 |
| URL entropy > 4.5 | +15 |
| Domain < 90 days old | +10 |
| Excessive redirects | +10 |
| WHOIS unavailable | +5 |

Thresholds: `≥80 = critical` · `≥60 = high` · `≥30 = medium` · `<30 = low`

---

## Image Agent

```
extract_content → detect_signals → score_risk → generate_explanation
```

**extract_content** — Tesseract OCR on the uploaded image. The image is re-encoded by `ImageSanitizer` first to strip EXIF metadata.

**Signal scoring**

| Signal | Trigger | Points |
|--------|---------|--------|
| Prize / lottery scam | "you won", "claim your", "iphone 17", "scan to claim", "lucky winner", etc. | +50 |
| Credential phishing | "password", "enter your pin", "verify account" | +35 |
| Fake GCash receipt | Brand name + any 2 of: (₱/PHP marker, reference keyword, sent/successful status) | +35 |
| Social engineering | Weighted keyword matching across 6 categories | variable |
| RAG match | Each matching knowledge base document | +10 (max +20) |

---

## Social Engineering Agent

Shared by Text and Image agents. Weighted pattern matching across six categories:

| Category | Example patterns |
|----------|-----------------|
| Urgency | "act now", "expires today", "last chance" |
| Fear / threat | "account suspended", "arrest warrant" |
| Fake authority | "NBI", "BIR", "BSP advisory", "official notice" |
| Impersonation | "GCash support", "Lazada seller", "BDO bank" |
| Payment pressure | "send ₱500 first", "GCash only", "no receipt needed" |
| Too good to be true | "you won", "free iPhone", "₱50,000 reward" |

---

## QR Agent

```
decode_qr → analyze_content → score_risk → generate_explanation
```

Decodes QR with `pyzbar`. If the content is a URL, runs it through the full URL intelligence pipeline. If it is plain text, runs social engineering analysis.

---

## Database schema

```sql
CREATE TABLE scans (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID,                    -- NULL for anonymous scans
    input_type       TEXT NOT NULL,           -- url | image | text | qr
    risk_level       TEXT NOT NULL,           -- low | medium | high | critical
    confidence_score FLOAT NOT NULL,
    explanation      TEXT NOT NULL,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE findings (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id      UUID REFERENCES scans(id) ON DELETE CASCADE,
    finding_type TEXT NOT NULL,
    description  TEXT NOT NULL,
    severity     TEXT NOT NULL               -- low | medium | high | critical
);

CREATE TABLE rag_documents (
    id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source    TEXT NOT NULL,                 -- e.g. "BSP Advisory 2024-01"
    content   TEXT NOT NULL,
    embedding VECTOR(384),                   -- BAAI/bge-small-en-v1.5
    metadata  JSONB DEFAULT '{}'
);
CREATE INDEX ON rag_documents USING ivfflat (embedding vector_cosine_ops);
```

---

## Security architecture

### SSRF protection (`safe_fetch.py`)
All outbound HTTP requests are gated through `safe_fetch.py`, which:
- Resolves the destination IP before connecting
- Blocks `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.0.0/16`
- Blocks the AWS EC2 metadata endpoint (`169.254.169.254`)
- Enforces 5-second timeout and max 5 redirects

### Image safety (`image_sanitizer.py`)
All uploaded images are:
1. Re-encoded with Pillow to strip EXIF / XMP metadata
2. Optionally scanned by ClamAV before OCR
3. Never persisted to disk — processed entirely in memory

### Rate limiting
SlowAPI + Redis enforces per-IP limits on all `/scan/*` endpoints.

### Security headers
Every response includes `Strict-Transport-Security`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and a restrictive `Content-Security-Policy`.

---

## Observability

- **Sentry** — exception tracking with FastAPI integration
- **OpenTelemetry** — distributed tracing (configure via `OTEL_*` env vars)
- **LangSmith** — LangGraph trace capture for prompt debugging
- **Structured JSON logging** — every request logs `request_id`, `method`, `path`, `status`, `duration_ms`

---

## Scalability notes

The architecture is horizontally scalable without code changes:
- API servers are stateless — all state lives in Postgres and Redis
- Heavy jobs (large images, slow WHOIS) can be offloaded to Celery workers
- pgvector IVFFlat index scales to millions of RAG documents
- Upgrading Render free → paid tier enables autoscaling with zero config changes
