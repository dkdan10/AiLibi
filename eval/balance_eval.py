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
counts explicit tick-limit evidence separately from aborted, unfinished, and
unverified outcomes; only verified terminal outcomes enter its win buckets.

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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, NoReturn

from engine.entities import PlayerId, Role
from engine.events import (
    EngineEvent,
    KilledEvent,
)
from engine.world import Map, WorldState, load_canonical_map
from eval.replay_walk import (
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
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
    MeetingRunner,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    CrewTacticalPolicyStamp,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    GameStopReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLogEntry,
    TacticalPolicyStamp,
    compute_cost_usd,
    read_all_entries,
    recorded_completion_status,
)
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler
from orchestrator.run_limits import RunDeadline
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
    *,
    num_players: int,
    env: Mapping[str, str] | None = None,
    parent: GameBudget | None = None,
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
        parent=parent,
        max_cost_usd=_max_cost_usd_from_env(env),
        max_input_tokens=_BASE_INPUT_TOKENS + _PER_PLAYER_INPUT_TOKENS * num_players,
        max_output_tokens=_BASE_OUTPUT_TOKENS + _PER_PLAYER_OUTPUT_TOKENS * num_players,
    )


@dataclass(frozen=True)
class BalanceReport:
    """Verified win counts plus separate reasons for nonterminal recordings.

    The mutually exclusive buckets cover every recorded game. A completed
    historical report without replay verification belongs to ``unverified``.
    """

    games: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    seeds_used: tuple[int, ...]
    aborted: int = 0
    unfinished: int = 0
    unverified: int = 0

    @property
    def verified_outcomes(self) -> int:
        return self.crew_wins + self.impostor_wins

    def __post_init__(self) -> None:
        bucket_total = (
            self.crew_wins
            + self.impostor_wins
            + self.tick_budget_reached
            + self.aborted
            + self.unfinished
            + self.unverified
        )
        if bucket_total != self.games:
            raise ValueError(
                "BalanceReport bucket totals must sum to games: "
                f"crew={self.crew_wins} impostors={self.impostor_wins} "
                f"tick_budget={self.tick_budget_reached} aborted={self.aborted} "
                f"unfinished={self.unfinished} unverified={self.unverified} != games={self.games}"
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
    tactical_policy_stamp: TacticalPolicyStamp | None = None,
    crew_policy_stamp: CrewTacticalPolicyStamp | None = None,
    meeting_runner_factory: Callable[[], MeetingRunner] | None = None,
    tournament_budget: GameBudget | None = None,
    deadline: RunDeadline | None = None,
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

    ``force`` is threaded into each per-seed :class:`HeadlessGame`.
    ``force=True`` replaces that seed's replay and observation audit together
    when it starts, leaving later seeds' outputs intact if the run stops early.
    The default (``False``) refuses either existing output before replacement,
    so an old audit cannot silently accumulate another game's packets.

    A meeting that aborts on a structured-output parse failure is caught per
    seed: the orchestrator has already recorded the failed call's spend to the
    replay, so this folds the partial replay into a ``winner=None``
    :class:`~eval.report_schema.GameReport` (roles re-seeded from the game setup)
    and continues. One crashed meeting therefore does not discard the whole
    tournament, and the failed-call spend still appears in the report.

    ``tactical_policy_stamp`` is the additive-optional tactical-policy provenance
    stamp (Task 15.9): the pass-through that lets a learned-policy recording stamp
    every game's ``game_over`` record without a later out-of-scope edit. It is
    forwarded verbatim to each per-seed :class:`HeadlessGame`; the default
    (``None``) records the absent = scripted-FSM-default stamp, byte-identical to
    the pre-15.9 path. ``scripts/run_tournament.py`` exposes it as the
    ``--tactical-policy-stamp`` CLI flag (the seam the Task-15.12 corpus wrapper
    drives).

    ``crew_policy_stamp`` is the additive crew-side provenance pass-through (Task
    18.7): the crew twin of ``tactical_policy_stamp``, forwarded verbatim to each
    per-seed :class:`HeadlessGame` as ``crew_tactical_policy_stamp`` so a
    learned-crew recording stamps every game's ``game_over`` record in its own
    DISTINCT :class:`~orchestrator.replay.CrewTacticalPolicyStamp` slot (never
    conflated with the impostor stamp). The default (``None``) records the absent =
    scripted-crew-default stamp, byte-identical to the pre-18.7 path.
    ``scripts/run_tournament.py``'s learned-crew arm drives it.

    ``meeting_runner_factory`` (Task 15.13) is the additive-optional per-game
    meeting-runner factory, mirroring the default path's fresh-runner-per-game
    construction: when supplied it is invoked once per seed and the produced
    runner is installed in that seed's :class:`HeadlessGame` in place of
    :func:`~orchestrator.game.build_default_meeting_runner` (a fresh runner per
    game keeps per-game recording state unshared, exactly like the default). The
    seam exists so surrogate-driven tournaments
    (:func:`training.surrogate.runner.load_surrogate_runner_factory`) produce
    standard :class:`~eval.report_schema.TournamentReport` artifacts for
    DIAGNOSTICS — final champion scoring still always uses a real meeting path
    (the default runner; the bake-off's reporting rule). The default (``None``)
    keeps the runner construction byte-identical to the pre-15.13 path.

    ``tournament_budget`` optionally supplies the parent of each fresh per-game
    budget. The sequential seed loop shares that cumulative allowance without
    resetting it. ``deadline`` additionally checks tick boundaries and bounds
    asynchronous meeting work. These limits require the default budgeted runner;
    an opaque custom runner cannot promise to enforce provider limits.

    Raises ``RuntimeError`` if any game ends at ``MEETING_PHASE_REACHED`` (the
    Task 3.13 runner wire-up regressed). Re-raises any non-parse-failure
    exception from a game unchanged (AGENTS.md "no silent fallbacks").
    """

    if not seeds:
        raise ValueError("seeds must be non-empty")
    if meeting_runner_factory is not None and (
        tournament_budget is not None or deadline is not None
    ):
        raise ValueError("Whole-run limits require the budgeted default meeting runner")
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
        if meeting_runner_factory is not None:
            meeting_runner = meeting_runner_factory()
        else:
            game_budget = _resolve_game_budget(
                num_players=num_players, parent=tournament_budget
            )
            meeting_runner = (
                build_default_meeting_runner(budget=game_budget)
                if deadline is None
                else build_default_meeting_runner(budget=game_budget, deadline=deadline)
            )
        game = HeadlessGame(
            deadline=deadline,
            seed=seed,
            game_map=resolved_map,
            agent_factory=resolved_factory,
            replay_path=replay_path,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=max_ticks),
            meeting_runner=meeting_runner,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
            crew_tactical_policy_stamp=crew_policy_stamp,
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
            roles = _seeded_roles(
                seed=seed,
                game_map=resolved_map,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
            )
            _current_replay_facts(
                replay_path,
                seed=seed,
                roles=roles,
                tasks_per_crewmate=tasks_per_crewmate,
                game_map=resolved_map,
            )
            games.append(
                _game_report_from_replay(
                    seed=seed,
                    # No HeadlessGameResult exists on the abort path, so re-seed
                    # to recover the role ground truth from the seeded game setup
                    # (still never the replay JSONL — the leak firewall keeps
                    # roles out of replay).
                    roles=roles,
                    fallback_reason=(
                        f"meeting aborted before game_over ({failure.error_type})"
                    ),
                    replay_path=replay_path,
                    integrity_verified=True,
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
        # Kill-gifted accounting (Task 8.17): derived from a deterministic engine
        # walk of the just-recorded replay, with the roster this run used.
        kill_gift = _current_replay_facts(
            result.replay_path,
            seed=seed,
            roles=roles,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=resolved_map,
        )
        games.append(
            _game_report_from_replay(
                seed=seed,
                roles=roles,
                fallback_reason=result.outcome,
                replay_path=result.replay_path,
                integrity_verified=True,
                kill_gifted=kill_gift.kill_gifted,
                instances_dropped=kill_gift.instances_dropped,
                instances_complete_at_win=kill_gift.instances_complete_at_win,
            )
        )

    return build_tournament_report(games=games, seeds=seeds_tuple)


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
    tasks_per_crewmate: int = 1,
    game_map: Map | None = None,
    derive_kill_gift: bool = True,
) -> TournamentReport:
    """Certify recorded games against their setup before assembling a report.

    Each recording is reconstructed with the supplied seed, roster, task count,
    and map. Role truth must match that seeded setup. The shared spectator
    validator checks original row order, meeting boundaries, hashes, and any
    recorded terminal outcome. Valid prefixes remain partial games.

    ``derive_kill_gift=False`` omits the optional task-accounting fields; it
    never disables integrity validation. Frozen analyses that intentionally
    interpret recorded outcomes without current-engine certification must use
    :func:`load_historical_tournament_report` explicitly.
    """

    return _load_tournament_report(
        replay_dir,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        derive_kill_gift=derive_kill_gift,
        historical=False,
    )


def load_historical_tournament_report(
    replay_dir: Path,
    *,
    roles_by_seed: Mapping[int, Mapping[PlayerId, Role]],
) -> TournamentReport:
    """Fold frozen evidence without certifying it under the current engine.

    This compatibility path preserves historical prompt-regression and validity
    analyses whose contracts own their reconstruction checks separately. It
    parses recorded outcomes and costs, with no derived kill-gift metrics or
    current setup validation. It must not publish a newly certified outcome.
    """

    return _load_tournament_report(
        replay_dir,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=1,
        game_map=None,
        derive_kill_gift=False,
        historical=True,
    )


def _load_tournament_report(
    replay_dir: Path,
    *,
    roles_by_seed: Mapping[int, Mapping[PlayerId, Role]],
    tasks_per_crewmate: int,
    game_map: Map | None,
    derive_kill_gift: bool,
    historical: bool,
) -> TournamentReport:
    """Share the recorded-row fold while making certification explicit."""

    if not roles_by_seed:
        raise ValueError("roles_by_seed must be non-empty")

    resolved_map = game_map if game_map is not None else load_canonical_map()
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
        facts = (
            _current_replay_facts(
                replay_path,
                seed=seed,
                roles=roles_by_seed[seed],
                tasks_per_crewmate=tasks_per_crewmate,
                game_map=resolved_map,
            )
            if not historical
            else _NO_KILL_GIFT
        )
        kill_gift = facts if derive_kill_gift else _NO_KILL_GIFT
        games.append(
            _game_report_from_replay(
                seed=seed,
                roles=roles_by_seed[seed],
                fallback_reason=_LOADED_REPLAY_FALLBACK_REASON,
                replay_path=replay_path,
                integrity_verified=not historical,
                kill_gifted=kill_gift.kill_gifted,
                instances_dropped=kill_gift.instances_dropped,
                instances_complete_at_win=kill_gift.instances_complete_at_win,
            )
        )

    return build_tournament_report(games=games, seeds=seeds)


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


@dataclass(frozen=True)
class _KillGiftFacts:
    """One game's kill-gifted accounting (Task 8.17; DESIGN.md §3.5; audit gp-4).

    The three additive :class:`~eval.report_schema.GameReport` facts, derived
    deterministically by :func:`_kill_gift_accounting`'s engine walk. See that
    function and :class:`~eval.report_schema.GameReport` for the field meanings.
    """

    kill_gifted: bool
    instances_dropped: int
    instances_complete_at_win: int


_NO_KILL_GIFT: Final[_KillGiftFacts] = _KillGiftFacts(
    kill_gifted=False, instances_dropped=0, instances_complete_at_win=0
)


def _current_replay_facts(
    replay_path: Path,
    *,
    seed: int,
    roles: Mapping[PlayerId, Role],
    tasks_per_crewmate: int,
    game_map: Map,
) -> _KillGiftFacts:
    """Validate setup and timeline while collecting optional task facts."""

    seeded_roles = _seeded_roles(
        seed=seed,
        game_map=game_map,
        num_players=len(roles),
        num_impostors=sum(role == "IMPOSTOR" for role in roles.values()),
        tasks_per_crewmate=tasks_per_crewmate,
    )
    if dict(roles) != seeded_roles:
        raise ReplayIntegrityError(
            game_id=f"headless-seed-{seed}",
            code="role_setup_mismatch",
            detail="supplied role truth differs from the seeded recording setup",
        )
    return _kill_gift_accounting(
        replay_path,
        seed=seed,
        roles=roles,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=_CURRENT_REPORT_WALK_CONFIG,
    )


def _kill_gift_accounting(
    replay_path: Path,
    *,
    seed: int,
    roles: Mapping[PlayerId, Role],
    tasks_per_crewmate: int,
    game_map: Map,
    config: ReplayWalkConfig | None = None,
) -> _KillGiftFacts:
    """Derive a game's kill-gifted facts from a deterministic engine replay walk.

    Task 8.17 (DESIGN.md §3.5; audit gp-4 / A-A-1 / B-B-7). The §3.5 dead-owner
    drop means a recorded *action* row is not enough: a kill can be
    engine-rejected, and the task pool completes only via RESOLVED events, so the
    facts must come from re-running the engine, not from the raw rows. This
    re-seeds the game and re-applies the recorded action stream (and meeting
    outcomes) through :func:`eval.replay_walk.walk_replay` under the named
    ``kill-gift`` profile (Task 19.25) -- the same read-only playback
    :func:`eval.win_condition_selfcheck.check_replay_win_condition` performs --
    verifying every reconstructed ``state_hash`` against the recording so a wrong
    roster (or a determinism break) fails loud rather than yielding misleading
    counts.

    Returns (all derived from the walk, never the raw rows):

    * ``kill_gifted`` -- ``True`` iff the recorded winner is ``CREWMATES`` by
      ``CREWMATE_TASKS`` AND the game ended on a *tick* (not a meeting
      resolution) whose events resolve a ``Killed`` whose victim held >= 1
      INCOMPLETE task instance at kill resolution (the §3.5 dead-owner drop then
      removed it, tipping the crew pool to complete). The predicate is anchored
      to the VICTIM, not the tick's completion set: a same-tick task completion
      by ANOTHER player does NOT mask the gift (audit gp-4 / A-A-2 corrected the
      old completion-based definition, which undercounted 8/46 vs the true
      11/46 -- e.g. seed 11), while a victim that self-completed its OWN last
      instance the same tick before the kill is correctly excluded (the
      completed instance survives the drop, so nothing was gifted -- seed 40).
      See :func:`_final_kill_dropped_victim_instance`. A ``CREWMATE_TASKS`` win
      declared by an ejection's task drop is not kill-gifted either (no kill
      resolved on the deciding step). ``False`` for every other outcome and for a
      partial game.
    * ``instances_dropped`` -- the seeded instance count minus ``len(state.tasks)``
      at game end (how many instances the §3.5 drop removed over the game).
    * ``instances_complete_at_win`` -- the completed instances still in
      ``state.tasks`` at game end.

    ``num_players`` / ``num_impostors`` are read off ``roles`` (the in-memory
    ground truth the fold already carries); only ``tasks_per_crewmate`` and
    ``game_map`` -- which ``roles`` cannot supply -- are passed explicitly so the
    re-seed matches the recording. A missing replay file (the pathological
    zero-tick game) yields the no-kill-gift defaults rather than raising, exactly
    as :func:`_game_report_from_replay` treats it as an empty log.
    """

    if not replay_path.exists():
        return _NO_KILL_GIFT

    num_players = len(roles)
    num_impostors = sum(1 for role in roles.values() if role == "IMPOSTOR")

    # The events of the advance_tick that ended the game, plus the PRE-tick (=
    # pre-§3.5-drop) state that tick started from; both are only set when the game
    # ends ON A TICK (an ejection-driven game-over resolves in a meeting, which
    # cannot carry a kill, so they stay empty/None -> not kill-gifted). The
    # pre-drop state lets the predicate read the victim's instance set at kill
    # resolution (audit gp-4 / A-A-2).
    final_tick_events: tuple[EngineEvent, ...] = ()
    pre_final_tick_state: WorldState | None = None
    game_over_on_tick = False
    seeded_instance_count: int | None = None
    final_state: WorldState | None = None
    game_end = None

    for walk_event in walk_replay(
        replay_path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
        config=config if config is not None else _KILL_GIFT_WALK_CONFIG,
    ):
        if isinstance(walk_event, TickOpened):
            if seeded_instance_count is None:
                seeded_instance_count = len(walk_event.state.tasks)
        elif isinstance(walk_event, TickAdvanced):
            if walk_event.state.phase == "GAME_OVER":
                final_tick_events = walk_event.events
                pre_final_tick_state = walk_event.pre_state
                game_over_on_tick = True
        elif isinstance(walk_event, WalkComplete):
            final_state = walk_event.state
            game_end = walk_event.game_end

    if final_state is None or seeded_instance_count is None:
        # A recorded game always carries at least one tick row; an empty file is
        # the zero-tick pathology handled by the missing-file default above.
        return _NO_KILL_GIFT

    instances_dropped = seeded_instance_count - len(final_state.tasks)
    instances_complete_at_win = sum(
        1 for task in final_state.tasks.values() if task.completed
    )

    winner = game_end.winner if game_end is not None else None
    reason = game_end.reason if game_end is not None else None
    kill_gifted = (
        winner == "CREWMATES"
        and reason == "CREWMATE_TASKS"
        and game_over_on_tick
        and _final_kill_dropped_victim_instance(
            final_tick_events=final_tick_events,
            pre_drop_state=pre_final_tick_state,
            post_drop_state=final_state,
        )
    )
    return _KillGiftFacts(
        kill_gifted=kill_gifted,
        instances_dropped=instances_dropped,
        instances_complete_at_win=instances_complete_at_win,
    )


def _final_kill_dropped_victim_instance(
    *,
    final_tick_events: tuple[EngineEvent, ...],
    pre_drop_state: WorldState | None,
    post_drop_state: WorldState,
) -> bool:
    """True iff the game-ending tick's kill removed >= 1 of its victim's instances.

    The victim-anchored kill-gift predicate (DESIGN.md §3.5; audit gp-4 / A-A-2).
    The §3.5 dead-owner drop removes exactly the victim's INCOMPLETE task
    instances at kill resolution and leaves the completed ones, so a victim whose
    instance count fell from the pre-drop (pre-tick) state to the post-drop
    (game-over) state held >= 1 incomplete instance when the kill resolved -- the
    drop is what tipped the crew pool to complete, i.e. the win was gifted.

    Reading the count DIFFERENCE rather than the pre-drop incomplete count is what
    makes the predicate victim-anchored rather than tick-anchored:

    * a same-tick task completion by ANOTHER player does not touch this victim's
      count, so it cannot mask a genuine gift -- the bug the old completion-based
      definition had (undercounting 8/46 vs the true 11/46; seed 11 tick 20:
      victim p-6 killed holding ``upload_logs`` 4/6 while p-5 completes a
      different instance the same tick);
    * a victim that self-completed its OWN last instance the same tick before the
      kill leaves an unchanged count (the completed instance survives the drop),
      so it is correctly excluded (seed 40 tick 22).

    ``pre_drop_state`` is ``None`` only when the game did not end on a tick (an
    ejection-driven game-over carries no kill), which is never kill-gifted, so
    that yields ``False``. Counting is conserved through a tick except for the
    §3.5 drop -- ``do_task`` mutates progress, never the instance set -- so the
    per-victim count difference is exactly the instances that kill dropped.
    """

    if pre_drop_state is None:
        return False
    for event in final_tick_events:
        if not isinstance(event, KilledEvent):
            continue
        victim = event.target
        pre_count = sum(
            1 for task in pre_drop_state.tasks.values() if task.owner == victim
        )
        post_count = sum(
            1 for task in post_drop_state.tasks.values() if task.owner == victim
        )
        if pre_count > post_count:
            return True
    return False


def _raise_kill_gift_walk_violation(violation: WalkViolation) -> NoReturn:
    """Fail loud if the kill-gift walk's reconstructed ``state_hash`` diverges.

    Mirrors :func:`eval.win_condition_selfcheck._raise_walk_violation`: a
    divergence means the roster passed to :func:`_kill_gift_accounting` does not
    match the recording (or engine playback is non-deterministic), so the
    derived counts would be wrong -- raise rather than report a misleading
    number.
    """

    raise ValueError(
        f"kill-gift accounting reconstruction diverged for {violation.game_id!r} at "
        f"tick {violation.tick}: recorded {violation.expected!r}, reconstructed "
        f"{violation.actual!r}. The "
        "roster passed to _kill_gift_accounting does not match the recording, "
        "or engine playback is non-deterministic."
    )


# The named Task 19.25 profile (see eval/replay_walk.py's drift record): verify
# per-tick hashes + each meeting's state_hash_after; TRUNCATE on a partial
# meeting, mirroring the loader's partial-replay handling.
_KILL_GIFT_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="kill-gift",
    on_violation=_raise_kill_gift_walk_violation,
    verify_tick_hashes=True,
    verify_action_dispositions=True,
    missing_meeting_row="truncate",
    verify_meeting_post_hashes=True,
)


def _raise_current_report_violation(violation: WalkViolation) -> NoReturn:
    raise ReplayIntegrityError(
        game_id=violation.game_id,
        code=violation.kind,
        tick=violation.tick,
        detail=(f"recorded {violation.expected!r}, reconstructed {violation.actual!r}"),
    )


_CURRENT_REPORT_WALK_CONFIG: Final[ReplayWalkConfig] = ReplayWalkConfig(
    supports_temporal_observations=True,
    profile="current-report",
    supports_experiments=True,
    on_violation=_raise_current_report_violation,
    verify_tick_hashes=True,
    verify_action_dispositions=True,
    missing_meeting_row="truncate",
    verify_meeting_post_hashes=True,
    verify_chronology_and_outcome=True,
)


def _tournament_aggregates(
    games: Sequence[GameReport],
) -> tuple[int, int, float | None]:
    """Roll up the per-game kill-gift facts for a :class:`TournamentReport`.

    Returns ``(kill_gifted_wins, instances_dropped_total,
    mean_instances_complete_at_win)``. The mean is taken over the
    ``CREWMATE_TASKS`` *wins* -- the games the "completed-at-win" metric is about
    (audit gp-4) -- and is ``None`` when the tournament had no such win, the same
    undefined-not-zero sentinel the other eval rates use for an empty
    denominator. See :class:`~eval.report_schema.TournamentReport`.
    """

    kill_gifted_wins = sum(1 for game in games if game.kill_gifted)
    instances_dropped_total = sum(game.instances_dropped for game in games)
    task_win_completes = [
        game.instances_complete_at_win
        for game in games
        if game.winner == "CREWMATES" and game.reason == "CREWMATE_TASKS"
    ]
    mean_complete = (
        sum(task_win_completes) / len(task_win_completes)
        if task_win_completes
        else None
    )
    return kill_gifted_wins, instances_dropped_total, mean_complete


def build_tournament_report(
    *, games: Sequence[GameReport], seeds: Sequence[int]
) -> TournamentReport:
    """Assemble one report from retained games without re-running or reclassifying them."""
    kill_gifted_wins, instances_dropped_total, mean_complete = _tournament_aggregates(
        games
    )
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=tuple(games),
        seeds_used=tuple(seeds),
        kill_gifted_wins=kill_gifted_wins,
        instances_dropped_total=instances_dropped_total,
        mean_instances_complete_at_win=mean_complete,
    )


def _balance_report_from_tournament(report: TournamentReport) -> BalanceReport:
    """Count verified terminal outcomes without treating an interruption as a limit."""
    return BalanceReport(
        games=len(report.games),
        crew_wins=sum(
            game.outcome_verified and game.winner == "CREWMATES"
            for game in report.games
        ),
        impostor_wins=sum(
            game.outcome_verified and game.winner == "IMPOSTORS"
            for game in report.games
        ),
        tick_budget_reached=sum(
            game.completion_status == "tick_limited" for game in report.games
        ),
        aborted=sum(game.completion_status == "aborted" for game in report.games),
        unfinished=sum(game.completion_status == "unfinished" for game in report.games),
        unverified=sum(
            game.completion_status == "completed" and not game.outcome_verified
            for game in report.games
        ),
        seeds_used=tuple(game.seed for game in report.games),
    )


def _game_report_from_replay(
    *,
    seed: int,
    roles: Mapping[PlayerId, Role],
    fallback_reason: str,
    replay_path: Path,
    integrity_verified: bool = False,
    kill_gifted: bool = False,
    instances_dropped: int = 0,
    instances_complete_at_win: int = 0,
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

    ``kill_gifted`` / ``instances_dropped`` / ``instances_complete_at_win`` are
    the Task 8.17 kill-gift facts (DESIGN.md §3.5; audit gp-4). They are
    supplied by the caller -- which derives them from a deterministic engine
    walk via :func:`_kill_gift_accounting` (the walk needs the roster +
    ``game_map`` this fold does not carry) -- and default to the no-kill-gift
    values for raw-fold unit tests and historical analyses. Current public
    callers validate reconstruction before this fold; raw cost accounting
    remains independently available for records that cannot certify an outcome.
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

    trigger_index = _trigger_kind_index(entries)
    meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
    meetings = tuple(
        _meeting_report_from_entry(entry, trigger_index) for entry in meeting_entries
    )
    failed_calls = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
    end = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
    stop = next((e for e in entries if isinstance(e, GameStopReplayEntry)), None)
    status = recorded_completion_status(entries)
    if status == "unfinished":
        if fallback_reason == "TICK_BUDGET_REACHED":
            status = "tick_limited"
        elif fallback_reason.startswith("meeting aborted"):
            status = "aborted"

    # An aborted opening still used the run's prompt set. Preserve its version
    # stamp even when no meeting reached a resolution.
    prompt_versions: Mapping[str, str] = next(
        (
            dict(entry.prompt_versions)
            for entry in entries
            if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry))
        ),
        {},
    )
    game_id = entries[0].game_id if entries else f"headless-seed-{seed}"

    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=end.winner if end is not None else None,
        reason=end.reason
        if end is not None
        else stop.reason
        if stop is not None
        else fallback_reason,
        final_tick=end.tick if end is not None else None,
        completion_status=status,
        outcome_verified=integrity_verified
        and end is not None
        and end.winner is not None,
        roles=roles,
        replay_ref=replay_path.name,
        meetings=meetings,
        failed_calls=failed_calls,
        prompt_versions=prompt_versions,
        cost=_game_cost_summary(total_cost_usd=total_cost_usd, entries=entries),
        kill_gifted=kill_gifted,
        instances_dropped=instances_dropped,
        instances_complete_at_win=instances_complete_at_win,
    )


def _trigger_kind_index(
    entries: tuple[ReplayLogEntry, ...],
) -> dict[tuple[int, PlayerId], Literal["report", "emergency"]]:
    """Index the meeting-triggering action kind by ``(tick, actor)``.

    A meeting opens only when the engine applies a ``report`` or ``emergency``
    action, and :meth:`orchestrator.replay.ReplayLog.record_tick` persists that
    action in the trigger tick's per-tick row. This walks the ``kind="tick"``
    rows and maps ``(tick, actor) -> action_type`` for those two action kinds, so
    :func:`_meeting_report_from_entry` can recover the engine-recorded trigger
    (equivalent to :attr:`engine.events.MeetingTriggeredEvent.trigger`) without a
    replay-format change. ``(tick, actor)`` is unique — a tick is unique per game
    (``read_all_entries`` rejects duplicate ticks) and an actor submits one
    action per tick — so the map is unambiguous; a rejected ``report`` by a
    different actor at the same tick keys to that actor, never the one whose
    action actually opened the meeting (``MeetingReplayEntry.triggered_by``).
    """

    index: dict[tuple[int, PlayerId], Literal["report", "emergency"]] = {}
    for entry in entries:
        if not isinstance(entry, ReplayEntry):
            continue
        for action in entry.actions:
            kind = action.get("type")
            if kind in ("report", "emergency"):
                index[(entry.tick, action["actor"])] = kind
    return index


def _meeting_report_from_entry(
    entry: MeetingReplayEntry,
    trigger_index: Mapping[tuple[int, PlayerId], Literal["report", "emergency"]],
) -> MeetingReport:
    """Map a ``MeetingReplayEntry`` to a :class:`MeetingReport` (near 1:1).

    The replay entry's engine-determinism fields (``state_hash_before`` /
    ``state_hash_after``), its ``game_id``, and its per-meeting
    ``prompt_versions`` (collapsed to game level in
    :func:`_game_report_from_replay`) are intentionally dropped; everything a
    Phase 5 behavioral metric reads is carried over verbatim.

    ``trigger`` is the one field NOT on the replay row: it is recovered from
    ``trigger_index`` (:func:`_trigger_kind_index`) keyed by the meeting's
    ``(tick, triggered_by)``. The lookup is the engine-recorded trigger action,
    so the trigger breakdown is authoritative — never the agent's self-reported
    ``FoundBodyObservation``. A meeting whose trigger action is absent (a corrupt
    or truncated replay) is fail-loud: a meeting cannot open without one, so the
    kind is recovered, never defaulted (AGENTS.md "no silent fallbacks").
    """

    trigger = trigger_index.get((entry.tick, entry.triggered_by))
    if trigger is None:
        raise ValueError(
            f"meeting {entry.meeting_id!r} (game {entry.game_id!r}, tick "
            f"{entry.tick}) has no recorded report/emergency action by its "
            f"triggering player {entry.triggered_by!r} in that tick's replay "
            "row. A meeting cannot open without one, so the replay is corrupt or "
            "truncated; the trigger kind is recovered from the engine-recorded "
            "action, not defaulted."
        )

    return MeetingReport(
        meeting_id=entry.meeting_id,
        tick=entry.tick,
        triggered_by=entry.triggered_by,
        trigger=trigger,
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
    aborted-meeting calls and ``failed_calls`` — in one pass, so
    ``sum(by_model.values())`` reconciles to
    ``total_cost_usd``. Counting spend here once is the single place it is
    counted; the cost dashboard (Task 5.5) must not re-add failed-call cost.
    """

    total_input_tokens = 0
    total_output_tokens = 0
    by_model: dict[str, float] = {}
    for entry in entries:
        if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry)):
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
    "build_tournament_report",
    "load_tournament_report",
    "load_historical_tournament_report",
    "run_balance_eval",
    "run_tournament_eval",
]
