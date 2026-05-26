import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture(autouse=True)
def reset_rate_limits():
    from app.core.limiter import limiter
    limiter._storage.reset()
    yield


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
