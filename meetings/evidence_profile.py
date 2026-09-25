"""Immutable, explicitly bound versions of meeting evidence experiments."""

from __future__ import annotations

import os
from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, field_validator

EvidenceVersion = Literal[1, 2]

EVIDENCE_REASONING_ENV: Final = "AILIBI_EVIDENCE_REASONING"
BOUNDED_REBUTTAL_ENV: Final = "AILIBI_BOUNDED_REBUTTAL"
PUBLIC_ACCOUNTS_ENV: Final = "AILIBI_PUBLIC_ACCOUNTS"
ATTRIBUTED_TESTIMONY_ENV: Final = "AILIBI_ATTRIBUTED_TESTIMONY"

#: The registry of independently versioned meeting experiments: each ambient
#: env switch and the :class:`MeetingEvidenceProfile` field it resolves. The
#: resolvers below read these names, so a rename here moves the switch itself
#: -- and ``scripts/check_doc_facts.py`` holds ``.env.example`` to this
#: registry, the way it already holds it to the substrate-lever registry, so a
#: switch cannot be renamed, dropped or misspelled in the template unnoticed.
EXPERIMENT_ENV_NAMES: Final[Mapping[str, str]] = MappingProxyType(
    {
        EVIDENCE_REASONING_ENV: "evidence_reasoning_version",
        BOUNDED_REBUTTAL_ENV: "bounded_rebuttal_version",
        PUBLIC_ACCOUNTS_ENV: "public_account_version",
        ATTRIBUTED_TESTIMONY_ENV: "attributed_testimony_version",
    }
)


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
    if source.get(EVIDENCE_REASONING_ENV, "").strip() == "2":
        return 2
    return 1 if _enabled(EVIDENCE_REASONING_ENV, source) else None


def bounded_rebuttal_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Resolve the independently opt-in additional-reply experiment."""

    return _enabled(BOUNDED_REBUTTAL_ENV, env)


#: Profile fields no environment switch resolves: a declared experiment config
#: is their only source, through :func:`profile_from_config`.
CONFIG_ONLY_PROFILE_FIELDS: Final[tuple[str, ...]] = (
    "ballot_kill_row_version",
    "impostor_ballot_version",
)


class MeetingEvidenceProfile(BaseModel):
    """Versions captured before work begins; ``None`` preserves recorded behavior."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_reasoning_version: EvidenceVersion | None = None
    bounded_rebuttal_version: Literal[1] | None = None
    public_account_version: Literal[1] | None = None
    attributed_testimony_version: Literal[1] | None = None
    ballot_kill_row_version: Literal[1] | None = None
    impostor_ballot_version: Literal[1] | None = None

    @field_validator(
        "evidence_reasoning_version",
        "bounded_rebuttal_version",
        "public_account_version",
        "attributed_testimony_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
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
        """Capture the four switches from one environment snapshot.

        The :data:`CONFIG_ONLY_PROFILE_FIELDS` have no switch and stay ``None``
        here whatever the environment holds.
        """

        source = dict(os.environ if env is None else env)
        return cls(
            evidence_reasoning_version=evidence_reasoning_version(source),
            bounded_rebuttal_version=1 if bounded_rebuttal_enabled(source) else None,
            public_account_version=1 if _enabled(PUBLIC_ACCOUNTS_ENV, source) else None,
            attributed_testimony_version=1
            if _enabled(ATTRIBUTED_TESTIMONY_ENV, source)
            else None,
        )


def profile_from_config(values: Mapping[str, object]) -> MeetingEvidenceProfile:
    """The profile a declared experiment config selects, from its meeting values.

    ``values`` carries exactly this profile's fields: the orchestrator selects
    them from the recorded config by its field-layer classification, so this
    package never imports the wiring module. A missing or extra field raises
    rather than defaulting, since the two field sets must stay equal.
    """

    expected = set(MeetingEvidenceProfile.model_fields)
    if set(values) != expected:
        raise ValueError(
            "meeting values disagree with the profile's fields: missing "
            f"{sorted(expected - set(values))}, unknown {sorted(set(values) - expected)}"
        )
    return MeetingEvidenceProfile.model_validate(dict(values))
