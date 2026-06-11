"""Fastly challenge solver subsystem."""

from __future__ import annotations

from .errors import (
    FastlyChallengeError,
    FastlyChallengeNotSupportedError,
    FastlyChallengeParseError,
    FastlyChallengeValueError,
)
from .fastly import FastlyChallengeSolver
from .metrics import ClientMetricsChallengeProvider
from .parser import CHALLENGE_MARKER, extract_script_url, has_challenge, parse_challenge_script
from .pat import PATChallengeProvider
from .pow import PoWChallenge, PoWChallengeProvider
from .response_builder import ChallengeResponseBuilder
from .types import ChallengeConfig, ChallengeContext, ChallengeType

__all__ = [
    "CHALLENGE_MARKER",
    "ChallengeConfig",
    "ChallengeContext",
    "ChallengeResponseBuilder",
    "ChallengeType",
    "ClientMetricsChallengeProvider",
    "FastlyChallengeError",
    "FastlyChallengeNotSupportedError",
    "FastlyChallengeParseError",
    "FastlyChallengeSolver",
    "FastlyChallengeValueError",
    "PATChallengeProvider",
    "PoWChallenge",
    "PoWChallengeProvider",
    "extract_script_url",
    "has_challenge",
    "parse_challenge_script",
]
