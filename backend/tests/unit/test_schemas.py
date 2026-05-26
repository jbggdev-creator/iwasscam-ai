import pytest
from pydantic import ValidationError
from app.schemas.scan import UrlScanRequest, TextScanRequest


def test_url_scan_request_valid():
    req = UrlScanRequest(url="https://example.com/path")
    assert req.url is not None


def test_url_scan_request_blocks_localhost():
    with pytest.raises(ValidationError, match="Private or internal URLs"):
        UrlScanRequest(url="http://localhost/login")


def test_url_scan_request_blocks_metadata():
    with pytest.raises(ValidationError, match="Private or internal URLs"):
        UrlScanRequest(url="http://169.254.169.254/latest/meta-data/")


def test_text_scan_request_valid():
    req = TextScanRequest(scenario="A recruiter asked me to pay ₱500 before the interview.")
    assert len(req.scenario) >= 10


def test_text_scan_request_too_short():
    with pytest.raises(ValidationError):
        TextScanRequest(scenario="short")


def test_text_scan_request_too_long():
    with pytest.raises(ValidationError):
        TextScanRequest(scenario="x" * 2001)
