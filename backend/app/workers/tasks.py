import asyncio
import base64
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)

_RETRY_KWARGS = {"max_retries": 3, "default_retry_delay": 10}


async def _run_url_scan(url: str) -> dict:
    from app.agents.url_agent import url_graph
    from app.core.guardrails import sanitize_explanation
    from app.db.repositories.scan_repo import scan_repo
    from app.db.session import async_session_factory
    from app.schemas.scan import InputType

    state = await url_graph.ainvoke(
        {
            "url": url,
            "features": None,
            "risk_score": 0,
            "risk_level": "low",
            "confidence": 0.5,
            "findings": [],
            "explanation": "",
        }
    )
    explanation = sanitize_explanation(state["explanation"])

    async with async_session_factory() as db:
        scan = await scan_repo.create(
            db,
            input_type=InputType.url,
            risk_level=state["risk_level"],
            confidence_score=state["confidence"],
            explanation=explanation,
        )
        for raw in state["findings"]:
            await scan_repo.add_finding(
                db,
                scan_id=scan.id,
                finding_type=raw["finding_type"],
                description=raw["description"],
                severity=raw["severity"],
            )
        await db.commit()

    return {"scan_id": str(scan.id), "risk_level": state["risk_level"]}


async def _run_text_scan(scenario: str) -> dict:
    from app.agents.text_agent import text_graph
    from app.core.guardrails import sanitize_explanation
    from app.db.repositories.scan_repo import scan_repo
    from app.db.session import async_session_factory
    from app.schemas.scan import InputType
    from app.services.rag_service import rag_service

    async with async_session_factory() as db:
        try:
            rag_context = await rag_service.retrieve(db, scenario)
        except Exception:
            rag_context = []

        state = await text_graph.ainvoke(
            {
                "scenario": scenario,
                "rag_context": rag_context,
                "se_signals": [],
                "se_score": 0,
                "se_confidence": 0.5,
                "risk_score": 0,
                "risk_level": "low",
                "confidence": 0.5,
                "findings": [],
                "explanation": "",
            }
        )
        explanation = sanitize_explanation(state["explanation"])

        scan = await scan_repo.create(
            db,
            input_type=InputType.text,
            risk_level=state["risk_level"],
            confidence_score=state["confidence"],
            explanation=explanation,
        )
        for raw in state["findings"]:
            await scan_repo.add_finding(
                db,
                scan_id=scan.id,
                finding_type=raw["finding_type"],
                description=raw["description"],
                severity=raw["severity"],
            )
        await db.commit()

    return {"scan_id": str(scan.id), "risk_level": state["risk_level"]}


async def _run_image_scan(image_b64: str) -> dict:
    from app.agents.image_agent import image_graph
    from app.core.guardrails import sanitize_explanation
    from app.db.repositories.scan_repo import scan_repo
    from app.db.session import async_session_factory
    from app.schemas.scan import InputType
    from app.services.image_sanitizer import sanitize_image

    image_bytes = sanitize_image(base64.b64decode(image_b64))

    async with async_session_factory() as db:
        try:
            from app.services.rag_service import rag_service
            rag_context = await rag_service.retrieve(db, "screenshot image analysis suspicious")
        except Exception:
            rag_context = []

        state = await image_graph.ainvoke(
            {
                "image_bytes": image_bytes,
                "extracted_text": "",
                "rag_context": rag_context,
                "se_signals": [],
                "se_score": 0,
                "risk_score": 0,
                "risk_level": "low",
                "confidence": 0.5,
                "findings": [],
                "explanation": "",
            }
        )
        explanation = sanitize_explanation(state["explanation"])

        scan = await scan_repo.create(
            db,
            input_type=InputType.image,
            risk_level=state["risk_level"],
            confidence_score=state["confidence"],
            explanation=explanation,
        )
        for raw in state["findings"]:
            await scan_repo.add_finding(
                db,
                scan_id=scan.id,
                finding_type=raw["finding_type"],
                description=raw["description"],
                severity=raw["severity"],
            )
        await db.commit()

    return {"scan_id": str(scan.id), "risk_level": state["risk_level"]}


async def _run_qr_scan(image_b64: str) -> dict:
    from app.agents.qr_agent import qr_graph
    from app.core.guardrails import sanitize_explanation
    from app.db.repositories.scan_repo import scan_repo
    from app.db.session import async_session_factory
    from app.schemas.scan import InputType
    from app.services.image_sanitizer import sanitize_image

    image_bytes = sanitize_image(base64.b64decode(image_b64))

    async with async_session_factory() as db:
        state = await qr_graph.ainvoke(
            {
                "image_bytes": image_bytes,
                "decoded_content": "",
                "content_type": "unreadable",
                "risk_score": 0,
                "risk_level": "low",
                "confidence": 0.5,
                "findings": [],
                "explanation": "",
            }
        )
        explanation = sanitize_explanation(state["explanation"])

        scan = await scan_repo.create(
            db,
            input_type=InputType.qr,
            risk_level=state["risk_level"],
            confidence_score=state["confidence"],
            explanation=explanation,
        )
        for raw in state["findings"]:
            await scan_repo.add_finding(
                db,
                scan_id=scan.id,
                finding_type=raw["finding_type"],
                description=raw["description"],
                severity=raw["severity"],
            )
        await db.commit()

    return {"scan_id": str(scan.id), "risk_level": state["risk_level"]}


@celery_app.task(bind=True, **_RETRY_KWARGS, name="app.workers.tasks.scan_url_task")
def scan_url_task(self, url: str) -> dict:
    try:
        return asyncio.run(_run_url_scan(url))
    except Exception as exc:
        logger.error("scan_url_task failed for %s: %s", url, exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, **_RETRY_KWARGS, name="app.workers.tasks.scan_text_task")
def scan_text_task(self, scenario: str) -> dict:
    try:
        return asyncio.run(_run_text_scan(scenario))
    except Exception as exc:
        logger.error("scan_text_task failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, **_RETRY_KWARGS, name="app.workers.tasks.scan_image_task")
def scan_image_task(self, image_b64: str) -> dict:
    """Accepts base64-encoded image bytes."""
    try:
        return asyncio.run(_run_image_scan(image_b64))
    except Exception as exc:
        logger.error("scan_image_task failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, **_RETRY_KWARGS, name="app.workers.tasks.scan_qr_task")
def scan_qr_task(self, image_b64: str) -> dict:
    """Accepts base64-encoded image bytes."""
    try:
        return asyncio.run(_run_qr_scan(image_b64))
    except Exception as exc:
        logger.error("scan_qr_task failed: %s", exc, exc_info=True)
        raise self.retry(exc=exc)
