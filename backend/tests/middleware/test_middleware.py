from unittest.mock import AsyncMock, patch

import pytest


class TestSecurityHeaders:
    async def test_security_headers_present(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get("/api/v1/health")

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
        assert "max-age=63072000" in response.headers["Strict-Transport-Security"]

    async def test_referrer_policy_present(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get("/api/v1/health")

        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


class TestRequestID:
    async def test_response_contains_request_id(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get("/api/v1/health")

        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    async def test_client_provided_request_id_is_echoed(self, client):
        custom_id = "test-request-id-123"
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get(
                    "/api/v1/health",
                    headers={"X-Request-ID": custom_id},
                )

        assert response.headers["X-Request-ID"] == custom_id


class TestRequestSizeLimit:
    async def test_rejects_oversized_content_length(self, client):
        large_content_length = str(2 * 1024 * 1024)
        response = await client.post(
            "/api/v1/scan/text",
            content=b"x",
            headers={"Content-Length": large_content_length, "Content-Type": "application/json"},
        )
        assert response.status_code == 413

    async def test_allows_normal_sized_body(self, client):
        response = await client.post(
            "/api/v1/scan/text",
            json={"scenario": "hi"},
        )
        # Fails at Pydantic validation (too short), not size check
        assert response.status_code == 422
