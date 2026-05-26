from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "iwasscam",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "app.workers.tasks.scan_image_task": {"queue": "heavy"},
        "app.workers.tasks.scan_qr_task": {"queue": "heavy"},
        "app.workers.tasks.scan_url_task": {"queue": "default"},
        "app.workers.tasks.scan_text_task": {"queue": "default"},
    },
)
