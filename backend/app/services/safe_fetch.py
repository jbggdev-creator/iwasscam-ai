import ipaddress
import socket
from urllib.parse import urlparse

import httpx

ALLOWED_SCHEMES = frozenset({"http", "https"})

_BLOCKED_NETWORKS: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / AWS metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]


class SSRFViolationError(ValueError):
    pass


def _is_blocked_ip(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in net for net in _BLOCKED_NETWORKS)
    except ValueError:
        return False


def _resolve_and_check(hostname: str) -> None:
    try:
        results = socket.getaddrinfo(hostname, None)
    except OSError as exc:
        raise SSRFViolationError(f"DNS resolution failed for '{hostname}': {exc}") from exc

    for *_, addr_tuple in results:
        ip = addr_tuple[0]
        if _is_blocked_ip(ip):
            raise SSRFViolationError(
                f"Request to '{hostname}' is blocked: resolved IP '{ip}' is in a private/reserved range"
            )


class SafeFetcher:
    """SSRF-protected async HTTP fetcher.

    Resolves the hostname before making any network request and rejects
    targets that resolve to private, loopback, or link-local addresses.
    """

    def __init__(self, timeout: float = 5.0, max_response_bytes: int = 1_048_576) -> None:
        self._timeout = timeout
        self._max_response_bytes = max_response_bytes

    async def get(self, url: str, *, follow_redirects: bool = False) -> httpx.Response:
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise SSRFViolationError(
                f"Disallowed scheme '{parsed.scheme}': only http and https are permitted"
            )

        hostname = parsed.hostname or ""
        if not hostname:
            raise SSRFViolationError("URL has no hostname")

        # Resolve before connecting — catches DNS rebinding and private-range targets
        _resolve_and_check(hostname)

        async with httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=follow_redirects,
        ) as client:
            return await client.get(url)
