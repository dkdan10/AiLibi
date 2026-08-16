"""Tests for the relocated ranking-row contract (Task 19.19).

The defensive tests that lived inside the deleted ``tests/training/test_realpath.py``
(the ``-v3`` round-trip + the four invalid-proof cases), MOVED here so the
committed rankings' row contract keeps its coverage after the campaign machinery
retired. What changed is only where the row comes from: the deleted test built
one by RUNNING a re-rank; there is no re-rank any more, so these read the
COMMITTED bytes the contract actually has to keep validating — all 16 ``-v3``
crew rows, across the six committed ranking files that carry them. That makes
the round-trip a stronger claim than before: it is checked against every real
artifact row, not a fixture.

Also pins :class:`RealPathSeedTelemetry`'s validators. They relocated with the
row (the row carries the telemetry tuple) and were previously exercised only
through the campaign runner that built them, so without this they would land in
the surviving module untested.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from training.realpath_schema import (
    SCHEMA_VERSION,
    RealPathRerankRow,
    RealPathSeedTelemetry,
)

#: Every committed ranking file carrying ``-v3`` crew rows. The census over
#: every committed ``ranking*.jsonl`` finds exactly two shapes: 60 ``-v1``
#: impostor rows (which the generator validates through its own relaxed model,
#: because the frozen 18.24 corpus predates the two recorder-identity fields)
#: and these 16 ``-v3`` crew rows. The list is pinned rather than globbed, and
#: :func:`test_the_pinned_files_are_every_committed_v3_ranking` proves it stays
#: exhaustive — a new ``-v3`` artifact must fail loud, not slip past uncovered.
_ARTIFACT_ROOT = Path("training/artifacts/coevo")
_CREW_RANKINGS: tuple[Path, ...] = tuple(
    _ARTIFACT_ROOT / relative
    for relative in (
        "realpath-crew/run-c1-crew-owned-tasks/ranking-4000-4002.jsonl",
        "realpath-crew/run-c1-crew-owned-tasks/ranking-4003-4005.jsonl",
        "realpath-crew/run-c2-crew-general/ranking-4000-4002.jsonl",
        "realpath-crew/run-c2-crew-general/ranking-4003-4005.jsonl",
        "realpath-crew/run-c2-crew-general/stability-inputs-filtered/"
        "ranking-4000-4002.jsonl",
        "realpath-crew/run-c2-crew-general/stability-inputs-filtered/"
        "ranking-4003-4005.jsonl",
    )
)

#: The row the shape/validator cases mutate. One file's first row is enough for
#: those — they assert on the MODEL's behaviour, not on corpus breadth, which
#: :func:`test_committed_v3_rows_round_trip` covers over all of them.
_CANONICAL_CREW_RANKING = _CREW_RANKINGS[1]


def _rows_of(path: Path) -> list[str]:
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    assert lines, f"{path} carries no rows"
    return lines


def _committed_rows() -> list[str]:
    return [line for path in _CREW_RANKINGS for line in _rows_of(path)]


def _crew_payload() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(_rows_of(_CANONICAL_CREW_RANKING)[0])
    return payload


# --------------------------------------------------------------------------- #
# Round-trip: the committed bytes validate and re-serialize identically         #
# --------------------------------------------------------------------------- #


def test_the_pinned_files_are_every_committed_v3_ranking() -> None:
    """The pin is exhaustive: no committed ``-v3`` row escapes the round-trip.

    Without this, a new crew ranking could land carrying rows nothing validates
    — the round-trip below would still pass while covering less than it claims.
    """

    discovered = {
        path
        for path in sorted(_ARTIFACT_ROOT.rglob("ranking*.jsonl"))
        for line in _rows_of(path)
        if json.loads(line)["schema_version"] == SCHEMA_VERSION
    }
    assert discovered == set(_CREW_RANKINGS)
    assert len(_committed_rows()) == 16


def test_committed_v3_rows_round_trip() -> None:
    """Every committed ``-v3`` row validates STRICTLY and re-serializes to itself.

    ``to_json_line`` is the committed row form (key-sorted JSONL), so a
    round-trip that drifts by one key or one coerced type would change the bytes
    a downstream table joins on.
    """

    for line in _committed_rows():
        row = RealPathRerankRow.model_validate_json(line, strict=True)
        assert row.schema_version == SCHEMA_VERSION
        assert json.loads(row.to_json_line()) == json.loads(line)
        # A crew row carries the crew-side proof block, populated.
        assert row.crew_stamp is not None
        assert row.crew_stamp_verified_games >= 1
        assert row.seed_telemetry


def test_the_v3_row_carries_both_arms_field_sets() -> None:
    payload = _crew_payload()
    assert payload["schema_version"] == "realpath-rerank-v3"
    assert set(payload) >= {
        "crew_stamp",
        "crew_stamp_equals_computed_digest",
        "crew_stamp_uniform",
        "crew_stamp_verified_games",
        "opponent_stamp",
        "opponent_weights_sha256",
    }


def test_an_impostor_row_keeps_the_v2_shape_with_every_crew_field_empty() -> None:
    """The crew arm is additive-optional: never populated by default.

    An impostor-only row keeps the exact ``-v2`` shape apart from the version
    string. Built by clearing the crew/opponent block off a committed row, so
    the assertion is about the MODEL's defaults, not about a fixture's spelling.
    """

    impostor = RealPathRerankRow.model_validate(
        {
            **_crew_payload(),
            "crew_stamp": None,
            "crew_stamp_verified_games": 0,
            "crew_stamp_uniform": False,
            "crew_stamp_equals_computed_digest": False,
            "opponent_stamp": None,
            "opponent_weights_sha256": None,
        }
    )
    assert impostor.crew_stamp is None
    assert impostor.crew_stamp_verified_games == 0
    assert impostor.crew_stamp_uniform is False
    assert impostor.crew_stamp_equals_computed_digest is False
    assert impostor.opponent_weights_sha256 is None
    assert impostor.opponent_stamp is None


# --------------------------------------------------------------------------- #
# Invalid proofs: the two sides' blocks may never contradict each other         #
# --------------------------------------------------------------------------- #


def test_a_crew_proof_without_a_crew_stamp_is_refused() -> None:
    """A crew proof with no crew stamp claims an identity nothing proved."""

    payload = _crew_payload()
    with pytest.raises(ValidationError, match="no crew_stamp carries no crew proof"):
        RealPathRerankRow.model_validate(
            {**payload, "crew_stamp": None, "crew_stamp_verified_games": 2}
        )


def test_a_crew_stamp_with_zero_verified_games_is_refused() -> None:
    """The mirror claim: a stamp is READ BACK from bytes, so bytes must exist."""

    payload = _crew_payload()
    with pytest.raises(ValidationError, match="at least one decisive game"):
        RealPathRerankRow.model_validate({**payload, "crew_stamp_verified_games": 0})


def test_a_half_present_opponent_identity_is_refused() -> None:
    """The frozen opponent's identity is whole or absent, never half-declared."""

    payload = _crew_payload()
    with pytest.raises(ValidationError, match="whole or absent"):
        RealPathRerankRow.model_validate({**payload, "opponent_stamp": None})


