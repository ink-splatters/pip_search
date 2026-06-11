"""Challenge response state machine."""

from __future__ import annotations

from typing import Any, ClassVar, Protocol

from loguru import logger

from .errors import FastlyChallengeError, FastlyChallengeNotSupportedError
from .types import (
    ChallengeContext,
    ChallengeData,
    ChallengeResponse,
    ChallengeType,
    MetricsProvider,
    PATProvider,
    PoWProvider,
)


class Dataclass(Protocol):
    # as already noted in comments, checking for this attribute is currently
    # the most reliable way to ascertain that something is a dataclass
    __dataclass_fields__: ClassVar[dict[str, Any]]



def extra_info(extra: Dataclass) -> str | None:
    import json
    import dataclasses
    return json.dumps(dataclasses.asdict(extra)) if logger._core.min_level <=5 else ""


class ChallengeResponseBuilder:
    """Build challenge response payloads for one challenge round."""

    def __init__(
        self,
        *,
        pat_provider: PATProvider,
        pow_provider: PoWProvider,
        metrics_provider: MetricsProvider,
    ) -> None:
        self._pat_provider = pat_provider
        self._pow_provider = pow_provider
        self._metrics_provider = metrics_provider

    def build(
        self,
        config: dict[str,Any],
        *,
        context: ChallengeContext,
    ) -> list[ChallengeResponse]:
        """Build response payload list for a Fastly challenge round."""
        challenges: list[ChallengeData] = config.challenges
        responses: list[ChallengeResponse] = []

        for challenge in challenges:
            challenge_type = str(challenge.get("ty", ""))

            match challenge_type:
                case ChallengeType.PAT:
                    responses.append(self._pat_provider.solve(context=context))

                case ChallengeType.POW:
                    responses.append(self._pow_provider.solve(challenge))

                case ChallengeType.CLIENT_METRICS:
                    responses.append(self._metrics_provider.solve())

                case ChallengeType.CAPTCHA:
                    raise FastlyChallengeNotSupportedError("; ".join([
                        "CAPTCHA challenge is unsupported",
                        extra_info(extra=config)]))


                case _:
                    raise FastlyChallengeError("; ".join([
                        f"unknown challenge type: {challenge_type}",
                        extra_info(extra=config)]))

        return responses
