import re

_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\bthis is (?:definitely|certainly|absolutely) (?:a )?scam\b", re.IGNORECASE),
        "this shows strong signs of being a scam",
    ),
    (
        re.compile(r"\b(?:guaranteed|confirmed) fraud\b", re.IGNORECASE),
        "likely fraud",
    ),
    (
        re.compile(r"\b(?:guaranteed|confirmed) scam\b", re.IGNORECASE),
        "likely scam",
    ),
    (
        re.compile(r"\b(?:guaranteed|confirmed) fake\b", re.IGNORECASE),
        "likely fake",
    ),
    (
        re.compile(
            r"\bthey (?:are|were) (?:definitely|certainly) (?:scamming|defrauding|stealing)\b",
            re.IGNORECASE,
        ),
        "they may be involved in suspicious activity",
    ),
    (
        re.compile(
            r"\bthis (?:is|was) (?:definitively|conclusively) (?:fraudulent|fake|illegal)\b",
            re.IGNORECASE,
        ),
        "this appears fraudulent",
    ),
]


def sanitize_explanation(text: str) -> str:
    """Replace definitive accusation language with cautionary equivalents."""
    result = text
    for pattern, replacement in _REPLACEMENTS:
        result = pattern.sub(replacement, result)
    return result
