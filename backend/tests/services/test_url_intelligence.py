import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone, timedelta

from app.services.url_intelligence import UrlIntelligenceService, UrlFeatures


@pytest.fixture
def service():
    return UrlIntelligenceService()


def _make_whois(days_ago: int):
    mock_w = MagicMock()
    mock_w.creation_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return mock_w


class TestUrlParsing:
    async def test_extracts_domain_and_tld(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://example.com/path?q=1")
        assert features.domain == "example"
        assert features.tld == "com"

    async def test_extracts_subdomain(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://login.evil.tk/phish")
        assert features.subdomain == "login"

    async def test_detects_https_scheme(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://example.com/")
        assert features.scheme == "https"


class TestDomainAge:
    async def test_new_domain_detected(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(5)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://new-site.com/")
        assert features.domain_age_days == 5

    async def test_whois_failure_returns_none(self, service):
        with patch("app.services.url_intelligence.whois.whois", side_effect=Exception("no whois")):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://example.com/")
        assert features.domain_age_days is None
        assert features.whois_error is True

    async def test_list_creation_date_handled(self, service):
        mock_w = MagicMock()
        mock_w.creation_date = [
            datetime.now(timezone.utc) - timedelta(days=200),
            datetime.now(timezone.utc) - timedelta(days=100),
        ]
        with patch("app.services.url_intelligence.whois.whois", return_value=mock_w):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://example.com/")
        assert features.domain_age_days == 200


class TestSuspiciousTld:
    @pytest.mark.parametrize("tld", ["tk", "ml", "ga", "cf", "gq", "xyz", "click", "download"])
    async def test_known_bad_tlds_flagged(self, service, tld):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(1)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze(f"https://evil.{tld}/scam")
        assert features.is_suspicious_tld is True

    async def test_legitimate_tld_not_flagged(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(1000)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://bank.com/login")
        assert features.is_suspicious_tld is False


class TestUrlEntropy:
    async def test_high_entropy_url(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze(
                    "https://xn--a4h.xn--p1ai/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
                )
        assert features.url_entropy > 3.0

    async def test_simple_url_lower_entropy(self, service):
        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient"):
                features = await service.analyze("https://google.com/")
        assert features.url_entropy < 4.5


class TestSslCheck:
    async def test_ssl_valid_on_success(self, service):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(return_value=mock_resp)

        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient", return_value=mock_client):
                features = await service.analyze("https://example.com/")
        assert features.ssl_valid is True

    async def test_ssl_invalid_on_ssl_error(self, service):
        import httpx
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("SSL error"))

        with patch("app.services.url_intelligence.whois.whois", return_value=_make_whois(365)):
            with patch("app.services.url_intelligence.httpx.AsyncClient", return_value=mock_client):
                features = await service.analyze("https://bad-cert.example.com/")
        assert features.ssl_valid is False
