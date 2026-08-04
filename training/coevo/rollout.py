"""FROZEN (Phase 19 tier map, training/README.md): concluded campaign machinery.
Bug fixes and evidence readers only; no new search.

The dual-role co-evolution rollout (Task 18.19).

The co-evo twin of ``training.bakeoff.harness.rollout_candidate``
(harness.py:665-723, interposes impostor decisions only) and
``training.crew.scorer.rollout_crew_candidate`` (scorer.py:891-950, interposes
crew decisions only): ONE full production game in which BOTH sides are
independently the scripted FSM (``None``), a live candidate, or a frozen learned
artifact, driven through :func:`~training.coevo.factory.build_coevo_factory`,
and scored for BOTH sides' inner fitness off the SAME reconstructed episode.

Structurally identical to the two single-side rollouts: resolve the canonical
map when ``None``, ``mkdir`` the output dir, write
``replay-seed-{seed}.jsonl``, drive :class:`orchestrator.game.HeadlessGame`
through the co-evo factory with ``force=True``, ``game.run()``, then
:func:`training.rollout.reconstruct_episode` with ``episode_boundary="full_game"``
(the state-hash-verified typed episode). ``meeting_runner_factory=None`` is the
real (deterministic fake-provider) meeting path both twins hard-wire.

Both sides' fitness come from the ONE rollout: the impostor side through
``inner_episode_fitness`` over the impostor trace, the crew side through
``crew_inner_episode_fitness`` over the crew trace — the same pure
``(rollout, trace)`` fitness functions the single-side paths use, so a
single-side co-evo run scores byte-identically to its single-side twin. Per the
18.16 conviction doctrine the SAME :class:`ConvictionFitnessTerm` object serves
BOTH sides (one frozen artifact, one shared counter); ``conviction=None`` means
the term is STRUCTURALLY ABSENT on both, never a zero-weighted ghost.

This is a TRAINING rollout: it does NOT stamp the replay. The two-identity
provenance recording (an impostor ``TacticalPolicyStamp`` beside a crew
``CrewTacticalPolicyStamp`` on one ``game_over`` row) is
``scripts/run_tournament.py``'s ``--crew-artifact`` arm — training rollouts
never stamp (the ``rollout_candidate`` / ``rollout_crew_candidate`` precedent).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from engine.world import Map, load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    HeadlessGame,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from training.bakeoff.goodhart import MeetingRunnerFactory
from training.bakeoff.harness import (
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    BakeoffPolicy,
    ConvictionFitnessTerm,
    DecisionTrace,
    inner_episode_fitness,
)
from training.coevo.factory import build_coevo_factory
from training.crew.scorer import (
    CrewDecisionTrace,
    CrewTrackPolicy,
    crew_inner_episode_fitness,
)
from training.rollout import EpisodeRollout, reconstruct_episode


@dataclass(frozen=True)
class CoevoRolloutResult:
    """The scored artifacts of one dual-role co-evo game (Task 18.19).

    Rides the ONE reconstructed episode alongside BOTH sides' inner fitness and
    BOTH EPISODE-LOCAL traces (this game's decisions only — never a caller's
    cross-seed accumulator), so a caller (18.20's hall of fame, 18.21's
    alternating-freeze driver) reads impostor and crew fitness from a single
    rollout without re-running the game. The two identities stay in DISTINCT
    fields/types — an impostor ``DecisionTrace`` and a crew
    ``CrewDecisionTrace`` — so they can never be positionally conflated. A
    truncated (tick-budget-capped) episode scores both fitnesses at the
    documented :data:`~training.bakeoff.harness.TRUNCATED_EPISODE_FITNESS` via
    the pure fitness functions, never a silent skip.
    """

    rollout: EpisodeRollout
    impostor_fitness: float
    crew_fitness: float
    impostor_trace: DecisionTrace
    crew_trace: CrewDecisionTrace


def _fold_impostor_trace(into: DecisionTrace, episode: DecisionTrace) -> None:
    """Fold one episode's impostor trace into a set-level accumulator.

    The nine numeric accumulator fields, byte-for-byte the fold
    ``training.bakeoff.harness._score_eval_pass`` performs on the impostor side
    (harness.py:1501-1510 — the impostor ``DecisionTrace`` has no ``fold``
    method, unlike :meth:`~training.crew.scorer.CrewDecisionTrace.fold`).
    ``anchor_policy`` is CONFIG, not an accumulator, and never folds.
    """

    into.impostor_decisions += episode.impostor_decisions
    into.scored_decisions += episode.scored_decisions
    into.anchor_ce_sum += episode.anchor_ce_sum
    into.offmenu_decisions += episode.offmenu_decisions
    into.agreement_hits += episode.agreement_hits
    into.opportunities += episode.opportunities
    into.kills_taken += episode.kills_taken
    into.conviction_supply_sum += episode.conviction_supply_sum
    into.conviction_meetings += episode.conviction_meetings


def rollout_coevo(
    impostor_policy: BakeoffPolicy | None,
    crew_policy: CrewTrackPolicy | None,
    seed: int,
    *,
    output_dir: Path,
    game_map: Map | None = None,
    num_players: int = BAKEOFF_NUM_PLAYERS,
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS,
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE,
    meeting_runner_factory: MeetingRunnerFactory | None = None,
    max_ticks: int = DEFAULT_MAX_TICKS,
    impostor_anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT,
    crew_anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT,
    conviction: ConvictionFitnessTerm | None = None,
    impostor_trace: DecisionTrace | None = None,
    crew_trace: CrewDecisionTrace | None = None,
) -> CoevoRolloutResult:
    """Run ONE full production game with both sides and score both (Task 18.19).

    Mirrors ``rollout_candidate`` (harness.py:665-723) / ``rollout_crew_candidate``
    (scorer.py:891-950) structurally, wiring BOTH override paths through
    :func:`~training.coevo.factory.build_coevo_factory`. Resolves the canonical
    map when ``game_map`` is ``None``, writes ``replay-seed-{seed}.jsonl`` under
    ``output_dir``, drives :class:`orchestrator.game.HeadlessGame` with
    ``force=True``, and returns the state-hash-verified typed episode alongside
    both fitnesses and both traces.

    Traces: scoring is ALWAYS per-episode — fresh EPISODE-LOCAL trace objects
    thread into the factory (where the wrappers write per-decision) AND into the
    fitness calls AND ride the result. A caller-supplied ``impostor_trace`` /
    ``crew_trace`` is a SET-LEVEL accumulator, never the scoring input: the
    episode's numbers FOLD INTO it after scoring (the
    ``training.bakeoff.harness._score_eval_pass`` idiom, harness.py:1469-1510 —
    :func:`_fold_impostor_trace` on the impostor side,
    :meth:`~training.crew.scorer.CrewDecisionTrace.fold` on the crew side), so a
    driver can accumulate across seeds while each seed's fitness stays
    uncontaminated by earlier games' anchor-CE/conviction means. The impostor
    episode trace INHERITS the accumulator's configured ``anchor_policy`` (the
    18.16 anchor seam is CONFIG, not an accumulator — dropping it would silently
    re-anchor the CE back onto the scripted FSM).

    Both sides' fitness come from the ONE rollout:
    ``inner_episode_fitness(rollout, impostor_trace, anchor_weight=impostor_anchor_weight,
    conviction=conviction)`` for the impostor side, and the ``"CREWMATE"``-side
    ``crew_inner_episode_fitness(rollout, crew_trace, anchor_weight=crew_anchor_weight,
    conviction=conviction)`` for the crew side. Per the 18.16 doctrine the SAME
    ``ConvictionFitnessTerm`` object serves both sides (``None`` = structurally
    absent). A truncated episode scores both at ``TRUNCATED_EPISODE_FITNESS``.

    ``meeting_runner_factory=None`` is the real (deterministic fake-provider)
    meeting path. This is a TRAINING rollout — it does NOT stamp the replay; the
    dual-stamp recording path is ``scripts/run_tournament.py``'s ``--crew-artifact``
    arm.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    # Episode-LOCAL traces score this rollout; a caller-supplied trace is a
    # set-level accumulator folded into AFTER scoring (see the docstring). The
    # impostor episode trace inherits the accumulator's configured anchor_policy
    # so an alternative-anchor driver keys this episode's CE on its own anchor.
    episode_impostor_trace = DecisionTrace(
        anchor_policy=(
            impostor_trace.anchor_policy if impostor_trace is not None else None
        )
    )
    episode_crew_trace = CrewDecisionTrace()
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_path = output_dir / f"replay-seed-{seed}.jsonl"
    factory = build_coevo_factory(
        impostor_policy,
        crew_policy,
        game_map=resolved_map,
        impostor_trace=episode_impostor_trace,
        crew_trace=episode_crew_trace,
    )
    if meeting_runner_factory is not None:
        meeting_runner = meeting_runner_factory()
    else:
        meeting_runner = build_default_meeting_runner(
            llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
        )
    game = HeadlessGame(
        seed=seed,
        game_map=resolved_map,
        agent_factory=factory,
        replay_path=replay_path,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=meeting_runner,
        force=True,
    )
    game.run()
    rollout = reconstruct_episode(
        replay_path,
        game_map=resolved_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        episode_boundary="full_game",
    )
    impostor_fitness = inner_episode_fitness(
        rollout,
        episode_impostor_trace,
        anchor_weight=impostor_anchor_weight,
        conviction=conviction,
    )
    crew_fitness = crew_inner_episode_fitness(
        rollout,
        episode_crew_trace,
        anchor_weight=crew_anchor_weight,
        conviction=conviction,
    )
    # Fold this episode into the caller's set-level accumulators AFTER scoring
    # (the _score_eval_pass discipline), so per-seed fitness never reads earlier
    # games' means while a driver still accumulates across seeds.
    if impostor_trace is not None:
        _fold_impostor_trace(impostor_trace, episode_impostor_trace)
    if crew_trace is not None:
        crew_trace.fold(episode_crew_trace)
    return CoevoRolloutResult(
        rollout=rollout,
        impostor_fitness=impostor_fitness,
        crew_fitness=crew_fitness,
        impostor_trace=episode_impostor_trace,
        crew_trace=episode_crew_trace,
    )
