"""The HARD validity gate — composed pass/fail checks over a replay-set dir.

Task 15.1 (tasks/phase-15.md) productizes the audit-cited ``validity_gate.py``
(audits/audit-phase-14-close.md §1, §3, §8; audits/post-phase-14-pause.md §2.1;
tasks/post-phase-14-clean-up.md H1). This module is the LIBRARY FOLD behind the
two CLIs — ``scripts/validity_gate.py`` (hard pass/fail) and
``scripts/measure_baseline.py`` (the R-gate measurement, which reuses the
loaders here). It WIRES the existing committed folds; it never re-implements a
metric that already has a tested home:

* meeting rate — :func:`eval.meeting_quality.compute_meeting_rate`
* win-condition self-check — :mod:`eval.win_condition_selfcheck`
* tournament assembly — :func:`eval.balance_eval.load_tournament_report`
* byte-identity walk — ``scripts/_verify_samples.py`` (the machinery behind it)

Every check is PURE and OFFLINE: the whole gate runs on a fresh clone with no
network and no ``AILIBI_*`` env. Roles ground truth is recovered by re-seeding
the engine from each replay's seed (the deterministic recipe
``scripts/build_sample_report.py`` uses to BUILD the committed report), so the
gate depends only on the committed ``replay-seed-*.jsonl`` + ``roster.json`` and
does not read the committed ``tournament-eval-report.json`` at all.

The ten gate checks (each named + individually reported), per the Task-15.1
Definition of Done plus the Phase-14-close §1 betrayal row:

1. ``all_games_reach_game_over`` — every recorded game wrote a ``game_over`` row
   the reconstruction walk actually REACHES, the §6.3 win-condition invariant
   holds (:mod:`eval.win_condition_selfcheck`), and the recorded ``winner`` /
   ``reason`` match the engine's reconstructed ``GameOverEvent``. A forged
   outcome label and a truncated tick stream both survive byte-identity; both
   fail here (truncation under the ``truncated_replay`` reason token).
2. ``meeting_rate_and_resolution`` — ``meeting_rate >= 0.60`` and every triggered
   meeting resolved (no failed call aborted a meeting without a resolved entry).
3. ``no_duplicate_meeting_rows`` — no game records two meeting rows for the same
   meeting id / tick (``ReplayLoader`` dedups by tick, so byte-identity misses the
   double-count the report fold would otherwise absorb).
4. ``no_tick_1_kills`` — zero resolved kills at tick <= 1 (the spawn-cooldown
   guard; :func:`orchestrator.seeder.seed_initial_state` makes a tick-1 kill
   impossible, so any is a regression).
5. ``no_friendly_fire_kills`` — zero resolved kills whose victim is an impostor
   (the engine role-aware kill guard held).
6. ``no_betrayal_ballots_or_accusations`` — no impostor ballot or accusation names
   a fellow impostor (the §7.12 firewall row on the audit's §1 table).
7. ``no_railroaded_crew_ejections`` — the restored Task-14.12 tripwire: no crew
   member's vote-prompt suspicion rendered at a clamped 1.0 driven by >= 2
   same-meeting contradiction flags.
8. ``no_dangling_primary_reason_id`` — every ballot ``primary_reason_id``
   references a real transcript turn id in its meeting.
9. ``cost_and_provenance_exact`` — every game's substrate-flag stamp equals the
   canonical snapshot with the canonical key set; a single coherent model +
   prompt set across the run (optionally pinned to exact expected values); a game
   that called the model carries a prompt-version stamp; every aggregate AND
   per-call cost row finite and non-negative (optionally required to be $0).
10. ``byte_identical_reconstruction`` — the recorded state-hash chain reconstructs
   byte-identically under the current engine (``scripts/_verify_samples.py``);
   a verifier that raises on malformed input is reported as a failure, not a crash.

The whole gate is crash-proof on untrusted input: a corrupt replay that raises
out of report assembly / substrate reads / reconstruction fails the affected
checks (closed) rather than escaping — the report is always emitted.

JSON report schema (``ValidityGateReport.model_dump()`` / ``--json``), consumed
by the 15.15 harness and the 15.7 / 15.18 audits — STABLE::

    {
      "replay_set_dir": str,          # the directory that was gated
      "passed": bool,                 # AND over every check.passed
      "games_total": int,             # number of replay-seed-*.jsonl games
      "checks": [                     # one entry per named check, in gate order
        {
          "name": str,                # stable check slug (see the list above)
          "passed": bool,
          "summary": str,             # one-line human-readable result
          "violations": [str, ...],   # per-item detail; empty iff passed
          "facts": {str: (bool|int|float|str|null), ...}  # surfaced metrics
        },
        ...
      ]
    }

The library public surface (stable — downstream tasks import these):
:class:`ValidityCheck`, :class:`ValidityGateReport`, :func:`run_validity_gate`.
"""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, NoReturn, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from api import replay_loader
from engine.entities import PlayerId, Role
from engine.events import GameOverEvent, KilledEvent
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import load_tournament_report
from eval.meeting_quality import compute_meeting_rate
from eval.replay_walk import (
    MeetingApplied,
    ReplayWalkConfig,
    TickAdvanced,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.win_condition_selfcheck import WinConditionSelfCheck
from meetings.schemas import AccusationClaim
from orchestrator.replay import (
    GameEndReplayEntry,
    ReplayLog,
    SUBSTRATE_FLAG_KEYS,
    WinnerSide,
    read_all_entries,
    read_substrate_flags,
    substrate_flag_snapshot,
)
from orchestrator.seeder import seed_initial_state

# Malformed-input raises that the resilient gate converts into failed checks
# rather than letting escape (a corrupted candidate dir must never crash the CLI).
_MALFORMED_INPUT_ERRORS: Final[tuple[type[Exception], ...]] = (
    ReplayLog.CorruptedFileError,
    ValidationError,
    ValueError,
    KeyError,
    FileNotFoundError,
)

# ``scripts/`` is on ``mypy_path`` (pyproject) but is not an importable package;
# ``_verify_samples`` is explicitly "importable for unit tests" (its docstring),
# and its ``verify_samples`` IS the tested machinery behind the byte-identity
# walk this gate must call rather than shelling out. Put ``scripts/`` on
# ``sys.path`` the same guarded way the scripts themselves bootstrap the repo
# root, then import the tool. Kept local + commented so the one backwards
# (eval -> scripts) edge is explicit and swappable.
_SCRIPTS_DIR: Final[Path] = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _verify_samples import verify_samples  # noqa: E402

FactValue: TypeAlias = bool | int | float | str | None
"""A JSON scalar surfaced on a :class:`ValidityCheck` ``facts`` map."""

# The Stage-A meeting-enablement floor (audits/audit-phase-14-close.md §1;
# eval.meeting_quality docstring): the HARD threshold this gate enforces.
MEETING_RATE_FLOOR: Final[float] = 0.60
# The reason token every truncated-replay violation carries. A recorded
# ``game_over`` row the reconstruction never earns (the walk stopped short, or
# the row names no winner) is corruption, not a legitimate short game: the
# engine writes that row only after a ``GameOverEvent``, and a tick-budget cap
# returns without writing one at all (orchestrator.game.HeadlessGame).
TRUNCATED_REPLAY_REASON: Final[str] = "truncated_replay"
# The audit's supporting statistical-power floor on resolved meetings. Reported
# on the meeting check's facts but NOT hard-gated: the CLIs accept an arbitrary
# (possibly small) replay set, whereas >= 30 is a power note about the canonical
# baseline sets specifically (see the module ## Decisions in the PR).
MIN_RESOLVED_MEETINGS_NOTE: Final[int] = 30

# A resolved kill at or below this tick is the spawn-rush regression the
# kill-cooldown guard should make impossible (orchestrator.seeder).
TICK_1_KILL_BAR: Final[int] = 1

# The Task-14.12 railroad tripwire (tests/meetings/test_manager.py::
# test_no_crew_row_is_railroaded_to_certain_guilt). A crew row rendered at a
# clamped certain-guilt suspicion driven by >= this many same-meeting
# contradiction flags is the railroad defect.
CERTAIN_GUILT_SUSPICION: Final[float] = 1.0
SAME_MEETING_FLAG_BAR: Final[int] = 2
# The committed vote_ballot.j2 renders the voter's suspicion graph under this
# header as "- `p-N`: suspicion X, trust Y" rows (the same parse the 14.12
# tripwire test uses to read the recorded rendered values).
_SUSPICION_GRAPH_HEADER: Final[str] = "## Your suspicion of each player"
_SUSPICION_GRAPH_ROW_RE: Final[re.Pattern[str]] = re.compile(
    r"`(?P<pid>p-\d+)`: suspicion (?P<sus>[0-9]*\.?[0-9]+), "
    r"trust (?P<trust>[0-9]*\.?[0-9]+)"
)

# The flat 4p/1i MVP baseline is the only committed set without a roster.json
# (mirrors scripts/build_sample_report.py). A dir with no descriptor defaults
# to these knobs; every other set ships roster.json.
_FLAT_DEFAULT_KNOBS: Final[tuple[int, int, int]] = (4, 1, 1)


class ValidityCheck(BaseModel):
    """One named validity-gate check's result (frozen value object).

    ``violations`` holds a per-item description for each failing row (empty iff
    ``passed``); ``facts`` surfaces the machine-readable metrics a downstream
    audit reads (e.g. the meeting rate, the ejection split). See the module JSON
    schema.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    passed: bool
    summary: str
    violations: tuple[str, ...] = ()
    facts: Mapping[str, FactValue] = Field(default_factory=dict)


class ValidityGateReport(BaseModel):
    """The composed gate verdict over one replay-set directory (frozen).

    ``passed`` is the AND over every ``check.passed``. A gate CLI exits non-zero
    when this is ``False`` and names the failing checks (:meth:`failing_checks`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    passed: bool
    games_total: int
    checks: tuple[ValidityCheck, ...]

    def failing_checks(self) -> tuple[str, ...]:
        """The ``name`` of every check that did not pass, in gate order."""

        return tuple(check.name for check in self.checks if not check.passed)


@dataclass(frozen=True)
class _KillFact:
    """One resolved kill recovered from engine reconstruction of a replay."""

    seed: int
    tick: int
    killer: PlayerId
    killer_role: Role | None
    victim: PlayerId
    victim_role: Role | None


@dataclass(frozen=True)
class _GameReconstruction:
    """The engine-derived facts for one recorded game (one reconstruction walk)."""

    seed: int
    win_check: WinConditionSelfCheck
    kills: tuple[_KillFact, ...]
    # The winner/reason the ENGINE emitted at the reconstructed terminal state
    # (from the ``GameOverEvent``), independent of the recorded ``game_over`` row
    # — ``None`` if reconstruction never reached game over. Compared against the
    # recorded outcome to catch a forged winner/reason (state hashes do not cover
    # the recorded label).
    reconstructed_winner: WinnerSide | None
    reconstructed_reason: str | None
    # Whether the ``game_over`` row is the recording's LAST physical record.
    # The walk stops at the terminal state, so a row of ANY kind written after
    # it is never replayed and never hash-verified — it would ride into the
    # accepted corpus inside otherwise-verified bytes.
    game_over_is_last_record: bool


# --------------------------------------------------------------------------- #
# Set loaders (shared with scripts/measure_baseline.py)                        #
# --------------------------------------------------------------------------- #


def resolve_roster_knobs(sample_dir: Path) -> tuple[int, int, int]:
    """``(num_players, num_impostors, tasks_per_crewmate)`` for a replay set.

    Reuses :func:`api.replay_loader._load_roster_config` (the single fail-loud
    ``roster.json`` parser, exactly as ``scripts/build_sample_report.py`` does),
    so a malformed roster raises here; a missing descriptor is the flat 4p/1i
    default.
    """

    roster = replay_loader._load_roster_config(sample_dir)
    if roster is None:
        return _FLAT_DEFAULT_KNOBS
    return (roster.num_players, roster.num_impostors, roster.tasks_per_crewmate)


def seeds_on_disk(sample_dir: Path) -> list[int]:
    """Seeds with a committed ``replay-seed-{n}.jsonl``, sorted and de-duplicated."""

    return sorted(
        {
            int(path.stem.rsplit("-", 1)[1])
            for path in sample_dir.glob("replay-seed-*.jsonl")
        }
    )


def roles_by_seed(
    sample_dir: Path,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map | None = None,
) -> dict[int, dict[PlayerId, Role]]:
    """Recover per-seed role ground truth by re-seeding the engine.

    Roles are firewalled out of the replay JSONL, so this re-runs
    :func:`orchestrator.seeder.seed_initial_state` for each committed seed — the
    same deterministic recipe ``scripts/build_sample_report.py`` uses to build
    the committed report. The reconstruction walks (and the byte-identity check)
    verify every ``state_hash``, so a wrong roster fails loud rather than
    silently mislabelling roles.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    out: dict[int, dict[PlayerId, Role]] = {}
    for seed in seeds_on_disk(sample_dir):
        state = seed_initial_state(
            seed=seed,
            game_map=resolved_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        out[seed] = {pid: player.role for pid, player in state.players.items()}
    return out


def assemble_tournament_report(sample_dir: Path) -> TournamentReport:
    """Fold a replay set's committed bytes into a typed :class:`TournamentReport`.

    The shared loader for both CLIs: resolve the roster, recover roles by
    re-seeding, then call :func:`eval.balance_eval.load_tournament_report` with
    ``derive_kill_gift=False`` (the R-gate folds and the report-based validity
    checks never consume the kill-gift fields, so this does NO engine re-run — it
    folds the frozen recorded outcomes). Pure and offline.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    if not per_seed_roles:
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")
    return load_tournament_report(
        sample_dir,
        roles_by_seed=per_seed_roles,
        tasks_per_crewmate=tasks_per_crewmate,
        derive_kill_gift=False,
    )


# --------------------------------------------------------------------------- #
# Engine reconstruction (kills + win-condition) — one walk per game            #
# --------------------------------------------------------------------------- #


def _reconstruct_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> _GameReconstruction:
    """Re-seed + replay one game to recover its resolved kills + §6.3 self-check.

    A single read-only engine playback — :func:`eval.replay_walk.walk_replay`
    under the named ``validity-gate`` profile (Task 19.25; the same walk
    :func:`eval.win_condition_selfcheck.check_replay_win_condition` performs) —
    that additionally collects every resolved :class:`~engine.events.KilledEvent`
    — kills have no importable metric home, so they are recovered here. Every
    reconstructed ``state_hash`` is verified against the recording, so a wrong
    roster or a determinism break raises :class:`ValueError`. The produced
    :class:`~eval.win_condition_selfcheck.WinConditionSelfCheck` uses the tested
    :func:`~eval.win_condition_selfcheck.win_condition_is_consistent` predicate
    (a unit test cross-checks it against ``check_replay_win_condition``).
    """

    game_id = f"headless-seed-{seed}"

    kills: list[_KillFact] = []
    first_zero_impostor_tick: int | None = None
    reconstructed_winner: WinnerSide | None = None
    reconstructed_reason: str | None = None
    game_end = None

    def _record_zero(tick: int, state: WorldState) -> None:
        nonlocal first_zero_impostor_tick
        if first_zero_impostor_tick is not None:
            return
        alive_impostors = sum(
            1
            for player in state.players.values()
            if player.alive and player.role == "IMPOSTOR"
        )
        if alive_impostors == 0:
            first_zero_impostor_tick = tick

    for walk_event in walk_replay(
        replay_path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=_WALK_CONFIG,
    ):
        if isinstance(walk_event, TickAdvanced):
            for event in walk_event.events:
                if isinstance(event, GameOverEvent):
                    reconstructed_winner = event.winner
                    reconstructed_reason = event.reason
                elif isinstance(event, KilledEvent):
                    kills.append(
                        _KillFact(
                            seed=seed,
                            tick=event.tick,
                            killer=event.actor,
                            killer_role=roles.get(event.actor),
                            victim=event.target,
                            victim_role=roles.get(event.target),
                        )
                    )
            _record_zero(walk_event.entry.tick, walk_event.state)
        elif isinstance(walk_event, MeetingApplied):
            for event in walk_event.post_events:
                if isinstance(event, GameOverEvent):
                    reconstructed_winner = event.winner
                    reconstructed_reason = event.reason
            _record_zero(walk_event.entry.tick, walk_event.state)
        elif isinstance(walk_event, WalkComplete):
            game_end = walk_event.game_end

    win_check = WinConditionSelfCheck(
        game_id=game_id,
        seed=seed,
        winner=game_end.winner if game_end is not None else None,
        reason=game_end.reason if game_end is not None else None,
        first_zero_impostor_tick=first_zero_impostor_tick,
        game_over_tick=game_end.tick if game_end is not None else None,
    )
    entries = read_all_entries(replay_path)
    return _GameReconstruction(
        seed=seed,
        win_check=win_check,
        kills=tuple(kills),
        reconstructed_winner=reconstructed_winner,
        reconstructed_reason=reconstructed_reason,
        game_over_is_last_record=bool(entries)
        and isinstance(entries[-1], GameEndReplayEntry),
    )


def _raise_walk_violation(violation: WalkViolation) -> NoReturn:
    if violation.kind == "trailing_replay_rows":
        raise ValueError(
            f"validity-gate reconstruction rejected {violation.game_id!r}: the "
            f"replay carries rows after the terminal GAME_OVER at tick "
            f"{violation.terminal_tick}. The walk stops at the terminal state, so "
            "those rows would ride along inside 'verified' bytes unvalidated."
        )
    raise ValueError(
        f"validity-gate reconstruction diverged for {violation.game_id!r} at tick "
        f"{violation.tick}: recorded {violation.expected!r}, reconstructed "
        f"{violation.actual!r}. The roster "
        "does not match the recording, or engine playback is non-deterministic."
    )


# The named Task 19.25 profile (see eval/replay_walk.py's drift record): verify
# per-tick hashes + each meeting's state_hash_after; TRUNCATE on a partial
# meeting — the gate deliberately serves what a recording contains, matching
# the loader (the completeness checks own game-over/duplicate-row policing) —
# and REJECT rows recorded after the terminal GAME_OVER, which the walk never
# reaches and therefore never hash-verifies.
_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="validity-gate",
    on_violation=_raise_walk_violation,
    verify_tick_hashes=True,
    verify_action_dispositions=True,
    missing_meeting_row="truncate",
    verify_meeting_post_hashes=True,
    reject_trailing_rows=True,
)


def _reconstruct_set(sample_dir: Path) -> list[_GameReconstruction]:
    """Reconstruct every game in the set (roster + re-seeded roles)."""

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    return [
        _reconstruct_game(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            game_map=game_map,
        )
        for seed in seeds_on_disk(sample_dir)
    ]


# --------------------------------------------------------------------------- #
# Individual checks (pure over their minimal inputs — unit-testable)           #
# --------------------------------------------------------------------------- #


def check_all_games_reach_game_over(
    reconstructions: Sequence[_GameReconstruction],
) -> ValidityCheck:
    """Every game's terminal state is RECORDED, RECONSTRUCTED, and consistent.

    A game passes only when the recording and the engine agree it ended: the
    replay carries a ``game_over`` row naming a winner, the reconstruction walk
    reaches that terminal state, the two outcomes match, and the §6.3 win
    invariant holds.

    Three failure shapes, each of which byte-identity alone lets through. A
    recorded ``game_over`` ``winner`` / ``reason`` is metadata NOT covered by the
    state-hash chain, so a forged label survives reconstruction — comparing it
    against the reconstructed :class:`GameOverEvent` (which
    ``scripts/measure_baseline.py`` folds into the win split + R1) fails it here.
    Dropping trailing tick rows shortens the walk without breaking the chain, so
    a truncated replay keeps its ``game_over`` row while the walk stops short —
    presence of the row is not entitlement to it, and both that shape and a row
    naming no winner fail as ``truncated_replay``; symmetrically, the
    ``game_over`` row must be the recording's LAST record, since the walk stops
    at the terminal and anything after it is never replayed. The check cannot
    false-positive
    on a legitimate short game: ``orchestrator.game.HeadlessGame`` writes the row
    only after the engine fires a ``GameOverEvent`` and returns without one when
    the tick budget caps the game, so a recorded terminal the walk never reaches
    is unconditionally corruption. Mirrors the corpus walk's rejection in
    :mod:`training.anchor_study`.
    """

    violations: list[str] = []
    for game in reconstructions:
        check = game.win_check
        recorded_terminal = check.game_over_tick is not None
        walked_terminal = game.reconstructed_winner is not None
        if not recorded_terminal:
            violations.append(
                f"seed {game.seed}: no game_over row (game never reached game_over)"
            )
        elif not check.is_consistent:
            violations.append(
                f"seed {game.seed}: §6.3 regression — last impostor eliminated at "
                f"tick {check.first_zero_impostor_tick} but game_over at tick "
                f"{check.game_over_tick}"
            )
        if recorded_terminal and check.winner is None:
            violations.append(
                f"seed {game.seed}: {TRUNCATED_REPLAY_REASON} — the recorded "
                "game_over row names no winner (partial recording)"
            )
        if recorded_terminal and not game.game_over_is_last_record:
            violations.append(
                f"seed {game.seed}: rows are recorded after the game_over row "
                "(never replayed, never hash-verified)"
            )
        if recorded_terminal and not walked_terminal:
            violations.append(
                f"seed {game.seed}: {TRUNCATED_REPLAY_REASON} — game_over recorded "
                f"at tick {check.game_over_tick} but the reconstructed walk never "
                "reached GAME_OVER (truncated tick stream)"
            )
        elif walked_terminal and (
            check.winner != game.reconstructed_winner
            or check.reason != game.reconstructed_reason
        ):
            violations.append(
                f"seed {game.seed}: recorded outcome {check.winner}/{check.reason} "
                f"!= reconstructed {game.reconstructed_winner}/"
                f"{game.reconstructed_reason} (forged game_over label)"
            )
    total = len(reconstructions)
    # Reconstruction-confirmed terminals only: a recorded row the walk never
    # earned must never be summarised as a game that reached game_over.
    reached = sum(
        1
        for g in reconstructions
        if g.win_check.game_over_tick is not None and g.reconstructed_winner is not None
    )
    return ValidityCheck(
        name="all_games_reach_game_over",
        passed=not violations,
        summary=(
            f"{reached}/{total} games reached a reconstructed game_over with a "
            "consistent win condition"
        ),
        violations=tuple(violations),
        facts={"games_total": total, "games_reached_game_over": reached},
    )


def check_meeting_rate_and_resolution(report: TournamentReport) -> ValidityCheck:
    """``meeting_rate >= 0.60`` and every triggered meeting resolved.

    Wires :func:`eval.meeting_quality.compute_meeting_rate` for the rate. A
    meeting is unresolved when a game recorded a failed call for a meeting id that
    never produced a resolved :class:`~eval.report_schema.MeetingReport`.
    """

    meeting = compute_meeting_rate(report)
    rate = meeting.meeting_rate

    unresolved: list[str] = []
    for game in report.games:
        resolved_ids = {m.meeting_id for m in game.meetings}
        for failed in game.failed_calls:
            if failed.meeting_id not in resolved_ids:
                unresolved.append(
                    f"{game.game_id}: meeting {failed.meeting_id} aborted "
                    f"({failed.error_type}) without a resolved entry"
                )

    rate_ok = rate is not None and rate >= MEETING_RATE_FLOOR
    violations: list[str] = []
    if not rate_ok:
        shown = "undefined" if rate is None else f"{rate:.3f}"
        violations.append(f"meeting_rate {shown} < floor {MEETING_RATE_FLOOR:.2f}")
    violations.extend(sorted(set(unresolved)))
    return ValidityCheck(
        name="meeting_rate_and_resolution",
        passed=not violations,
        summary=(
            f"meeting_rate {rate if rate is None else round(rate, 4)} "
            f"(floor {MEETING_RATE_FLOOR:.2f}); {meeting.meetings_total} resolved "
            f"meetings; {len(set(unresolved))} unresolved"
        ),
        violations=tuple(violations),
        facts={
            "meeting_rate": rate,
            "resolved_meetings": meeting.meetings_total,
            "games_with_meeting": meeting.games_with_meeting,
            "unresolved_meetings": len(set(unresolved)),
            "min_resolved_meetings_note": MIN_RESOLVED_MEETINGS_NOTE,
        },
    )


def check_no_duplicate_meeting_rows(report: TournamentReport) -> ValidityCheck:
    """No game records two meeting rows for the same meeting id or tick.

    ``api.replay_loader.ReplayLoader`` collapses duplicate meeting rows by tick,
    so the byte-identity check reports clean while
    :func:`eval.balance_eval.load_tournament_report` counts BOTH — double-counting
    resolved meetings, ballots, and cost. This structural check catches the
    duplication byte-identity cannot (each ``meeting_id`` is unique per game and
    at most one meeting resolves per tick).
    """

    violations: list[str] = []
    meetings_total = 0
    for game in report.games:
        seen_ids: set[str] = set()
        seen_ticks: set[int] = set()
        for meeting in game.meetings:
            meetings_total += 1
            if meeting.meeting_id in seen_ids:
                violations.append(
                    f"seed {game.seed}: duplicate meeting row {meeting.meeting_id}"
                )
            seen_ids.add(meeting.meeting_id)
            if meeting.tick in seen_ticks:
                violations.append(
                    f"seed {game.seed}: two meetings recorded at tick {meeting.tick}"
                )
            seen_ticks.add(meeting.tick)
    return ValidityCheck(
        name="no_duplicate_meeting_rows",
        passed=not violations,
        summary=f"{len(violations)} duplicate meeting rows over {meetings_total} (want 0)",
        violations=tuple(violations),
        facts={
            "duplicate_meeting_rows": len(violations),
            "meetings_total": meetings_total,
        },
    )


def check_no_tick_1_kills(kills: Sequence[_KillFact]) -> ValidityCheck:
    """Zero resolved kills at tick <= 1 (the spawn-cooldown regression)."""

    offenders = [k for k in kills if k.tick <= TICK_1_KILL_BAR]
    violations = [
        f"seed {k.seed}: {k.killer} killed {k.victim} at tick {k.tick} "
        "(kill cooldown should make an opening-tick kill impossible)"
        for k in offenders
    ]
    return ValidityCheck(
        name="no_tick_1_kills",
        passed=not offenders,
        summary=f"{len(offenders)} kills at tick <= {TICK_1_KILL_BAR} (want 0)",
        violations=tuple(violations),
        facts={"tick_1_kills": len(offenders), "total_kills": len(kills)},
    )


def check_no_friendly_fire_kills(kills: Sequence[_KillFact]) -> ValidityCheck:
    """Zero resolved kills whose VICTIM is an impostor (the role-aware guard)."""

    offenders = [k for k in kills if k.victim_role == "IMPOSTOR"]
    violations = [
        f"seed {k.seed}: {k.killer} ({k.killer_role}) killed impostor {k.victim} "
        f"at tick {k.tick}"
        for k in offenders
    ]
    return ValidityCheck(
        name="no_friendly_fire_kills",
        passed=not offenders,
        summary=f"{len(offenders)} impostor-on-impostor kills (want 0)",
        violations=tuple(violations),
        facts={"friendly_fire_kills": len(offenders), "total_kills": len(kills)},
    )


def check_no_betrayal(report: TournamentReport) -> ValidityCheck:
    """No impostor ballot or accusation names a FELLOW (other) impostor (§7.12 firewall).

    The Phase-14 close validity table (audits/audit-phase-14-close.md §1) carries
    ``betrayal ballots/accusations`` as a HARD row: the §7.12 firewall makes an
    impostor voting/accusing a teammate structurally absent, so a non-zero count
    on a multi-impostor set is a regression. Vacuously satisfied for a
    single-impostor set (no teammate exists to betray).

    "Teammate" means a FELLOW impostor — a DIFFERENT one. The firewall the check
    verifies drops targets in ``meetings.manager`` ``fellow_impostor_ids`` (Task
    7.12), which is "the sorted ids of the OTHER impostors" (manager.py:496) —
    self is deliberately excluded, because accusing/voting YOURSELF betrays no
    teammate. So a SELF-target (``against == speaker`` / ``target == voter``) is
    NOT a betrayal and is excluded here, matching the firewall's semantics. (A
    self-accusation is a strategically-odd but firewall-clean model output: Task
    15.7's baseline-3 v5 prompts introduced a handful — 3/851 multi-impostor
    9p2i ballots — where an accused impostor echoes an accusation naming itself;
    that is a Phase-16 dialogue-quality finding, not a firewall breach. Before
    this refinement the check counted ``against in impostors`` incl. self, so it
    was strictly stricter than the firewall it validates.)
    """

    violations: list[str] = []
    ballots_checked = 0
    accusations_checked = 0
    for game in report.games:
        impostors = {pid for pid, role in game.roles.items() if role == "IMPOSTOR"}
        if len(impostors) < 2:
            continue
        for meeting in game.meetings:
            for ballot in meeting.ballots:
                ballots_checked += 1
                if (
                    ballot.voter in impostors
                    and ballot.target != "SKIP"
                    and ballot.target in impostors
                    and ballot.target
                    != ballot.voter  # self-vote is not fellow-betrayal
                ):
                    violations.append(
                        f"seed {game.seed} meeting {meeting.meeting_id}: impostor "
                        f"{ballot.voter} voted against teammate {ballot.target}"
                    )
            for turn in meeting.transcript.turns:
                if turn.speaker not in impostors:
                    continue
                for claim in turn.claims:
                    if isinstance(claim, AccusationClaim):
                        accusations_checked += 1
                        if (
                            claim.against in impostors
                            and claim.against != turn.speaker  # self is not a fellow
                        ):
                            violations.append(
                                f"seed {game.seed} meeting {meeting.meeting_id}: "
                                f"impostor {turn.speaker} accused teammate "
                                f"{claim.against}"
                            )
    return ValidityCheck(
        name="no_betrayal_ballots_or_accusations",
        passed=not violations,
        summary=(
            f"{len(violations)} teammate-betrayal ballots/accusations over "
            f"{ballots_checked} multi-impostor ballots (want 0)"
        ),
        violations=tuple(violations),
        facts={
            "betrayals": len(violations),
            "multi_impostor_ballots": ballots_checked,
            "impostor_accusations": accusations_checked,
        },
    )


def _rendered_suspicions(meeting: MeetingReport, subject: PlayerId) -> list[float]:
    """Every suspicion value the meeting's vote prompts rendered for ``subject``.

    Reads ``meeting.llm_calls[].prompt`` and parses the committed suspicion-graph
    block — the same parse the Task-14.12 tripwire test uses.
    """

    values: list[float] = []
    for call in meeting.llm_calls:
        prompt = call.prompt
        if _SUSPICION_GRAPH_HEADER not in prompt:
            continue
        block = prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1].split("## ", 1)[0]
        values.extend(
            float(match.group("sus"))
            for match in _SUSPICION_GRAPH_ROW_RE.finditer(block)
            if match.group("pid") == subject
        )
    return values


