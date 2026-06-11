"""Fastly challenge solver errors."""

from __future__ import annotations


class FastlyChallengeError(RuntimeError):
    """Base exception for Fastly challenge failures."""


class FastlyChallengeParseError(FastlyChallengeError):
    """Raised when challenge payload parsing fails."""


class FastlyChallengeValueError(FastlyChallengeError):
    """Raised when challenge parameters are unexpected or invalid."""


class FastlyChallengeNotSupportedError(FastlyChallengeError):
    """Raised when the challenge type is not supported."""
