from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from app.services.embedding_service import EmbeddingService, get_embedding_service


class TestEmbeddingService:
    def test_embed_one_returns_correct_dimension(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")

        mock_model = MagicMock()
        mock_model.embed.return_value = iter([np.zeros(384)])

        with patch.object(service, "_get_model", return_value=mock_model):
            result = service._encode_sync(["test text"])

        assert len(result) == 1
        assert len(result[0]) == 384

    def test_encode_sync_multiple_texts(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")

        embeddings = [np.ones(384) * i for i in range(3)]
        mock_model = MagicMock()
        mock_model.embed.return_value = iter(embeddings)

        with patch.object(service, "_get_model", return_value=mock_model):
            result = service._encode_sync(["a", "b", "c"])

        assert len(result) == 3
        assert result[0] == [0.0] * 384

    def test_get_model_lazy_loads(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")
        assert service._model is None

        mock_model = MagicMock()
        with patch("fastembed.TextEmbedding", return_value=mock_model):
            model = service._get_model()

        assert model is mock_model
        assert service._model is mock_model

    def test_get_model_caches_on_second_call(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")
        mock_model = MagicMock()
        service._model = mock_model

        with patch("fastembed.TextEmbedding") as mock_cls:
            result = service._get_model()

        mock_cls.assert_not_called()
        assert result is mock_model

    async def test_embed_returns_list_of_vectors(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")

        with patch.object(service, "_encode_sync", return_value=[[0.1] * 384, [0.2] * 384]):
            result = await service.embed(["text one", "text two"])

        assert len(result) == 2
        assert len(result[0]) == 384

    async def test_embed_one_returns_single_vector(self):
        service = EmbeddingService("BAAI/bge-small-en-v1.5")

        with patch.object(service, "_encode_sync", return_value=[[0.5] * 384]):
            result = await service.embed_one("single text")

        assert len(result) == 384
        assert result[0] == pytest.approx(0.5)


def test_get_embedding_service_returns_singleton():
    get_embedding_service.cache_clear()
    svc1 = get_embedding_service()
    svc2 = get_embedding_service()
    assert svc1 is svc2