def check_no_railroaded_crew_ejections(report: TournamentReport) -> ValidityCheck:
    """The restored Task-14.12 tripwire: zero railroaded crew rows.

    A crew member is railroaded when a vote prompt rendered their suspicion at a
    clamped 1.0 driven by >= 2 same-meeting contradiction flags naming them (a
    1.0 with < 2 flags is the legitimate across-meeting accumulator, which stays
    allowed). Mirrors ``tests/meetings/test_manager.py::
    test_no_crew_row_is_railroaded_to_certain_guilt``.
    """

    violations: list[str] = []
    rendered_rows = 0
    for game in report.games:
        for meeting in game.meetings:
            for player_id, role in game.roles.items():
                if role != "CREWMATE":
                    continue
                rendered = _rendered_suspicions(meeting, player_id)
                rendered_rows += len(rendered)
                if not any(value >= CERTAIN_GUILT_SUSPICION for value in rendered):
                    continue
                same_meeting_flags = sum(
                    1 for flag in meeting.contradictions if player_id in flag.subjects
                )
                if same_meeting_flags >= SAME_MEETING_FLAG_BAR:
                    violations.append(
                        f"seed {game.seed} meeting {meeting.meeting_id}: crew "
                        f"{player_id} rendered at clamped 1.0 off "
                        f"{same_meeting_flags} same-meeting flags"
                    )
    return ValidityCheck(
        name="no_railroaded_crew_ejections",
        passed=not violations,
        summary=(
            f"{len(violations)} railroaded crew rows over {rendered_rows} rendered "
            "crew suspicions (want 0)"
        ),
        violations=tuple(violations),
        facts={
            "railroaded_crew_rows": len(violations),
            "rendered_crew_rows": rendered_rows,
        },
    )


