#!/bin/sh
echo "[start] Python import check..."
python3 -c "from app.main import app; print('[start] Import OK')" 2>&1 || echo "[start] Import FAILED — uvicorn will show the real error"
echo "[start] Running Alembic migrations..."
if alembic upgrade head; then
    echo "[start] Migrations OK."
else
    echo "[start] WARNING: Alembic migration failed (exit $?). Starting server anyway."
fi
echo "[start] Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2
