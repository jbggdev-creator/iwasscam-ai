import asyncio
import logging
from functools import lru_cache
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384  # BAAI/bge-small-en-v1.5


class EmbeddingService:
    """Wraps fastembed TextEmbedding with lazy model loading and async support."""

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model: Any = None

    def _get_model(self) -> Any:
        if self._model is None:
            from fastembed import TextEmbedding
            logger.info("Loading embedding model: %s", self._model_name)
            self._model = TextEmbedding(self._model_name, cache_dir="/app/.cache/fastembed")
        return self._model

    def _encode_sync(self, texts: list[str]) -> list[list[float]]:
        model = self._get_model()
        return [emb.tolist() for emb in model.embed(texts)]

    async def embed(self, texts: list[str]) -> list[list[float]]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._encode_sync, texts)

    async def embed_one(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    return EmbeddingService(settings.embedding_model)