def check_no_dangling_primary_reason_id(report: TournamentReport) -> ValidityCheck:
    """Every ballot ``primary_reason_id`` references a real transcript turn id."""

    violations: list[str] = []
    ballots_total = 0
    for game in report.games:
        for meeting in game.meetings:
            turn_ids = {turn.turn_id for turn in meeting.transcript.turns}
            for ballot in meeting.ballots:
                ballots_total += 1
                reason = ballot.primary_reason_id
                if reason is not None and reason not in turn_ids:
                    violations.append(
                        f"seed {game.seed} meeting {meeting.meeting_id}: ballot by "
                        f"{ballot.voter} cites turn {reason!r}, absent from the "
                        "transcript"
                    )
    return ValidityCheck(
        name="no_dangling_primary_reason_id",
        passed=not violations,
        summary=(
            f"{len(violations)} dangling primary_reason_id over {ballots_total} "
            "ballots (want 0)"
        ),
        violations=tuple(violations),
        facts={"dangling_reason_ids": len(violations), "ballots_total": ballots_total},
    )


def check_cost_and_provenance(
    report: TournamentReport,
    substrate_by_seed: Mapping[int, Mapping[str, bool] | None],
    *,
    expected_model: str | None = None,
    expected_prompt_versions: Mapping[str, str] | None = None,
    require_zero_cost: bool = False,
) -> ValidityCheck:
    """Substrate-flag stamp, model, prompt set, and cost rows all coherent (+ exact).

    * Every game's ``game_over`` substrate stamp agrees with the canonical build
      snapshot on every canonical lever's boolean (the same tolerant match the
      replay loader's ``_assert_substrate_matches`` enforces to refuse
      cross-substrate reconstruction): an always-on lever must be present and
      True, a DEFAULT-OFF toggleable lever a recording predates may be absent
      (reads False on both sides), and an unknown key is a stripped/foreign stamp.
    * A single coherent per-game model set + prompt-version set across the run (a
      coherent mixed-tier set is valid, drift is not). Because the CLIs gate an
      ARBITRARY dir, the model / prompt-set VALUES are not hard-coded; pass
      ``expected_model`` / ``expected_prompt_versions`` (from the recording config,
      e.g. the 15.7 / 15.12 re-records) to additionally pin them EXACTLY. A game
      that recorded model calls (non-empty ``by_model``) but carries NO
      prompt-version stamp is a stripped-provenance failure.
    * Every cost row is finite and non-negative — both the per-game
      :class:`~eval.report_schema.GameCostSummary` AND each per-call
      ``llm_calls`` / ``failed_calls`` row (a corrupt per-call figure can hide
      inside a still-positive aggregate). ``require_zero_cost`` (opt-in, for the
      audit's ``cost rows = 0`` flat-rate baselines) additionally demands every
      row be exactly ``0.0``.
    """

    snapshot = substrate_flag_snapshot()
    canonical_keys = set(SUBSTRATE_FLAG_KEYS)
    violations: list[str] = []

    for seed in sorted(substrate_by_seed):
        stamp = substrate_by_seed[seed]
        if stamp is None:
            violations.append(f"seed {seed}: no substrate_flags stamp on game_over")
            continue
        # Mirror the replay loader's ``_assert_substrate_matches`` (the "same
        # match" this check claims): compare each canonical lever's BOOLEAN
        # against the build snapshot rather than demanding an exact key SET. A
        # recording predating a DEFAULT-OFF toggleable lever (Task 15.5's
        # ``reporter_exculpation``) omits that key, which reads as ``False`` on
        # both sides -- so the committed baseline stays coherent while OFF -- yet
        # an always-on lever's key must still be present and True, and a wrong
        # value still fails. An unknown key NOT in the canonical set is a
        # stripped / foreign stamp.
        unknown = sorted(set(stamp) - canonical_keys)
        if unknown:
            violations.append(
                f"seed {seed}: unknown substrate keys {unknown} "
                f"(canonical {sorted(canonical_keys)})"
            )
        differing = sorted(
            key
            for key in canonical_keys
            if bool(stamp.get(key)) != bool(snapshot.get(key))
        )
        if differing:
            violations.append(
                f"seed {seed}: substrate stamp {dict(stamp)} disagrees with build "
                f"snapshot {snapshot} on {differing}"
            )

    # A game with no meeting records no LLM call, so its prompt_versions / by_model
    # are legitimately empty. Coherence is over the NON-EMPTY stamps only.
    model_sets: set[tuple[str, ...]] = set()
    prompt_sets: set[tuple[tuple[str, str], ...]] = set()
    all_models: set[str] = set()
    for game in report.games:
        if game.cost.by_model:
            model_sets.add(tuple(sorted(game.cost.by_model.keys())))
            all_models.update(game.cost.by_model)
        if game.prompt_versions:
            prompt_sets.add(tuple(sorted(game.prompt_versions.items())))
        # A game that called the model MUST carry a prompt-version stamp; an empty
        # map on a game with recorded calls is stripped provenance, not the
        # legitimately-empty no-meeting case.
        if game.cost.by_model and not game.prompt_versions:
            violations.append(
                f"{game.game_id}: recorded model calls but empty prompt_versions "
                "(stripped prompt provenance)"
            )
        _fold_cost_row_violations(game, violations, require_zero_cost=require_zero_cost)

    if len(model_sets) > 1:
        violations.append(f"inconsistent model sets across games: {sorted(model_sets)}")
    if len(prompt_sets) > 1:
        violations.append(
            f"multiple prompt-version sets across the set ({len(prompt_sets)} distinct)"
        )
    if not model_sets:
        violations.append("no model recorded on any game cost row")

    # Exact provenance pins (opt-in — the recording config supplies them).
    if expected_model is not None and all_models != {expected_model}:
        violations.append(
            f"model provenance {sorted(all_models)} != expected [{expected_model!r}]"
        )
    if expected_prompt_versions is not None:
        want = tuple(sorted(expected_prompt_versions.items()))
        if not prompt_sets:
            violations.append(
                "expected prompt-version provenance "
                f"{dict(expected_prompt_versions)} but the set records none"
            )
        elif any(recorded != want for recorded in prompt_sets):
            violations.append(
                "prompt-version provenance does not match expected "
                f"{dict(expected_prompt_versions)}"
            )

    models = next(iter(model_sets), ())
    model_name = ", ".join(models) if models else None
    prompt_set = next(iter(prompt_sets), ())
    return ValidityCheck(
        name="cost_and_provenance_exact",
        passed=not violations,
        summary=(
            f"model={model_name!r}, {len(prompt_set)} prompt versions, substrate "
            f"stamped exact on {len(substrate_by_seed)} games"
        ),
        violations=tuple(violations),
        facts={
            "model": model_name,
            "prompt_versions": len(prompt_set),
            "substrate_stamp_ok": not any("substrate" in v for v in violations),
            "games_total": len(report.games),
        },
    )


