from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from typing import Any


class InvalidBodyPreviewLengthError(ValueError):
    def __init__(self, truncate_len: int):
        super().__init__(f"truncate_len cannot be < 0: {truncate_len}")


class Redactor:
    def __init__(self, sensitive_headers: AbstractSet[str]):
        self._sensitive_headers = sensitive_headers

    def redact(self, headers: Mapping[str, Any] | None) -> dict[str, str]:
        if not headers:
            return {}
        out: dict[str, str] = {}
        for k, v in headers.items():
            out[k] = "<redacted>" if k.lower() in self._sensitive_headers else v
        return out


def body_preview(body: Any, truncate_len: int = 4000) -> str:
    if truncate_len < 0:
        raise InvalidBodyPreviewLengthError(truncate_len)
    if isinstance(body, (bytes, bytearray)):
        text = body.decode("utf-8", errors="replace")
    else:
        text = str(body)
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    return (
        (text[:truncate_len] + "…<truncated>" if len(text) > truncate_len else "")
        if truncate_len > 0
        else text
    )
