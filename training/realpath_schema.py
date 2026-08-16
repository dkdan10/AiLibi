"""The committed re-rank ranking-row contract (Task 19.19).

The row schema of the 18.17/18.31/18.32 real-path re-rank campaigns, RELOCATED
here when Task 19.19 retired the campaign machinery (``training/realpath.py``,
the one-shot ops surface, and its test file). The campaigns concluded; their
RANKINGS are committed under ``training/artifacts/coevo/realpath*/`` and are
still read — by ``scripts/generate_campaign_tables.py`` (the §4.0 stability
table it reproduces into ``measurement-stability.json``) and by the reports that
cite those numbers. So the row contract outlives the machinery that wrote it,
validators and all: this module is the complete dependency closure the committed
bytes need to round-trip and be re-validated, and nothing more.

Nothing here records anything. There is no runner, no provider, no filesystem
work — a reader validates committed JSONL against these models and the proof
blocks either hold or fail loud. The wall-clock, retry, resume, tranche-claim
and pre-screen machinery retired with ``training/realpath.py``; recover it from
git history if a future campaign needs it (the last version is the commit that
deleted it).

Public surface (stable — downstream tasks import these):
:class:`RealPathRerankRow`, :class:`RealPathSeedTelemetry`.
"""

from __future__ import annotations

import json
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from eval.validity import ValidityGateReport
from eval.watchability import WatchabilityReport
from orchestrator.replay import CrewTacticalPolicyStamp, TacticalPolicyStamp

#: The row schema the committed rankings declare. ``-v3`` (Task 18.32) is the
#: tip: it adds the CREW arm's fields, all additive and optional. The
#: ``-v1`` / ``-v2`` predecessors are handled by the reader
#: (``scripts/generate_campaign_tables.py`` relaxes the two recorder-identity
#: fields for ``-v1``), never by a second model here.
SCHEMA_VERSION: Final[str] = "realpath-rerank-v3"


