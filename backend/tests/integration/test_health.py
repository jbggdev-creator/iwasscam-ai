from unittest.mock import AsyncMock, patch

import pytest


class TestHealthEndpoint:
    async def test_returns_ok_when_all_healthy(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] is True
        assert data["redis"] is True
        assert "version" in data

    async def test_returns_503_when_db_down(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=False)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=True)):
                response = await client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["db"] is False
        assert data["redis"] is True

    async def test_returns_503_when_redis_down(self, client):
        with patch("app.api.v1.health._ping_db", AsyncMock(return_value=True)):
            with patch("app.api.v1.health._ping_redis", AsyncMock(return_value=False)):
                response = await client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["redis"] is False
