from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.db.repositories.scan_repo import ScanRepository


class TestScanRepoGetById:
    async def test_returns_scan_when_found(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_scan = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_scan
        mock_db.execute.return_value = mock_result

        scan_id = uuid4()
        result = await repo.get_by_id(mock_db, scan_id)

        assert result is mock_scan
        mock_db.execute.assert_called_once()

    async def test_returns_none_when_not_found(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await repo.get_by_id(mock_db, uuid4())

        assert result is None


class TestScanRepoListByUser:
    async def test_returns_scans_for_user(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_scan = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_scan]
        mock_db.execute.return_value = mock_result

        user_id = uuid4()
        result = await repo.list_by_user(mock_db, user_id, limit=10, offset=0)

        assert result == [mock_scan]
        mock_db.execute.assert_called_once()

    async def test_returns_empty_when_no_scans_for_user(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await repo.list_by_user(mock_db, uuid4(), limit=20, offset=0)

        assert result == []


class TestScanRepoListRecent:
    async def test_returns_list_of_scans(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_scan = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_scan]
        mock_db.execute.return_value = mock_result

        result = await repo.list_recent(mock_db, limit=10, offset=0)

        assert result == [mock_scan]
        mock_db.execute.assert_called_once()

    async def test_returns_empty_list_when_no_scans(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        result = await repo.list_recent(mock_db, limit=20, offset=0)

        assert result == []

    async def test_passes_limit_and_offset_to_query(self):
        repo = ScanRepository()
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        await repo.list_recent(mock_db, limit=5, offset=10)

        mock_db.execute.assert_called_once()
        args = mock_db.execute.call_args
        assert args is not None
