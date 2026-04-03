"""Parsing utilities for Fastly challenge HTML/script payloads."""

from __future__ import annotations

import re
import json
from typing import Any

from .errors import FastlyChallengeParseError
from .types import ChallengeConfig, ChallengeData

CHALLENGE_MARKER = "_fs-ch-"


def has_challenge(html: str) -> bool:
    """Return whether response body contains a Fastly challenge marker."""
    return CHALLENGE_MARKER in html


def extract_script_url(html: str, *, base_url: str) -> str:
    """Extract challenge script URL from challenge page HTML."""
    challenge_match = re.search(rf"/{CHALLENGE_MARKER}([^/\"']+)/", html)
    if not challenge_match:
        raise FastlyChallengeParseError("Could not find challenge ID in HTML")

    challenge_id = challenge_match.group(1)
    return f"{base_url.rstrip('/')}/{CHALLENGE_MARKER}{challenge_id}/script.js?reload=true"


def parse_challenge_script(script: str) -> ChallengeConfig:
    """Parse challenge script and extract initial challenge configuration."""
    init_match = re.search(
        r'init\(\s*(\[.*?\])\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']',
        script,
        re.DOTALL,
    )
    if not init_match:
        raise FastlyChallengeParseError("Could not locate init() call in script")

    array_str = init_match.group(1)
    token = init_match.group(2)
    path = init_match.group(3)

    try:
        parsed = json.loads(array_str)
    except json.JSONDecodeError as exc:
        raise FastlyChallengeParseError(f"Challenge JSON parse failed: {exc}") from exc

    challenges = validate_challenges(parsed)
    return ChallengeConfig(challenges=challenges, token=token, path=path)


def validate_challenges(payload: object) -> list[ChallengeData]:
    """Validate raw challenge payloads and return typed challenge objects."""
    if not isinstance(payload, list):
        raise FastlyChallengeParseError("Challenge JSON was not a list")

    return [_validate_challenge(item) for item in payload]


def _validate_challenge(payload: object) -> ChallengeData:
    """Validate one raw challenge object and return a typed mapping."""
    if not isinstance(payload, dict):
        raise FastlyChallengeParseError("Challenge list contained non-object entries")

    challenge: dict[str, Any] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            raise FastlyChallengeParseError("Challenge list contained non-object entries")
        challenge[key] = value

    return challenge
