# IwasScam AI — Product Requirements & Technical Architecture

## Overview

IwasScam AI is a production-grade AI-powered scam detection and trust verification web platform designed specifically for the Philippine market.

The platform allows users to:
- upload screenshots
- paste suspicious URLs
- describe scam scenarios
- upload voice recordings
- analyze QR codes
- inspect phishing attempts
- verify online sellers

The system uses multimodal AI, retrieval-augmented generation (RAG), cybersecurity intelligence, and explainable risk scoring to help users determine whether content is suspicious, fraudulent, or malicious.

---

# Primary Product Goal

Create a secure, scalable, explainable AI platform that helps Filipinos avoid scams while demonstrating production-grade AI engineering and cybersecurity architecture.

---

# Product Philosophy

## Priorities

1. Explainability over black-box AI
2. Security-first architecture
3. Grounded responses over hallucinations
4. Fast and reliable UX
5. Minimal attack surface
6. Production-ready AI systems
7. Real-world practical utility

---

# Phase 1 Scope (MVP)

## Supported Inputs

### 1. URL Analysis
Users can paste:
- phishing URLs
- suspicious domains
- fake login pages
- scam product links
- fake job sites

### 2. Screenshot Upload
Users can upload:
- GCash receipts
- Messenger screenshots
- Facebook Marketplace chats
- phishing emails
- suspicious conversations

### 3. Freeform Scenario Input
Example:

"A recruiter asked me to pay ₱500 for onboarding before the interview."

### 4. QR Code Upload
Analyze QR code destinations.

---

# NOT Included In Phase 1

The following features are intentionally disabled during MVP:

- community reporting system
- public comments
- social feeds
- browser extension
- voice analysis
- account-to-account messaging
- public profile system
- crypto wallet integrations
- AI memory personalization
- user-generated public content
- automated external crawling

Reason:
Reduce attack surface and simplify infrastructure.

---

# Core MVP Features

## 1. Scam Risk Analysis

Outputs:
- scam probability
- confidence score
- identified risk patterns
- explanation
- safety recommendation

---

## 2. Explainable AI

The AI must explain WHY something is suspicious.

Example:

- Newly registered domain
- Uses urgency manipulation
- Suspicious payment request
- Fake receipt inconsistencies
- Domain impersonation detected

---

## 3. URL Intelligence

Checks:
- WHOIS age
- suspicious TLDs
- redirects
- SSL validity
- phishing databases
- domain reputation

---

## 4. Screenshot Intelligence

Processes:
- OCR extraction
- phishing detection
- fake receipt analysis
- suspicious language detection

---

## 5. RAG Knowledge Base

The AI retrieves grounded context from:
- BSP advisories
- SEC warnings
- DICT alerts
- phishing datasets
- curated scam reports

---

# Recommended Technology Stack

This stack is optimized for:
- AI engineering portfolios
- production deployment
- scalability
- cybersecurity hardening
- solo developer maintainability

---

# Frontend Stack

## Framework

### Next.js 15

Reason:
- production-ready
- excellent SSR support
- secure routing
- scalable architecture
- edge support
- modern React ecosystem

---

## Styling

### TailwindCSS

### shadcn/ui

Reason:
- accessible components
- clean UI system
- customizable
- lightweight

---

## Frontend Validation

### Zod

Reason:
- runtime validation
- schema safety
- API validation

---

## File Uploads

### UploadThing
OR
### Supabase Storage

Reason:
- signed uploads
- file restrictions
- secure storage

---

# Backend Stack

## Primary API Framework

### FastAPI

Reason:
- excellent for AI systems
- async support
- Python ecosystem
- type safety
- scalable
- ideal for LangGraph

---

## AI Workflow Orchestration

### LangGraph

Reason:
- stateful workflows
- retries
- agent orchestration
- branching logic
- production AI workflows

This is the MOST relevant stack for 2026 AI engineering.

---

## AI Framework

### LangChain

Used for:
- tool calling
- retrieval pipelines
- prompt templates
- RAG integration

---

# AI Models

## Primary LLM

### Qwen 3

Reason:
- strong multilingual capability
- good English + Filipino handling
- efficient inference
- cost-effective
- strong reasoning

---

## Vision Model

### Qwen2.5-VL

Used for:
- screenshot analysis
- fake receipt analysis
- phishing screenshot understanding

---

## OCR Engine

### PaddleOCR

Reason:
- excellent OCR quality
- lightweight
- open-source
- strong screenshot extraction

