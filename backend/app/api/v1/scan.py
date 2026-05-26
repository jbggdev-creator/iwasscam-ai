import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.text_agent import text_graph
from app.agents.url_agent import url_graph
from app.api.deps import get_db
from app.core.guardrails import sanitize_explanation
from app.core.limiter import limiter
from app.db.repositories.scan_repo import scan_repo
from app.schemas.scan import (
    FindingResponse,
    InputType,
    RiskLevel,
    ScanListResponse,
    ScanResponse,
    TextScanRequest,
    UrlScanRequest,
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan", tags=["scan"])

_INITIAL_URL_STATE = {
    "features": None,
    "risk_score": 0,
    "risk_level": "low",
    "confidence": 0.5,
    "findings": [],
    "explanation": "",
}

_INITIAL_TEXT_STATE = {
    "rag_context": [],
    "se_signals": [],
    "se_score": 0,
    "se_confidence": 0.5,
    "risk_score": 0,
    "risk_level": "low",
    "confidence": 0.5,
    "findings": [],
    "explanation": "",
}


@router.post("/url", response_model=ScanResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def scan_url(
    request: Request,
    body: UrlScanRequest,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    url_str = str(body.url)

    try:
        state = await url_graph.ainvoke({**_INITIAL_URL_STATE, "url": url_str})
    except Exception as exc:
        logger.error("URL agent failed for %s: %s", url_str, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again.",
        )

    explanation = sanitize_explanation(state["explanation"])
    scan = await scan_repo.create(
        db,
        input_type=InputType.url,
        risk_level=state["risk_level"],
        confidence_score=state["confidence"],
        explanation=explanation,
    )

    persisted_findings = []
    for raw in state["findings"]:
        finding = await scan_repo.add_finding(
            db,
            scan_id=scan.id,
            finding_type=raw["finding_type"],
            description=raw["description"],
            severity=raw["severity"],
        )
        persisted_findings.append(finding)

    await db.commit()

    return ScanResponse(
        id=scan.id,
        input_type=InputType.url,
        risk_level=RiskLevel(state["risk_level"]),
        confidence_score=state["confidence"],
        explanation=explanation,
        findings=[
            FindingResponse(
                id=f.id,
                finding_type=f.finding_type,
                description=f.description,
                severity=RiskLevel(f.severity),
            )
            for f in persisted_findings
        ],
        created_at=scan.created_at,
    )


@router.get("", response_model=ScanListResponse)
async def list_scans(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> ScanListResponse:
    if limit > 100:
        limit = 100
    offset = (page - 1) * limit
    scans = await scan_repo.list_recent(db, limit=limit, offset=offset)
    return ScanListResponse(
        scans=[
            ScanResponse(
                id=s.id,
                input_type=InputType(s.input_type),
                risk_level=RiskLevel(s.risk_level),
                confidence_score=s.confidence_score,
                explanation=s.explanation,
                findings=[
                    FindingResponse(
                        id=f.id,
                        finding_type=f.finding_type,
                        description=f.description,
                        severity=RiskLevel(f.severity),
                    )
                    for f in s.findings
                ],
                created_at=s.created_at,
            )
            for s in scans
        ],
        page=page,
        limit=limit,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    scan = await scan_repo.get_by_id(db, scan_id)
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    return ScanResponse(
        id=scan.id,
        input_type=InputType(scan.input_type),
        risk_level=RiskLevel(scan.risk_level),
        confidence_score=scan.confidence_score,
        explanation=scan.explanation,
        findings=[
            FindingResponse(
                id=f.id,
                finding_type=f.finding_type,
                description=f.description,
                severity=RiskLevel(f.severity),
            )
            for f in scan.findings
        ],
        created_at=scan.created_at,
    )


@router.post("/image", response_model=ScanResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def scan_image(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are accepted",
        )

    from app.core.config import get_settings
    settings = get_settings()
    image_bytes = await file.read()
    if len(image_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

    from app.services import clamav_service
    from app.services.image_sanitizer import ImageSanitizationError, sanitize_image

    await clamav_service.scan_bytes(image_bytes)

    try:
        image_bytes = sanitize_image(image_bytes)
    except ImageSanitizationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    try:
        rag_context = await rag_service.retrieve(db, "screenshot image analysis suspicious")
    except Exception:
        rag_context = []

    from app.agents.image_agent import image_graph

    initial_state = {
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

    try:
        state = await image_graph.ainvoke(initial_state)
    except Exception as exc:
        logger.error("Image agent failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again.",
        )

    explanation = sanitize_explanation(state["explanation"])
    scan = await scan_repo.create(
        db,
        input_type=InputType.image,
        risk_level=state["risk_level"],
        confidence_score=state["confidence"],
        explanation=explanation,
    )

    persisted_findings = []
    for raw in state["findings"]:
        finding = await scan_repo.add_finding(
            db,
            scan_id=scan.id,
            finding_type=raw["finding_type"],
            description=raw["description"],
            severity=raw["severity"],
        )
        persisted_findings.append(finding)

    await db.commit()

    return ScanResponse(
        id=scan.id,
        input_type=InputType.image,
        risk_level=RiskLevel(state["risk_level"]),
        confidence_score=state["confidence"],
        explanation=explanation,
        findings=[
            FindingResponse(
                id=f.id,
                finding_type=f.finding_type,
                description=f.description,
                severity=RiskLevel(f.severity),
            )
            for f in persisted_findings
        ],
        created_at=scan.created_at,
    )


@router.post("/text", response_model=ScanResponse, status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def scan_text(
    request: Request,
    body: TextScanRequest,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    try:
        rag_context = await rag_service.retrieve(db, body.scenario)
    except Exception as exc:
        logger.warning("RAG retrieval failed, continuing without context: %s", exc)
        rag_context = []

    try:
        state = await text_graph.ainvoke(
            {**_INITIAL_TEXT_STATE, "scenario": body.scenario, "rag_context": rag_context}
        )
    except Exception as exc:
        logger.error("Text agent failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again.",
        )

    explanation = sanitize_explanation(state["explanation"])
    scan = await scan_repo.create(
        db,
        input_type=InputType.text,
        risk_level=state["risk_level"],
        confidence_score=state["confidence"],
        explanation=explanation,
    )

    persisted_findings = []
    for raw in state["findings"]:
        finding = await scan_repo.add_finding(
            db,
            scan_id=scan.id,
            finding_type=raw["finding_type"],
            description=raw["description"],
            severity=raw["severity"],
        )
        persisted_findings.append(finding)

    await db.commit()

    return ScanResponse(
        id=scan.id,
        input_type=InputType.text,
        risk_level=RiskLevel(state["risk_level"]),
        confidence_score=state["confidence"],
        explanation=explanation,
        findings=[
            FindingResponse(
                id=f.id,
                finding_type=f.finding_type,
                description=f.description,
                severity=RiskLevel(f.severity),
            )
            for f in persisted_findings
        ],
        created_at=scan.created_at,
    )


@router.post("/qr", response_model=ScanResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def scan_qr(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, and WebP images are accepted",
        )

    from app.core.config import get_settings
    settings = get_settings()
    image_bytes = await file.read()
    if len(image_bytes) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

    from app.services import clamav_service
    from app.services.image_sanitizer import ImageSanitizationError, sanitize_image

    await clamav_service.scan_bytes(image_bytes)

    try:
        image_bytes = sanitize_image(image_bytes)
    except ImageSanitizationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    from app.agents.qr_agent import qr_graph

    initial_state = {
        "image_bytes": image_bytes,
        "decoded_content": "",
        "content_type": "unreadable",
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }

    try:
        state = await qr_graph.ainvoke(initial_state)
    except Exception as exc:
        logger.error("QR agent failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed. Please try again.",
        )

    explanation = sanitize_explanation(state["explanation"])
    scan = await scan_repo.create(
        db,
        input_type=InputType.qr,
        risk_level=state["risk_level"],
        confidence_score=state["confidence"],
        explanation=explanation,
    )

    persisted_findings = []
    for raw in state["findings"]:
        finding = await scan_repo.add_finding(
            db,
            scan_id=scan.id,
            finding_type=raw["finding_type"],
            description=raw["description"],
            severity=raw["severity"],
        )
        persisted_findings.append(finding)

    await db.commit()

    return ScanResponse(
        id=scan.id,
        input_type=InputType.qr,
        risk_level=RiskLevel(state["risk_level"]),
        confidence_score=state["confidence"],
        explanation=explanation,
        findings=[
            FindingResponse(
                id=f.id,
                finding_type=f.finding_type,
                description=f.description,
                severity=RiskLevel(f.severity),
            )
            for f in persisted_findings
        ],
        created_at=scan.created_at,
    )