class RealPathSeedTelemetry(BaseModel):
    """Per-seed recording telemetry (frozen, extra='forbid').

    ``attempts`` is the total attempts (>= 1) including the successful one;
    ``error_types`` is the failed-attempt exception class names in order, so
    ``len(error_types) == attempts - 1``. ``degraded_recordings`` counts normal
    returns whose replay carried NO ``game_over`` stamp (the real-provider
    parse-fold abort case). ``tick_budget_reached`` marks the accepted
    non-decisive outcome: the game hit the scheduler cap, so its replay has no
    ``game_over`` row (and no stamp bytes) BY DESIGN — never retried, and
    excluded from stamp verification. ``wall_seconds`` is cumulative monotonic
    time across all attempts, rounded to 3 places.

    ``resumed`` (Task 18.31) marks an element the recording invocation did NOT
    record: a pre-existing replay that satisfied the whole conjunctive resume
    predicate. Such an entry carries ``attempts=0`` (honest — no recording was
    attempted), empty counters, and ``tick_budget_reached=False``: a capped
    replay has no ``game_over`` row, so it can never satisfy the predicate.
    ``wall_seconds`` is then the verification cost.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    attempts: int
    timed_out_attempts: int
    degraded_recordings: int
    tick_budget_reached: bool
    error_types: tuple[str, ...]
    wall_seconds: float
    resumed: bool = False

    @model_validator(mode="after")
    def _validate(self) -> RealPathSeedTelemetry:
        if self.resumed:
            if self.attempts != 0:
                raise ValueError(
                    f"a resumed element attempts no recording; got "
                    f"attempts={self.attempts!r}"
                )
            if self.error_types:
                raise ValueError(
                    "a resumed element records no failed attempt; got "
                    f"error_types={self.error_types!r}"
                )
            if self.tick_budget_reached:
                raise ValueError(
                    "a tick-budget replay carries no game_over stamp and is "
                    "therefore never resumable; got tick_budget_reached=True"
                )
        elif self.attempts < 1:
            raise ValueError(f"attempts must be >= 1; got {self.attempts!r}")
        if len(self.error_types) != max(self.attempts - 1, 0):
            raise ValueError(
                "error_types must record one entry per failed attempt "
                f"(len == attempts - 1); got {len(self.error_types)} entries for "
                f"attempts={self.attempts!r}"
            )
        for count in (self.timed_out_attempts, self.degraded_recordings):
            if count < 0:
                raise ValueError("attempt counters must be >= 0")
        if self.wall_seconds < 0:
            raise ValueError(f"wall_seconds must be >= 0; got {self.wall_seconds!r}")
        return self


class RealPathRerankRow(BaseModel):
    """One candidate's committed ranking row (frozen, extra='forbid').

    ``stamp`` is the READ-BACK stamp (recovered from the recorded bytes), never
    the in-memory launch stamp; ``stamp_verified_games`` counts the DECISIVE
    games whose bytes proved it (a tick-budget game has no ``game_over`` row and
    is excluded — see ``seed_telemetry``'s ``tick_budget_reached``). Core
    metrics are flattened scalars (no ``scripts/`` type in the row schema); a
    ``float | None`` core field stays ``None`` when its denominator is empty and
    is never coerced to ``0.0``.

    ``realpath-rerank-v3`` (Task 18.32) adds the CREW arm's fields, all additive
    and optional, so an impostor-only row keeps its exact ``-v2`` shape apart
    from the version string. The two sides of a recording keep DISTINCT homes,
    because that is what stops one identity being re-read as the other's (the
    18.19 conflation guard, read-side):

    * ``stamp`` / ``stamp_verified_games`` / ``stamp_uniform`` /
      ``stamp_equals_computed_digest`` remain the IMPOSTOR-side read-back proof.
      On an impostor leg that is the candidate, unchanged. On a CREW leg it is
      the frozen opponent when one is installed; with no opponent the impostor
      side IS the scripted FSM, so the row carries
      :func:`~orchestrator.replay.fsm_default_tactical_policy_stamp` with
      ``stamp_verified_games == 0`` — an absent stamp MEANS the FSM default
      (replay.py), and the recorder proved the absence rather than assuming it;
    * ``crew_stamp`` / ``crew_stamp_verified_games`` / ``crew_stamp_uniform`` /
      ``crew_stamp_equals_computed_digest`` are the CREW-side twins, populated
      only on a crew leg (``None`` / ``0`` / ``False`` on an impostor leg, where
      the recorder PROVED no crew stamp was written);
    * ``opponent_weights_sha256`` / ``opponent_stamp`` are the DECLARED identity
      of the frozen opponent artifact — the sha-verified sidecar digest and the
      artifact's own ``stamp.json``. They are not a duplicate of ``stamp``: that
      one is read back from the recorded bytes, these are what the leg loaded,
      and the recorder required them to agree.

    ``weights_sha256`` is always THE CANDIDATE's computed genome digest, on
    either side — it is the arm key every downstream table joins on.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = SCHEMA_VERSION
    label: str
    mode: str
    generation_indices: tuple[int, ...]
    stamp: TacticalPolicyStamp
    weights_sha256: str
    stamp_verified_games: int
    stamp_uniform: bool
    stamp_equals_computed_digest: bool
    #: WHO recorded these bytes and on WHAT topology (Task 18.31, ``-v2``). The
    #: leg manifest already carried both, but a manifest lives beside the
    #: recordings and a ranking row travels alone: two tranche rankings written
    #: into one leg directory by separate calls could use different providers,
    #: prompt sets, custom runners or maps while agreeing on every protocol
    #: field, and the §4.0 stability table would then report that behavioural
    #: change as provider/seed noise (Codex review on PR #314). The backend
    #: digest hashes the whole identity mapping; the map sha is carried
    #: separately because the topology is the one protocol axis a reader is
    #: likely to want to compare without reconstructing the identity.
    recording_backend_sha256: str
    game_map_sha256: str
    seeds: tuple[int, ...]
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    max_ticks: int
    baseline_id: str
    meeting_timeout_seconds: float
    max_attempts: int
    seed_telemetry: tuple[RealPathSeedTelemetry, ...]
    validity: ValidityGateReport
    watchability: WatchabilityReport
    core_games_total: int
    core_impostor_win_rate: float
    core_ejection_accuracy: float | None
    core_genuine_class_conversion: float | None
    core_meeting_rate: float | None
    validity_passed: bool
    referee_passed: bool
    selection_score: float
    rank: int
    #: The CREW arm (Task 18.32, ``-v3``), additive and optional throughout.
    crew_stamp: CrewTacticalPolicyStamp | None = None
    crew_stamp_verified_games: int = 0
    crew_stamp_uniform: bool = False
    crew_stamp_equals_computed_digest: bool = False
    #: The FROZEN OPPONENT installed in the impostor slot for every candidate in
    #: this leg (``None`` = the scripted-FSM comparator cell).
    opponent_weights_sha256: str | None = None
    opponent_stamp: TacticalPolicyStamp | None = None

    @model_validator(mode="after")
    def _validate(self) -> RealPathRerankRow:
        # A row states which side it ranks, and the two sides' proof blocks must
        # not contradict each other: a crew stamp with zero verified games would
        # claim an identity nothing on disk proved, and an opponent digest that
        # disagrees with its own stamp is the 17.14 conflation defect in the
        # committed artifact rather than in the recording.
        if self.crew_stamp is None:
            if self.crew_stamp_verified_games or self.crew_stamp_uniform:
                raise ValueError(
                    "a row with no crew_stamp carries no crew proof; got "
                    f"crew_stamp_verified_games={self.crew_stamp_verified_games!r}, "
                    f"crew_stamp_uniform={self.crew_stamp_uniform!r}"
                )
            if self.crew_stamp_equals_computed_digest:
                raise ValueError(
                    "a row with no crew_stamp cannot claim its crew digest was "
                    "verified against the computed genome digest"
                )
        elif self.crew_stamp_verified_games < 1:
            raise ValueError(
                "a crew_stamp is READ BACK from bytes, so a row carrying one "
                "names at least one decisive game that proved it; got "
                f"crew_stamp_verified_games={self.crew_stamp_verified_games!r}"
            )
        if (self.opponent_stamp is None) != (self.opponent_weights_sha256 is None):
            raise ValueError(
                "the frozen opponent's identity is whole or absent; got "
                f"opponent_weights_sha256={self.opponent_weights_sha256!r}, "
                f"opponent_stamp={self.opponent_stamp!r}"
            )
        if (
            self.opponent_stamp is not None
            and self.opponent_stamp.weights_sha256 != self.opponent_weights_sha256
        ):
            raise ValueError(
                "the frozen opponent's stamp names "
                f"{self.opponent_stamp.weights_sha256!r} but the row records "
                f"{self.opponent_weights_sha256!r}; a stamp names the bytes it "
                "was frozen from (the 17.14 conflation guard)"
            )
        return self

    def to_json_line(self) -> str:
        """Serialize to a single, key-sorted JSONL line (the committed row form)."""

        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


__all__ = [
    "SCHEMA_VERSION",
    "RealPathRerankRow",
    "RealPathSeedTelemetry",
]
