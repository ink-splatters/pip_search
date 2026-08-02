"""Fastly challenge solver errors."""

from typing import Self


class FastlyChallengeError(RuntimeError):
    """Base exception for Fastly challenge failures."""

    @classmethod
    def challenge_probe_failed(cls, status_code: int) -> Self:
        return cls(f"Challenge probe failed: HTTP {status_code}")

    @classmethod
    def challenge_script_fetch_failed(cls, status_code: int) -> Self:
        return cls(f"Failed to fetch challenge script: HTTP {status_code}")

    @classmethod
    def challenge_not_completed(cls) -> Self:
        return cls("Challenge did not complete successfully")

    @classmethod
    def post_back_failed(cls, status_code: int) -> Self:
        return cls(f"Post-back failed: HTTP {status_code}")

    @classmethod
    def pow_solution_not_found(cls) -> Self:
        return cls("PoW solution not found")


class FastlyChallengeUnsolvable(FastlyChallengeError):
    """Raised when the challenge requires unsupported solving."""

    @classmethod
    def captcha(cls) -> Self:
        return cls("CAPTCHA challenge cannot be solved")

    @classmethod
    def pow_suffix_too_large(cls, suffix_len: int) -> Self:
        return cls(f"PoW suffix length too large: {suffix_len}")


class FastlyChallengeParseError(FastlyChallengeError):
    """Raised when challenge payload parsing fails."""

    @classmethod
    def missing_challenge_id(cls) -> Self:
        return cls("Could not find challenge ID in HTML")

    @classmethod
    def missing_init_call(cls) -> Self:
        return cls("Could not locate init() call in script")

    @classmethod
    def challenge_json_parse_failed(cls, error: Exception) -> Self:
        return cls(f"Challenge JSON parse failed: {error}")

    @classmethod
    def challenge_json_not_list(cls) -> Self:
        return cls("Challenge JSON was not a list")

    @classmethod
    def challenge_entry_not_object(cls) -> Self:
        return cls("Challenge list contained non-object entries")

    @classmethod
    def pow_data_payload_invalid(cls) -> Self:
        return cls("Missing/invalid PoW data payload")

    @classmethod
    def pow_field_invalid(cls, field: str) -> Self:
        return cls(f"Missing/invalid PoW field: {field}")

    @classmethod
    def post_back_json_invalid(cls, error: Exception) -> Self:
        return cls(f"Invalid JSON from post-back: {error}")

    @classmethod
    def post_back_expected_object(cls) -> Self:
        return cls("Invalid JSON from post-back: expected object")
