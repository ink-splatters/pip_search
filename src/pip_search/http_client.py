"""HTTP client utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import httpx

if TYPE_CHECKING:
    from collections.abc import MutableMapping

from loguru import logger


class HTTPClient(httpx.Client):
    """HTTPX client with request/response logging."""

    _SENSITIVE_HEADERS: Final[frozenset[str]] = frozenset({"authorization", "cookie"})

    def request(self, method: str, url: httpx.URL | str, **kwargs: Any) -> httpx.Response:
        """Make request with logging."""
        method_u = method.upper()
        timeout = kwargs.get("timeout")

        def redact(headers: MutableMapping[str, str] | None) -> dict[str, str] | None:
            if not headers:
                return None
            out: dict[str, str] = {}
            for k, v in headers.items():
                out[k] = "<redacted>" if k.lower() in self._SENSITIVE_HEADERS else v
            return out

        def body_preview(body: Any) -> str | None:
            if body is None:
                return None
            if isinstance(body, (bytes, bytearray)):
                try:
                    text = body.decode("utf-8", errors="replace")
                except Exception:
                    return f"<{type(body).__name__} {len(body)} bytes>"
            else:
                text = str(body)
            text = text.replace("\r", "\\r").replace("\n", "\\n")
            return text[:4000] + ("…<truncated>" if len(text) > 4000 else "")

        try:
            resp = super().request(method_u, url, **kwargs)
        except httpx.RequestError:
            logger.exception(
                "HTTP request failed: method={} url={} timeout={} kwargs_headers={}",
                method_u,
                url,
                timeout,
                redact(kwargs.get("headers")),
            )
            raise

        chain = [*resp.history, resp]
        for i, r in enumerate(chain):
            req = r.request
            is_final = i == len(chain) - 1

            logger.info("HTTP {} {} -> {}", req.method, req.url, r.status_code)
            logger.debug(
                "HTTP request: method={} url={} timeout={} headers={} body={}",
                req.method,
                req.url,
                timeout,
                redact(dict(req.headers)),
                body_preview(req.content),
            )
            logger.debug(
                "HTTP response: url={} status={} headers={} body_len={}",
                req.url,
                r.status_code,
                redact(dict(r.headers)),
                len(r.content or b""),
            )

            if is_final:
                logger.opt(lazy=True).debug(
                    "HTTP response body preview: {}",
                    lambda content=r.content: body_preview(content),
                )

        return resp