---

## Embedding Model

### BAAI/bge-small-en-v1.5

Reason:
- fast
- efficient
- strong retrieval quality

---

# Database Stack

## Primary Database

### PostgreSQL 16

Reason:
- battle-tested
- relational consistency
- secure
- scalable
- supports pgvector

---

## Vector Database

### pgvector

Reason:
- integrated into Postgres
- simpler infra
- sufficient for MVP
- lower operational complexity

Do NOT use Pinecone initially.

Reason:
- unnecessary cost
- unnecessary complexity
- pgvector is enough for Phase 1

---

# Queue & Async Jobs

## Redis

Used for:
- caching
- queues
- rate limiting
- async processing

---

## Celery

Used for:
- OCR jobs
- URL scans
- background analysis
- retry handling

---

# Authentication

## Better Auth

Reason:
- modern
- secure
- self-hostable
- TypeScript-first
- avoids vendor lock-in

---

# Deployment

## Frontend

### Vercel

Reason:
- optimized for Next.js
- edge support
- easy CI/CD

---

## Backend

### Railway

Reason:
- simpler deployment
- ideal for MVP
- easy scaling
- lower ops burden

Alternative:
- Fly.io

---

# Monitoring & Observability

## LangSmith

Track:
- prompt traces
- hallucinations
- retrieval quality
- agent execution

---

## OpenTelemetry

Track:
- latency
- failures
- performance
- distributed tracing

---

## Sentry

Track:
- frontend crashes
- backend exceptions
- API failures

---

# Security Architecture

SECURITY IS A FIRST-CLASS REQUIREMENT.

---

# Core Security Principles

1. Zero trust architecture
2. Minimal attack surface
3. Strict validation everywhere
4. No unnecessary features
5. Least privilege access
6. Secure-by-default design

---

# Authentication Security

## Required

- httpOnly cookies
- CSRF protection
- secure session handling
- short session lifetimes
- device/session invalidation

---

# API Security

## Required

### Rate Limiting

Per:
- IP
- account
- endpoint

Use:
- Redis-based rate limiting

---

## Input Validation

ALL inputs validated using:
- Zod
- Pydantic

Never trust client input.

---

## Request Size Limits

Strict upload limits:
- image max size
- URL length limit
- payload restrictions

---

## Signed Upload URLs

Never expose raw storage buckets.

---

# File Upload Security

## REQUIRED

### MIME Type Validation

Reject:
- executables
- scripts
- archives
- unsupported formats

---

## Malware Scanning

Use:
- ClamAV

Before processing uploads.

---

## Image Re-Encoding

Re-encode uploaded images.

Reason:
Prevent payload injection inside image metadata.

---

## Sandbox Processing

All uploads processed in isolated containers.

---

# AI Security

## Prompt Injection Defense

Implement:
- instruction isolation
- retrieval sanitization
- system prompt separation
- content filtering

---

## Output Guardrails

Prevent:
- fabricated accusations
- unsupported claims
- hallucinated evidence

The AI must avoid:
- declaring someone definitively guilty
- making legal accusations

Instead use:
- risk probabilities
- suspicious indicators
- cautionary language

---

## RAG Grounding

All high-risk outputs must reference retrieved evidence.

---

# URL Security

## SSRF Protection

NEVER allow:
- internal IP requests
- localhost requests
- cloud metadata access

Block:
- 127.0.0.1
- localhost
- private IP ranges
- AWS metadata endpoints

---

## Safe URL Fetching

Use:
- sandbox fetch workers
- timeouts
- redirect limits

---

# Infrastructure Security

## Secrets Management

Use:
- Doppler
OR
- Railway encrypted variables

Never hardcode secrets.

---

## Docker Hardening

Required:
- non-root containers
- minimal images
- read-only filesystem where possible
- dependency pinning

---

## Database Security

Required:
- encrypted connections
- private networking
- role-based access
- restricted DB permissions

---

# Logging Policy

NEVER log:
- uploaded screenshots
- personal messages
- passwords
- tokens
- payment details

Sanitize logs.

---

# AI System Architecture

## High-Level Flow

```txt
User Input
    ↓
Input Validation Layer
    ↓
Input Router Agent
    ↓
Specialized AI Pipelines
    ↓
Risk Scoring Engine
    ↓
RAG Retrieval Layer
    ↓
Explanation Generator
    ↓
Frontend Response
```

---

# AI Agents

