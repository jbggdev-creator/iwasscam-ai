import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.schemas.scan import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


async def _ping_db(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("DB health check failed: %s", exc)
        return False


async def _ping_redis(redis_url: str) -> bool:
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(redis_url)
        await r.ping()
        await r.aclose()
        return True
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    settings = get_settings()
    db_ok = await _ping_db(db)
    redis_ok = await _ping_redis(settings.redis_url)

    if not (db_ok and redis_ok):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="ok" if (db_ok and redis_ok) else "degraded",
        version=settings.app_version,
        db=db_ok,
        redis=redis_ok,
    )