def _fold_cost_row_violations(
    game: GameReport, violations: list[str], *, require_zero_cost: bool = False
) -> None:
    """Validate a game's aggregate AND per-call cost rows (finite, non-negative).

    With ``require_zero_cost`` every cost figure must additionally be exactly
    ``0.0`` (the audit's flat-rate ``cost rows = 0`` row, opt-in per set).
    """

    cost = game.cost
    if not _is_finite_nonneg(cost.total_cost_usd):
        violations.append(
            f"{game.game_id}: total_cost_usd {cost.total_cost_usd!r} is not "
            "finite / >= 0"
        )
    elif require_zero_cost and cost.total_cost_usd != 0.0:
        violations.append(
            f"{game.game_id}: total_cost_usd {cost.total_cost_usd} != 0 "
            "(--require-zero-cost)"
        )
    if cost.total_input_tokens < 0 or cost.total_output_tokens < 0:
        violations.append(f"{game.game_id}: negative aggregate token count")
    for meeting in game.meetings:
        for call in meeting.llm_calls:
            if (
                call.input_tokens < 0
                or call.output_tokens < 0
                or not _is_finite_nonneg(call.cost_usd)
            ):
                violations.append(
                    f"{game.game_id} meeting {meeting.meeting_id}: malformed "
                    f"llm_call cost row (in={call.input_tokens}, "
                    f"out={call.output_tokens}, usd={call.cost_usd!r})"
                )
            elif require_zero_cost and call.cost_usd != 0.0:
                violations.append(
                    f"{game.game_id} meeting {meeting.meeting_id}: llm_call "
                    f"cost_usd {call.cost_usd} != 0 (--require-zero-cost)"
                )
    for failed in game.failed_calls:
        if (
            failed.input_tokens < 0
            or failed.output_tokens < 0
            or not _is_finite_nonneg(failed.cost_usd)
        ):
            violations.append(
                f"{game.game_id}: malformed failed_call cost row "
                f"(in={failed.input_tokens}, out={failed.output_tokens}, "
                f"usd={failed.cost_usd!r})"
            )
        elif require_zero_cost and failed.cost_usd != 0.0:
            violations.append(
                f"{game.game_id}: failed_call cost_usd {failed.cost_usd} != 0 "
                "(--require-zero-cost)"
            )


