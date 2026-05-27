from urllib.parse import urlparse, unquote

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import get_settings


def _asyncpg_connect_args(database_url: str, ssl: bool) -> tuple[str, dict]:
    """
    Return (clean_url, connect_args) with username/password extracted explicitly.
    SQLAlchemy's URL parser truncates usernames containing dots (e.g. Supabase
    pooler usernames like postgres.projectref), causing auth failures. Passing them
    via connect_args bypasses the parser entirely.
    """
    parsed = urlparse(database_url)
    username = unquote(parsed.username or "")
    password = unquote(parsed.password or "")
    host = parsed.hostname or ""
    port = parsed.port or 5432
    database = (parsed.path or "/postgres").lstrip("/") or "postgres"
    clean_url = f"postgresql+asyncpg://{host}:{port}/{database}"
    connect_args: dict = {"user": username, "password": password}
    if ssl:
        import ssl as _ssl
        ssl_ctx = _ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = _ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    return clean_url, connect_args


def _make_engine():
    settings = get_settings()
    is_prod = settings.environment == "production"
    clean_url, connect_args = _asyncpg_connect_args(settings.database_url, ssl=is_prod)
    return create_async_engine(
        clean_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.debug,
        connect_args=connect_args,
    )


engine = _make_engine()
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
