import ipaddress

from pydantic import BaseModel, HttpUrl, field_validator
from enum import Enum
from uuid import UUID
from datetime import datetime


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class InputType(str, Enum):
    url = "url"
    image = "image"
    text = "text"
    qr = "qr"


# ── Requests ──────────────────────────────────────────────────────────────────

class UrlScanRequest(BaseModel):
    url: HttpUrl

    @field_validator("url")
    @classmethod
    def block_private_urls(cls, v: HttpUrl) -> HttpUrl:
        host = v.host or ""

        if host.lower() in {"localhost", "0.0.0.0"}:
            raise ValueError("Private or internal URLs are not allowed")

        try:
            addr = ipaddress.ip_address(host)
            if not addr.is_global:
                raise ValueError("Private or internal URLs are not allowed")
        except ValueError as exc:
            if "Private or internal" in str(exc):
                raise
            # Not a bare IP address — hostname is validated at request time

        return v


class TextScanRequest(BaseModel):
    scenario: str

    @field_validator("scenario")
    @classmethod
    def validate_scenario(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Scenario must be at least 10 characters")
        if len(v) > 2000:
            raise ValueError("Scenario must be under 2000 characters")
        return v


# ── Responses ─────────────────────────────────────────────────────────────────

class FindingResponse(BaseModel):
    id: UUID
    finding_type: str
    description: str
    severity: RiskLevel


class ScanResponse(BaseModel):
    id: UUID
    input_type: InputType
    risk_level: RiskLevel
    confidence_score: float
    explanation: str
    findings: list[FindingResponse]
    created_at: datetime


class ScanListResponse(BaseModel):
    scans: list[ScanResponse]
    page: int
    limit: int


class HealthResponse(BaseModel):
    status: str
    version: str
    db: bool = True
    redis: bool = True
