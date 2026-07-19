"""Task 18.5 — the anchor study: λ sweep + filtered-BC anchor refinement.

The two cheap training-side levers on the exact gauges the committed champion
failed (audits/audit-phase-18-planning.md §2.4, adopted without an owner slot;
§6 carries the piKL reading — the anchor-KL weight is the legibility dial, so
the honest move is to sweep it and read the Pareto rather than fold
watchability into fitness, which stays forbidden):

1. **The λ sweep.** Re-run the utility-es training
   (:class:`training.bakeoff.utility_es.UtilityEsEntrant`, consumed through its
   public seam — 285 s/run at the full budget on the fake path,
   ``training/bakeoff/utility_es.py:708-718``) at a grid of anchor weights and
   score every champion through the standing fake-path protocol
   (:func:`training.bakeoff.harness.evaluate_candidate` on the frozen 30-seed
   corpus test split). The λ=1.0 cell doubles as the determinism cross-check:
   it must reproduce the committed champion byte-identically
   (``training/artifacts/impostor/utility-es/weights.json``), or the sweep
   fails loud — a drifted training loop would silently invalidate every row.

2. **The filtered-BC anchor refinement.** Fit an ALTERNATIVE anchor policy in
   the utility-scorer family (a conditional logit over the FSM option-feature
   menu, :data:`training.bakeoff.utility_es.OPTION_FEATURE_NAMES`) over the
   corpus's crew-winning/high-flag games — the corpus as a PRIOR SOURCE, never
   a training environment: the decision stream is re-derived from the recorded
   bytes by walking the recorded actions through the pure engine (the
   ``training.rollout.reconstruct_episode`` recipe) while rebuilding each
   impostor's observation packets and episodic memory through the production
   perception path, with every re-derived FSM decision VERIFIED against the
   recorded action (fail loud on any divergence). The fit mirrors the
   ``Fo6Logistic`` / ``BallotPredictor`` deterministic recipe
   (``training/surrogate/fidelity.py:302-419``, ``ballots.py``): zeros init,
   fixed epochs/learning-rate, full-batch gradient descent, no RNG. Evaluation
   is OFFLINE only — per-decision agreement with the FSM over the corpus
   decision stream, where it diverges and toward what. The
   ES-leg-under-the-refined-anchor is deliberately NOT run here: the harness's
   anchor-CE is computed against the FSM's own choice
   (``training/bakeoff/harness.py:569-590``), and swapping the anchor needs the
   additive anchor-policy seam Task 18.16 adds — the refined-anchor ES leg is a
   named campaign entrant configuration at Task 18.24, which holds both the
   artifact (this task) and the seam (18.16).

Report-only: no champion ships from this study. Deterministic, $0, CPU. Every
frozen artifact under ``training/artifacts/anchor_study/`` carries the
corpus/floor substrate sha it was fitted/selected against
(:func:`compute_substrate_sha`) — the 18.24 campaign refuses stale-substrate
seeds without the cheap deterministic re-fit/re-run at the adopted substrate.

Determinism caveat (the surrogate precedent, ``BallotPredictor.fit``): the λ
sweep and the corpus walk are bit-deterministic across platforms (pure-Python
ES mutation RNG + the deterministic engine), but the filtered-BC fit is numpy
full-batch gradient descent — deterministic for a given decision order ON A
GIVEN PLATFORM, byte-identical on the recording platform and ULP-equivalent
elsewhere (numpy's SIMD summation grouping varies by CPU). The COMMITTED
artifact bytes — not a refit — are the frozen ground truth the sha256 sidecars
pin.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final

import numpy as np
from pydantic import BaseModel, ConfigDict, TypeAdapter

from agents.tactical.features import weights_to_hex_json
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.actions import Action
from engine.entities import PlayerId
from engine.events import EngineEvent, GameOverEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, load_canonical_map
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map, translate_action_intent
from orchestrator.game import TacticalAgent, apply_meeting_result
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    WinnerSide,
    # The reconstruction-walk hash primitive, imported exactly like
    # training/rollout.py does (the 15.8 precedent for this private seam).
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state
from training.bakeoff.harness import (
    ANCHOR_CE_EPSILON,
    BAKEOFF_BASELINE_ID,
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    CORPUS_SPLITS_PATH,
    BakeoffProtocolConfig,
    BakeoffResult,
    TrainedCandidate,
    default_protocol_config,
    evaluate_candidate,
    intent_key,
    load_candidate_weights,
    write_candidate_artifact,
)
from training.bakeoff.utility_es import (
    OPTION_FEATURE_NAMES,
    UtilityEsEntrant,
    build_utility_scorer_policy,
    enumerate_options,
    utility_es_budget,
    utility_genome_length,
)

# The reconstruction meeting-result rebuild, shared with the 15.8 walk (the
# same private-seam import posture as ``orchestrator.replay._state_hash``
# above: one canonical rebuild, never a drifting re-derivation).
from training.rollout import _meeting_result_from_entry

# The engine action adapter for the recorded rows (the 15.8 walk's idiom).
_ACTION_ADAPTER: Final[TypeAdapter[Action]] = TypeAdapter(Action)

# --------------------------------------------------------------------------- #
# Study constants (stated BEFORE any run, per the standing pre-registration    #
# discipline).                                                                 #
# --------------------------------------------------------------------------- #

# The anchor-weight grid the contract names. λ=1.0 is the committed champion's
# weight (DEFAULT_ANCHOR_PENALTY_WEIGHT) and doubles as the determinism
# cross-check cell.
LAMBDA_GRID: Final[tuple[float, ...]] = (0.25, 0.5, 1.0, 2.0, 4.0)

# The filtered-BC source (the task contract's section ref): the frozen
# baseline-5 ML corpus.
CORPUS_DIR: Final[Path] = Path("replays/ml_corpus/9p2i")

# Where this study freezes its byte-addressable artifacts (the seeds Task
# 18.24 reloads): one ``<entrant>/`` dir per candidate with float-hex
# ``weights.json`` + sha256 sidecar + a ``config.json`` carrying the substrate
# sha, plus the deterministic ``study.json`` index.
ANCHOR_STUDY_ARTIFACT_ROOT: Final[Path] = Path("training/artifacts/anchor_study")
STUDY_INDEX_FILENAME: Final[str] = "study.json"

REPORT_PATH: Final[Path] = Path("training/reports/report-anchor-study.md")

# The committed λ=1.0 champion the determinism cross-check reproduces.
COMMITTED_CHAMPION_DIR: Final[Path] = Path("training/artifacts/impostor/utility-es")

# The high-flag game filter threshold: the baseline-5 9p2i ``flags_per_meeting``
# supply floor, 90/179 (eval/watchability.py, the Task-16.17 close record; the
# §1.3 flip bar's supply gauge — the exact gauge the champion failed at
# 0.4255). Pinned as the committed ratio per the standing test idiom
# (tests/training/test_bakeoff_harness.py::_FLAGS_PER_MEETING_FLOOR) rather
# than importing ``eval.watchability`` into a training module: the bake-off
# entrant firewall keeps training-side modules eval-free, and this study
# consumes the floor as a NUMBER, not the gauge.
HIGH_FLAG_FLOOR: Final[float] = 90 / 179

# The filtered-BC fit hyperparameters — the Fo6Logistic / BallotPredictor
# deterministic recipe verbatim (training/surrogate/fidelity.py:316,
# ballots.py DEFAULT_EPOCHS / DEFAULT_LEARNING_RATE): zeros init, fixed
# epochs/lr, full-batch, no RNG.
FILTERED_BC_EPOCHS: Final[int] = 300
FILTERED_BC_LEARNING_RATE: Final[float] = 0.3

# The per-decision sample weight for games that satisfy BOTH filter criteria
# (crew-winning AND high-flag): the purest "watchable winning play" exemplars
# count double; a single-criterion game counts once. This is the "weighted" in
# the §2.4 weighted logistic, stated before the fit.
BOTH_CRITERIA_WEIGHT: Final[float] = 2.0

# The filtered-BC artifact's entrant/dir name under the study artifact root.
FILTERED_BC_ENTRANT: Final[str] = "filtered-bc-anchor"

_WEIGHTS_FILENAME: Final[str] = "weights.json"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _corpus_replays_sha256(corpus_dir: Path) -> str:
    """One digest over the corpus's recorded game bytes (sorted filenames).

    Per-file sha256 digests folded in sorted-filename order, so the substrate
    sha moves when ANY replay byte moves — even a refresh that (wrongly)
    leaves ``MANIFEST.md``/``splits.json`` untouched (Codex review on
    PR #292): the filtered-BC anchor is fitted FROM these bytes, so their
    identity is part of the substrate, not a workflow assumption.
    """

    digest = hashlib.sha256()
    for path in sorted(corpus_dir.glob("replay-seed-*.jsonl")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(_sha256_hex(path.read_bytes()).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def compute_substrate_sha(
    corpus_dir: Path = CORPUS_DIR,
    *,
    baseline_id: str = BAKEOFF_BASELINE_ID,
    high_flag_floor: float = HIGH_FLAG_FLOOR,
) -> str:
    """The corpus/floor substrate identity this study's artifacts bind to.

    No such digest existed before this task (Task 18.5 invents it; 18.6 stamps
    the same obligation on the MAP-Elites cells, and 18.20/18.24 read it at
    seed ingest). Following the repo's hashing idiom (sha256 over a canonical
    ``sort_keys`` JSON payload — ``training/surrogate/ballots.py`` /
    ``training/bakeoff/harness.py``), the payload pins:

    * the baseline id the selection floors are keyed by,
    * content digests of the corpus ``MANIFEST.md`` + ``splits.json`` (the
      recorded substrate's provenance: model, prompt versions, lever slate,
      git shas, and the by-game split rule) AND of the recorded game bytes
      themselves (:func:`_corpus_replays_sha256` — the fit source; any
      re-record or byte drift moves the sha even if the metadata files were
      wrongly left untouched), and
    * the ``flags_per_meeting`` floor value this study filters against — the
      floor ACTUALLY USED (``high_flag_floor``, defaulting to the committed
      baseline-5 pin): a re-fit at an adopted baseline passes the re-pinned
      floor alongside its ``baseline_id`` and the sha moves with both (Codex
      review on PR #292).

    A Wave-1 substrate adoption (the 18.13 corpus re-record) changes this sha,
    which is exactly the 18.24 stale-seed refusal firing: every artifact under
    ``training/artifacts/anchor_study/`` is then re-fit/re-run (cheap,
    deterministic) at the adopted substrate before it may seed the campaign.
    """

    payload = {
        "baseline_id": baseline_id,
        "corpus_manifest_sha256": _sha256_hex(
            (corpus_dir / "MANIFEST.md").read_bytes()
        ),
        "corpus_replays_sha256": _corpus_replays_sha256(corpus_dir),
        "corpus_set": corpus_dir.name,
        "corpus_splits_sha256": _sha256_hex((corpus_dir / "splits.json").read_bytes()),
        "flags_per_meeting_floor": high_flag_floor,
    }
    return _sha256_hex(json.dumps(payload, sort_keys=True).encode("utf-8"))


def corpus_seeds(corpus_dir: Path = CORPUS_DIR) -> tuple[int, ...]:
    """Every corpus game seed, from the committed ``splits.json`` (sorted).

    Validated as a UNIQUE partition that exactly matches the corpus's
    ``replay-seed-*.jsonl`` files (Codex review on PR #292): a seed
    duplicated across buckets would silently double-weight its game in the
    filtered-BC fit, and a listed-but-missing (or present-but-unlisted)
    replay would silently drop (or shadow) a game while the substrate sha
    still hashes the on-disk bytes — both fail loud instead.
    """

    splits_path = corpus_dir / "splits.json"
    raw = json.loads(splits_path.read_text())
    listed = [int(seed) for bucket in ("train", "val", "test") for seed in raw[bucket]]
    if not listed:
        raise ValueError(f"{splits_path} lists no game seeds")
    duplicates = sorted({seed for seed in listed if listed.count(seed) > 1})
    if duplicates:
        raise ValueError(
            f"{splits_path} lists seeds in more than one bucket (or twice in "
            f"one): {duplicates!r}"
        )
    on_disk = {
        _seed_from_replay_path(path) for path in corpus_dir.glob("replay-seed-*.jsonl")
    }
    missing = sorted(set(listed) - on_disk)
    unlisted = sorted(on_disk - set(listed))
    if missing or unlisted:
        raise ValueError(
            f"{splits_path} does not match the corpus replay files: "
            f"listed-but-missing {missing!r}, present-but-unlisted {unlisted!r}"
        )
    return tuple(sorted(listed))


# --------------------------------------------------------------------------- #
# The corpus decision-stream walk.                                             #
# --------------------------------------------------------------------------- #


class CorpusWalkError(RuntimeError):
    """Raised when the recorded corpus bytes fail to reconstruct exactly.

    Either an engine ``state_hash`` disagreed (the ``reconstruct_episode``
    failure class: corrupted / drifted / wrong-roster bytes) or a re-derived
    FSM decision disagreed with the recorded action — the proof obligation
    that the rebuilt packets + episodic memory are byte-faithful to what the
    recorded impostors actually saw. Either way a dataset harvested from the
    stream would be silently wrong, so the walk fails loud (AGENTS.md "no
    silent fallbacks").
    """


@dataclass(frozen=True)
class CorpusDecision:
    """One recorded impostor decision, re-derived from the corpus bytes.

    ``features`` is the per-option :data:`OPTION_FEATURE_NAMES` matrix (one row
    per menu option, in menu order), ``option_intent_keys`` /
    ``option_kinds`` the parallel intent-key / menu-kind labels, and
    ``fsm_intent_key`` the canonical key of the choice the recorded FSM
    actually made (verified against the recorded action). ``fsm_option_index``
    is the first menu index realizing that key, or ``None`` when the FSM's
    choice is off its own menu (possible: the decide() ladder holds a few
    fall-throughs the menu does not mirror — tallied, never silently dropped).
    """

    seed: int
    tick: int
    actor: PlayerId
    option_kinds: tuple[str, ...]
    option_intent_keys: tuple[str, ...]
    features: tuple[tuple[float, ...], ...]
    fsm_intent_key: str
    fsm_option_index: int | None


@dataclass(frozen=True)
class CorpusGameFacts:
    """Per-game filter facts read off the recorded bytes during the walk.

    ``flags_per_meeting`` counts the PERSISTED contradiction rows on the
    game's meeting entries (the byte-committed evidence record; the referee's
    set-level gauge additionally re-derives transcript flags, so this count is
    conservative — stated in the report). This is the production gauge's own
    trust posture (``eval/watchability`` reads persisted vent flags because
    the transcript re-derivation structurally cannot reproduce them);
    contradiction rows are not part of the engine hash chain, and their byte
    identity is pinned instead by the substrate sha's replay-bytes digest —
    a drifted/forged row moves :func:`compute_substrate_sha` and the 18.24
    stale-seed refusal fires. ``high_flag`` compares against the
    ``high_flag_floor`` the walk was given (default: the committed baseline-5
    pin :data:`HIGH_FLAG_FLOOR`); ``crew_winning`` reads the recorded winner.
    """

    seed: int
    winner: WinnerSide | None
    meetings: int
    persisted_flags: int
    flags_per_meeting: float
    crew_winning: bool
    high_flag: bool
    decisions: int
    fsm_offmenu_decisions: int

    @property
    def qualifies(self) -> bool:
        return self.crew_winning or self.high_flag

    @property
    def sample_weight(self) -> float:
        """The stated per-decision fit weight (0.0 when the game is filtered out)."""

        if not self.qualifies:
            return 0.0
        if self.crew_winning and self.high_flag:
            return BOTH_CRITERIA_WEIGHT
        return 1.0


def _seed_from_replay_path(replay_path: Path) -> int:
    stem = replay_path.stem
    prefix = "replay-seed-"
    if not stem.startswith(prefix):
        raise ValueError(
            f"corpus replay filename {replay_path.name!r} does not follow the "
            f"'replay-seed-<seed>.jsonl' convention"
        )
    return int(stem[len(prefix) :])


def walk_corpus_game(
    replay_path: Path,
    *,
    game_map: Map | None = None,
    num_players: int = BAKEOFF_NUM_PLAYERS,
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS,
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE,
    high_flag_floor: float = HIGH_FLAG_FLOOR,
) -> tuple[CorpusGameFacts, tuple[CorpusDecision, ...]]:
    """Re-derive one recorded game's impostor decision stream from its bytes.

    The :func:`training.rollout.reconstruct_episode` recipe (re-seed, feed the
    recorded actions through :func:`engine.tick.advance_tick`, verify every
    ``state_hash``, apply recorded meeting rows via
    :func:`orchestrator.game.apply_meeting_result`) interleaved with the
    production observation/perception path: before each recorded tick's
    actions are applied, every recorded impostor's
    :class:`~observation.service.ObservationService` packet is rebuilt from
    the pre-action state + the previous step's engine events (exactly
    ``HeadlessGame._run_loop``'s ``_build_packets`` inputs, including the
    post-meeting event splice), fed through a live
    :class:`~orchestrator.game.TacticalAgent` (perception → episodic memory →
    the scripted FSM), and the re-derived intent is VERIFIED against the
    recorded action through the production
    :func:`~orchestrator.boundary.translate_action_intent`. The option menu
    (:func:`~training.bakeoff.utility_es.enumerate_options`) is then harvested
    off the same live packet/memory.

    Meeting-time memory folds (the belief absorb + the ``reported`` testimony
    rows) are deliberately NOT replayed: the impostor FSM and the option menu
    read only packet fields and perception-written episodic rows
    (``saw_player`` / body / sabotage / self-state types —
    ``ImpostorPolicy._scored_targets`` filters on ``EVENT_SAW_PLAYER``, which
    testimony rows are structurally not), so the folds cannot move a tactical
    decision — and the per-decision recorded-action verification PROVES it on
    every walked game rather than assuming it.
    """

    seed = _seed_from_replay_path(replay_path)
    resolved_map = game_map if game_map is not None else load_canonical_map()
    public_map = public_map_from_engine_map(resolved_map)

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {}
    for meeting_row in entries:
        if not isinstance(meeting_row, MeetingReplayEntry):
            continue
        if meeting_row.tick in meeting_by_tick:
            # Collapsing duplicates would let the LAST row (with, e.g., forged
            # contradictions but honest state hashes) both pass the visited
            # check and move the flags census (Codex review on PR #292).
            raise CorpusWalkError(
                f"seed {seed}: replay carries duplicate meeting rows for tick "
                f"{meeting_row.tick}"
            )
        meeting_by_tick[meeting_row.tick] = meeting_row
    game_end = next(
        (entry for entry in entries if isinstance(entry, GameEndReplayEntry)), None
    )

    state = seed_initial_state(
        seed=seed,
        game_map=resolved_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    impostor_ids = tuple(
        sorted(
            pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
        )
    )
    agents = {
        pid: TacticalAgent(
            agent_id=pid, policy=ImpostorPolicy(agent_id=pid), role="IMPOSTOR"
        )
        for pid in impostor_ids
    }

    decisions: list[CorpusDecision] = []
    offmenu = 0
    winner: WinnerSide | None = None
    visited_meeting_ticks: set[int] = set()
    last_events: tuple[EngineEvent, ...] = ()

    # The observation audit is routed to the null device exactly like the
    # no-replay training path (orchestrator/game.py): the walk writes NOTHING.
    observation_service = ObservationService(
        game_map=resolved_map, audit_log_path=Path(os.devnull)
    )
    processed_rows = 0
    try:
        for entry in tick_entries:
            processed_rows += 1
            recorded_by_actor: dict[str, Mapping[str, object]] = {}
            for raw in entry.actions:
                actor = raw.get("actor")
                if not isinstance(actor, str):
                    raise CorpusWalkError(
                        f"seed {seed}: tick {entry.tick} carries an action row "
                        f"without a string actor: {dict(raw)!r}"
                    )
                if actor in recorded_by_actor:
                    # The orchestrator submits exactly one action per living
                    # actor; a duplicate row is corruption, and duplicate
                    # ``wait`` rows may not trip the state-hash check — never
                    # collapse them silently (Codex review on PR #292).
                    raise CorpusWalkError(
                        f"seed {seed}: tick {entry.tick} carries duplicate "
                        f"action rows for actor {actor!r}"
                    )
                recorded_by_actor[actor] = raw
            # The production invariant, enforced exactly: one action per
            # LIVING actor at the pre-action state — an extra row (a ghost or
            # dead actor, engine-rejected without moving the hash) or a
            # missing row (a dropped ``wait`` the hash may not catch) is
            # corruption, never a silent no-op (Codex review on PR #292).
            living = {
                player_id for player_id, player in state.players.items() if player.alive
            }
            ghost_actors = sorted(set(recorded_by_actor) - living)
            if ghost_actors:
                raise CorpusWalkError(
                    f"seed {seed}: tick {entry.tick} carries action rows from "
                    f"actors outside the living roster: {ghost_actors!r}"
                )
            unaccounted = sorted(living - set(recorded_by_actor))
            if unaccounted:
                raise CorpusWalkError(
                    f"seed {seed}: tick {entry.tick} has no recorded action "
                    f"rows for the living players {unaccounted!r} (partial or "
                    "corrupted replay row)"
                )
            for pid in impostor_ids:
                raw_action = recorded_by_actor.get(pid)
                if raw_action is None:
                    continue  # dead/ejected (the living-set check ran above)
                packet = observation_service.build_packet(
                    world_state=state, agent_id=pid, engine_events=last_events
                )
                fsm_intent = agents[pid].decide(packet, public_map)
                derived = translate_action_intent(fsm_intent)
                recorded = _ACTION_ADAPTER.validate_python(dict(raw_action))
                if derived != recorded:
                    raise CorpusWalkError(
                        f"seed {seed}: tick {entry.tick} impostor {pid!r} "
                        f"re-derived {derived!r} != recorded {recorded!r} "
                        "(the rebuilt perception stream has drifted from the "
                        "recording)"
                    )
                options = enumerate_options(packet, public_map, agents[pid].memory)
                fsm_key = intent_key(fsm_intent)
                option_keys = tuple(intent_key(option.intent) for option in options)
                fsm_index = next(
                    (index for index, key in enumerate(option_keys) if key == fsm_key),
                    None,
                )
                if fsm_index is None:
                    offmenu += 1
                decisions.append(
                    CorpusDecision(
                        seed=seed,
                        tick=entry.tick,
                        actor=pid,
                        option_kinds=tuple(option.kind for option in options),
                        option_intent_keys=option_keys,
                        features=tuple(option.features for option in options),
                        fsm_intent_key=fsm_key,
                        fsm_option_index=fsm_index,
                    )
                )

            state, tick_events = advance_tick(
                state,
                [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions],
                game_map=resolved_map,
            )
            actual = _state_hash(state)
            if actual != entry.state_hash:
                raise CorpusWalkError(
                    f"seed {seed}: tick {entry.tick} reconstructed {actual!r} != "
                    f"recorded {entry.state_hash!r} (roster mismatch or drift)"
                )
            last_events = tuple(tick_events)
            for event in tick_events:
                if isinstance(event, GameOverEvent):
                    winner = event.winner
            if state.phase == "GAME_OVER":
                break
            if state.phase != "MEETING":
                continue

            trigger_event = next(
                (e for e in tick_events if isinstance(e, MeetingTriggeredEvent)), None
            )
            if trigger_event is None:
                raise CorpusWalkError(
                    f"seed {seed}: tick {entry.tick} entered MEETING with no "
                    "MeetingTriggeredEvent in the reconstructed events"
                )
            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                raise CorpusWalkError(
                    f"seed {seed}: tick {entry.tick} entered MEETING but the "
                    "replay carries no meeting row for that tick"
                )
            visited_meeting_ticks.add(entry.tick)
            if meeting_entry.state_hash_before != actual:
                raise CorpusWalkError(
                    f"seed {seed}: meeting at tick {entry.tick} recorded "
                    f"state_hash_before {meeting_entry.state_hash_before!r} != "
                    f"reconstructed {actual!r}"
                )
            result = _meeting_result_from_entry(meeting_entry)
            state, post_events = apply_meeting_result(
                state,
                result,
                game_map=resolved_map,
                triggering_body_id=trigger_event.body_id,
            )
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                raise CorpusWalkError(
                    f"seed {seed}: meeting at tick {entry.tick} reconstructed "
                    f"{after!r} != recorded {meeting_entry.state_hash_after!r}"
                )
            # Preserve the trigger tick's events beside the meeting's own (the
            # production loop's post-meeting perception splice).
            last_events = last_events + tuple(post_events)
            for event in post_events:
                if isinstance(event, GameOverEvent):
                    winner = event.winner
            if state.phase == "GAME_OVER":
                break
    finally:
        observation_service.close()

    # The walk's charter is VERIFIED committed bytes: a corpus game is always
    # terminal, so a missing/void ``game_over`` row or a tick stream that never
    # reached GAME_OVER is a truncated or partial replay — fail loud instead of
    # silently entering a ``winner=None`` game into the filter and the fit
    # (Codex review on PR #292).
    if game_end is None or game_end.winner is None:
        raise CorpusWalkError(
            f"seed {seed}: replay carries no terminal game_over winner "
            "(truncated or partial recording)"
        )
    if winner is None:
        raise CorpusWalkError(
            f"seed {seed}: the reconstructed walk never reached GAME_OVER "
            "(truncated tick stream)"
        )
    if winner != game_end.winner:
        raise CorpusWalkError(
            f"seed {seed}: reconstructed winner {winner!r} != recorded "
            f"game_over winner {game_end.winner!r}"
        )

    # No tick rows may trail the terminal state: the GAME_OVER break stops
    # validating, so an appended forged row would otherwise ride along inside
    # "verified" bytes without ever being checked (Codex review on PR #292).
    if processed_rows != len(tick_entries):
        raise CorpusWalkError(
            f"seed {seed}: replay carries {len(tick_entries) - processed_rows} "
            "tick rows after the terminal GAME_OVER state (never validated)"
        )

    # Every meeting row must have been visited (state-hash-verified) by the
    # walk: a stale extra row at a tick the engine never entered could move
    # the flags census — and therefore ``high_flag`` and the fit set — without
    # ever being verified (Codex review on PR #292).
    unvisited = sorted(set(meeting_by_tick) - visited_meeting_ticks)
    if unvisited:
        raise CorpusWalkError(
            f"seed {seed}: replay carries meeting rows at ticks {unvisited!r} "
            "the reconstructed walk never entered (stale or corrupted rows)"
        )

    meetings = len(meeting_by_tick)
    persisted_flags = sum(
        len(entry.contradictions) for entry in meeting_by_tick.values()
    )
    flags_per_meeting = persisted_flags / meetings if meetings else 0.0
    facts = CorpusGameFacts(
        seed=seed,
        winner=winner,
        meetings=meetings,
        persisted_flags=persisted_flags,
        flags_per_meeting=flags_per_meeting,
        crew_winning=winner == "CREWMATES",
        high_flag=meetings > 0 and flags_per_meeting >= high_flag_floor,
        decisions=len(decisions),
        fsm_offmenu_decisions=offmenu,
    )
    return facts, tuple(decisions)


def walk_corpus(
    seeds: Sequence[int],
    *,
    corpus_dir: Path = CORPUS_DIR,
    game_map: Map | None = None,
    high_flag_floor: float = HIGH_FLAG_FLOOR,
) -> tuple[tuple[CorpusGameFacts, ...], tuple[CorpusDecision, ...]]:
    """Walk the listed corpus games; return per-game facts + the pooled stream."""

    resolved_map = game_map if game_map is not None else load_canonical_map()
    facts: list[CorpusGameFacts] = []
    decisions: list[CorpusDecision] = []
    for seed in seeds:
        game_facts, game_decisions = walk_corpus_game(
            corpus_dir / f"replay-seed-{seed}.jsonl",
            game_map=resolved_map,
            high_flag_floor=high_flag_floor,
        )
        facts.append(game_facts)
        decisions.extend(game_decisions)
    return tuple(facts), tuple(decisions)


# --------------------------------------------------------------------------- #
# The filtered-BC fit (numpy weighted conditional logit over the option menu). #
# --------------------------------------------------------------------------- #


def fit_filtered_bc_anchor(
    decisions: Sequence[CorpusDecision],
    *,
    sample_weights: Sequence[float] | None = None,
    epochs: int = FILTERED_BC_EPOCHS,
    learning_rate: float = FILTERED_BC_LEARNING_RATE,
) -> tuple[float, ...]:
    """Fit the refined anchor over a decision stream (Task 18.5 public seam).

    A weighted conditional logit in the utility-scorer family: one shared
    weight vector over the per-option :data:`OPTION_FEATURE_NAMES` features,
    softmax over each decision's menu, maximizing the weighted log-likelihood
    of the FSM's recorded choice — with probability mass GROUPED by canonical
    intent key exactly as the harness's anchor-CE reads a choice distribution
    (two menu options realizing the same intent pool their mass). Decisions
    whose FSM choice is off the menu carry no likelihood and are excluded
    (the caller tallies them; never a silent drop of an on-menu decision).

    The recipe mirrors ``Fo6Logistic`` / ``BallotPredictor``
    (training/surrogate): per-feature standardization over the fit rows
    (zero-variance columns pass through), ZEROS init, ``epochs`` full-batch
    gradient steps at ``learning_rate`` with the gradient normalized by the
    total sample weight, and NO RNG anywhere. Deterministic for a given
    decision order on a given platform; byte-identical on the recording
    platform and ULP-equivalent across CPUs (the numpy SIMD caveat the module
    docstring states).

    Returns the RAW-FEATURE genome (length
    :func:`~training.bakeoff.utility_es.utility_genome_length`): the
    standardization is folded back into the weights (``w_raw = w_std / std``;
    the fold's per-option-constant offset cancels in the softmax, so the
    trailing bias slot is exactly ``0.0``) — byte-compatible with
    :func:`~training.bakeoff.utility_es.build_utility_scorer_policy` and the
    18.16 anchor-policy seam.

    ``sample_weights`` aligns with ``decisions`` (default: every decision
    weighs 1.0); non-positive weights are refused — a filtered-out decision is
    excluded by the caller, never smuggled in at weight zero.
    """

    if sample_weights is not None and len(sample_weights) != len(decisions):
        raise ValueError(
            f"sample_weights length {len(sample_weights)} != decisions "
            f"length {len(decisions)}"
        )
    fit_rows: list[tuple[CorpusDecision, float]] = []
    for index, decision in enumerate(decisions):
        weight = 1.0 if sample_weights is None else float(sample_weights[index])
        if weight <= 0.0:
            raise ValueError(
                f"sample weight {weight!r} at index {index} is not positive; "
                "exclude filtered-out decisions instead of zero-weighting them"
            )
        if decision.fsm_option_index is None:
            continue  # off-menu FSM choice: no likelihood to fit
        fit_rows.append((decision, weight))
    if not fit_rows:
        raise ValueError(
            "fit_filtered_bc_anchor received no on-menu decisions; the anchor "
            "cannot be fit on an empty stream"
        )

    feature_count = len(OPTION_FEATURE_NAMES)
    max_options = max(len(decision.features) for decision, _ in fit_rows)
    count = len(fit_rows)
    features = np.zeros((count, max_options, feature_count), dtype=np.float64)
    valid = np.zeros((count, max_options), dtype=bool)
    in_group = np.zeros((count, max_options), dtype=bool)
    weights_column = np.zeros(count, dtype=np.float64)
    for row, (decision, weight) in enumerate(fit_rows):
        menu = np.asarray(decision.features, dtype=np.float64)
        features[row, : menu.shape[0], :] = menu
        valid[row, : menu.shape[0]] = True
        for index, key in enumerate(decision.option_intent_keys):
            if key == decision.fsm_intent_key:
                in_group[row, index] = True
        weights_column[row] = weight

    # Standardize over the VALID option rows (the Fo6 recipe's conditioning
    # step); zero-variance columns pass through untouched.
    flat = features[valid]
    mean = flat.mean(axis=0)
    std = flat.std(axis=0)
    std[std == 0.0] = 1.0
    standardized = np.where(valid[:, :, None], (features - mean) / std, 0.0)

    head = np.zeros(feature_count, dtype=np.float64)
    total_weight = float(weights_column.sum())
    for _ in range(epochs):
        utilities = np.einsum("nkf,f->nk", standardized, head)
        utilities = np.where(valid, utilities, -np.inf)
        peak = utilities.max(axis=1, keepdims=True)
        exp = np.where(valid, np.exp(utilities - peak), 0.0)
        probs = exp / exp.sum(axis=1, keepdims=True)
        group_mass = np.where(in_group, probs, 0.0).sum(axis=1, keepdims=True)
        # d(-log P_group)/d(u_k) = p_k - p_k * 1[k in group] / P_group.
        grad_logits = probs - np.where(in_group, probs, 0.0) / group_mass
        grad_logits *= weights_column[:, None]
        gradient = np.einsum("nk,nkf->f", grad_logits, standardized) / total_weight
        head -= learning_rate * gradient

    raw_head = head / std
    genome = tuple(float(value) for value in raw_head) + (0.0,)
    if len(genome) != utility_genome_length():
        raise AssertionError(
            f"fit produced genome length {len(genome)} != {utility_genome_length()}"
        )
    return genome


# --------------------------------------------------------------------------- #
# Offline evaluation (per-decision FSM agreement / divergence / anchor-CE).    #
# --------------------------------------------------------------------------- #


class DivergenceCell(BaseModel):
    """One (FSM choice kind → anchor choice kind) disagreement bucket."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    fsm_intent_kind: str
    anchor_intent_kind: str
    count: int


class OfflineAgreement(BaseModel):
    """Per-decision agreement of one genome with the FSM over a stream."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    decisions: int
    agreement_hits: int
    agreement: float
    mean_anchor_ce: float
    # STRUCTURAL off-menu only: the FSM's choice realizes no menu option
    # (zero grouped mass before any clamp). An on-menu key a sharp genome
    # drives below the epsilon is NOT off-menu — it is tallied in
    # ``ce_clamped_decisions`` (Codex review on PR #292), which counts every
    # epsilon clamp the ``mean_anchor_ce`` column absorbed (structural
    # off-menu decisions necessarily clamp, so it is a superset tally).
    fsm_offmenu_decisions: int
    ce_clamped_decisions: int
    per_kind_agreement: Mapping[str, tuple[int, int]]
    divergence: tuple[DivergenceCell, ...]


def _intent_kind(key: str) -> str:
    return key.split(":", 1)[0]


def evaluate_anchor_offline(
    genome: Sequence[float],
    decisions: Sequence[CorpusDecision],
    *,
    label: str,
) -> OfflineAgreement:
    """Score one utility-family genome against the FSM over a decision stream.

    Agreement is top-1 by the frozen policy's exact arbitration (score DESC,
    canonical intent-key ASC — the :class:`UtilityScorerPolicy` tie-break);
    ``mean_anchor_ce`` is the harness's anchor cross-entropy semantics
    verbatim (softmax mass grouped by intent key at the FSM's key, clamped at
    :data:`~training.bakeoff.harness.ANCHOR_CE_EPSILON`; an off-menu FSM
    choice clamps and is tallied). ``divergence`` buckets every disagreement
    by (FSM intent kind → anchor intent kind), sorted by count DESC then
    lexically — where it diverges and toward what.
    """

    expected = utility_genome_length()
    if len(genome) != expected:
        raise ValueError(f"genome length {len(genome)} != expected {expected}")
    if not decisions:
        raise ValueError("evaluate_anchor_offline received an empty stream")
    head = np.asarray(genome[:-1], dtype=np.float64)
    bias = float(genome[-1])

    hits = 0
    offmenu = 0
    clamped = 0
    ce_sum = 0.0
    per_kind: dict[str, list[int]] = {}
    divergence: dict[tuple[str, str], int] = {}
    for decision in decisions:
        menu = np.asarray(decision.features, dtype=np.float64)
        scores = menu @ head + bias
        chosen_index = min(
            range(len(scores)),
            key=lambda index: (
                -float(scores[index]),
                decision.option_intent_keys[index],
            ),
        )
        chosen_key = decision.option_intent_keys[chosen_index]

        peak = float(scores.max())
        exp = np.exp(scores - peak)
        probs = exp / float(exp.sum())
        mass = 0.0
        for index, key in enumerate(decision.option_intent_keys):
            if key == decision.fsm_intent_key:
                mass += float(probs[index])
        if decision.fsm_option_index is None:
            offmenu += 1
        if mass < ANCHOR_CE_EPSILON:
            mass = ANCHOR_CE_EPSILON
            clamped += 1
        ce_sum += -math.log(mass)

        fsm_kind = _intent_kind(decision.fsm_intent_key)
        bucket = per_kind.setdefault(fsm_kind, [0, 0])
        bucket[0] += 1
        if chosen_key == decision.fsm_intent_key:
            hits += 1
            bucket[1] += 1
        else:
            pair = (fsm_kind, _intent_kind(chosen_key))
            divergence[pair] = divergence.get(pair, 0) + 1

    cells = tuple(
        DivergenceCell(fsm_intent_kind=fsm, anchor_intent_kind=anchor, count=count)
        for (fsm, anchor), count in sorted(
            divergence.items(), key=lambda item: (-item[1], item[0])
        )
    )
    return OfflineAgreement(
        label=label,
        decisions=len(decisions),
        agreement_hits=hits,
        agreement=hits / len(decisions),
        mean_anchor_ce=ce_sum / len(decisions),
        fsm_offmenu_decisions=offmenu,
        ce_clamped_decisions=clamped,
        per_kind_agreement={
            kind: (bucket[0], bucket[1]) for kind, bucket in sorted(per_kind.items())
        },
        divergence=cells,
    )


# --------------------------------------------------------------------------- #
# The λ sweep.                                                                 #
# --------------------------------------------------------------------------- #


class DeterminismCrossCheck(BaseModel):
    """The λ=1.0 byte-identity verdict against the committed champion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lambda_value: float
    committed_weights_sha256: str
    sweep_weights_sha256: str
    byte_identical: bool


