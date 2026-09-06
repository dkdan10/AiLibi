"""Opt-in temporal perception version; legacy recordings omit the version."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final

ENV_TEMPORAL_OBSERVATIONS: Final[str] = "AILIBI_TEMPORAL_OBSERVATIONS"


def temporal_observations_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Enable source-time event delivery only when explicitly requested."""

    values = os.environ if env is None else env
    return values.get(ENV_TEMPORAL_OBSERVATIONS, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
