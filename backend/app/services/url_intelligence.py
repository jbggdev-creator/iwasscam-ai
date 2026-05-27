import asyncio
import math
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
import tldextract
import whois

_SUSPICIOUS_TLDS = frozenset({
    "tk", "ml", "ga", "cf", "gq",       # Freenom free TLDs — extremely common in phishing
    "xyz", "click", "download", "top",
    "work", "loan", "gdn", "men",
    "stream", "win", "racing", "date",
    "trade", "accountant", "science",
    "party", "review", "faith", "bid",
    "cricket", "webcam", "link",
})

# Character substitutions used in homograph / typosquatting attacks.
# Multi-char pairs are listed first so they're replaced before single-char ones.
_CHAR_SUBS: list[tuple[str, str]] = [
    ("vv", "w"), ("rn", "m"), ("cl", "d"),
    ("0", "o"), ("1", "l"), ("3", "e"), ("4", "a"),
    ("5", "s"), ("6", "b"), ("7", "t"), ("@", "a"),
]

# Well-known brands commonly impersonated in Philippine phishing campaigns.
_BRAND_DOMAINS = frozenset({
    "facebook", "google", "gmail", "youtube", "instagram", "twitter", "x",
    "tiktok", "paypal", "gcash", "maya", "paymaya",
    "bpi", "bdo", "metrobank", "unionbank", "landbank", "rcbc", "eastwest",
    "pnb", "chinabank",
    "lazada", "shopee", "grab", "netflix", "apple", "microsoft", "amazon",
    "payoneer", "wise", "remitly", "yahoo", "outlook", "linkedin",
    "whatsapp", "viber", "telegram", "spotify",
})


def _normalize_homoglyphs(text: str) -> str:
    result = text.lower()
    for fake, real in _CHAR_SUBS:
        result = result.replace(fake, real)
    return result


def _levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        return _levenshtein(b, a)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for ch_a in a:
        curr = [prev[0] + 1]
        for j, ch_b in enumerate(b):
            curr.append(min(prev[j] + (ch_a != ch_b), prev[j + 1] + 1, curr[-1] + 1))
        prev = curr
    return prev[-1]


def detect_brand_impersonation(domain: str) -> tuple[bool, str]:
    """Returns (is_impersonation, impersonated_brand).

    Catches homoglyph substitutions (faceb0ok → facebook) and
    one-character typosquatting (facebok → facebook).
    """
    normalized = _normalize_homoglyphs(domain)
    for brand in _BRAND_DOMAINS:
        # Exact match after normalization but not before → homoglyph attack confirmed.
        if normalized == brand and domain.lower() != brand:
            return True, brand
        # One-edit distance after normalization → typosquatting.
        if normalized != brand and _levenshtein(normalized, brand) == 1:
            return True, brand
    return False, ""

_WHOIS_TIMEOUT = 5.0


@dataclass
class UrlFeatures:
    url: str
    domain: str
    tld: str
    subdomain: str
    scheme: str
    domain_age_days: int | None
    ssl_valid: bool
    redirect_count: int
    final_url: str
    url_entropy: float
    is_suspicious_tld: bool
    whois_error: bool
    is_brand_impersonation: bool
    impersonated_brand: str


def _shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


async def _get_domain_age(domain: str) -> tuple[int | None, bool]:
    """Returns (age_in_days, whois_error)."""
    try:
        w = await asyncio.wait_for(
            asyncio.to_thread(whois.whois, domain),
            timeout=_WHOIS_TIMEOUT,
        )
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date is None:
            return None, True
        if creation_date.tzinfo is None:
            creation_date = creation_date.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - creation_date).days
        return max(0, age_days), False
    except Exception:
        return None, True


async def _check_ssl(domain: str) -> bool:
    try:
        async with httpx.AsyncClient(verify=True, timeout=5.0, follow_redirects=False) as client:
            await client.get(f"https://{domain}")
        return True
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
        return False
    except Exception:
        return False


async def _follow_redirects(url: str) -> tuple[int, str]:
    current_url = url
    redirect_count = 0

    try:
        async with httpx.AsyncClient(follow_redirects=False, timeout=5.0) as client:
            for _ in range(5):
                try:
                    response = await client.get(current_url)
                    if response.is_redirect:
                        location = response.headers.get("location", "").strip()
                        if not location:
                            break
                        redirect_count += 1
                        current_url = location
                    else:
                        break
                except Exception:
                    break
    except Exception:
        pass

    return redirect_count, current_url


class UrlIntelligenceService:
    """Extracts security-relevant signals from a URL without user data logging."""

    async def analyze(self, url: str) -> UrlFeatures:
        parsed = urlparse(url)
        extracted = tldextract.extract(url)

        domain = extracted.domain
        tld = extracted.suffix
        subdomain = extracted.subdomain
        scheme = parsed.scheme

        domain_age_days, whois_error = await _get_domain_age(f"{domain}.{tld}")
        ssl_valid = await _check_ssl(f"{domain}.{tld}")
        redirect_count, final_url = await _follow_redirects(url)
        url_entropy = _shannon_entropy(url)
        is_suspicious_tld = tld.lower() in _SUSPICIOUS_TLDS
        is_brand_impersonation, impersonated_brand = detect_brand_impersonation(domain)

        return UrlFeatures(
            url=url,
            domain=domain,
            tld=tld,
            subdomain=subdomain,
            scheme=scheme,
            domain_age_days=domain_age_days,
            ssl_valid=ssl_valid,
            redirect_count=redirect_count,
            final_url=final_url,
            url_entropy=url_entropy,
            is_suspicious_tld=is_suspicious_tld,
            whois_error=whois_error,
            is_brand_impersonation=is_brand_impersonation,
            impersonated_brand=impersonated_brand,
        )
