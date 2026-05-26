from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.scan import Finding, Scan


class ScanRepository:
    async def create(
        self,
        db: AsyncSession,
        *,
        input_type: str,
        risk_level: str,
        confidence_score: float,
        explanation: str,
        user_id: UUID | None = None,
    ) -> Scan:
        scan = Scan(
            input_type=input_type,
            risk_level=risk_level,
            confidence_score=confidence_score,
            explanation=explanation,
            user_id=user_id,
        )
        db.add(scan)
        await db.flush()
        return scan

    async def add_finding(
        self,
        db: AsyncSession,
        *,
        scan_id: UUID,
        finding_type: str,
        description: str,
        severity: str,
    ) -> Finding:
        finding = Finding(
            scan_id=scan_id,
            finding_type=finding_type,
            description=description,
            severity=severity,
        )
        db.add(finding)
        return finding

    async def get_by_id(self, db: AsyncSession, scan_id: UUID) -> Scan | None:
        stmt = (
            select(Scan)
            .where(Scan.id == scan_id)
            .options(selectinload(Scan.findings))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Scan]:
        stmt = (
            select(Scan)
            .where(Scan.user_id == user_id)
            .options(selectinload(Scan.findings))
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(
        self,
        db: AsyncSession,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Scan]:
        stmt = (
            select(Scan)
            .options(selectinload(Scan.findings))
            .order_by(Scan.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


scan_repo = ScanRepository()