class SweepRow(BaseModel):
    """One λ cell's deterministic metric tuple (distilled from the row).

    Every field the definition of done names — fitness, anchor-CE, win rate,
    take-rate, descriptor footprint on the standing 30-seed protocol — plus
    the referee/validity columns the standing protocol computes anyway and the
    train-side diagnostics. Wall-clocks stay OUT (they belong to the report
    prose): this model serializes into the frozen ``study.json`` index, which
    must be a pure function of the committed bytes.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    lambda_value: float
    entrant: str
    artifact_path: str
    weights_sha256: str
    inner_fitness_real: float
    mean_shaped_reward_real: float | None
    truncated_episodes_real: int
    inner_fitness_surrogate: float | None
    anchor_cross_entropy: float
    anchor_ce_flagged: bool
    anchor_offmenu_decisions: int
    fsm_intent_agreement: float | None
    impostor_win_rate: float
    take_rate: float | None
    take_opportunities: int
    descriptor_footprint: Mapping[str, float]
    referee_passed: bool
    referee_mean_score: float
    supply_floors_passed: bool
    validity_passed: bool
    leak_test_passed: bool
    determinism_deterministic: bool
    train_champion_fitness: float
    es_digest: str


def _lambda_entrant_name(lambda_value: float) -> str:
    # str(float) is the canonical repr ("1.0", "0.25"): the entrant/dir names
    # 18.24 addresses stay unambiguous across the grid.
    return f"lambda-{lambda_value}"


def _sweep_row(
    lambda_value: float, candidate: TrainedCandidate, result: BakeoffResult
) -> SweepRow:
    metadata = dict(candidate.train_metadata)
    champion_fitness = metadata.get("champion_fitness")
    return SweepRow(
        lambda_value=lambda_value,
        entrant=result.entrant,
        artifact_path=result.artifact_path,
        weights_sha256=result.weights_sha256,
        inner_fitness_real=result.inner_fitness_real,
        mean_shaped_reward_real=result.mean_shaped_reward_real,
        truncated_episodes_real=result.truncated_episodes_real,
        inner_fitness_surrogate=result.inner_fitness_surrogate,
        anchor_cross_entropy=result.anchor_cross_entropy,
        anchor_ce_flagged=result.anchor_ce_flagged,
        anchor_offmenu_decisions=result.anchor_offmenu_decisions,
        fsm_intent_agreement=result.fsm_intent_agreement,
        impostor_win_rate=result.impostor_win_rate,
        take_rate=result.take_rate,
        take_opportunities=result.take_opportunities,
        descriptor_footprint=dict(result.descriptor_footprint),
        referee_passed=result.referee_passed,
        referee_mean_score=result.referee_mean_score,
        supply_floors_passed=result.supply_floors_passed,
        validity_passed=result.validity_passed,
        leak_test_passed=result.leak_test_passed,
        determinism_deterministic=result.determinism.deterministic,
        train_champion_fitness=(
            float(champion_fitness)
            if isinstance(champion_fitness, (int, float))
            else math.nan
        ),
        es_digest=str(metadata.get("es_digest", "")),
    )


def run_lambda_sweep(
    *,
    budget: str = "full",
    lambda_grid: Sequence[float] = LAMBDA_GRID,
    protocol: BakeoffProtocolConfig | None = None,
    artifact_root: Path = ANCHOR_STUDY_ARTIFACT_ROOT,
    substrate_sha: str,
    game_map: Map | None = None,
    verify_committed_champion: bool = True,
) -> tuple[tuple[SweepRow, ...], DeterminismCrossCheck | None, float]:
    """Train + score the anchor-weight grid through the standing protocol.

    One :class:`BakeoffProtocolConfig` instance scores every cell (the
    staleness-cap doctrine: one cumulative surrogate counter per run). Each
    cell's champion freezes under ``artifact_root/lambda-<λ>/`` with its
    config carrying the substrate sha. At the full budget the λ=1.0 cell is
    byte-compared against the committed champion and a mismatch RAISES — a
    training loop that no longer reproduces the committed genome invalidates
    every other cell silently, so the sweep refuses to report over it.

    ``verify_committed_champion=False`` is the documented POST-ADOPTION
    escape (Codex review on PR #292): the committed champion is a baseline-5
    artifact, so the stale-seed recovery re-run at an ADOPTED substrate
    (new meeting layer / re-recorded corpus) legitimately produces different
    bytes — the comparison still runs and is RECORDED in the cross-check,
    it just no longer refuses the sweep. At the standing substrate the
    default (``True``) keeps the fail-loud guard.

    Returns ``(rows, cross_check, train_wall_clock_s)``; ``cross_check`` is
    ``None`` when the grid holds no λ=1.0 cell.
    """

    resolved_protocol = protocol if protocol is not None else default_protocol_config()
    rows: list[SweepRow] = []
    cross_check: DeterminismCrossCheck | None = None
    train_wall_clock = 0.0
    for lambda_value in lambda_grid:
        entrant = UtilityEsEntrant(
            config=utility_es_budget(budget, anchor_weight=lambda_value),
            game_map=game_map,
        )
        candidate = entrant.train()
        train_wall_clock += candidate.train_wall_clock_s
        relabeled = replace(
            candidate,
            entrant=_lambda_entrant_name(lambda_value),
            config={
                **dict(candidate.config),
                # The λ-specific identity must live in the CONFIG too, not
                # only the directory name: 18.24's config-driven provenance
                # would otherwise see every cell as "utility-es" (Codex
                # review on PR #292). The training method the cell re-ran is
                # preserved as ``base_entrant``.
                "base_entrant": candidate.entrant,
                "entrant": _lambda_entrant_name(lambda_value),
                "study": "anchor-study",
                "substrate_sha": substrate_sha,
                "train_budget": budget,
            },
        )
        if lambda_value == 1.0:
            cross_check = _cross_check_committed_champion(
                relabeled, enforce=budget == "full" and verify_committed_champion
            )
        result = evaluate_candidate(
            relabeled, resolved_protocol, artifact_root=artifact_root, game_map=game_map
        )
        rows.append(_sweep_row(lambda_value, relabeled, result))
    return tuple(rows), cross_check, train_wall_clock


def _cross_check_committed_champion(
    candidate: TrainedCandidate, *, enforce: bool
) -> DeterminismCrossCheck:
    """Byte-compare a λ=1.0 sweep champion against the committed artifact.

    ``enforce=True`` (the full budget) raises on a mismatch — the determinism
    cross-check the definition of done requires. A ci-budget run compares
    without enforcement (its 1-generation champion is legitimately a different
    genome) so the mechanism stays exercised in tests.
    """

    committed_bytes = (COMMITTED_CHAMPION_DIR / _WEIGHTS_FILENAME).read_bytes()
    sweep_bytes = (weights_to_hex_json(candidate.weights) + "\n").encode("utf-8")
    check = DeterminismCrossCheck(
        lambda_value=1.0,
        committed_weights_sha256=_sha256_hex(committed_bytes),
        sweep_weights_sha256=_sha256_hex(sweep_bytes),
        byte_identical=committed_bytes == sweep_bytes,
    )
    if enforce and not check.byte_identical:
        raise RuntimeError(
            "the λ=1.0 full-budget sweep did not reproduce the committed "
            f"utility-es champion byte-identically (committed "
            f"{check.committed_weights_sha256}, sweep "
            f"{check.sweep_weights_sha256}); the training loop has drifted and "
            "every sweep cell is suspect"
        )
    return check


# --------------------------------------------------------------------------- #
# The study report (the Task 18.5 public type) + the driver.                   #
# --------------------------------------------------------------------------- #


class CorpusFilterSummary(BaseModel):
    """The stated game filter, measured on the walked corpus."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    games_walked: int
    crew_winning_games: int
    high_flag_games: int
    both_criteria_games: int
    qualifying_games: int
    qualifying_seeds: tuple[int, ...]
    total_decisions: int
    fit_decisions: int
    fit_weight_total: float
    fsm_offmenu_decisions: int
    high_flag_floor: float
    both_criteria_weight: float


class FilteredBcReport(BaseModel):
    """The filtered-BC anchor's fit + offline evaluation record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entrant: str
    artifact_path: str
    weights_sha256: str
    epochs: int
    learning_rate: float
    filter_summary: CorpusFilterSummary
    overall: OfflineAgreement
    in_filter: OfflineAgreement
    out_of_filter: OfflineAgreement
    committed_champion_overall: OfflineAgreement


class AnchorStudyReport(BaseModel):
    """The Task 18.5 study record (public type — 18.24 seeds from it).

    A pure function of the committed bytes: no wall-clocks, no timestamps —
    those live in the rendered report's prose. Serialized (sorted keys) into
    ``training/artifacts/anchor_study/study.json`` beside the frozen
    candidate/anchor artifacts it indexes.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    baseline_id: str
    substrate_sha: str
    corpus_set: str
    train_budget: str
    lambda_grid: tuple[float, ...]
    eval_seeds: tuple[int, ...]
    sweep_rows: tuple[SweepRow, ...]
    determinism_cross_check: DeterminismCrossCheck | None
    filtered_bc: FilteredBcReport
    recommended_campaign_seeds: tuple[str, ...]

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"


def _recommend_campaign_seeds(rows: Sequence[SweepRow]) -> tuple[str, ...]:
    """Name the 18.24 seed candidates: the sweep's Pareto set + the anchor.

    A λ cell is named iff no other cell weakly dominates it on the study's
    Pareto axes (mean shaped reward UP, anchor-CE DOWN) — the fitness/legibility
    front the piKL reading says λ trades along. The filtered-BC anchor is
    always named: it is the 18.16 anchor-policy seam's entrant configuration,
    not a champion, so it seeds regardless of the sweep's front.
    """

    named: list[str] = []
    for row in rows:
        shaped = row.mean_shaped_reward_real
        if shaped is None:
            continue
        dominated = False
        for other in rows:
            other_shaped = other.mean_shaped_reward_real
            if other is row or other_shaped is None:
                continue
            if (
                other_shaped >= shaped
                and other.anchor_cross_entropy <= row.anchor_cross_entropy
                and (
                    other_shaped > shaped
                    or other.anchor_cross_entropy < row.anchor_cross_entropy
                )
            ):
                dominated = True
                break
        if not dominated:
            named.append(row.entrant)
    named.append(FILTERED_BC_ENTRANT)
    return tuple(named)


def _freeze_filtered_bc_anchor(
    genome: tuple[float, ...],
    *,
    artifact_root: Path,
    substrate_sha: str,
    filter_summary: CorpusFilterSummary,
    game_map: Map | None = None,
) -> tuple[str, str]:
    """Freeze the refined anchor (float-hex + sha sidecar + substrate config).

    Reuses the harness's artifact writer through a :class:`TrainedCandidate`
    shell so the layout is byte-compatible with every other frozen candidate
    (the 18.24 loader reads one format). Returns ``(artifact_path, sha256)``.
    """

    candidate = TrainedCandidate(
        entrant=FILTERED_BC_ENTRANT,
        policy=build_utility_scorer_policy(genome, game_map=game_map),
        weights=genome,
        config={
            "anchor_policy_family": "utility-option-softmax",
            "entrant": FILTERED_BC_ENTRANT,
            "epochs": FILTERED_BC_EPOCHS,
            "feature_names": list(OPTION_FEATURE_NAMES),
            "filter": {
                "both_criteria_weight": BOTH_CRITERIA_WEIGHT,
                "high_flag_floor": filter_summary.high_flag_floor,
                "qualifying_seeds": list(filter_summary.qualifying_seeds),
                "rule": (
                    "crew-winning (recorded winner CREWMATES) OR high-flag "
                    "(persisted contradiction rows per meeting >= the "
                    "configured flags_per_meeting supply floor, the "
                    "high_flag_floor field); games satisfying BOTH weigh "
                    "double"
                ),
            },
            "genome_length": len(genome),
            "learning_rate": FILTERED_BC_LEARNING_RATE,
            "study": "anchor-study",
            "substrate_sha": substrate_sha,
        },
    )
    entrant_dir, digest = write_candidate_artifact(candidate, artifact_root)
    return str(entrant_dir), digest


def _filter_summary(
    facts: Sequence[CorpusGameFacts], *, high_flag_floor: float = HIGH_FLAG_FLOOR
) -> CorpusFilterSummary:
    qualifying = [game for game in facts if game.qualifies]
    # Only ON-MENU decisions carry likelihood into the fit
    # (:func:`fit_filtered_bc_anchor` excludes off-menu FSM choices), so the
    # frozen census counts exactly the rows the fit consumed (Codex review on
    # PR #292); the off-menu tally stays reported beside it.
    fit_decisions = sum(
        game.decisions - game.fsm_offmenu_decisions for game in qualifying
    )
    return CorpusFilterSummary(
        games_walked=len(facts),
        crew_winning_games=sum(1 for game in facts if game.crew_winning),
        high_flag_games=sum(1 for game in facts if game.high_flag),
        both_criteria_games=sum(
            1 for game in facts if game.crew_winning and game.high_flag
        ),
        qualifying_games=len(qualifying),
        qualifying_seeds=tuple(game.seed for game in qualifying),
        total_decisions=sum(game.decisions for game in facts),
        fit_decisions=fit_decisions,
        fit_weight_total=math.fsum(
            game.sample_weight * (game.decisions - game.fsm_offmenu_decisions)
            for game in qualifying
        ),
        fsm_offmenu_decisions=sum(game.fsm_offmenu_decisions for game in facts),
        high_flag_floor=high_flag_floor,
        both_criteria_weight=BOTH_CRITERIA_WEIGHT,
    )


def run_anchor_study(
    *,
    budget: str = "full",
    lambda_grid: Sequence[float] = LAMBDA_GRID,
    corpus_seed_subset: Sequence[int] | None = None,
    corpus_dir: Path = CORPUS_DIR,
    artifact_root: Path = ANCHOR_STUDY_ARTIFACT_ROOT,
    protocol: BakeoffProtocolConfig | None = None,
    report_path: Path | None = None,
    game_map: Map | None = None,
    high_flag_floor: float = HIGH_FLAG_FLOOR,
    verify_committed_champion: bool = True,
) -> AnchorStudyReport:
    """The study driver: sweep + walk + fit + offline eval + freeze + report.

    ``budget`` selects the committed utility-es training budgets (``"ci"`` /
    ``"full"``); ``corpus_seed_subset=None`` walks the whole corpus (the
    committed study), a subset keeps tests seconds-scale. ``protocol=None``
    scores through :func:`default_protocol_config` (the standing 30-seed
    protocol); tests pass a tiny protocol. When ``report_path`` is set the
    rendered Markdown report is written there.

    The POST-ADOPTION re-fit (the 18.24 stale-seed recovery) passes the
    adopted substrate explicitly: the re-pinned ``high_flag_floor`` beside
    the protocol's new ``baseline_id`` (both fold into the substrate sha),
    and ``verify_committed_champion=False`` (the committed λ=1.0 champion is
    a baseline-5 artifact — see :func:`run_lambda_sweep`). The committed
    defaults reproduce the shipped study byte-for-byte.
    """

    started = time.perf_counter()
    # The λ sweep trains through the COMMITTED utility_es_budget, whose train
    # seeds bind to the harness corpus (a public seam this study must not
    # fork). A swept study against a DIFFERENT corpus directory would stamp
    # its artifacts with one corpus while training on another (Codex review
    # on PR #292) — refuse it; a substrate adoption re-points the harness
    # corpus first (the 18.13/18.14 re-pins), and a fit-only re-run
    # (``lambda_grid=()``) stays free to target any corpus.
    if lambda_grid and corpus_dir.resolve() != CORPUS_SPLITS_PATH.parent.resolve():
        raise ValueError(
            f"the λ sweep's training seeds bind to the harness corpus "
            f"({CORPUS_SPLITS_PATH.parent}), not {corpus_dir}; re-point the "
            "harness corpus (the 18.13/18.14 re-pins) before sweeping, or "
            "run a fit-only study (lambda_grid=())"
        )
    # ONE protocol instance for the whole run (the staleness-cap doctrine: one
    # cumulative surrogate counter outlives every cell this run scores), and
    # the substrate sha is keyed to THAT protocol's baseline — a re-pinned
    # baseline must move the frozen provenance with the scoring floors, never
    # trail the module default (Codex review on PR #292).
    resolved_protocol = protocol if protocol is not None else default_protocol_config()
    substrate_sha = compute_substrate_sha(
        corpus_dir,
        baseline_id=resolved_protocol.baseline_id,
        high_flag_floor=high_flag_floor,
    )
    sweep_rows, cross_check, train_wall_clock = run_lambda_sweep(
        budget=budget,
        lambda_grid=lambda_grid,
        protocol=resolved_protocol,
        artifact_root=artifact_root,
        substrate_sha=substrate_sha,
        game_map=game_map,
        verify_committed_champion=verify_committed_champion,
    )

    seeds = (
        tuple(corpus_seed_subset)
        if corpus_seed_subset is not None
        else corpus_seeds(corpus_dir)
    )
    facts, decisions = walk_corpus(
        seeds,
        corpus_dir=corpus_dir,
        game_map=game_map,
        high_flag_floor=high_flag_floor,
    )
    summary = _filter_summary(facts, high_flag_floor=high_flag_floor)

    weight_by_seed = {game.seed: game.sample_weight for game in facts}
    fit_decisions = [
        decision for decision in decisions if weight_by_seed[decision.seed] > 0.0
    ]
    fit_weights = [weight_by_seed[decision.seed] for decision in fit_decisions]
    genome = fit_filtered_bc_anchor(fit_decisions, sample_weights=fit_weights)

    in_filter = [
        decision for decision in decisions if weight_by_seed[decision.seed] > 0.0
    ]
    out_of_filter = [
        decision for decision in decisions if weight_by_seed[decision.seed] == 0.0
    ]
    overall_eval = evaluate_anchor_offline(genome, decisions, label="all corpus games")
    in_eval = evaluate_anchor_offline(genome, in_filter, label="in-filter games")
    out_eval = (
        evaluate_anchor_offline(genome, out_of_filter, label="out-of-filter games")
        if out_of_filter
        else OfflineAgreement(
            label="out-of-filter games",
            decisions=0,
            agreement_hits=0,
            agreement=0.0,
            mean_anchor_ce=0.0,
            fsm_offmenu_decisions=0,
            ce_clamped_decisions=0,
            per_kind_agreement={},
            divergence=(),
        )
    )
    committed_genome = load_candidate_weights(COMMITTED_CHAMPION_DIR)
    champion_eval = evaluate_anchor_offline(
        committed_genome, decisions, label="committed utility-es champion"
    )

    anchor_path, anchor_sha = _freeze_filtered_bc_anchor(
        genome,
        artifact_root=artifact_root,
        substrate_sha=substrate_sha,
        filter_summary=summary,
        game_map=game_map,
    )
    filtered_bc = FilteredBcReport(
        entrant=FILTERED_BC_ENTRANT,
        artifact_path=anchor_path,
        weights_sha256=anchor_sha,
        epochs=FILTERED_BC_EPOCHS,
        learning_rate=FILTERED_BC_LEARNING_RATE,
        filter_summary=summary,
        overall=overall_eval,
        in_filter=in_eval,
        out_of_filter=out_eval,
        committed_champion_overall=champion_eval,
    )

    report = AnchorStudyReport(
        baseline_id=resolved_protocol.baseline_id,
        substrate_sha=substrate_sha,
        corpus_set=corpus_dir.name,
        train_budget=budget,
        lambda_grid=tuple(lambda_grid),
        eval_seeds=resolved_protocol.eval_seeds,
        sweep_rows=sweep_rows,
        determinism_cross_check=cross_check,
        filtered_bc=filtered_bc,
        recommended_campaign_seeds=_recommend_campaign_seeds(sweep_rows),
    )
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / STUDY_INDEX_FILENAME).write_text(report.to_json())
    if report_path is not None:
        wall_clock = time.perf_counter() - started
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            render_report(
                report, train_wall_clock_s=train_wall_clock, wall_clock_s=wall_clock
            )
        )
    return report


