"""Opt-in temporal perception version; legacy recordings omit the version."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final, Literal

ENV_TEMPORAL_OBSERVATIONS: Final[str] = "AILIBI_TEMPORAL_OBSERVATIONS"


def temporal_observations_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Enable source-time event delivery only when explicitly requested."""

    return temporal_observation_version(env) is not None


def temporal_observation_version(
    env: Mapping[str, str] | None = None,
) -> Literal[1, 2] | None:
    """Freeze an explicit interpretation; historical boolean ON selects v1."""

    values = os.environ if env is None else env
    value = values.get(ENV_TEMPORAL_OBSERVATIONS, "").strip().lower()
    if value in {"", "0", "false", "no", "off"}:
        return None
    if value in {"1", "true", "yes", "on"}:
        return 1
    if value == "2":
        return 2
    raise ValueError(f"unsupported temporal observation version: {value!r}")


def validate_temporal_version(value: object) -> Literal[1, 2] | None:
    if value is None:
        return None
    if type(value) is not int:
        raise ValueError("temporal observation version must be an integer")
    if value == 1:
        return 1
    if value == 2:
        return 2
    raise ValueError("unsupported temporal observation version")
