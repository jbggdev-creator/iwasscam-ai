import logging
import re
import sys
from typing import Any

_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'(password["\']?\s*[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(token["\']?\s*[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(authorization:\s*)\S+', re.IGNORECASE),
    re.compile(r'(api[_-]?key["\']?\s*[:=]\s*)\S+', re.IGNORECASE),
    re.compile(r'(secret["\']?\s*[:=]\s*)\S+', re.IGNORECASE),
]


def _redact(text: str) -> str:
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text


def _redact_args(args: Any) -> Any:
    if not args:
        return args
    if isinstance(args, tuple):
        return tuple(_redact(str(a)) if isinstance(a, str) else a for a in args)
    return args


class _SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact(str(record.msg))
        record.args = _redact_args(record.args)
        return True


def configure_logging(debug: bool = False, log_format: str = "json") -> None:
    level = logging.DEBUG if debug else logging.INFO

    if log_format == "json":
        try:
            from pythonjsonlogger.json import JsonFormatter

            handler: logging.Handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
            )
        except ImportError:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            )
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    handler.addFilter(_SensitiveDataFilter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
