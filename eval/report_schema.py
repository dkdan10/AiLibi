"""Typed per-tournament eval report schema (DESIGN.md §11.3, §11.4).

This module is the Phase 5 hub. Every metric module (vote correctness,
accusation calibration, alibi fabrication, cost dashboard), the tournament
integration, the dashboard, and the prompt-regression suite consume this one
typed artifact instead of re-scraping raw replay JSONL ad hoc (DESIGN.md
§11.3). Its field names and nesting are load-bearing: a rename after the
downstream metric modules ship forces a multi-way edit, which is why the
schema carries an explicit :data:`CURRENT_FORMAT_VERSION` marker from day one.

The report is an **aggregation layer**, not a from-scratch data model. The
data it carries already exists as typed per-game replay records written during
Phase 3/4 (DESIGN.md §11.4):

* :class:`orchestrator.replay.GameEndReplayEntry` -- the decisive winner and
  reason per game.
* :class:`orchestrator.replay.MeetingReplayEntry` -- per meeting: transcript,
  ballots, contradictions, outcome, ejected player, the per-call LLM records,
  and the prompt-template versions in play.
* :class:`orchestrator.replay.LLMCallRecord` -- per LLM call: model, token
  usage, USD cost, originating agent, call kind.
* :class:`orchestrator.replay.FailedCallReplayEntry` -- a meeting-aborting LLM
  call that failed schema validation: the model / token / USD-cost metadata for
  spend the provider already charged, recorded because the meeting crashed
  before a ``MeetingReplayEntry`` was written.

One required input is NOT in those replay records: the per-game **role ground
truth** (which players are impostors). The leak firewall keeps roles out of
agent-visible data, and the replay JSONL never persists them, but the Phase 5
meeting-quality metrics are defined as pure analyzers over *this* report
(DESIGN.md §11.3): vote correctness is ``roles[ejected] == "IMPOSTOR"`` (Task
5.2), accusation calibration needs the actual-impostor rate of accusation
targets (Task 5.3), and alibi fabrication counts impostor alibis (Task 5.4).
So :class:`GameReport` carries a ``roles`` map -- post-game ground truth the
loader (Task 5.6) fills from the seeded game setup, never exposed to agents --
so those metrics never re-derive engine state.

The leaf meeting artifact types (:class:`~meetings.schemas.MeetingTranscript`,
:class:`~meetings.schemas.VoteBallot`,
:class:`~meetings.schemas.ContradictionRef`,
:class:`~meetings.schemas.MeetingOutcome`,
:data:`~meetings.schemas.PlayerId`) and the per-call
:class:`~orchestrator.replay.LLMCallRecord` /
:data:`~orchestrator.replay.WinnerSide` alias are reused **by import** rather
than redefined, so there is exactly one definition of each payload and no
drift between the replay records and this report.

Three-level nesting -- tournament -> game -> meeting:

* :class:`TournamentReport` -- the top-level artifact, carrying the
  ``format_version`` and every game.
* :class:`GameReport` -- one game: decisive outcome, the final tick, the
  impostor/crewmate role ground truth, a reference to the game's replay file,
  the prompt-template versions in play, the per-game LLM cost roll-up, its
  meetings, and any meeting-aborting failed LLM calls (so their already-charged
  spend is not dropped).
* :class:`MeetingReport` -- one resolved meeting: the structured artifacts a
  metric reads (transcript, ballots, contradictions, outcome, ejected player)
  plus the per-call LLM telemetry.
* :class:`GameCostSummary` -- the per-game LLM cost / usage roll-up.

This task ships the schema, its format-version validator, and unit tests only.
It does NOT wire ``scripts/run_tournament.py`` to emit the report and does NOT
migrate ``eval.balance_eval.run_balance_eval``'s return type -- that
JSONL->report adapter and the ``BalanceReport`` migration land in Task 5.6.
Phase 5 metric outputs are likewise attached by downstream tooling that
*composes* over this report (e.g. wrapping it or keying results by
``GameReport.game_id``); they never mutate the raw per-game replay records.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)

from engine.entities import Role
from meetings.schemas import (
    ContradictionRef,
    MeetingOutcome,
    MeetingTranscript,
    PlayerId,
    VoteBallot,
)
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord, WinnerSide

# Current on-disk format of :class:`TournamentReport`. Bumped only when the
# schema changes shape in a way older readers cannot interpret. The version is
# namespaced to this report and is independent of the per-tick / per-meeting
# replay JSONL records in ``orchestrator.replay`` (see the PR's ``## Decisions``
# block): the report is a fresh artifact, so versioning it does not require
# touching the already-shipped replay entry models.
CURRENT_FORMAT_VERSION: Final[int] = 1


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base shared by every report model.

    Mirrors the conventions in :mod:`orchestrator.replay` and
    :mod:`meetings.schemas`: report artifacts are immutable value objects and
    an unexpected field is a bug, not something to silently absorb (AGENTS.md
    "no silent fallbacks").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")


class GameCostSummary(_FrozenModel):
    """Per-game LLM cost and token-usage roll-up (DESIGN.md §10.4, §11.3).

    Aggregates the per-call :class:`~orchestrator.replay.LLMCallRecord`
    telemetry captured across a game's meetings into the totals the cost
    dashboard (Task 5.5) reports. ``by_model`` keys the spend by the model id
    the adapter actually called so a mixed-tier game (e.g. Sonnet meetings plus
    Haiku triggers) is auditable per model. The per-call records remain
    available on each :class:`MeetingReport` for finer-grained analysis; this
    summary is the convenience reduction.
    """

    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    by_model: Mapping[str, float]


class MeetingReport(_FrozenModel):
    """One resolved meeting's structured artifacts (DESIGN.md §11.3, §11.4).

    Composes the metric-relevant payloads from
    :class:`orchestrator.replay.MeetingReplayEntry` without re-parsing JSONL.
    The leaf types are imported from :mod:`meetings.schemas` (transcript,
    ballots, contradictions, outcome) and :mod:`orchestrator.replay`
    (``llm_calls``), never redefined.

    Engine-determinism artifacts (the before/after state hashes on the replay
    entry) are intentionally omitted: they pin the engine-owned mutation for
    byte-identity replay, not anything a Phase 5 behavioral metric consumes.
    """

    meeting_id: str
    tick: int
    triggered_by: PlayerId
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    transcript: MeetingTranscript
    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...]
    llm_calls: tuple[LLMCallRecord, ...]


class GameReport(_FrozenModel):
    """One game's decisive outcome and meeting artifacts (DESIGN.md §11.3, §11.4).

    Composes :class:`orchestrator.replay.GameEndReplayEntry` (``winner`` /
    ``reason`` / ``tick``) with the game's meetings. ``winner`` is ``None`` for
    a non-decisive game (e.g. the tick budget was reached, or a partial/crashed
    run that never wrote a ``game_over`` record) -- matching
    :data:`orchestrator.replay.WinnerSide`'s nullability -- so the report stays
    faithful to a partial tournament rather than coercing an undecided game
    into a decisive bucket. ``final_tick`` carries
    :attr:`~orchestrator.replay.GameEndReplayEntry.tick` so the game-length
    distribution DESIGN.md §11.3 asks of balance eval is computable from this
    report alone; it is ``None`` for a game whose ``game_over`` record carried
    no tick (or was never written).

    ``roles`` is the post-game role ground truth: every player mapped to
    ``"CREWMATE"`` / ``"IMPOSTOR"`` (:data:`engine.entities.Role`). The replay
    JSONL never persists roles -- the leak firewall keeps them out of
    agent-visible data -- but the meeting-quality metrics (tasks 5.2-5.4) are
    pure analyzers over this report and need ``roles[player] == "IMPOSTOR"`` to
    judge whether an ejection/accusation was correct (DESIGN.md §11.3). The
    loader (Task 5.6) fills it from the seeded game setup; it is eval ground
    truth only and is never shown to an agent, so it does not touch the
    observation firewall.

    ``failed_calls`` carries the
    :class:`~orchestrator.replay.FailedCallReplayEntry` records for this game:
    LLM calls that aborted a meeting on schema-validation failure before a
    completed :class:`MeetingReport` could exist. They live at game level (not
    nested under a meeting, since that meeting never resolved) and are kept
    because the canonical cost reducer
    :func:`orchestrator.replay.compute_cost_usd` counts their already-charged
    tokens; dropping them would make the Task 5.5 cost metric undercount spend
    for any run where a meeting crashed. Empty for the common case where every
    meeting completed.

    ``replay_ref`` is the bare per-seed replay filename
    (``replay-seed-{seed}.jsonl``), matching how
    :func:`eval.balance_eval.run_balance_eval` names files; it is resolved
    relative to the tournament output directory by whichever tool reads it (the
    JSONL->report loader lands in Task 5.6). ``prompt_versions`` records the
    static prompt-template version markers in play for the game; the source
    records carry them per meeting, but templates are loaded once per run and
    do not change mid-game, so they collapse losslessly to game granularity --
    the level the cost dashboard (Task 5.5) and prompt-version provenance need.
    """

    game_id: str
    seed: int
    winner: WinnerSide | None
    reason: str
    final_tick: int | None
    roles: Mapping[PlayerId, Role]
    replay_ref: str
    meetings: tuple[MeetingReport, ...]
    failed_calls: tuple[FailedCallReplayEntry, ...]
    prompt_versions: Mapping[str, str]
    cost: GameCostSummary


class TournamentReport(_FrozenModel):
    """Top-level typed tournament artifact (DESIGN.md §11.3, §11.4).

    The single object Phase 5 tooling reads instead of scraping raw replay
    JSONL. ``games`` holds one :class:`GameReport` per recorded game and
    ``seeds_used`` lists every seed the tournament attempted. The two are equal
    in length for a complete run but ``len(games)`` may be smaller for a
    partial/crashed tournament (some seeds never produced a recorded game), so
    no cross-field equality is enforced here -- partial-run robustness is a
    stated Phase 5 requirement.

    This report supersedes :class:`eval.balance_eval.BalanceReport` as the
    typed tournament artifact (Pydantic is the project convention for
    cross-module DTOs; see the PR's ``## Decisions`` block). Everything
    ``BalanceReport`` carries is representable without information loss:
    ``games`` count = ``len(self.games)``; ``crew_wins`` / ``impostor_wins`` =
    games whose ``winner`` is ``"CREWMATES"`` / ``"IMPOSTORS"``;
    ``tick_budget_reached`` = games whose ``winner`` is ``None`` (with the
    specific reason preserved on ``GameReport.reason``); ``seeds_used`` maps
    directly. The actual ``run_balance_eval`` migration is deferred to Task
    5.6, which keeps this task a pure additive schema definition.

    ``format_version`` is validated fail-loud: an unknown future version (one
    greater than this build's :data:`CURRENT_FORMAT_VERSION`) raises rather
    than being coerced or warned past (AGENTS.md "no silent fallbacks"). A
    version below current is rejected too while no migration path exists -- for
    v1 there is no prior version, so only ``1`` is valid. ``format_version`` is
    a required field with no default: a report whose marker is entirely absent
    raises rather than silently defaulting to v1 (audit E-E-1), on every path
    that builds the report -- ``model_validate_json``, ``model_validate`` of a
    Python dict, in-process construction, and the same paths for a report
    nested under :class:`eval.meeting_quality.TournamentEvalReport`. A report
    that lost its marker is corrupt or foreign, not a v1 report; the writer
    (:mod:`eval.balance_eval`) stamps the current version explicitly on
    construction.
    """

    format_version: int
    games: tuple[GameReport, ...]
    seeds_used: tuple[int, ...]

    @model_validator(mode="before")
    @classmethod
    def _require_format_version(cls, data: Any) -> Any:
        """Reject any report whose ``format_version`` marker is absent.

        ``format_version`` is a required field with no default, so every path
        that produces a :class:`TournamentReport` -- in-process construction,
        ``model_validate`` of a Python dict, ``model_validate_json``, and the
        same paths for a report nested under
        :class:`eval.meeting_quality.TournamentEvalReport` -- must carry the
        marker. A mapping that lost it is corrupt or foreign; failing loud beats
        silently coercing it to v1 (AGENTS.md "no silent fallbacks"; audit
        E-E-1). The writer (:func:`eval.balance_eval.run_tournament_eval` /
        :func:`eval.balance_eval.load_tournament_report`) stamps the current
        version explicitly on construction.

        This raises a clear, report-specific error in place of Pydantic's
        generic "Field required", and runs in every validation mode: a missing
        key cannot be distinguished from a constructor default in ``"python"``
        mode, which is exactly why the field carries no default.
        """

        if isinstance(data, Mapping) and "format_version" not in data:
            raise ValueError(
                "missing report format_version: a TournamentReport without a "
                "format_version marker cannot be read safely. Every report this "
                f"build writes stamps version {CURRENT_FORMAT_VERSION}; one "
                "without it is corrupt or was written by an incompatible tool, "
                "so it is rejected rather than defaulted to v1."
            )
        return data

    @field_validator("format_version")
    @classmethod
    def _validate_format_version(cls, value: int) -> int:
        if value > CURRENT_FORMAT_VERSION:
            raise ValueError(
                f"unknown report format_version {value}: this build understands "
                f"report formats up to version {CURRENT_FORMAT_VERSION}. The "
                "report was written by a newer AiLibi; upgrade to read it."
            )
        if value < CURRENT_FORMAT_VERSION:
            raise ValueError(
                f"unsupported report format_version {value}: no migration path "
                f"from versions below {CURRENT_FORMAT_VERSION} exists yet, so "
                f"only version {CURRENT_FORMAT_VERSION} is currently valid."
            )
        return value


__all__ = [
    "CURRENT_FORMAT_VERSION",
    "GameCostSummary",
    "GameReport",
    "MeetingReport",
    "TournamentReport",
]
