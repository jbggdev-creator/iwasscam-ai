import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
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
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    db_ok = await _ping_db(db)
    redis_ok = await _ping_redis(settings.redis_url)
    healthy = db_ok and redis_ok
    response = HealthResponse(
        status="ok" if healthy else "degraded",
        version=settings.app_version,
        db=db_ok,
        redis=redis_ok,
    )
    if not healthy:
        return JSONResponse(status_code=503, content=response.model_dump())
    return response
