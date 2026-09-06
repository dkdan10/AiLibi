"""Immutable, explicitly bound versions of meeting evidence experiments."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

EvidenceVersion = Literal[1, 2]


def _enabled(name: str, env: Mapping[str, str] | None) -> bool:
    source = os.environ if env is None else env
    value = source.get(name, "").strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"", "0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} requires a boolean switch, got {value!r}")


def evidence_reasoning_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Resolve the opt-in evidence-context and memory experiment."""

    return evidence_reasoning_version(env) is not None


def evidence_reasoning_version(
    env: Mapping[str, str] | None = None,
) -> EvidenceVersion | None:
    """Keep old true/1 selections on v1; v2 requires an explicit 2."""
    source = os.environ if env is None else env
    if source.get("AILIBI_EVIDENCE_REASONING", "").strip() == "2":
        return 2
    return 1 if _enabled("AILIBI_EVIDENCE_REASONING", source) else None


def bounded_rebuttal_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Resolve the independently opt-in additional-reply experiment."""

    return _enabled("AILIBI_BOUNDED_REBUTTAL", env)


class MeetingEvidenceProfile(BaseModel):
    """Versions captured before work begins; ``None`` preserves recorded behavior."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_reasoning_version: EvidenceVersion | None = None
    bounded_rebuttal_version: Literal[1] | None = None
    public_account_version: Literal[1] | None = None
    attributed_testimony_version: Literal[1] | None = None

    @field_validator(
        "evidence_reasoning_version",
        "bounded_rebuttal_version",
        "public_account_version",
        "attributed_testimony_version",
        mode="before",
    )
    @classmethod
    def _versions_are_integers(cls, value: object) -> object:
        if value is not None and type(value) is not int:
            raise ValueError("evidence versions must be integer version numbers")
        return value

    @classmethod
    def from_environment(
        cls, env: Mapping[str, str] | None = None
    ) -> MeetingEvidenceProfile:
        """Capture both switches from one environment snapshot."""

        source = dict(os.environ if env is None else env)
        return cls(
            evidence_reasoning_version=evidence_reasoning_version(source),
            bounded_rebuttal_version=1 if bounded_rebuttal_enabled(source) else None,
            public_account_version=1
            if _enabled("AILIBI_PUBLIC_ACCOUNTS", source)
            else None,
            attributed_testimony_version=1
            if _enabled("AILIBI_ATTRIBUTED_TESTIMONY", source)
            else None,
        )
