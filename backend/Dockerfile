# Stage 1: install Python dependencies
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /build
COPY pyproject.toml uv.lock ./
COPY app/ ./app/
RUN uv pip install --system --no-cache .

# Stage 2: minimal runtime image
FROM python:3.11-slim AS runtime

# System deps: tesseract (OCR) + libzbar (QR) + ca-certificates (SSL to Supabase)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libzbar0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY start.sh .

RUN chmod +x start.sh

# Pre-download fastembed model so it's baked into the image (no runtime download needed)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

RUN useradd --no-create-home --shell /bin/false appuser
# Give appuser read access to the cached model files
RUN chown -R appuser /root/.cache/fastembed 2>/dev/null || true

USER appuser

EXPOSE 8000

CMD ["./start.sh"]
