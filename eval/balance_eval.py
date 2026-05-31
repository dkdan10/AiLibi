"""Headless tournament harness (DESIGN.md §11.3).

Aggregates outcomes across many :class:`HeadlessGame` runs. The harness
reuses the single-game orchestrator from Task 2.8 — it does not implement
its own tick loop.

:func:`run_tournament_eval` is the primary entry point (Task 5.6): it runs
one game per seed, captures each game's role ground truth from the in-memory
:class:`~orchestrator.game.HeadlessGameResult`, folds that seed's replay JSONL
records back into a typed :class:`~eval.report_schema.GameReport`, and collects
them into a :class:`~eval.report_schema.TournamentReport`. That Pydantic report
is the typed tournament artifact the Phase 5 metric modules and dashboard
consume (it supersedes :class:`BalanceReport` per Task 5.1's ``## Decisions``).

:func:`run_balance_eval` is retained as a thin compatibility reducer over
:func:`run_tournament_eval`: it collapses the report's per-game ``winner`` into
the crew / impostor / tick-budget buckets the Phase 2 balance gate reads. There
is exactly one game-running path (``run_tournament_eval``); ``run_balance_eval``
adds no second loop.

``roles`` MUST come from the in-memory seeded result, never the replay file:
the leak firewall keeps roles out of agent-visible data and the replay JSONL
never persists them (``report_schema.py:28-29``). An empty ``roles`` map for a
finished game is fail-loud — tasks 5.2-5.4 silently score zero impostor signal
without it.

``TICK_BUDGET_REACHED`` is a non-decisive outcome: such a game writes no
``game_over`` replay row, so its :class:`GameReport` carries ``winner=None`` /
``final_tick=None`` (the partial-run-robustness contract). ``run_balance_eval``
maps ``winner is None`` to its ``tick_budget_reached`` bucket.

A meeting that aborts under a real provider (a structured-output response that
fails schema validation) records its already-charged spend as a
``FailedCallReplayEntry`` and then re-raises. ``run_tournament_eval`` catches
that specific abort per seed, folds the partial replay (tick records + the
failed call, no ``game_over``) into a ``GameReport`` with ``winner=None``, and
continues — so one crashed meeting does not discard the whole tournament and the
recorded failed-call spend still lands in the report. Any other exception is an
unexpected bug and propagates fail-loud (AGENTS.md "no silent fallbacks").

``MEETING_PHASE_REACHED`` is **not** a reachable outcome here. Task 3.13 made
the meeting runner the production default (every game runs through a
:func:`orchestrator.game.build_default_meeting_runner`), so the public
tournament path always resumes after a meeting. If a public tournament game
ever produces ``MEETING_PHASE_REACHED`` the runner wire-up has regressed and
:func:`run_tournament_eval` raises fail-loud rather than silently recording it
(AGENTS.md "no silent fallbacks").
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from llm.budget import GameBudget
from llm.provider import extract_parse_failure
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_TASKS_PER_CREWMATE,
    AgentFactory,
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayLogEntry,
    compute_cost_usd,
    read_all_entries,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state


# --- Per-game budget configuration (Task 7.7; DESIGN.md §9, §11.4) -----------
#
# The per-game USD cap is env-overridable and the token caps scale with the
# roster, so a higher-token local run (Task 7.8 on the free Ollama provider) is
# possible without editing this module each time.

# Env knob for the per-game USD cap. Unset/empty falls back to
# ``_DEFAULT_MAX_COST_USD`` so the frozen baseline path is byte-identical to
# before this knob existed (see :func:`run_tournament_eval`).
_ENV_MAX_COST_USD: Final[str] = "AILIBI_MAX_COST_USD"

# Historical per-game USD cap: a safety stop for live-provider meeting traffic
# (the :class:`~llm.budget.GameBudget` default is the lower $0.30; the tournament
# path raises it -- see :func:`run_tournament_eval`'s docstring). On the Ollama
# provider the USD dimension is zeroed (Task 7.5), so this cap is moot there and
# the roster-scaled TOKEN caps below are the operative ceiling.
_DEFAULT_MAX_COST_USD: Final[float] = 1.00

# Per-game TOKEN caps scale LINEARLY with roster size: a larger meeting (more
# players speaking, longer transcripts threaded back into every agent's prompt)
# needs proportionally more tokens, and the Phase 7 diagnosis found the fixed
# caps too low for 7-player meetings. The caps follow:
#   max_input_tokens  = _BASE_INPUT_TOKENS  + _PER_PLAYER_INPUT_TOKENS  * num_players
#   max_output_tokens = _BASE_OUTPUT_TOKENS + _PER_PLAYER_OUTPUT_TOKENS * num_players
# The constants are chosen so the canonical 4-player roster reproduces the
# historical fixed caps EXACTLY -- 1_000_000 input / 200_000 output, the
# ``GameBudget`` defaults the frozen baseline recorded against -- so an unset
# knob at 4p is byte-identical to before this scaling existed. A 7-player meeting
# then resolves to a strictly larger ceiling so it is not truncated (the
# operative limit on the free local Ollama provider, whose USD dimension is
# zeroed). Worked values:
#   4p: 400_000 + 150_000*4 = 1_000_000 in ; 80_000 + 30_000*4 = 200_000 out
#   7p: 400_000 + 150_000*7 = 1_450_000 in ; 80_000 + 30_000*7 = 290_000 out
_BASE_INPUT_TOKENS: Final[int] = 400_000
_PER_PLAYER_INPUT_TOKENS: Final[int] = 150_000
_BASE_OUTPUT_TOKENS: Final[int] = 80_000
_PER_PLAYER_OUTPUT_TOKENS: Final[int] = 30_000


def _max_cost_usd_from_env(env: Mapping[str, str] | None = None) -> float:
    """Resolve the per-game USD cap from ``AILIBI_MAX_COST_USD``.

    Returns :data:`_DEFAULT_MAX_COST_USD` when the var is unset/empty so the
    frozen baseline path is unchanged. A non-numeric value is fail-loud
    (AGENTS.md "no silent fallbacks") rather than silently substituting the
    default; range/finiteness validation (negative / NaN / inf) is delegated to
    :class:`~llm.budget.GameBudget`, which raises on all three.
    """

    environment = env if env is not None else os.environ
    raw = environment.get(_ENV_MAX_COST_USD, "").strip()
    if not raw:
        return _DEFAULT_MAX_COST_USD
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{_ENV_MAX_COST_USD} must be a number, got {raw!r}") from exc


def _resolve_game_budget(
    *, num_players: int, env: Mapping[str, str] | None = None
) -> GameBudget:
    """Build the per-game :class:`~llm.budget.GameBudget` for ``num_players``.

    The USD cap comes from ``AILIBI_MAX_COST_USD`` (default ``$1.00``) and the
    token caps scale linearly with the roster (see the module constants), so a
    7-player meeting gets a strictly larger token ceiling than a 4-player one. A
    4-player roster with the knob unset reproduces the historical fixed
    ``GameBudget(max_cost_usd=1.00)`` caps exactly, leaving the frozen baseline
    path unchanged.
    """

    return GameBudget(
        max_cost_usd=_max_cost_usd_from_env(env),
        max_input_tokens=_BASE_INPUT_TOKENS + _PER_PLAYER_INPUT_TOKENS * num_players,
        max_output_tokens=_BASE_OUTPUT_TOKENS + _PER_PLAYER_OUTPUT_TOKENS * num_players,
    )


@dataclass(frozen=True)
class BalanceReport:
    """Aggregated outcomes for one tournament run.

    ``games == crew_wins + impostor_wins + tick_budget_reached``. The
    constructor verifies this invariant so a bucket can never be silently
    dropped. There is no ``meeting_phase_reached`` bucket: meetings fire
    end-to-end from the public tournament path (Task 3.13), so every game
    is decisive or hits the tick budget.

    This dataclass is now a *derived* view: :func:`run_balance_eval` reduces a
    :class:`~eval.report_schema.TournamentReport` (the typed tournament
    artifact) into these buckets. The buckets are recoverable from the report
    without information loss — crew / impostor wins from ``GameReport.winner``
    and non-decisive games from ``winner is None`` — so the report supersedes
    this dataclass as the emitted artifact (Task 5.1 ``## Decisions``; proven by
    ``tests/eval/test_report_schema.py``).
    """

    games: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    seeds_used: tuple[int, ...]

    def __post_init__(self) -> None:
        bucket_total = self.crew_wins + self.impostor_wins + self.tick_budget_reached
        if bucket_total != self.games:
            raise ValueError(
                "BalanceReport bucket totals must sum to games: "
                f"crew={self.crew_wins} impostors={self.impostor_wins} "
                f"tick_budget={self.tick_budget_reached} != games={self.games}"
            )
        if self.games != len(self.seeds_used):
            raise ValueError(
                f"games={self.games} must equal len(seeds_used)={len(self.seeds_used)}"
            )


def run_tournament_eval(
    *,
    seeds: Sequence[int],
    output_dir: Path,
    game_map: Map | None = None,
    agent_factory: AgentFactory | None = None,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
    max_ticks: int = DEFAULT_MAX_TICKS,
    force: bool = False,
) -> TournamentReport:
    """Run one :class:`HeadlessGame` per seed and assemble a typed report.

    The Phase 5 tournament entry point (Task 5.6). For each seed it runs a
    game, captures the role ground truth from the in-memory
    :class:`~orchestrator.game.HeadlessGameResult` (``final_state.players``),
    folds that seed's replay JSONL records back into a
    :class:`~eval.report_schema.GameReport`, and collects every game into a
    :class:`~eval.report_schema.TournamentReport`.

    ``output_dir`` receives one ``replay-seed-{seed}.jsonl`` plus its matching
    audit log per seed (see :class:`orchestrator.replay.ReplayLog` and
    :class:`observation.audit.ObservationAuditLog`). Seeds must be unique so
    per-seed replay paths do not clobber each other. ``game_map`` and
    ``agent_factory`` default to :func:`engine.world.load_canonical_map` and
    :func:`orchestrator.game.build_default_agent_factory` so the common case is
    a one-line call.

    Each game runs through a fresh meeting runner and a fresh
    :class:`llm.budget.GameBudget` built by
    :func:`orchestrator.game.build_default_meeting_runner` (Task 3.13): meetings
    fire end-to-end and the per-game cost cap is enforced at call time. The
    budget is resolved by :func:`_resolve_game_budget` (Task 7.7): the USD cap
    comes from ``AILIBI_MAX_COST_USD`` (default ``$1.00`` -- a safety stop for
    live-provider meeting traffic, well above the ``$0.30`` ``GameBudget``
    default and the Phase 3 mean-cost merge gate, Task 3.16) and the token caps
    scale linearly with ``num_players`` so a 7-player meeting is not truncated.
    The 4-player roster with the knob unset reproduces the historical fixed caps
    exactly, so the frozen baseline path is unchanged; on the Ollama provider the
    USD dimension is zeroed (Task 7.5), leaving the roster-scaled token caps as
    the operative ceiling. A new runner + budget is constructed per game so the
    budget resets and the per-game recording state is not shared across the
    tournament.

    Because the runner is always wired, a custom ``agent_factory`` must yield
    agents that satisfy the :class:`~orchestrator.game.MeetingAwareAgent`
    protocol whenever a seed can reach a meeting; the default factory does. A
    non-MeetingAware factory only stays valid for sweeps whose tick budget is
    too small to trigger any meeting (e.g. the wait-agent unit tests).

    ``force`` is threaded into each per-seed
    :class:`~orchestrator.replay.ReplayLog`: ``force=True`` truncates a
    pre-existing ``replay-seed-{seed}.jsonl`` at construction — immediately
    before that seed's game writes it, so a crash partway through a re-run never
    deletes a later seed's replay that was never reached. The default
    (``False``) makes a re-run against an ``output_dir`` whose replay files
    exist fail loud rather than silently doubling them (DESIGN.md §11.4; Task
    4.16).

    A meeting that aborts on a structured-output parse failure is caught per
    seed: the orchestrator has already recorded the failed call's spend to the
    replay, so this folds the partial replay into a ``winner=None``
    :class:`~eval.report_schema.GameReport` (roles re-seeded from the game setup)
    and continues. One crashed meeting therefore does not discard the whole
    tournament, and the failed-call spend still appears in the report.

    Raises ``RuntimeError`` if any game ends at ``MEETING_PHASE_REACHED`` (the
    Task 3.13 runner wire-up regressed). Re-raises any non-parse-failure
    exception from a game unchanged (AGENTS.md "no silent fallbacks").
    """

    if not seeds:
        raise ValueError("seeds must be non-empty")
    seeds_tuple = tuple(seeds)
    if len(set(seeds_tuple)) != len(seeds_tuple):
        raise ValueError("seeds must be unique")

    resolved_map = game_map if game_map is not None else load_canonical_map()
    resolved_factory = (
        agent_factory if agent_factory is not None else build_default_agent_factory()
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    games: list[GameReport] = []

    for seed in seeds_tuple:
        replay_path = output_dir / f"replay-seed-{seed}.jsonl"
        game = HeadlessGame(
            seed=seed,
            game_map=resolved_map,
            agent_factory=resolved_factory,
            replay_path=replay_path,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=max_ticks),
            meeting_runner=build_default_meeting_runner(
                budget=_resolve_game_budget(num_players=num_players)
            ),
            force=force,
        )
        try:
            result = game.run()
        except Exception as exc:
            # A meeting that aborted on a structured-output parse failure has
            # already recorded its FailedCallReplayEntry (the already-charged
            # spend) to the replay before re-raising
            # (orchestrator.game._run_and_apply_meeting). Recover the partial
            # game from that replay so one crashed meeting does not discard the
            # whole tournament AND the recorded failed-call spend still lands in
            # the report — the partial-run case the failed_calls/cost path exists
            # for. Anything else is an unexpected bug, so re-raise fail-loud
            # (AGENTS.md "no silent fallbacks").
            failure = extract_parse_failure(exc)
            if failure is None:
                raise
            games.append(
                _game_report_from_replay(
                    seed=seed,
                    # No HeadlessGameResult exists on the abort path, so re-seed
                    # to recover the role ground truth from the seeded game setup
                    # (still never the replay JSONL — the leak firewall keeps
                    # roles out of replay).
                    roles=_seeded_roles(
                        seed=seed,
                        game_map=resolved_map,
                        num_players=num_players,
                        num_impostors=num_impostors,
                        tasks_per_crewmate=tasks_per_crewmate,
                    ),
                    fallback_reason=(
                        f"meeting aborted before game_over ({failure.error_type})"
                    ),
                    replay_path=replay_path,
                )
            )
            continue
        if result.outcome == "MEETING_PHASE_REACHED":
            raise RuntimeError(
                f"seed {seed} ended at MEETING_PHASE_REACHED; the public "
                "tournament path always wires a meeting runner, so this "
                "outcome indicates the Task 3.13 runner wire-up regressed"
            )
        # Roles come from the in-memory seeded result, NOT the replay JSONL:
        # the leak firewall keeps them out of replay (report_schema.py:28-29).
        roles = {
            player_id: player.role
            for player_id, player in result.final_state.players.items()
        }
        games.append(
            _game_report_from_replay(
                seed=seed,
                roles=roles,
                fallback_reason=result.outcome,
                replay_path=result.replay_path,
            )
        )

    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=tuple(games),
        seeds_used=seeds_tuple,
    )


def run_balance_eval(
    *,
    seeds: Sequence[int],
    output_dir: Path,
    game_map: Map | None = None,
    agent_factory: AgentFactory | None = None,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    max_ticks: int = DEFAULT_MAX_TICKS,
    force: bool = False,
) -> BalanceReport:
    """Run a tournament and reduce it to the balance buckets.

    A thin compatibility wrapper over :func:`run_tournament_eval`: it runs the
    single game-running path, then collapses the resulting
    :class:`~eval.report_schema.TournamentReport` into the crew / impostor /
    tick-budget :class:`BalanceReport` the Phase 2 balance gate reads. All
    arguments are forwarded unchanged, so existing callers keep their behavior
    while the typed report becomes the canonical artifact (Task 5.6).
    """

    report = run_tournament_eval(
        seeds=seeds,
        output_dir=output_dir,
        game_map=game_map,
        agent_factory=agent_factory,
        num_players=num_players,
        num_impostors=num_impostors,
        max_ticks=max_ticks,
        force=force,
    )
    return _balance_report_from_tournament(report)


# Reason recorded for a loaded game whose replay carries no ``game_over`` row
# (a partial / non-decisive recorded game). On the live tournament path
# ``run_tournament_eval`` supplies the in-memory outcome instead; the pure
# loader has no such outcome, so it states the fact plainly rather than
# inventing a winner (AGENTS.md "no silent fallbacks").
_LOADED_REPLAY_FALLBACK_REASON: Final[str] = "no game_over record in replay"


def load_tournament_report(
    replay_dir: Path,
    *,
    roles_by_seed: Mapping[int, Mapping[PlayerId, Role]],
) -> TournamentReport:
    """Assemble a :class:`TournamentReport` from recorded replay JSONL on disk.

    The public JSONL->report loader. For each seed in ``roles_by_seed`` (in
    ascending seed order) it reads ``replay_dir / "replay-seed-{seed}.jsonl"``
    and folds it into a :class:`~eval.report_schema.GameReport` via the SAME
    per-seed assembly :func:`run_tournament_eval` uses
    (:func:`_game_report_from_replay`, which in turn calls
    :func:`_game_cost_summary`) -- it does not duplicate the record->report
    mapping, so the two entry points cannot drift.

    This is the report-build path that has no live model and no engine re-run:
    given frozen recorded replays plus a deterministically-derived ``roles`` map,
    it reconstructs the typed tournament artifact the Phase 5 metrics analyze.
    ``run_tournament_eval`` (which runs games and captures roles from the
    in-memory result) is unchanged -- this is a behavior-preserving promotion of
    the existing private assembly to a public, directory-driven entry point
    (the prompt-regression suite, Task 5.8, is the first consumer).

    ``roles_by_seed`` supplies the per-game role ground truth (which players are
    impostors) keyed by seed. It is NOT read from the replay JSONL -- the leak
    firewall keeps roles out of replay -- so a caller derives it deterministically
    from the seeded game setup (e.g. :func:`orchestrator.seeder.seed_initial_state`).
    ``seeds_used`` on the returned report is the sorted tuple of those seeds.

    Fail-loud (AGENTS.md "no silent fallbacks"):

    * an empty ``roles_by_seed`` raises ``ValueError`` -- there is nothing to
      load and a zero-game report is almost certainly a caller mistake;
    * a seed whose ``replay-seed-{seed}.jsonl`` is absent raises
      ``FileNotFoundError`` -- the caller asserted a recorded game for that seed,
      so a missing file is an inconsistency, not something to skip silently;
    * an empty ``roles`` map for any seed, or a doubled/corrupted replay file,
      raises via :func:`_game_report_from_replay` exactly as on the live path.
    """

    if not roles_by_seed:
        raise ValueError("roles_by_seed must be non-empty")

    seeds = tuple(sorted(roles_by_seed))
    games: list[GameReport] = []
    for seed in seeds:
        replay_path = replay_dir / f"replay-seed-{seed}.jsonl"
        if not replay_path.exists():
            raise FileNotFoundError(
                f"seed {seed}: no recorded replay at {replay_path}. "
                "load_tournament_report folds frozen recorded replays; a seed "
                "with roles supplied but no replay file on disk is an "
                "inconsistency, not a game to skip."
            )
        games.append(
            _game_report_from_replay(
                seed=seed,
                roles=roles_by_seed[seed],
                fallback_reason=_LOADED_REPLAY_FALLBACK_REASON,
                replay_path=replay_path,
            )
        )

    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=tuple(games),
        seeds_used=seeds,
    )


def _seeded_roles(
    *,
    seed: int,
    game_map: Map,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
) -> dict[PlayerId, Role]:
    """Recover a game's role ground truth by re-running the deterministic seeding.

    Used only on the meeting-abort path, where no
    :class:`~orchestrator.game.HeadlessGameResult` exists to read roles from.
    :func:`orchestrator.seeder.seed_initial_state` is the same seeded game setup
    the aborted game ran (same seed + config) and roles never change mid-game, so
    this reconstructs the identical map the in-memory result would have carried —
    still the seeded setup, never the replay JSONL (the leak firewall).

    ``tasks_per_crewmate`` is threaded so the re-seed uses the exact config the
    aborted game ran. Roles themselves are independent of the task count, but
    passing it keeps this call identical to the game's own
    :func:`seed_initial_state` invocation rather than relying on a default that
    could drift from the harness.
    """

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    return {player_id: player.role for player_id, player in state.players.items()}


def _balance_report_from_tournament(report: TournamentReport) -> BalanceReport:
    """Collapse a :class:`TournamentReport` into the legacy balance buckets.

    Crew / impostor wins reduce out of ``GameReport.winner``; a non-decisive
    game (``winner is None``, i.e. it hit the tick budget and wrote no
    ``game_over`` row) maps to ``tick_budget_reached``. No information is lost —
    every game falls into exactly one bucket — so ``BalanceReport``'s
    sum-to-games invariant holds by construction.
    """

    crew_wins = sum(1 for game in report.games if game.winner == "CREWMATES")
    impostor_wins = sum(1 for game in report.games if game.winner == "IMPOSTORS")
    tick_budget_reached = sum(1 for game in report.games if game.winner is None)
    return BalanceReport(
        games=len(report.games),
        crew_wins=crew_wins,
        impostor_wins=impostor_wins,
        tick_budget_reached=tick_budget_reached,
        seeds_used=report.seeds_used,
    )


def _game_report_from_replay(
    *,
    seed: int,
    roles: Mapping[PlayerId, Role],
    fallback_reason: str,
    replay_path: Path,
) -> GameReport:
    """Fold one seed's replay JSONL + in-memory roles into a :class:`GameReport`.

    The JSONL→report loader deferred from Task 5.1. Reads the seed's replay
    records via :func:`orchestrator.replay.read_all_entries` (which fails loud
    on a doubled/corrupted file) and maps them: ``MeetingReplayEntry`` →
    :class:`~eval.report_schema.MeetingReport`, the single
    ``GameEndReplayEntry`` → ``winner`` / ``reason`` / ``final_tick``, and
    ``FailedCallReplayEntry`` rows → ``failed_calls``.

    ``roles`` is the in-memory role ground truth (never the replay JSONL); an
    empty map for a finished game is a fail-loud error, because the
    meeting-quality metrics (tasks 5.2-5.4) silently report zero impostor signal
    without it.

    Partial-run robustness: a game that crashed / hit the tick budget before a
    ``game_over`` row yields ``winner=None`` / ``final_tick=None`` and whatever
    meetings were recorded, using ``fallback_reason`` (the in-memory outcome)
    for ``reason``. A doubled/corrupted file still raises
    :class:`orchestrator.replay.ReplayLog.CorruptedFileError` via
    ``read_all_entries``.
    """

    if not roles:
        raise ValueError(
            f"seed {seed}: roles map is empty for a finished game. Roles are "
            "captured from the in-memory HeadlessGameResult.final_state, never "
            "the replay JSONL (the leak firewall keeps them out of replay); an "
            "empty map silently zeroes the impostor-signal metrics (tasks "
            "5.2-5.4), so this is fail-loud."
        )

    entries: tuple[ReplayLogEntry, ...]
    if replay_path.exists():
        entries = read_all_entries(replay_path)
        # total_cost_usd via the canonical reducer, which ALREADY folds in
        # failed-call cost. Never re-add failed_calls cost (no-double-count).
        total_cost_usd = compute_cost_usd(replay_path)
    else:
        # Pathological: a zero-tick game (max_ticks<=0) writes no records, so
        # the file was never created. Treat as an empty log rather than raising.
        entries = ()
        total_cost_usd = 0.0

    meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
    meetings = tuple(_meeting_report_from_entry(entry) for entry in meeting_entries)
    failed_calls = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
    end = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)

    # prompt_versions are constant within a run (templates load once), so they
    # collapse losslessly to game granularity; empty for a game with no meeting.
    prompt_versions: Mapping[str, str] = (
        dict(meeting_entries[0].prompt_versions) if meeting_entries else {}
    )
    game_id = entries[0].game_id if entries else f"headless-seed-{seed}"

    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=end.winner if end is not None else None,
        reason=end.reason if end is not None else fallback_reason,
        final_tick=end.tick if end is not None else None,
        roles=roles,
        replay_ref=replay_path.name,
        meetings=meetings,
        failed_calls=failed_calls,
        prompt_versions=prompt_versions,
        cost=_game_cost_summary(total_cost_usd=total_cost_usd, entries=entries),
    )


def _meeting_report_from_entry(entry: MeetingReplayEntry) -> MeetingReport:
    """Map a ``MeetingReplayEntry`` to a :class:`MeetingReport` (near 1:1).

    The replay entry's engine-determinism fields (``state_hash_before`` /
    ``state_hash_after``), its ``game_id``, and its per-meeting
    ``prompt_versions`` (collapsed to game level in
    :func:`_game_report_from_replay`) are intentionally dropped; everything a
    Phase 5 behavioral metric reads is carried over verbatim.
    """

    return MeetingReport(
        meeting_id=entry.meeting_id,
        tick=entry.tick,
        triggered_by=entry.triggered_by,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        transcript=entry.transcript,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        llm_calls=entry.llm_calls,
    )


def _game_cost_summary(
    *,
    total_cost_usd: float,
    entries: tuple[ReplayLogEntry, ...],
) -> GameCostSummary:
    """Build the per-game cost roll-up (DESIGN.md §10.4, §11.3).

    ``total_cost_usd`` is supplied by the canonical reducer
    :func:`orchestrator.replay.compute_cost_usd` (which already folds in
    failed-call spend). ``total_input_tokens`` / ``total_output_tokens`` /
    ``by_model`` are summed across the SAME records — meeting ``llm_calls`` plus
    ``failed_calls`` — in one pass, so ``sum(by_model.values())`` reconciles to
    ``total_cost_usd``. Counting spend here once is the single place it is
    counted; the cost dashboard (Task 5.5) must not re-add failed-call cost.
    """

    total_input_tokens = 0
    total_output_tokens = 0
    by_model: dict[str, float] = {}
    for entry in entries:
        if isinstance(entry, MeetingReplayEntry):
            for call in entry.llm_calls:
                total_input_tokens += call.input_tokens
                total_output_tokens += call.output_tokens
                by_model[call.model] = by_model.get(call.model, 0.0) + call.cost_usd
        elif isinstance(entry, FailedCallReplayEntry):
            total_input_tokens += entry.input_tokens
            total_output_tokens += entry.output_tokens
            by_model[entry.model] = by_model.get(entry.model, 0.0) + entry.cost_usd
    return GameCostSummary(
        total_cost_usd=total_cost_usd,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        by_model={model: by_model[model] for model in sorted(by_model)},
    )


__all__ = [
    "BalanceReport",
    "load_tournament_report",
    "run_balance_eval",
    "run_tournament_eval",
]
