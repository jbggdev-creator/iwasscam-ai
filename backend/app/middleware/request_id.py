import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_REQUEST_ID_CTX: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    return _REQUEST_ID_CTX.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = _REQUEST_ID_CTX.set(req_id)
        try:
            response = await call_next(request)
        finally:
            _REQUEST_ID_CTX.reset(token)
        response.headers["X-Request-ID"] = req_id
        return response
