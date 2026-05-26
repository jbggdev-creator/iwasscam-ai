from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rag_document import RagDocument


class RagRepository:
    async def create(
        self,
        db: AsyncSession,
        source: str,
        content: str,
        embedding: list[float],
        metadata: dict,
    ) -> RagDocument:
        doc = RagDocument(
            source=source,
            content=content,
            embedding=embedding,
            metadata_=metadata,
        )
        db.add(doc)
        await db.flush()
        return doc

    async def search_similar(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[RagDocument]:
        result = await db.execute(
            select(RagDocument)
            .where(RagDocument.embedding.is_not(None))
            .order_by(RagDocument.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(RagDocument))
        return result.scalar_one()


rag_repo = RagRepository()
