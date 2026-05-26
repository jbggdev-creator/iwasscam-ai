import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rag_document import RagDocument
from app.db.repositories.rag_repo import rag_repo
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class RagService:
    async def ingest(
        self,
        db: AsyncSession,
        source: str,
        content: str,
        metadata: dict | None = None,
    ) -> RagDocument:
        embedding_svc = get_embedding_service()
        embedding = await embedding_svc.embed_one(content)
        doc = await rag_repo.create(
            db,
            source=source,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
        )
        await db.commit()
        logger.debug("Ingested RAG document from source=%s", source)
        return doc

    async def retrieve(
        self,
        db: AsyncSession,
        query: str,
        limit: int | None = None,
    ) -> list[dict]:
        from app.core.config import get_settings
        effective_limit = limit if limit is not None else get_settings().rag_retrieval_limit

        embedding_svc = get_embedding_service()
        query_embedding = await embedding_svc.embed_one(query)
        docs = await rag_repo.search_similar(db, query_embedding, limit=effective_limit)

        return [
            {
                "source": doc.source,
                "content": doc.content,
                "metadata": doc.metadata_,
            }
            for doc in docs
        ]


rag_service = RagService()