def _is_finite_nonneg(value: float) -> bool:
    return math.isfinite(value) and value >= 0.0


def check_byte_identical_reconstruction(sample_dir: Path) -> ValidityCheck:
    """The recorded state-hash chain reconstructs byte-identically.

    Calls ``scripts/_verify_samples.py::verify_samples`` (the tested machinery
    behind ``verify_samples.sh``), which engine-replays every sample through
    :class:`api.replay_loader.ReplayLoader` and checks the state-hash chain,
    the meeting pre-hashes, and MANIFEST completeness.

    Because the gate accepts ARBITRARY candidate directories, a replay malformed
    in a way the verifier does not normalize (e.g. a dropped meeting row a later
    tick still references) can raise out of ``ReplayLoader`` rather than
    returning a failure. Such a raise IS a byte-identity failure, so it is caught
    and reported as one — the gate never crashes on untrusted input.
    """

    try:
        failures = verify_samples(sample_dir)
    except Exception as exc:  # noqa: BLE001 — any raise == "did not reconstruct"
        return ValidityCheck(
            name="byte_identical_reconstruction",
            passed=False,
            summary="reconstruction raised — replay set did not rebuild cleanly",
            violations=(f"{type(exc).__name__}: {exc}",),
            facts={"drifted_samples": -1, "raised": True},
        )
    violations = tuple(failure.render() for failure in failures)
    return ValidityCheck(
        name="byte_identical_reconstruction",
        passed=not failures,
        summary=(
            f"{len(failures)} samples drifted from byte-identical reconstruction "
            "(want 0)"
        ),
        violations=violations,
        facts={"drifted_samples": len(failures)},
    )


