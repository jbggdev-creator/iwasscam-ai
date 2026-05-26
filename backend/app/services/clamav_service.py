import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


async def scan_bytes(data: bytes) -> None:
    """Scan bytes for malware via ClamAV daemon.

    Raises HTTPException(422) if malware is detected.
    Returns silently if scanning is disabled or daemon is unavailable.
    """
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.clamav_enabled:
        return

    try:
        import clamd  # type: ignore[import]
    except ImportError:
        logger.warning("clamd package not installed — ClamAV scan skipped")
        return

    cd = _connect(clamd, settings)
    if cd is None:
        return

    try:
        result = cd.instream(data)
    except Exception as exc:
        logger.warning("ClamAV instream failed: %s — scan skipped", exc)
        return

    scan_result = result.get("stream")
    if scan_result and scan_result[0] == "FOUND":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Malware detected in uploaded file",
        )


def _connect(clamd: object, settings: object) -> object | None:  # type: ignore[return]
    import clamd as _clamd  # type: ignore[import]

    try:
        cd = _clamd.ClamdUnixSocket(settings.clamav_socket)  # type: ignore[attr-defined]
        cd.ping()
        return cd
    except Exception:
        pass

    try:
        cd = _clamd.ClamdNetworkSocket(  # type: ignore[attr-defined]
            settings.clamav_host, settings.clamav_port  # type: ignore[attr-defined]
        )
        cd.ping()
        return cd
    except Exception as exc:
        logger.warning("ClamAV daemon not reachable: %s — scan skipped", exc)
        return None
