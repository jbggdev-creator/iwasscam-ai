import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.safe_fetch import SafeFetcher, SSRFViolationError


class TestSSRFProtection:
    async def test_blocks_localhost(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="blocked"):
            await fetcher.get("http://localhost/admin")

    async def test_blocks_loopback_ip(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="blocked"):
            await fetcher.get("http://127.0.0.1/secret")

    async def test_blocks_private_10_range(self):
        fetcher = SafeFetcher()
        with patch("app.services.safe_fetch.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("10.0.0.1", 80))]
            with pytest.raises(SSRFViolationError, match="blocked"):
                await fetcher.get("http://internal.corp/api")

    async def test_blocks_private_192_168_range(self):
        fetcher = SafeFetcher()
        with patch("app.services.safe_fetch.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("192.168.1.1", 80))]
            with pytest.raises(SSRFViolationError, match="blocked"):
                await fetcher.get("http://router.local/")

    async def test_blocks_aws_metadata(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="blocked"):
            await fetcher.get("http://169.254.169.254/latest/meta-data/")

    async def test_blocks_0_0_0_0(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="blocked"):
            await fetcher.get("http://0.0.0.0/")

    async def test_blocks_non_http_schemes(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="scheme"):
            await fetcher.get("file:///etc/passwd")

    async def test_blocks_ftp_scheme(self):
        fetcher = SafeFetcher()
        with pytest.raises(SSRFViolationError, match="scheme"):
            await fetcher.get("ftp://files.example.com/data")

    async def test_allows_public_ip(self):
        fetcher = SafeFetcher()
        with patch("app.services.safe_fetch.socket.getaddrinfo") as mock_dns:
            mock_dns.return_value = [(None, None, None, None, ("93.184.216.34", 80))]
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            with patch("app.services.safe_fetch.httpx.AsyncClient", return_value=mock_client):
                response = await fetcher.get("http://example.com/")
                assert response.status_code == 200

    async def test_raises_on_dns_failure(self):
        fetcher = SafeFetcher()
        with patch("app.services.safe_fetch.socket.getaddrinfo", side_effect=OSError("DNS error")):
            with pytest.raises(SSRFViolationError, match="DNS"):
                await fetcher.get("http://nonexistent.invalid/")