def test_an_opponent_stamp_disagreeing_with_its_digest_is_refused() -> None:
    """A stamp names the bytes it was frozen from (the 17.14 conflation guard)."""

    payload = _crew_payload()
    with pytest.raises(ValidationError, match="17.14 conflation guard"):
        RealPathRerankRow.model_validate(
            {**payload, "opponent_weights_sha256": "0" * 64}
        )


# --------------------------------------------------------------------------- #
# The telemetry element's own validators (relocated with the row)               #
# --------------------------------------------------------------------------- #


def _telemetry(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "seed": 4003,
        "attempts": 1,
        "timed_out_attempts": 0,
        "degraded_recordings": 0,
        "tick_budget_reached": False,
        "error_types": [],
        "wall_seconds": 1.5,
        "resumed": False,
    }
    base.update(overrides)
    return base


def test_committed_telemetry_elements_validate() -> None:
    for line in _committed_rows():
        for element in json.loads(line)["seed_telemetry"]:
            assert RealPathSeedTelemetry.model_validate(element).seed >= 0


def test_error_types_records_one_entry_per_failed_attempt() -> None:
    assert (
        RealPathSeedTelemetry.model_validate(
            _telemetry(attempts=3, error_types=["TimeoutError", "RuntimeError"])
        ).attempts
        == 3
    )
    with pytest.raises(ValidationError, match="one entry per failed attempt"):
        RealPathSeedTelemetry.model_validate(
            _telemetry(attempts=3, error_types=["TimeoutError"])
        )


def test_a_recorded_element_attempts_at_least_once() -> None:
    with pytest.raises(ValidationError, match="attempts must be >= 1"):
        RealPathSeedTelemetry.model_validate(_telemetry(attempts=0))


def test_a_resumed_element_records_no_attempt() -> None:
    """``resumed`` means this invocation recorded nothing — honest counters."""

    resumed = RealPathSeedTelemetry.model_validate(
        _telemetry(attempts=0, resumed=True, wall_seconds=0.25)
    )
    assert resumed.resumed
    assert resumed.attempts == 0

    with pytest.raises(ValidationError, match="attempts no recording"):
        RealPathSeedTelemetry.model_validate(_telemetry(attempts=1, resumed=True))
    with pytest.raises(ValidationError, match="records no failed attempt"):
        RealPathSeedTelemetry.model_validate(
            _telemetry(attempts=0, resumed=True, error_types=["TimeoutError"])
        )


def test_a_tick_budget_element_is_never_resumable() -> None:
    """A capped replay has no ``game_over`` row, so it can never resume."""

    with pytest.raises(ValidationError, match="never resumable"):
        RealPathSeedTelemetry.model_validate(
            _telemetry(attempts=0, resumed=True, tick_budget_reached=True)
        )


def test_counters_and_wall_clock_are_non_negative() -> None:
    with pytest.raises(ValidationError, match="counters must be >= 0"):
        RealPathSeedTelemetry.model_validate(_telemetry(timed_out_attempts=-1))
    with pytest.raises(ValidationError, match="wall_seconds must be >= 0"):
        RealPathSeedTelemetry.model_validate(_telemetry(wall_seconds=-0.1))


def test_the_models_are_frozen_and_forbid_extras() -> None:
    row = RealPathRerankRow.model_validate(_crew_payload())
    with pytest.raises(ValidationError):
        row.rank = 99
    with pytest.raises(ValidationError):
        RealPathRerankRow.model_validate({**_crew_payload(), "unexpected": 1})
    with pytest.raises(ValidationError):
        RealPathSeedTelemetry.model_validate(_telemetry(unexpected=1))
