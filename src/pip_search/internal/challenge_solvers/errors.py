"""Fastly challenge solver errors."""



class FastlyChallengeError(RuntimeError):
    """Base exception for Fastly challenge failures."""


class FastlyChallengeUnsolvable(FastlyChallengeError):
    """Raised when the challenge requires unsupported solving."""


class FastlyChallengeParseError(FastlyChallengeError):
    """Raised when challenge payload parsing fails."""