# --------------------------------------------------------------------------- #
# The composed gate                                                            #
# --------------------------------------------------------------------------- #


def run_validity_gate(
    replay_set_dir: Path,
    *,
    expected_model: str | None = None,
    expected_prompt_versions: Mapping[str, str] | None = None,
    require_zero_cost: bool = False,
) -> ValidityGateReport:
    """Run every HARD validity check over ``replay_set_dir`` and compose the verdict.

    Pure and offline. Assembles the typed report (roster + re-seeded roles +
    frozen-outcome fold), reconstructs each game once (kills + win-condition +
    engine outcome), reads each game's substrate stamp, and folds the ten named
    checks into a :class:`ValidityGateReport` whose ``passed`` is the AND over all
    of them.

    Crash-proof on ARBITRARY input: the gate accepts untrusted candidate dirs, so
    a corrupt replay (duplicate tick / doubled ``game_over``) that raises out of
    report assembly, substrate reads, or reconstruction is converted into a failed
    check (``byte_identical_reconstruction`` reports the concrete corruption)
    rather than a traceback — downstream automation always receives the report.

    ``expected_model`` / ``expected_prompt_versions`` / ``require_zero_cost``
    optionally pin the provenance row to EXACT values / $0 cost (the recording
    config, e.g. the 15.7 / 15.12 re-records); omitted, the provenance check
    enforces coherence + well-formedness only (the generic default so an arbitrary
    candidate dir on a different model / paid provider is not falsely rejected).
    """

    if not replay_set_dir.is_dir():
        raise NotADirectoryError(f"replay-set directory not found: {replay_set_dir}")
    seeds = seeds_on_disk(replay_set_dir)
    if not seeds:
        raise ValueError(f"no replay-seed-*.jsonl found under {replay_set_dir}")

    # Byte-identity is independent and already crash-proof — it names the concrete
    # corruption behind any assembly/reconstruction failure below.
    byte_check = check_byte_identical_reconstruction(replay_set_dir)

    report: TournamentReport | None = None
    report_error: str | None = None
    try:
        report = assemble_tournament_report(replay_set_dir)
    except _MALFORMED_INPUT_ERRORS as exc:
        report_error = f"{type(exc).__name__}: {exc}"

    substrate_by_seed: dict[int, Mapping[str, bool] | None] | None = None
    substrate_error: str | None = None
    try:
        substrate_by_seed = {
            seed: read_substrate_flags(replay_set_dir / f"replay-seed-{seed}.jsonl")
            for seed in seeds
        }
    except _MALFORMED_INPUT_ERRORS as exc:
        substrate_error = f"{type(exc).__name__}: {exc}"

    reconstructions: list[_GameReconstruction] | None = None
    reconstruction_error: str | None = None
    try:
        reconstructions = _reconstruct_set(replay_set_dir)
    except _MALFORMED_INPUT_ERRORS as exc:
        reconstruction_error = f"{type(exc).__name__}: {exc}"

    if reconstructions is not None:
        all_kills = [kill for game in reconstructions for kill in game.kills]
        game_over_check = check_all_games_reach_game_over(reconstructions)
        tick_1_check = check_no_tick_1_kills(all_kills)
        friendly_fire_check = check_no_friendly_fire_kills(all_kills)
    else:
        game_over_check = _check_unavailable(
            "all_games_reach_game_over", reconstruction_error
        )
        tick_1_check = _check_unavailable("no_tick_1_kills", reconstruction_error)
        friendly_fire_check = _check_unavailable(
            "no_friendly_fire_kills", reconstruction_error
        )

    if report is not None:
        meeting_check = check_meeting_rate_and_resolution(report)
        dup_meeting_check = check_no_duplicate_meeting_rows(report)
        betrayal_check = check_no_betrayal(report)
        railroad_check = check_no_railroaded_crew_ejections(report)
        dangling_check = check_no_dangling_primary_reason_id(report)
    else:
        meeting_check = _check_unavailable("meeting_rate_and_resolution", report_error)
        dup_meeting_check = _check_unavailable(
            "no_duplicate_meeting_rows", report_error
        )
        betrayal_check = _check_unavailable(
            "no_betrayal_ballots_or_accusations", report_error
        )
        railroad_check = _check_unavailable(
            "no_railroaded_crew_ejections", report_error
        )
        dangling_check = _check_unavailable(
            "no_dangling_primary_reason_id", report_error
        )

    if report is not None and substrate_by_seed is not None:
        provenance_check = check_cost_and_provenance(
            report,
            substrate_by_seed,
            expected_model=expected_model,
            expected_prompt_versions=expected_prompt_versions,
            require_zero_cost=require_zero_cost,
        )
    else:
        provenance_check = _check_unavailable(
            "cost_and_provenance_exact", report_error or substrate_error
        )

    checks = (
        game_over_check,
        meeting_check,
        dup_meeting_check,
        tick_1_check,
        friendly_fire_check,
        betrayal_check,
        railroad_check,
        dangling_check,
        provenance_check,
        byte_check,
    )
    return ValidityGateReport(
        replay_set_dir=str(replay_set_dir),
        passed=all(check.passed for check in checks),
        games_total=len(seeds),
        checks=checks,
    )


