from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_scan_async(self, scan_id: str) -> dict:
    """Placeholder for async scan processing via LangGraph."""
    raise NotImplementedError("Async scan processing not yet implemented")
