from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.rag_service import RagService


@pytest.fixture
def service():
    return RagService()


class TestRagIngest:
    async def test_ingest_creates_document(self, service):
        mock_embedding = [0.1] * 384
        mock_doc = MagicMock()

        with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
            mock_emb = MagicMock()
            mock_emb.embed_one = AsyncMock(return_value=mock_embedding)
            mock_emb_factory.return_value = mock_emb

            with patch("app.services.rag_service.rag_repo.create", AsyncMock(return_value=mock_doc)):
                mock_db = AsyncMock()
                result = await service.ingest(
                    mock_db,
                    source="BSP Advisory",
                    content="This is a scam advisory.",
                    metadata={"type": "gcash_scam"},
                )

        assert result is mock_doc
        mock_db.commit.assert_awaited_once()

    async def test_ingest_uses_empty_metadata_by_default(self, service):
        mock_embedding = [0.0] * 384
        mock_doc = MagicMock()

        with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
            mock_emb = MagicMock()
            mock_emb.embed_one = AsyncMock(return_value=mock_embedding)
            mock_emb_factory.return_value = mock_emb

            with patch("app.services.rag_service.rag_repo.create", AsyncMock(return_value=mock_doc)) as mock_create:
                mock_db = AsyncMock()
                await service.ingest(mock_db, source="Test", content="Content with no metadata")

        _, kwargs = mock_create.call_args
        assert kwargs["metadata"] == {}


class TestRagRetrieve:
    async def test_retrieve_returns_formatted_dicts(self, service):
        mock_doc = MagicMock()
        mock_doc.source = "BSP Advisory"
        mock_doc.content = "Scam content."
        mock_doc.metadata_ = {"type": "gcash_scam"}

        with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
            mock_emb = MagicMock()
            mock_emb.embed_one = AsyncMock(return_value=[0.2] * 384)
            mock_emb_factory.return_value = mock_emb

            with patch("app.services.rag_service.rag_repo.search_similar", AsyncMock(return_value=[mock_doc])):
                mock_db = AsyncMock()
                results = await service.retrieve(mock_db, "suspicious gcash request")

        assert len(results) == 1
        assert results[0]["source"] == "BSP Advisory"
        assert results[0]["content"] == "Scam content."
        assert results[0]["metadata"] == {"type": "gcash_scam"}

    async def test_retrieve_empty_when_no_matches(self, service):
        with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
            mock_emb = MagicMock()
            mock_emb.embed_one = AsyncMock(return_value=[0.0] * 384)
            mock_emb_factory.return_value = mock_emb

            with patch("app.services.rag_service.rag_repo.search_similar", AsyncMock(return_value=[])):
                mock_db = AsyncMock()
                results = await service.retrieve(mock_db, "totally safe scenario")

        assert results == []

    async def test_retrieve_respects_custom_limit(self, service):
        with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
            mock_emb = MagicMock()
            mock_emb.embed_one = AsyncMock(return_value=[0.1] * 384)
            mock_emb_factory.return_value = mock_emb

            with patch("app.services.rag_service.rag_repo.search_similar", AsyncMock(return_value=[])) as mock_search:
                mock_db = AsyncMock()
                await service.retrieve(mock_db, "query", limit=10)

        mock_search.assert_awaited_once()
        _, kwargs = mock_search.call_args
        assert kwargs["limit"] == 10

    async def test_retrieve_uses_keyword_fallback_when_embedding_disabled(self, service):
        mock_doc = MagicMock()
        mock_doc.source = "BSP Advisory"
        mock_doc.content = "GCash scam advisory content."
        mock_doc.metadata_ = {}

        mock_settings = MagicMock()
        mock_settings.rag_embedding_enabled = False
        mock_settings.rag_retrieval_limit = 3

        with patch("app.services.rag_service.get_settings", return_value=mock_settings):
            with patch("app.services.rag_service.rag_repo.search_keyword", AsyncMock(return_value=[mock_doc])) as mock_kw:
                with patch("app.services.rag_service.rag_repo.search_similar") as mock_vec:
                    mock_db = AsyncMock()
                    results = await service.retrieve(mock_db, "gcash scam")

        mock_kw.assert_awaited_once()
        mock_vec.assert_not_called()
        assert len(results) == 1
        assert results[0]["source"] == "BSP Advisory"

    async def test_retrieve_skips_embedding_service_when_disabled(self, service):
        mock_settings = MagicMock()
        mock_settings.rag_embedding_enabled = False
        mock_settings.rag_retrieval_limit = 3

        with patch("app.services.rag_service.get_settings", return_value=mock_settings):
            with patch("app.services.rag_service.rag_repo.search_keyword", AsyncMock(return_value=[])):
                with patch("app.services.rag_service.get_embedding_service") as mock_emb_factory:
                    mock_db = AsyncMock()
                    await service.retrieve(mock_db, "investment scam")

        mock_emb_factory.assert_not_called()