def _check_unavailable(name: str, error: str | None) -> ValidityCheck:
    """A check that could not run because its input replay data was malformed.

    Fails closed (``passed=False``): if the bytes cannot be read/reconstructed the
    gate must not PASS. ``byte_identical_reconstruction`` reports the concrete
    corruption; this records that the dependent check was skipped because of it.
    """

    detail = error or "replay data unavailable (malformed input)"
    return ValidityCheck(
        name=name,
        passed=False,
        summary="check unavailable — replay data could not be read/reconstructed",
        violations=(detail,),
        facts={"input_available": False},
    )


__all__ = [
    "FactValue",
    "MEETING_RATE_FLOOR",
    "TRUNCATED_REPLAY_REASON",
    "ValidityCheck",
    "ValidityGateReport",
    "assemble_tournament_report",
    "check_all_games_reach_game_over",
    "check_byte_identical_reconstruction",
    "check_cost_and_provenance",
    "check_meeting_rate_and_resolution",
    "check_no_betrayal",
    "check_no_dangling_primary_reason_id",
    "check_no_duplicate_meeting_rows",
    "check_no_friendly_fire_kills",
    "check_no_railroaded_crew_ejections",
    "check_no_tick_1_kills",
    "resolve_roster_knobs",
    "roles_by_seed",
    "run_validity_gate",
    "seeds_on_disk",
]