## 1. Input Router Agent

Detects:
- URL
- image
- QR code
- text
- mixed content

Routes request appropriately.

---

## 2. URL Intelligence Agent

Checks:
- phishing patterns
- domain age
- suspicious redirects
- blacklists
- URL entropy

---

## 3. Screenshot Analysis Agent

Processes:
- OCR extraction
- receipt analysis
- fake UI detection
- phishing screenshots

---

## 4. Social Engineering Agent

Detects:
- urgency
- fear manipulation
- impersonation
- fake authority
- emotional coercion

---

## 5. Risk Scoring Agent

Combines:
- AI outputs
- threat intelligence
- RAG retrieval
- heuristics

Produces:
- risk level
- confidence score

---

## 6. Explanation Agent

Produces user-friendly output.

Goal:
Explain findings clearly.

---

# Database Schema

## users

```sql
id UUID PRIMARY KEY
email TEXT UNIQUE
password_hash TEXT
created_at TIMESTAMP
plan_type TEXT
```

---

## scans

```sql
id UUID PRIMARY KEY
user_id UUID
input_type TEXT
risk_level TEXT
confidence_score FLOAT
created_at TIMESTAMP
```

---

## findings

```sql
id UUID PRIMARY KEY
scan_id UUID
finding_type TEXT
description TEXT
severity TEXT
```

---

## rag_documents

```sql
id UUID PRIMARY KEY
source TEXT
content TEXT
embedding VECTOR
metadata JSONB
```

---

# API Design

## POST /scan/url

Analyze suspicious URL.

---

## POST /scan/image

Analyze screenshot.

---

## POST /scan/text

Analyze scam scenario.

---

## POST /scan/qr

Analyze QR code.

---

## GET /scan/:id

Retrieve scan result.

---

# Evaluation Framework

Evaluation is REQUIRED.

This is not optional.

---

# Metrics

## Classification Metrics

- precision
- recall
- F1 score
- false positive rate

---

## AI Metrics

- hallucination rate
- grounding accuracy
- explanation quality
- retrieval precision

---

## Operational Metrics

- latency
- failure rate
- token cost
- queue duration

---

# Evaluation Tools

## DeepEval

Used for:
- hallucination checks
- answer quality
- regression testing

---

## Ragas

Used for:
- retrieval evaluation
- grounding checks

---

## LangSmith

Used for:
- traces
- debugging
- workflow visibility

---

# Frontend Pages

## Public Pages

- Landing Page
- Features
- Scam Education
- Pricing
- Privacy Policy
- Terms

---

## Dashboard Pages

- Scanner
- Scan History
- Saved Reports
- Settings
- Billing

---

# UI/UX Requirements

## UX Goals

- simple
- trustworthy
- non-technical
- mobile-first
- fast

---

## Design Direction

Should feel like:
- cybersecurity dashboard
- fintech trust platform
- modern SaaS

Avoid:
- crypto aesthetic
- hacker aesthetic
- meme UI

---

# Performance Requirements

## Target Response Time

- URL scan: under 5 seconds
- image analysis: under 10 seconds
- OCR extraction: under 8 seconds

---

# Scalability Plan

## MVP

Single-region deployment.

---

## Future

Potential upgrades:
- Kubernetes
- autoscaling workers
- GPU inference nodes
- dedicated vector clusters

Not needed initially.

---

# Development Roadmap

## Week 1

- project setup
- auth
- DB schema
- Next.js frontend
- FastAPI backend

---

## Week 2

- URL scanner
- OCR pipeline
- basic AI analysis

---

## Week 3

- RAG ingestion
- LangGraph workflows
- risk scoring

---

## Week 4

- security hardening
- eval harness
- observability
- deployment

---

# Success Criteria

MVP is successful when:

- users can upload screenshots and URLs
- AI identifies common scams
- explanations are understandable
- outputs are grounded in evidence
- platform remains secure and stable
- hallucinations are minimized

---

# Resume Positioning

This project demonstrates:

- AI engineering
- multimodal AI systems
- cybersecurity engineering
- trust & safety systems
- fraud detection
- RAG pipelines
- LLMOps
- observability
- AI evaluation
- secure backend engineering
- production AI workflows

---

# Final Engineering Philosophy

Build a trustworthy AI system.

Do NOT build:
- hype AI
- magic AI
- black-box AI

Build:
- explainable AI
- evidence-based AI
- secure AI
- useful AI
- production-grade AI

