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
from typing import Any, Final, Literal

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
# replay JSONL records in ``orchestrator.replay`` (decision 10, DESIGN.md
# §11.4): the report is a fresh artifact, so versioning it does not require
# touching the already-shipped replay entry models -- those reject a stale or
# foreign replay via the per-tick ``state_hash`` plus the per-set
# ``roster.json`` sidecar, not a ``format_version`` field (see
# :mod:`orchestrator.replay`).
#
# v1 -> v2 (Task 8.11): the meeting-chain reshape (Tasks 8.7 / 8.10) changed the
# shape of :attr:`MeetingReport.transcript`, so a v1 report cannot be read under
# this model. The bump makes :meth:`TournamentReport._validate_format_version`
# reject every committed v1 ``tournament-eval-report.json`` fail-loud with no
# back-migration, which is why Task 8.12 regenerates the committed reports + the
# prompt-regression ``baseline.json`` in the same coordinated re-record.
#
# Task 9.6 (metric hygiene) STAYS at 2: it adds the conversion-leads block to
# :class:`eval.meeting_quality.TournamentEvalReport` -- the un-versioned metric
# WRAPPER -- and changes nothing in the persisted report tree this marker
# versions. Per the DESIGN.md §11.4 policy the version bumps only when older
# readers cannot interpret the shape; wrapper-level aggregates over an
# unchanged inner report do not qualify (the W0.3 ``meeting_rate`` precedent),
# and 9.6 regenerates every committed report in the same PR, so no pre-9.6
# wrapper JSON survives to be read.
#
# Task 10.4 (Phase-10 gate metrics) STAYS at 2 by the same rule: the
# ``gate_metrics`` block is another wrapper-level aggregate over the unchanged
# inner report (no persisted report/replay field changes shape), and both
# committed reports plus the prompt-regression baseline are regenerated in the
# same PR, so no pre-10.4 wrapper JSON survives to be read.
CURRENT_FORMAT_VERSION: Final[int] = 2


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

    ``trigger`` is the engine-recorded reason the meeting opened
    (:attr:`engine.events.MeetingTriggeredEvent.trigger`): ``"report"`` (a body
    was reported) or ``"emergency"`` (the emergency button). The replay row
    (:class:`orchestrator.replay.MeetingReplayEntry`) does not carry it, so the
    loader (:func:`eval.balance_eval._meeting_report_from_entry`) reconstructs it
    from the triggering ``report`` / ``emergency`` action recorded in the
    trigger-tick's per-tick replay row -- authoritative and equivalent to the
    engine event, never the agent's self-reported ``FoundBodyObservation``. The
    meeting-rate metric (:func:`eval.meeting_quality.compute_meeting_rate`) reads
    this field directly for its trigger breakdown.

    Engine-determinism artifacts (the before/after state hashes on the replay
    entry) are intentionally omitted: they pin the engine-owned mutation for
    byte-identity replay, not anything a Phase 5 behavioral metric consumes.
    """

    meeting_id: str
    tick: int
    triggered_by: PlayerId
    trigger: Literal["report", "emergency"]
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

    Kill-gifted win accounting (Task 8.17; DESIGN.md §3.5; audit gp-4 / A-A-1 /
    B-B-7). The §3.5 dead-owner drop rule means each impostor kill removes the
    victim's incomplete task instances, so a kill can itself complete the crew
    task pool and win the game *for* the crew on the kill tick -- a
    friendly-fire-class self-sabotage the impostor build is (by owner decision)
    not yet made task-aware about. The drop rule is KEPT; the report instead
    makes the artifact measurable so a balance read uses the kill-gifted split,
    never the raw crew win rate alone. Three additive, defaulted facts derived
    deterministically from an engine walk of this game's replay
    (:func:`eval.balance_eval._kill_gift_accounting`):

    * ``kill_gifted`` -- ``True`` iff the winner is ``CREWMATES`` by
      ``CREWMATE_TASKS`` AND the game-over tick resolved a kill AND no task
      instance completed on that tick. A tick where a kill and a task
      completion *both* resolve is NOT kill-gifted -- the task completion is
      treated as decisive (the alternative attribution is a Wave-1 priced
      question, not this field's). ``False`` for organic task wins, every
      non-``CREWMATE_TASKS`` outcome, and partial / non-decisive games.
    * ``instances_dropped`` -- the seeded instance count minus the live
      instance count at game end (``len(state.tasks)``): how many of the
      crew's task instances the opponent's kills removed from the denominator
      over the whole game (set-wide this was 222/700 = 31.7% in the gp-4 set).
    * ``instances_complete_at_win`` -- the number of completed instances still
      in ``state.tasks`` at game end (the audit's "completed-at-win",
      mean 10.1/14 over task wins).

    All three default (``False`` / ``0`` / ``0``) so a report serialized before
    this task -- a committed pre-fields v2 report -- still validates under
    ``extra="forbid"`` (a missing field with a default is permitted; only an
    *unknown* field is rejected). Task 8.18 regenerates the committed reports so
    the fields are populated from the re-recorded replays.
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
    kill_gifted: bool = False
    instances_dropped: int = 0
    instances_complete_at_win: int = 0


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
    version below current is rejected too while no migration path exists -- the
    v1 -> v2 bump (Task 8.11, for the §5.2 meeting-chain transcript reshape)
    ships no back-migration, so a committed v1 report is rejected fail-loud and
    only ``2`` is valid (Task 8.12 regenerates the committed reports to v2).
    ``format_version`` is a required field with no default: a report whose
    marker is entirely absent raises rather than silently defaulting (audit
    E-E-1), on every path that builds the report -- ``model_validate_json``,
    ``model_validate`` of a Python dict, in-process construction, and the same
    paths for a report nested under
    :class:`eval.meeting_quality.TournamentEvalReport`. A report that lost its
    marker is corrupt or foreign, not a v1 report; the writer
    (:mod:`eval.balance_eval`) stamps the current version explicitly on
    construction.

    Kill-gifted win accounting -- aggregates (Task 8.17; DESIGN.md §3.5; audit
    gp-4). Three additive, defaulted roll-ups of the per-game
    :class:`GameReport` kill-gift facts, so a balance read sees the kill-gifted
    split at tournament granularity without re-walking every game:

    * ``kill_gifted_wins`` -- how many games are ``kill_gifted`` (the count to
      subtract from the raw crew-win rate to read organic crew wins; 12/37 in
      the gp-4 set).
    * ``instances_dropped_total`` -- the sum of per-game ``instances_dropped``
      across the tournament (222 over the gp-4 set's 700 seeded instances).
    * ``mean_instances_complete_at_win`` -- the mean of
      ``instances_complete_at_win`` over the ``CREWMATE_TASKS`` *wins* (the
      games the metric is about), or ``None`` when the tournament had no such
      win -- the same "undefined, not 0.0" sentinel
      :class:`~eval.meeting_quality.MeetingRateReport` uses for an empty
      denominator.

    The roll-ups are computed by the writer (:mod:`eval.balance_eval`) from
    ``games`` at construction; they are NOT cross-validated against ``games``
    here. A committed pre-fields report's per-game facts all default, so its
    roll-ups also default (``0`` / ``0`` / ``None``) and stay self-consistent;
    enforcing a recompute would reject such a report (a defaulted ``None`` mean
    can never equal a recomputed ``0.0`` over the present-but-defaulted task
    wins), which is exactly the backward-compat load Task 8.17 must preserve.

    Instrument blocks live in their own modules, not here. The solvability
    ceiling is :class:`eval.solvability.SolvabilityReport`, reached through
    ``scripts/measure_baseline.py --solvability``, because this model is mirrored
    twice and a new field must be added to both mirrors in the same change: a
    defaulted field is dumped as ``null`` by ``model_dump(mode="json")`` and the
    ``extra="forbid"`` view at ``api/routes/eval.py::_TournamentReportEvalView``
    rejects it on the re-validation that serves ``/eval/tournament-report``,
    while an ``exclude=True`` field still appears in ``model_json_schema()`` and
    so still trips ``tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS``. The
    field-set tripwire in ``tests/eval/test_report_schema.py`` is what makes that
    obligation loud instead of a 500 in production.
    """

    format_version: int
    games: tuple[GameReport, ...]
    seeds_used: tuple[int, ...]
    kill_gifted_wins: int = 0
    instances_dropped_total: int = 0
    mean_instances_complete_at_win: float | None = None

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
