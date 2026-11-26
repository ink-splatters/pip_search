"""Fingerprint provider implementations used by challenge solvers."""

from importlib import import_module
from typing import Any

_FINGERPRINT_MODULE = "pip_search.internal.fingerprint"


class SealedFingerprintProvider:
    """Load fingerprint data from packaged sealed fingerprint payload."""

    def load(self) -> dict[str, Any]:
        """Return default sealed fingerprint payload."""
        module: Any = import_module(_FINGERPRINT_MODULE)
        return dict(module.default())
