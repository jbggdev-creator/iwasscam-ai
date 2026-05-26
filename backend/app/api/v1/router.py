from fastapi import APIRouter
from app.api.v1 import health, scan

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(scan.router)