# --------------------------------------------------------------------------- #
# The Markdown report renderer.                                                #
# --------------------------------------------------------------------------- #


def _fmt(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def render_report(
    report: AnchorStudyReport, *, train_wall_clock_s: float, wall_clock_s: float
) -> str:
    """Render the committed study report (the house report style)."""

    rows = report.sweep_rows
    check = report.determinism_cross_check
    bc = report.filtered_bc
    summary = bc.filter_summary

    def sweep_table() -> str:
        header = "| Metric | " + " | ".join(f"λ={row.lambda_value}" for row in rows)
        sep = "|---|" + "---|" * len(rows)
        lines = [header + " |", sep]
        metric_rows: list[tuple[str, list[str]]] = [
            (
                "inner fitness (real path, standing λ=1.0 gauge)",
                [_fmt(row.inner_fitness_real) for row in rows],
            ),
            (
                "mean shaped reward (real path)",
                [_fmt(row.mean_shaped_reward_real) for row in rows],
            ),
            ("anchor-CE (nats)", [_fmt(row.anchor_cross_entropy) for row in rows]),
            (
                "anchor-CE flagged (> 2.0 ceiling)",
                [str(row.anchor_ce_flagged) for row in rows],
            ),
            (
                "FSM intent agreement",
                [_fmt(row.fsm_intent_agreement) for row in rows],
            ),
            ("impostor win rate", [_fmt(row.impostor_win_rate) for row in rows]),
            (
                "take-rate (opportunities)",
                [f"{_fmt(row.take_rate)} ({row.take_opportunities})" for row in rows],
            ),
            (
                "referee mean (passed)",
                [
                    f"{_fmt(row.referee_mean_score, 2)} ({row.referee_passed})"
                    for row in rows
                ],
            ),
            (
                "supply floors passed",
                [str(row.supply_floors_passed) for row in rows],
            ),
            (
                "validity / leak / determinism",
                [
                    f"{row.validity_passed}/{row.leak_test_passed}/"
                    f"{row.determinism_deterministic}"
                    for row in rows
                ],
            ),
            (
                "train champion fitness (own λ)",
                [_fmt(row.train_champion_fitness) for row in rows],
            ),
            (
                "weights sha256 (12-hex)",
                [f"`{row.weights_sha256[:12]}`" for row in rows],
            ),
        ]
        for name, cells in metric_rows:
            lines.append("| " + name + " | " + " | ".join(cells) + " |")
        return "\n".join(lines)

    def sweep_reading() -> str:
        by_sha: dict[str, list[SweepRow]] = {}
        for row in rows:
            by_sha.setdefault(row.weights_sha256, []).append(row)
        lines: list[str] = []
        plateaus = [group for group in by_sha.values() if len(group) > 1]
        if plateaus:
            cells = "; ".join(
                "/".join(f"λ={row.lambda_value}" for row in group)
                + f" froze the SAME genome (`{group[0].weights_sha256[:12]}`)"
                for group in plateaus
            )
            lines.append(
                f"- **The dial has plateaus:** {cells} — at this ES budget no "
                "accept/reject comparison flips anywhere inside those bands "
                "(the fitness gap the λ change makes never re-orders an "
                "offspring against the incumbent)."
            )
        front = [
            row.entrant
            for row in rows
            if row.entrant in report.recommended_campaign_seeds
        ]
        if front:
            lines.append(
                "- **The Pareto front (mean shaped reward ↑, anchor-CE ↓) is "
                + ", ".join(f"`{name}`" for name in front)
                + ":** every other cell is weakly dominated — at this budget on "
                "the fake path a HEAVIER anchor did not cost shaped reward "
                f"(λ={rows[0].lambda_value} shaped "
                f"{_fmt(rows[0].mean_shaped_reward_real, 2)} / CE "
                f"{_fmt(rows[0].anchor_cross_entropy, 3)} → "
                f"λ={rows[-1].lambda_value} shaped "
                f"{_fmt(rows[-1].mean_shaped_reward_real, 2)} / CE "
                f"{_fmt(rows[-1].anchor_cross_entropy, 3)}). The fake path "
                "mints no convictions, so fitness and legibility are not yet "
                "in tension here — the tension the champion failed on lives "
                "in the referee gauges, and NO cell passes the supply floors "
                "(the flip bar stays open; this study only positions seeds)."
            )
        return "\n".join(lines)

    def descriptor_table() -> str:
        names = sorted(rows[0].descriptor_footprint) if rows else []
        header = "| Descriptor | " + " | ".join(f"λ={row.lambda_value}" for row in rows)
        lines = [header + " |", "|---|" + "---|" * len(rows)]
        for name in names:
            lines.append(
                "| "
                + name
                + " | "
                + " | ".join(_fmt(row.descriptor_footprint[name], 3) for row in rows)
                + " |"
            )
        return "\n".join(lines)

    def agreement_table() -> str:
        evals = (
            bc.overall,
            bc.in_filter,
            bc.out_of_filter,
            bc.committed_champion_overall,
        )
        lines = [
            "| Stream | decisions | agreement | mean anchor-CE (nats) | "
            "FSM off-menu | CE-clamped |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for entry in evals:
            lines.append(
                f"| {entry.label} | {entry.decisions} | {_fmt(entry.agreement)} | "
                f"{_fmt(entry.mean_anchor_ce)} | {entry.fsm_offmenu_decisions} | "
                f"{entry.ce_clamped_decisions} |"
            )
        return "\n".join(lines)

    def per_kind_table() -> str:
        lines = [
            "| FSM intent kind | decisions | anchor hits | agreement |",
            "|---|---:|---:|---:|",
        ]
        for kind, (total, kind_hits) in bc.overall.per_kind_agreement.items():
            lines.append(
                f"| {kind} | {total} | {kind_hits} | "
                f"{_fmt(kind_hits / total if total else 0.0)} |"
            )
        return "\n".join(lines)

    def divergence_table() -> str:
        lines = [
            "| FSM chose | anchor chose | count |",
            "|---|---|---:|",
        ]
        for cell in bc.overall.divergence[:12]:
            lines.append(
                f"| {cell.fsm_intent_kind} | {cell.anchor_intent_kind} | {cell.count} |"
            )
        return "\n".join(lines)

    check_lines = (
        f"λ=1.0 reproduced the committed champion **byte-identically** "
        f"(committed `{check.committed_weights_sha256[:12]}` == sweep "
        f"`{check.sweep_weights_sha256[:12]}`)."
        if check is not None and check.byte_identical
        else "λ=1.0 cross-check: NOT byte-identical (see study.json)."
        if check is not None
        else "the grid held no λ=1.0 cell (no cross-check ran)."
    )
    # The rendered budget must be the one the run ACTUALLY used — a ci or
    # rehearsal render must not read as full-budget results (Codex review on
    # PR #292); the full budget's shape is spelled out only when it applies.
    budget_detail = (
        " — ES 20 gen × 12 pop × 6 train seeds, σ 0.3, seed 0"
        if report.train_budget == "full"
        else ""
    )

    return f"""# The anchor study — λ sweep + filtered-BC anchor refinement (Task 18.5)

> **Task 18.5** (`tasks/phase-18.md`) — the two cheap levers on the exact
> gauges the champion failed (audits/audit-phase-18-planning.md §2.4; §6 the
> piKL reading).
> **Anchors:** training/bakeoff/harness.py `inner_episode_fitness` (:569-590,
> the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full
> budget); replays/ml_corpus/{report.corpus_set}/ (the filtered-BC source).
> **Substrate:** {report.baseline_id}; substrate sha `{report.substrate_sha}`
> (every frozen artifact under `training/artifacts/anchor_study/` carries it —
> the 18.24 stale-seed refusal reads it).
> **Committed artifacts:** `training/artifacts/anchor_study/<entrant>/`
> (float-hex `weights.json` + `weights.json.sha256` + `config.json` with the
> substrate sha) + `training/artifacts/anchor_study/study.json` (the
> deterministic index, the serialized `AnchorStudyReport`).
> **Command:** `uv run python -m training.anchor_study run --budget {report.train_budget}`
> (exit 0, {train_wall_clock_s:.0f} s training + {wall_clock_s - train_wall_clock_s:.0f} s
> scoring/walk = {wall_clock_s:.0f} s wall-clock, CPU-only, $0).
> **Report-only:** no champion ships from this study; the ES leg under the
> refined anchor is deliberately NOT run here (the harness's anchor-CE is
> computed against the FSM's own choice; the anchor-policy seam lands at
> 18.16, and the refined-anchor ES leg is a named 18.24 campaign entrant).

**The determinism cross-check, stated first:** {check_lines}

## 1. Protocol (fixed before any run)

- **Sweep grid:** λ ∈ {{{", ".join(str(value) for value in report.lambda_grid)}}} over
  the committed utility-es `{report.train_budget}` budget
  (`utility_es_budget("{report.train_budget}", anchor_weight=λ)`{budget_detail});
  every champion scored through the standing fake-path protocol
  (`evaluate_candidate`, the frozen 30-seed corpus test split
  {report.eval_seeds[0]}…{report.eval_seeds[-1]}), one shared protocol instance
  (one cumulative surrogate-staleness counter).
- **Fitness column caveat:** the reported inner fitness is the STANDING
  protocol's gauge (anchor weight 1.0 for every row — a common axis); each
  row's own-λ training objective is the `train champion fitness` row. The
  Pareto reading below uses mean shaped reward (performance) vs anchor-CE
  (legibility), both reported per row.
- **Filtered-BC filter (stated):** a corpus game qualifies iff its recorded
  winner is CREWMATES (crew-winning: the games where the evidence economy
  actually convicted) OR its persisted contradiction rows per meeting reach
  the `flags_per_meeting` supply floor {summary.high_flag_floor:.6f}
  (high-flag: the supply gauge the champion failed, read off the committed
  meeting rows — conservative vs the referee's set-level gauge, which
  additionally re-derives transcript flags). Games satisfying BOTH weigh
  {summary.both_criteria_weight:g}× in the fit (the purest "watchable winning
  play" exemplars).
- **Fit recipe:** numpy weighted conditional logit over the FSM option menu
  (grouped by canonical intent key, the anchor-CE semantics), standardized
  features, zeros init, {bc.epochs} full-batch epochs at lr
  {bc.learning_rate:g}, no RNG — the `Fo6Logistic`/`BallotPredictor`
  deterministic recipe. Deterministic on a given platform; a cross-CPU refit
  agrees to float ULP (numpy SIMD summation grouping), so the committed bytes
  + sha sidecar are the frozen ground truth (the surrogate precedent).
- **Walk verification:** every corpus game's decision stream is re-derived by
  walking the recorded actions through the pure engine with the production
  observation/perception path, and EVERY re-derived FSM intent is verified
  against the recorded action (plus every recorded state hash) — a single
  divergence fails the study loud.

## 2. The λ sweep ({len(rows)} cells, standing 30-seed protocol)

{sweep_table()}

### 2.1 Descriptor footprint (per-game means over the eval set)

{descriptor_table()}

### 2.2 Reading

{sweep_reading()}
- **The refined anchor vs the committed champion, on the corpus stream:** the
  filtered-BC anchor matches the FSM's choice on
  {_fmt(bc.overall.agreement)} of decisions (CE
  {_fmt(bc.overall.mean_anchor_ce)}); the committed champion matches on
  {_fmt(bc.committed_champion_overall.agreement)} (CE
  {_fmt(bc.committed_champion_overall.mean_anchor_ce)}) — the champion has
  drifted far from the legible anchor, which is the under-anchoring symptom
  the §2.4 reading predicts.
- **Structurally-zero anchor weights are expected:** a conditional logit over
  a menu can only learn from features that VARY within the menu; the
  decision-level constants (cooldown, sabotage state, crowd density …) carry
  exactly zero gradient and stay at their zeros init — not a degenerate fit.

## 3. The filtered-BC anchor

**Filter census:** {summary.games_walked} games walked, every state hash and
every re-derived FSM decision verified. Crew-winning {summary.crew_winning_games},
high-flag {summary.high_flag_games}, both {summary.both_criteria_games} →
{summary.qualifying_games} qualifying games, {summary.fit_decisions} fit
decisions (weight total {summary.fit_weight_total:g}) of
{summary.total_decisions} total corpus decisions;
{summary.fsm_offmenu_decisions} FSM decisions were off the option menu
(excluded from the fit, tallied here — never silently dropped).

### 3.1 Offline FSM agreement (per-decision, top-1 by the frozen arbitration)

{agreement_table()}

### 3.2 Where the anchor agrees, by FSM intent kind (all corpus games)

{per_kind_table()}

### 3.3 Where it diverges and toward what (top cells, all corpus games)

{divergence_table()}

## 4. Which candidates 18.24 should seed with

{chr(10).join(f"- `{name}`" for name in report.recommended_campaign_seeds)}

The λ cells above are the (mean shaped reward ↑, anchor-CE ↓) Pareto set —
the fitness/legibility front the piKL reading says the anchor weight trades
along; dominated cells stay frozen (byte-addressable) but are not named.
`{FILTERED_BC_ENTRANT}` is named as the 18.16 anchor-policy seam's entrant
configuration (the refined-anchor ES leg 18.24 runs), not as a champion.

## Reproduce

Every quoted number is a pure function of the committed bytes; nothing was
hand-computed.

```bash
uv run python -m training.anchor_study run --budget {report.train_budget}
```

- The λ=1.0 byte-identity + artifact integrity pins:
  `uv run pytest tests/training/test_anchor_study.py -q`
- The frozen index: `training/artifacts/anchor_study/study.json` (this
  report's tables are a rendering of it).

**Determinism caveat:** the sweep and the corpus walk are bit-deterministic
across platforms (pure-Python ES RNG + the deterministic engine + the fake
provider); the filtered-BC fit is numpy full-batch GD — byte-identical on the
recording platform, ULP-equivalent elsewhere. The committed artifact bytes are
the frozen ground truth the sha256 sidecars pin.

## How downstream consumes this

- **18.24 (the impostor campaign)** seeds entrants from
  `training/artifacts/anchor_study/<entrant>/weights.json` (sha-verified
  reload), refusing any artifact whose `config.json` `substrate_sha` !=
  `compute_substrate_sha()` at the campaign substrate without the cheap
  deterministic re-fit/re-run.
- **18.16 (fitness stack)** adds the additive anchor-policy seam;
  `{FILTERED_BC_ENTRANT}` is that seam's first candidate anchor.
- **18.4 / the campaign reports** read the sweep Pareto as the λ prior.
"""


# --------------------------------------------------------------------------- #
# CLI.                                                                         #
# --------------------------------------------------------------------------- #


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m training.anchor_study",
        description="The Task 18.5 anchor study: λ sweep + filtered-BC anchor.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser(
        "run", help="Run the study; freeze artifacts + write the report."
    )
    run_parser.add_argument("--budget", choices=("ci", "full"), default="full")
    run_parser.add_argument(
        "--artifacts", type=Path, default=ANCHOR_STUDY_ARTIFACT_ROOT
    )
    run_parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args(argv)

    report = run_anchor_study(
        budget=args.budget,
        artifact_root=args.artifacts,
        report_path=args.report,
    )
    print(report.to_json())
    return 0


__all__ = [
    "ANCHOR_STUDY_ARTIFACT_ROOT",
    "AnchorStudyReport",
    "BOTH_CRITERIA_WEIGHT",
    "CORPUS_DIR",
    "CorpusDecision",
    "CorpusFilterSummary",
    "CorpusGameFacts",
    "CorpusWalkError",
    "DeterminismCrossCheck",
    "DivergenceCell",
    "FILTERED_BC_ENTRANT",
    "FILTERED_BC_EPOCHS",
    "FILTERED_BC_LEARNING_RATE",
    "FilteredBcReport",
    "HIGH_FLAG_FLOOR",
    "LAMBDA_GRID",
    "OfflineAgreement",
    "REPORT_PATH",
    "SweepRow",
    "compute_substrate_sha",
    "corpus_seeds",
    "evaluate_anchor_offline",
    "fit_filtered_bc_anchor",
    "main",
    "render_report",
    "run_anchor_study",
    "run_lambda_sweep",
    "walk_corpus",
    "walk_corpus_game",
]


if __name__ == "__main__":
    raise SystemExit(main())
