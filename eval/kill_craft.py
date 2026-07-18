"""The kill-craft fold — kill-timing vs witness density + action-stream entropy.

Task 18.2 (tasks/phase-18.md; audits/audit-phase-18-planning.md §3.2, the Tier-B
gap rows "kill-timing vs witness density" and "behavioral diversity (action-stream
entropy)") promotes two byte-grounded emergence gauges into committed ``eval/``
folds, computed offline over the committed replay bytes with a state-hash-verified
reconstruction walk. Both are the first byte-grounded gauges of their kind:

* **Fold 1 — kill-timing vs witness density.** Per recorded kill, the count of
  living crew co-present with the kill room, and one room-hop away, at the kill
  tick (a per-tick occupancy census), correlated with the crew-witnessed bit. It
  answers the kill-craft question: *does the mover kill into witnesses, or wait
  them out?* (:class:`~engine.events.KilledEvent` carries ``tick`` / ``room`` /
  ``witnesses``; the occupancy census is the new fold over the walk.)

* **Fold 2 — action-stream behavioral entropy.** Per-agent Shannon entropy of
  action-kind choices, bucketed by a coarse agent-state (room-occupancy band ×
  cooldown state), aggregated into per-side cells. This is the *intent-level*
  diversity metric that **complements the lexical diversity cells**
  (``eval/vj_instruments.py`` — distinct-n / echo) with intent-level diversity:
  lexical diversity measures the words; this measures the action choices.

Census frame (the ⊆ agreement guarantee)
-----------------------------------------
Both folds read the **pre-advance decision state** — the ``WorldState`` fed into
:func:`engine.tick.advance_tick`, whose ``tick`` equals the recorded
``ReplayEntry.tick`` and against which the recorded actions were decided. The
engine, by contrast, computes ``KilledEvent.witnesses`` **mid-tick** (actions
apply in ascending actor-id order against the evolving state; witnesses are the
sorted living, non-vented players in the kill room excluding killer and victim —
``engine/rules.py``). Because movement is one room-hop per tick, every crew
witness recorded on a kill was, in the pre-advance state, either already in the
kill room (co-present) or in a room adjacent to it (one hop). So the crew-witness
set is a **subset of co-present ∪ one-hop** by construction, and the census is
verified to agree: a crew witness that lands in neither bucket would mean the
pre-advance census disagrees with the engine walk, which fails loud (below).

Fold-1 census predicate (per :class:`~engine.events.KilledEvent`)
-----------------------------------------------------------------
``co_present_crew`` counts players ``p`` where ``p`` is a CREWMATE, alive and not
in-vent in the pre-advance state, ``p.room == event.room``, and ``p !=
event.target`` (the victim is not their own witness pool; the killer is an
impostor and so is excluded by the crew filter). ``one_hop_crew`` is the same
predicate but ``p.room in game_map.room_neighbors(event.room)``. ``crew_witnessed``
is True iff any player on ``event.witnesses`` is a CREWMATE (mirrors
``eval.watchability._KillWitnessFact.crew_witnessed``). Crew never vent, so the
``not in_vent`` clause is total for crew but is stated for exactness.

Fold-2 bucketization (documented, deterministic — no float-ordering hazards)
----------------------------------------------------------------------------
For every recorded action of every living actor at every PLAY tick (every
``ReplayEntry`` is one PLAY decision tick), the action is bucketed by the actor's
coarse pre-advance state:

* ``kind`` — the raw recorded action ``"type"`` string, one of the nine engine
  action kinds (move, do_task, kill, vent, report, emergency, sabotage,
  repair_sabotage, wait).
* ``occupancy`` — the count of players ``q`` with ``q.alive and not q.in_vent and
  q.room == <actor's pre-advance room>``. The actor counts **itself** when it is
  not vented; a vented impostor is **not** counted in its own room (it is
  ``in_vent``), so a vented actor's occupancy excludes itself. Quantized into an
  ``occupancy_band``: ``"solo"`` when ``occupancy <= 1``, ``"pair"`` when ``== 2``,
  ``"crowd"`` when ``>= 3``.
* ``cooldown_state`` — byte-mechanical, read from ``WorldState.cooldowns``
  membership, **never** from role: ``"none"`` when the actor has no cooldown entry
  (crew are never in the map), ``"ready"`` when the entry ``== 0``, ``"cooling"``
  when ``> 0``.
* Bucket key: ``f"{cooldown_state}|{occupancy_band}"``.

Entropy is in **bits** (``math.log2``). Per agent (a ``(seed, player)`` pair):

* the **conditional** entropy ``H(kind | bucket)`` = ``sum`` over the agent's
  buckets (iterated in SORTED bucket order) of ``(n_bucket / n_total) *
  H_bucket``, where ``H_bucket = -sum`` over SORTED kinds of ``p * log2(p)``;
* the **unconditional** entropy over the agent's pooled kind counts (SORTED kinds).

Per-side cells (sides ``"CREWMATE"`` / ``"IMPOSTOR"`` from the re-seeded ground
truth) carry the agent count, the total decisions, the unweighted mean of the
per-agent conditional / unconditional entropies (summed in SORTED ``(seed,
player)`` order), and per-bucket **pooled** cells (every agent of the side pooled
into one kind distribution per bucket, then that distribution's entropy). Every
``Mapping`` field is built by SORTED iteration, and every entropy / mean sums over
a sorted (or fixed-collection-order) sequence — this is the DoD's "deterministic
(sorted, quantized) — no float-ordering hazards" item: two runs over the same
bytes yield byte-identical reports.

The Fold-1 aggregate correlations (point-biserial: the Pearson correlation between
the count and the 0/1 crew-witnessed bit) sum over the per-kill rows in their
FIXED collection order (seeds ascending, file order within a game); determinism
comes from that fixed row order. A correlation is ``None`` when either variable
has zero variance or there are no kills; a subgroup mean is ``None`` when its
subgroup is empty.

Reconstruction walk + fail-loud contract
----------------------------------------
The per-game walk MIRRORS ``eval.watchability._reconstruct_game_kills`` (the
kill-reconstruction precedent this fold extends, engine/events.py:76) and
``eval.funnel._walk_game`` (the fail-loud instrument-walk precedent): re-seed via
:func:`orchestrator.seeder.seed_initial_state`, feed the recorded actions through
:func:`engine.tick.advance_tick`, verify every ``state_hash``, and on a MEETING
tick rebuild the :class:`~meetings.schemas.MeetingResult` and apply it via
:func:`orchestrator.game.apply_meeting_result` (verifying
``state_hash_before`` / ``state_hash_after``). Neither private walk is imported:
neither exposes the per-tick occupancy, the recorded per-actor actions, and the
cooldown state this fold needs, and the referee (``eval/watchability.py``) is out
of scope — so the walk is duplicated locally, and **the duplication is noted for
Phase 19's review**.

Fail-loud instrument semantics (the funnel precedent, NOT watchability's
floor-the-set referee semantics): :class:`KillCraftReconstructionError` is raised
— naming the game/tick and what disagreed — on a per-tick ``state_hash`` mismatch,
a MEETING tick with no meeting row, a meeting ``state_hash_before`` /
``state_hash_after`` mismatch, a recorded action whose actor is missing or not
alive in the pre-advance state, and the census-agreement breach above. An
instrument must never silently under-measure (AGENTS.md "no silent fallbacks"), so
malformed bytes (a corrupt action row, a truncated file) are allowed to raise
naturally (pydantic / OS errors propagate) rather than being papered over.

Purity: offline, no network, no ``AILIBI_*`` env read, no LLM. The report is a
pure function of the committed bytes plus the re-seeded role ground truth, so two
runs produce identical reports.

STABLE JSON report schema (``KillCraftReport.model_dump()``) — downstream tasks
import :func:`compute_kill_craft_report` and :class:`KillCraftReport`::

    {
      "replay_set_dir": str,
      "num_players": int, "num_impostors": int, "tasks_per_crewmate": int,
      "games_total": int,
      # -- Fold 1: kill-timing vs witness density (over all kills) --
      "kills_total": int,
      "crew_witnessed_kills": int,
      "co_present_histogram": {int: int},   # co_present_crew -> #kills, keys sorted
      "one_hop_histogram": {int: int},      # one_hop_crew   -> #kills, keys sorted
      "mean_co_present_witnessed": float | null,
      "mean_co_present_unwitnessed": float | null,
      "mean_one_hop_witnessed": float | null,
      "mean_one_hop_unwitnessed": float | null,
      "witnessed_point_biserial_co_present": float | null,
      "witnessed_point_biserial_within_one_hop": float | null,
      "per_kill": [ KillWitnessDensityRow, ... ],   # collection order
      # -- Fold 2: action-stream behavioral entropy (per side) --
      "entropy_by_side": {                          # keys sorted
        "CREWMATE": ActionEntropyCells,
        "IMPOSTOR": ActionEntropyCells,
      }
    }

    KillWitnessDensityRow = {
      "seed": int, "tick": int, "room": str,
      "killer": str, "victim": str,
      "co_present_crew": int, "one_hop_crew": int, "crew_witnessed": bool,
    }

    ActionEntropyCells = {
      "agents": int, "decisions": int,
      "mean_conditional_entropy": float | null,
      "mean_unconditional_entropy": float | null,
      "buckets": { "<cooldown>|<band>": ActionEntropyBucketCell, ... },  # sorted
    }

    ActionEntropyBucketCell = {
      "decisions": int,
      "action_kinds": {str: int},   # kind -> count, keys sorted
      "entropy": float,             # pooled entropy of the side's kinds (bits)
    }
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, TypeAdapter

from engine.actions import Action
from engine.entities import PlayerId, PlayerState, Role, RoomId
from engine.events import KilledEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, load_canonical_map
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.schemas import MeetingResult
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# Occupancy-band edges (Fold 2): solo when <= 1, pair when == 2, crowd when >= 3.
_SOLO_MAX = 1
_PAIR = 2


class KillCraftReconstructionError(RuntimeError):
    """A recorded state hash, meeting row, action actor, or census did not agree.

    Raised during the walk — naming the game/tick and what disagreed — so a
    drifted / corrupted / truncated replay set fails loud rather than silently
    under-measuring (AGENTS.md "no silent fallbacks"; the funnel fail-loud
    precedent, NOT watchability's floor-the-set referee semantics). Fired on: a
    per-tick ``state_hash`` mismatch; a MEETING tick with no meeting row; a
    meeting ``state_hash_before`` / ``state_hash_after`` mismatch; a recorded
    action whose actor is missing or not alive in the pre-advance state; and a
    crew witness that lands in neither the co-present nor the one-hop census.
    """


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base, matching the report-schema convention."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class KillWitnessDensityRow(_FrozenModel):
    """One recorded kill's witness-density census (Fold 1).

    ``co_present_crew`` / ``one_hop_crew`` are the counts of living, non-vented
    CREWMATEs (excluding the victim) in the kill room / an adjacent room in the
    pre-advance decision state; ``crew_witnessed`` is the engine's crew-witness
    bit for the same kill.
    """

    seed: int
    tick: int
    room: RoomId
    killer: PlayerId
    victim: PlayerId
    co_present_crew: int
    one_hop_crew: int
    crew_witnessed: bool


class ActionEntropyBucketCell(_FrozenModel):
    """One side's pooled action-kind distribution within one coarse-state bucket."""

    decisions: int
    action_kinds: Mapping[str, int]
    entropy: float


class ActionEntropyCells(_FrozenModel):
    """One side's action-stream behavioral-entropy cells (Fold 2)."""

    agents: int
    decisions: int
    mean_conditional_entropy: float | None
    mean_unconditional_entropy: float | None
    buckets: Mapping[str, ActionEntropyBucketCell]


class KillCraftReport(_FrozenModel):
    """Set-level kill-craft result (Task 18.2): Fold 1 + Fold 2 over a replay set."""

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    # -- Fold 1: kill-timing vs witness density --
    kills_total: int
    crew_witnessed_kills: int
    co_present_histogram: Mapping[int, int]
    one_hop_histogram: Mapping[int, int]
    mean_co_present_witnessed: float | None
    mean_co_present_unwitnessed: float | None
    mean_one_hop_witnessed: float | None
    mean_one_hop_unwitnessed: float | None
    witnessed_point_biserial_co_present: float | None
    witnessed_point_biserial_within_one_hop: float | None
    per_kill: tuple[KillWitnessDensityRow, ...]
    # -- Fold 2: action-stream behavioral entropy --
    entropy_by_side: Mapping[str, ActionEntropyCells]


# A per (seed, player) bucket -> kind -> count structure.
_AgentBucketCounts = dict[str, dict[str, int]]


@dataclass
class _GameWalk:
    """The kill-craft reconstruction of one recorded game.

    ``kills`` are the per-kill census rows in file order; ``agent_counts`` maps
    each living player to its ``bucket -> kind -> count`` action-stream tally.
    """

    kills: list[KillWitnessDensityRow] = field(default_factory=list)
    agent_counts: dict[PlayerId, _AgentBucketCounts] = field(default_factory=dict)


def compute_kill_craft_report(sample_dir: Path) -> KillCraftReport:
    """Compute the kill-craft report over one committed replay set (Task 18.2).

    Pure + offline: resolve the roster, recover per-seed role ground truth by
    re-seeding, walk every committed game (re-seed + ``advance_tick`` + verify
    every ``state_hash`` + apply meetings), and fold the two kill-craft measures.
    Fails loud (:class:`KillCraftReconstructionError`) on any reconstruction
    disagreement — never silently under-measures.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    seeds = seeds_on_disk(sample_dir)

    per_kill: list[KillWitnessDensityRow] = []
    # Keyed (seed, player) so the same "p-1" in different games stays distinct.
    per_agent_counts: dict[tuple[int, PlayerId], _AgentBucketCounts] = {}
    for seed in seeds:
        roles = per_seed_roles[seed]
        walk = _walk_game(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=roles,
            game_map=game_map,
        )
        per_kill.extend(walk.kills)
        for pid, buckets in walk.agent_counts.items():
            per_agent_counts[(seed, pid)] = buckets

    fold1 = _fold1_cells(per_kill)
    entropy_by_side = _entropy_by_side(per_agent_counts, per_seed_roles)

    return KillCraftReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        kills_total=fold1.kills_total,
        crew_witnessed_kills=fold1.crew_witnessed_kills,
        co_present_histogram=fold1.co_present_histogram,
        one_hop_histogram=fold1.one_hop_histogram,
        mean_co_present_witnessed=fold1.mean_co_present_witnessed,
        mean_co_present_unwitnessed=fold1.mean_co_present_unwitnessed,
        mean_one_hop_witnessed=fold1.mean_one_hop_witnessed,
        mean_one_hop_unwitnessed=fold1.mean_one_hop_unwitnessed,
        witnessed_point_biserial_co_present=fold1.witnessed_point_biserial_co_present,
        witnessed_point_biserial_within_one_hop=(
            fold1.witnessed_point_biserial_within_one_hop
        ),
        per_kill=tuple(per_kill),
        entropy_by_side=entropy_by_side,
    )


# --------------------------------------------------------------------------- #
# The reconstruction walk (mirrors watchability._reconstruct_game_kills +      #
# funnel._walk_game; see the module docstring's mirror/duplication note).      #
# --------------------------------------------------------------------------- #


def _deserialize_actions(raw_actions: Sequence[Mapping[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _walk_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> _GameWalk:
    """Re-seed + replay one game, folding both kill-craft measures per tick."""

    game_id = f"headless-seed-{seed}"
    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    walk = _GameWalk()
    for entry in tick_entries:
        # The pre-advance decision state: the recorded actions were decided here,
        # and it is the census frame for both folds (see the docstring).
        pre_players = state.players
        pre_cooldowns = state.cooldowns

        _fold_entropy(
            entry=entry,
            game_id=game_id,
            pre_players=pre_players,
            pre_cooldowns=pre_cooldowns,
            agent_counts=walk.agent_counts,
        )

        actions = _deserialize_actions(entry.actions)
        state, events = advance_tick(state, actions, game_map=game_map)
        actual = _state_hash(state)
        if actual != entry.state_hash:
            raise KillCraftReconstructionError(
                f"{game_id}: tick {entry.tick} reconstructed {actual!r} != recorded "
                f"{entry.state_hash!r} (roster mismatch or engine non-determinism)"
            )

        for event in events:
            if isinstance(event, KilledEvent):
                walk.kills.append(_kill_row(seed, event, pre_players, roles, game_map))

        if state.phase == "GAME_OVER":
            break
        if state.phase != "MEETING":
            continue

        meeting_entry = meeting_by_tick.get(entry.tick)
        if meeting_entry is None:
            raise KillCraftReconstructionError(
                f"{game_id}: tick {entry.tick} entered MEETING but the replay "
                "carries no meeting row for that tick (partial recording or "
                "drifted meeting tick) — refusing to silently under-measure"
            )
        if meeting_entry.state_hash_before != actual:
            raise KillCraftReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} recorded state_hash_before "
                f"{meeting_entry.state_hash_before!r} != reconstructed pre-meeting "
                f"state {actual!r}"
            )

        body_id = next(
            (e.body_id for e in events if isinstance(e, MeetingTriggeredEvent)), None
        )
        result = MeetingResult(
            meeting_id=meeting_entry.meeting_id,
            triggered_by=meeting_entry.triggered_by,
            trigger_tick=meeting_entry.tick,
            outcome=meeting_entry.outcome,
            ejected_player_id=meeting_entry.ejected_player_id,
            ballots=meeting_entry.ballots,
            contradictions=meeting_entry.contradictions,
            transcript=meeting_entry.transcript,
        )
        state, _post_events = apply_meeting_result(
            state, result, game_map=game_map, triggering_body_id=body_id
        )
        after = _state_hash(state)
        if after != meeting_entry.state_hash_after:
            raise KillCraftReconstructionError(
                f"{game_id}: meeting at tick {entry.tick} reconstructed {after!r} != "
                f"recorded {meeting_entry.state_hash_after!r}"
            )
        if state.phase == "GAME_OVER":
            break

    return walk


def _fold_entropy(
    *,
    entry: ReplayEntry,
    game_id: str,
    pre_players: Mapping[PlayerId, PlayerState],
    pre_cooldowns: Mapping[PlayerId, int],
    agent_counts: dict[PlayerId, _AgentBucketCounts],
) -> None:
    """Fold each recorded action into its ``bucket -> kind`` tally (Fold 2).

    Reads the raw ``actor`` / ``type`` off the recorded action dict (before
    deserialization) and buckets by the actor's pre-advance coarse state. Raises
    on an action whose actor is missing or not alive in the pre-advance state.
    """

    for raw in entry.actions:
        actor: PlayerId = raw["actor"]
        kind: str = raw["type"]
        player = pre_players.get(actor)
        if player is None or not player.alive:
            raise KillCraftReconstructionError(
                f"{game_id}: tick {entry.tick} recorded an action for actor "
                f"{actor!r} that is missing or not alive in the pre-advance state"
            )
        occupancy = sum(
            1
            for other in pre_players.values()
            if other.alive and not other.in_vent and other.room == player.room
        )
        bucket = f"{_cooldown_state(actor, pre_cooldowns)}|{_occupancy_band(occupancy)}"
        buckets = agent_counts.setdefault(actor, {})
        kinds = buckets.setdefault(bucket, {})
        kinds[kind] = kinds.get(kind, 0) + 1


def _occupancy_band(occupancy: int) -> str:
    if occupancy <= _SOLO_MAX:
        return "solo"
    if occupancy == _PAIR:
        return "pair"
    return "crowd"


def _cooldown_state(actor: PlayerId, cooldowns: Mapping[PlayerId, int]) -> str:
    """Byte-mechanical cooldown state from dict membership (never from role)."""

    if actor not in cooldowns:
        return "none"
    return "ready" if cooldowns[actor] == 0 else "cooling"


def _kill_row(
    seed: int,
    event: KilledEvent,
    pre_players: Mapping[PlayerId, PlayerState],
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> KillWitnessDensityRow:
    """The witness-density census for one kill from the pre-advance snapshot.

    Enforces the ⊆ agreement guarantee: every crew witness on the event must be
    co-present or one hop away in the pre-advance census, else the census would
    not agree with the engine walk's per-tick state.
    """

    neighbors = frozenset(game_map.room_neighbors(event.room))
    co_present: set[PlayerId] = set()
    one_hop: set[PlayerId] = set()
    for pid, player in pre_players.items():
        if roles.get(pid) != "CREWMATE":
            continue
        if not player.alive or player.in_vent or pid == event.target:
            continue
        if player.room == event.room:
            co_present.add(pid)
        elif player.room in neighbors:
            one_hop.add(pid)

    for witness in event.witnesses:
        if roles.get(witness) != "CREWMATE":
            continue
        if witness not in co_present and witness not in one_hop:
            raise KillCraftReconstructionError(
                f"headless-seed-{seed}: kill at tick {event.tick} in {event.room!r}: "
                f"crew witness {witness!r} (pre-advance room "
                f"{pre_players[witness].room!r}) is neither co-present nor one hop "
                "away — the census disagrees with the engine walk"
            )

    return KillWitnessDensityRow(
        seed=seed,
        tick=event.tick,
        room=event.room,
        killer=event.actor,
        victim=event.target,
        co_present_crew=len(co_present),
        one_hop_crew=len(one_hop),
        crew_witnessed=any(roles.get(w) == "CREWMATE" for w in event.witnesses),
    )


# --------------------------------------------------------------------------- #
# Fold 1 aggregation — witness-density cells + point-biserial correlations.     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Fold1Cells:
    """The Fold-1 aggregate cells (typed carrier for the report constructor)."""

    kills_total: int
    crew_witnessed_kills: int
    co_present_histogram: dict[int, int]
    one_hop_histogram: dict[int, int]
    mean_co_present_witnessed: float | None
    mean_co_present_unwitnessed: float | None
    mean_one_hop_witnessed: float | None
    mean_one_hop_unwitnessed: float | None
    witnessed_point_biserial_co_present: float | None
    witnessed_point_biserial_within_one_hop: float | None


def _fold1_cells(per_kill: list[KillWitnessDensityRow]) -> _Fold1Cells:
    """The Fold-1 aggregate cells over the per-kill rows (in collection order)."""

    witnessed = [row for row in per_kill if row.crew_witnessed]
    unwitnessed = [row for row in per_kill if not row.crew_witnessed]
    ys = [1.0 if row.crew_witnessed else 0.0 for row in per_kill]
    co_present = [float(row.co_present_crew) for row in per_kill]
    within_one_hop = [float(row.co_present_crew + row.one_hop_crew) for row in per_kill]

    return _Fold1Cells(
        kills_total=len(per_kill),
        crew_witnessed_kills=len(witnessed),
        co_present_histogram=_histogram(row.co_present_crew for row in per_kill),
        one_hop_histogram=_histogram(row.one_hop_crew for row in per_kill),
        mean_co_present_witnessed=_mean_or_none(
            [float(row.co_present_crew) for row in witnessed]
        ),
        mean_co_present_unwitnessed=_mean_or_none(
            [float(row.co_present_crew) for row in unwitnessed]
        ),
        mean_one_hop_witnessed=_mean_or_none(
            [float(row.one_hop_crew) for row in witnessed]
        ),
        mean_one_hop_unwitnessed=_mean_or_none(
            [float(row.one_hop_crew) for row in unwitnessed]
        ),
        witnessed_point_biserial_co_present=_pearson(co_present, ys),
        witnessed_point_biserial_within_one_hop=_pearson(within_one_hop, ys),
    )


def _histogram(values: Iterable[int]) -> dict[int, int]:
    """Count occurrences of each integer value, keys sorted ascending."""

    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return {key: counts[key] for key in sorted(counts)}


def _mean_or_none(values: Sequence[float]) -> float | None:
    """Mean over ``values`` in their given (fixed) order; ``None`` when empty."""

    if not values:
        return None
    total = 0.0
    for value in values:
        total += value
    return total / len(values)


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Pearson correlation, summed in fixed order; ``None`` on zero variance/empty.

    Determinism comes from the fixed collection order of the per-kill rows (see
    the docstring); the sums below never reorder their inputs.
    """

    n = len(xs)
    if n == 0:
        return None
    mean_x = _mean_or_none(xs)
    mean_y = _mean_or_none(ys)
    assert mean_x is not None and mean_y is not None  # n > 0
    s_xy = 0.0
    s_xx = 0.0
    s_yy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mean_x
        dy = y - mean_y
        s_xy += dx * dy
        s_xx += dx * dx
        s_yy += dy * dy
    if s_xx == 0.0 or s_yy == 0.0:
        return None
    return s_xy / math.sqrt(s_xx * s_yy)


# --------------------------------------------------------------------------- #
# Fold 2 aggregation — per-side action-stream entropy cells.                    #
# --------------------------------------------------------------------------- #


def _entropy_by_side(
    per_agent_counts: Mapping[tuple[int, PlayerId], _AgentBucketCounts],
    per_seed_roles: Mapping[int, Mapping[PlayerId, Role]],
) -> dict[str, ActionEntropyCells]:
    """Aggregate the per-agent action tallies into per-side entropy cells."""

    cells: dict[str, ActionEntropyCells] = {}
    for side in ("CREWMATE", "IMPOSTOR"):  # sorted keys
        agent_keys = sorted(
            key
            for key, buckets in per_agent_counts.items()
            if per_seed_roles[key[0]].get(key[1]) == side
            and _total_decisions(buckets) >= 1
        )
        conditional = [_conditional_entropy(per_agent_counts[k]) for k in agent_keys]
        unconditional = [
            _shannon_entropy(_pool_kinds(per_agent_counts[k])) for k in agent_keys
        ]
        cells[side] = ActionEntropyCells(
            agents=len(agent_keys),
            decisions=sum(_total_decisions(per_agent_counts[k]) for k in agent_keys),
            mean_conditional_entropy=_mean_or_none(conditional),
            mean_unconditional_entropy=_mean_or_none(unconditional),
            buckets=_side_bucket_cells(per_agent_counts[k] for k in agent_keys),
        )
    return cells


def _side_bucket_cells(
    agent_bucket_counts: Iterable[_AgentBucketCounts],
) -> dict[str, ActionEntropyBucketCell]:
    """Pool every agent's per-bucket kind counts into one cell per bucket (sorted)."""

    pooled: dict[str, dict[str, int]] = {}
    for buckets in agent_bucket_counts:
        for bucket in sorted(buckets):
            destination = pooled.setdefault(bucket, {})
            for kind in sorted(buckets[bucket]):
                destination[kind] = destination.get(kind, 0) + buckets[bucket][kind]

    cells: dict[str, ActionEntropyBucketCell] = {}
    for bucket in sorted(pooled):
        kinds = pooled[bucket]
        cells[bucket] = ActionEntropyBucketCell(
            decisions=sum(kinds.values()),
            action_kinds={kind: kinds[kind] for kind in sorted(kinds)},
            entropy=_shannon_entropy(kinds),
        )
    return cells


def _total_decisions(buckets: Mapping[str, Mapping[str, int]]) -> int:
    return sum(sum(kinds.values()) for kinds in buckets.values())


def _pool_kinds(buckets: Mapping[str, Mapping[str, int]]) -> dict[str, int]:
    """Pool an agent's kind counts across all its buckets (sorted iteration)."""

    pooled: dict[str, int] = {}
    for bucket in sorted(buckets):
        for kind in sorted(buckets[bucket]):
            pooled[kind] = pooled.get(kind, 0) + buckets[bucket][kind]
    return pooled


def _conditional_entropy(buckets: Mapping[str, Mapping[str, int]]) -> float:
    """H(kind | bucket) in bits: bucket-weighted mean of per-bucket kind entropy."""

    total = _total_decisions(buckets)
    if total == 0:
        return 0.0
    entropy = 0.0
    for bucket in sorted(buckets):
        kinds = buckets[bucket]
        n_bucket = sum(kinds.values())
        if n_bucket == 0:
            continue
        entropy += (n_bucket / total) * _shannon_entropy(kinds)
    return entropy


def _shannon_entropy(counts: Mapping[str, int]) -> float:
    """Shannon entropy (bits) of a kind distribution, summed over SORTED kinds."""

    total = sum(counts.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for kind in sorted(counts):
        count = counts[kind]
        if count == 0:
            continue
        probability = count / total
        entropy -= probability * math.log2(probability)
    return entropy


__all__ = [
    "ActionEntropyBucketCell",
    "ActionEntropyCells",
    "KillCraftReconstructionError",
    "KillCraftReport",
    "KillWitnessDensityRow",
    "compute_kill_craft_report",
]
