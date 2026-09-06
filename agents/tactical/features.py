"""Encoder v2 — the versioned, memory-carrying tactical feature encoder (Task 15.10).

The prior ML-spike encoder (``experiments/lab/ml_spike/core.py:60-83``) is 34-dim
and **memoryless**: a single-packet room-count vector. That is the structural
reason its behavior clone capped below FSM parity — the FSM's stalk is
history-dependent (``audits/post-phase-14-ML-planning.md`` §6.3), and a
single-packet encoder cannot represent it. This module ships the production
encoder that carries the agent's OWN memory into the feature vector.

Doctrine (all four are load-bearing and enforced by tests):

* **Firewall-legal.** Lives under ``agents/`` and imports NOTHING from
  ``engine/``. The engine-free observation schemas (``ObservationPacket`` /
  ``PublicMapView``) and the agent's own engine-free memory
  (``agents/memory/``) are the entire input surface. The ``agents ↛ engine``
  import contract plus the schema-file firewall test
  (``tests/test_firewall.py``) cover it.
* **Pure-Python inference.** No ``numpy`` / ``torch`` import anywhere — the
  whole encode → forward path is stdlib ``math`` + lists. This is the locked
  Wave-1 dependency posture (DESIGN.md-adjacent, ``tasks/phase-15.md`` locked
  decision 2): BLAS reductions are not bit-stable across machines / thread
  counts, so production inference under ``agents/`` stays pure-Python and
  ``numpy`` is confined to ``training/`` by an import-linter contract. A firewall
  test rejects a synthetic ``import numpy`` planted under ``agents/``.
* **Deterministic.** Every belief-derived value is INTEGER-QUANTIZED to a fixed
  grid (:data:`BELIEF_QUANT_LEVELS`) BEFORE it touches a feature or a comparison,
  and every roster iteration is ``sorted()`` (the repo's lexical-tie-break
  idiom). Belief suspicion / trust are floats accumulated from non-power-of-two
  deltas and ``BeliefState.known_players()`` is dict-insertion-ordered
  (``audits/post-phase-14-ML-planning.md`` §6.3 determinism hazard); quantizing
  first kills the float residue that could flip an argmax, and sorted iteration
  kills the ordering hazard. There is NO raw-float comparison in this module.
* **Total.** Every packet shape the committed corpora produce encodes without
  error: ``moved_players`` is optional (omitted from the packet JSON when empty
  — never ``[]``-assumed), an empty memory encodes to zeros, and a room id absent
  from the map's room set is skipped rather than raising.

Firewall note for the leak review (the one place role-blind observation and
role-private memory meet). The encoder reads ONLY the agent's OWN
:class:`~agents.memory.store.AgentMemory` — its own episodic sighting log (the
per-tick source of the last-seen ``(tick, room)`` ages, keyed on EVERY seen
player rather than only the ones perception minted a belief row for; the
render-time ``WorkingMemory.last_seen`` cache is merged in as a secondary
source), and its own :class:`~agents.memory.beliefs.BeliefState` suspicion /
trust. It NEVER reaches another agent's memory or private state, so a feature can
never fold in another agent's role-private information. The belief
suspicion / trust it consumes are the SAME self-held signals the crew tactical
layer already uses — ``EmergencyPacingTracker._over_gate``
(``agents/tactical/crewmate_policy.py``) reads the agent's own max suspicion over
presumed-living players against the identical
:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD` gate. This encoder
widens NOTHING beyond that self-held belief surface; any future widening must be
documented here so the leak review has one place to look. The leak-test
factory mode (``eval/leak_test.py``) scans every packet a factory-built agent
consumes, catching a leak the import-linter cannot see.

Encoder v3 widening (Task 18.22), documented here as the single leak-review
locus. The v3 subclass (:class:`TacticalFeatureEncoderV3`) appends three blocks
below the byte-identical v2 prefix, and every one stays inside the same self-held
surface:

* **meeting-history scalars** read the agent's OWN
  :class:`~agents.memory.working.MeetingHistory` — a channel fed EXCLUSIVELY from
  the ``note_meeting_concluded`` hook's PUBLIC payload (the resume tick and the
  announced ejection outcome, both facts every player at the table saw), so no
  engine-private or other-agent state crosses in (the same public footing as a
  meeting's ``dead_ids``; see :func:`agents.memory.store.record_meeting_outcome`).
* **witness slots** are computed from the agent's OWN ``packet.visible_players``
  plus its OWN ``self_state.fellow_impostor_ids`` (the identical privileged self
  channel the post-meeting belief fold already reads) — who the agent can see,
  and how many co-located NON-teammate players would witness a kill (a fellow
  impostor poses no report risk, the FSM ``co_present`` semantics) — never
  another agent's vision.
* **last-seen recency slots** re-read the SAME ``_combined_last_seen`` merge the
  v2 last-seen slots use (own episodic sightings + own render cache), only at a
  short horizon the v2 50-tick normalizer cannot resolve.

No v3 block reaches another agent's memory or any packet field the v2 encoder did
not already consume, so the firewall holds unchanged.

Weights posture (Wave 1). A learned policy's weights are serialized as
**float64-hex JSON** (:func:`weights_to_hex_json` / :func:`weights_from_hex_json`)
— an exact, lossless round-trip pinned by test, so a champion's genome
reconstructs bit-identically on the inference path. The int-quantization of
weights (as opposed to the belief-feature quantization above, which is already
integer) is a separate question deliberately DEFERRED to the PAUSE (Task 15.18):
Wave 1 ships float-hex, and only if the pause approves does an int-quantized
weight format land. :data:`ENCODER_VERSION` feeds the 15.9 tactical-policy stamp;
a layout change is only legal via an :data:`ENCODER_VERSION` bump, pinned by the
golden test.
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, Final

from agents.memory.store import AgentMemory, MemoryStore
from agents.memory.working import WorkingMemory
from agents.perception import EVENT_SAW_PLAYER, EVENT_SAW_PLAYER_MOVE
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView

# The encoder-layout version. Bumping this is the ONLY sanctioned way to change
# the feature layout (the golden test pins the layout to this version), and it
# is the ``encoder_version`` field the Task-15.9 tactical-policy provenance stamp
# records so a recorded game attributes its features to an exact encoder identity.
ENCODER_VERSION: Final[str] = "v2"

# Fixed roster-slot count for the roster-dependent feature blocks. Roster-
# dependent features (per-player belief / last-seen) need fixed-slot encoding so
# the dimension is constant across roster presets (9p2i and 4p1i share the map,
# so R is fixed; the roster differs, so unused slots zero-fill). Slots are filled
# by the known players SORTED lexically by ``player_id`` (the repo tie-break
# idiom); the canonical presets top out at 9 players (``p-1``..``p-9``), so 9
# slots cover both with no truncation.
DEFAULT_ROSTER_SLOTS: Final[int] = 9

# How many ticks back count as "recent" for the episodic-recency and last-seen
# occupancy features. A window, not the whole game, so the recency signal stays
# bounded and comparable across game lengths.
DEFAULT_RECENCY_WINDOW: Final[int] = 8

# The integer grid every unit-interval belief value is quantized to before it
# touches a feature or a comparison (the §6.3 residue-flips-argmax mitigation).
# 1000 levels = 0.001 granularity: fine enough to preserve the belief signal,
# coarse enough that the ~1e-16 float residue from summing 0.05/0.08/0.2/... never
# moves a bucket. All belief comparisons below are integer comparisons on this
# grid — there is deliberately no ``>=`` on a raw belief float anywhere here.
BELIEF_QUANT_LEVELS: Final[int] = 1000

# Normalizers keeping count / age features in ~[0, 1] without a raw-float
# comparison in the belief path (these normalize OBSERVATION counts, not beliefs).
_COOLDOWN_NORM: Final[float] = 5.0  # kill cooldown seeds to 4 (canonical_1)
_COUNT_NORM: Final[float] = 8.0  # ~roster-sized normalizer for room/visible counts
_LASTSEEN_AGE_NORM: Final[float] = 50.0  # cap for the last-seen age feature
_EVENT_COUNT_NORM: Final[float] = 32.0  # episodic-event-count normalizer

# Per-slot feature counts (documented segment sizes; the golden test pins them).
_BELIEF_FEATURES_PER_SLOT: Final[int] = 4  # suspicion, trust, over_gate, filled
_LASTSEEN_FEATURES_PER_SLOT: Final[int] = 2  # age, seen

# The fixed scalar block, in order. Named here so the golden test and the module
# both read one source of truth for the layout.
#
# ``heard_vent_use`` is a reserved zero, retaining the frozen v2/v3 layout and
# committed weights. Removing the position requires a new encoder version.
# The duplicate audible producer retired at baseline 8.
_SCALAR_FEATURE_NAMES: Final[tuple[str, ...]] = (
    "cooldown_norm",
    "has_cooldown",
    "in_vent",
    "is_impostor",
    "task_completion_percent",
    "sabotage_active",
    "sabotage_is_gating",
    "num_visible_players_norm",
    "num_visible_bodies_norm",
    "num_moved_players_norm",
    "heard_vent_use",
    "heard_sabotage_alarm",
    "known_players_norm",
    "max_suspicion",
    "count_over_gate_norm",
    "episodic_recent_norm",
    "episodic_total_norm",
)


def _clamp_unit(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def quantize_unit_interval(value: float) -> int:
    """Quantize a unit-interval float to an integer on the :data:`BELIEF_QUANT_LEVELS` grid.

    Clamps to ``[0, 1]`` first (belief scores are already clamped there, but a
    caller may pass a derived value), then rounds to the nearest grid point.
    Returns an ``int`` in ``[0, BELIEF_QUANT_LEVELS]``. This is the single
    chokepoint that turns a belief float into an integer BEFORE any comparison,
    so the encoder never compares raw belief floats (the §6.3 hazard).
    """

    return round(_clamp_unit(value) * BELIEF_QUANT_LEVELS)


# The eject gate on the quantized grid (``DEFAULT_SKIP_CONFIDENCE_THRESHOLD`` is
# 0.60; the crew's ``_over_gate`` reads suspicion against it). Comparing the
# quantized suspicion int against this quantized gate int is the over-gate test —
# an integer comparison, never a raw-float one.
_SUSPICION_GATE_QUANTUM: Final[int] = quantize_unit_interval(
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD
)


@dataclass(frozen=True)
class FeatureSegment:
    """One named, fixed-size block of the feature vector (Task 15.10 golden layout).

    The encoder's layout is the ordered tuple of these segments; their sizes sum
    to the total dimension. The golden test pins the tuple, so any layout change
    is caught unless it rides an :data:`ENCODER_VERSION` bump.
    """

    name: str
    size: int


class TacticalFeatureEncoder:
    """Encode ``(ObservationPacket, PublicMapView, AgentMemory)`` into a fixed float vector.

    Memory-carrying (the spike's memoryless encoder is the baseline): the vector
    folds the agent's own belief suspicion / trust (integer-quantized), its
    working-memory last-seen ages, and its episodic recency alongside the
    single-packet observation features. Deterministic, pure-Python, firewall-legal
    — see the module docstring for the full doctrine.

    Signature is stable per the task contract: :class:`TacticalFeatureEncoder`
    and :data:`ENCODER_VERSION` are what downstream (15.15 bake-off) imports.
    """

    # ``ClassVar`` rather than ``Final`` (Task 18.22): the v3 subclass overrides
    # this with its own version stamp, and ``Final`` forbids the override.
    # Behavior is identical -- a per-class constant read off the instance.
    version: ClassVar[str] = ENCODER_VERSION

    def __init__(
        self,
        *,
        roster_slots: int = DEFAULT_ROSTER_SLOTS,
        recency_window: int = DEFAULT_RECENCY_WINDOW,
    ) -> None:
        if roster_slots <= 0:
            raise ValueError(f"roster_slots must be positive, got {roster_slots}")
        if recency_window < 0:
            raise ValueError(
                f"recency_window must be non-negative, got {recency_window}"
            )
        self._roster_slots = roster_slots
        self._recency_window = recency_window

    @property
    def roster_slots(self) -> int:
        return self._roster_slots

    @property
    def recency_window(self) -> int:
        return self._recency_window

    def feature_layout(self, public_map: PublicMapView) -> tuple[FeatureSegment, ...]:
        """The ordered, named segment layout for ``public_map`` (Task 15.10).

        The dimension is a pure function of the map's room count and the fixed
        roster-slot count, so it is constant across the two committed roster
        presets (same map ⇒ same R). The golden test pins this tuple.
        """

        rooms = len(public_map.room_ids)
        return (
            FeatureSegment("self_room_onehot", rooms),
            FeatureSegment("visible_players_by_room", rooms),
            FeatureSegment("visible_bodies_by_room", rooms),
            FeatureSegment("lastseen_occupancy_by_room", rooms),
            FeatureSegment("scalars", len(_SCALAR_FEATURE_NAMES)),
            FeatureSegment(
                "belief_slots", self._roster_slots * _BELIEF_FEATURES_PER_SLOT
            ),
            FeatureSegment(
                "lastseen_slots", self._roster_slots * _LASTSEEN_FEATURES_PER_SLOT
            ),
        )

    def feature_dimension(self, public_map: PublicMapView) -> int:
        """Total feature-vector length for ``public_map`` (sum of segment sizes)."""

        return sum(segment.size for segment in self.feature_layout(public_map))

    def encode(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
    ) -> tuple[float, ...]:
        """Encode one decision into a fixed-length float vector.

        Total over every committed-corpus packet shape. Reads only ``packet``,
        the static ``public_map`` topology, and the agent's OWN ``memory`` — no
        engine, no other agent's state. Belief values are integer-quantized
        before use; roster iteration is sorted lexically.
        """

        rooms = sorted(public_map.room_ids)
        room_index = {room: i for i, room in enumerate(rooms)}
        num_rooms = len(rooms)

        self_room = _block(num_rooms)
        idx = room_index.get(packet.self_state.room)
        if idx is not None:
            self_room[idx] = 1.0

        players_by_room = _block(num_rooms)
        for view in packet.visible_players:
            room_idx = room_index.get(view.room)
            if room_idx is not None:
                players_by_room[room_idx] += 1.0 / _COUNT_NORM

        bodies_by_room = _block(num_rooms)
        for body in packet.visible_bodies:
            room_idx = room_index.get(body.room)
            if room_idx is not None:
                bodies_by_room[room_idx] += 1.0 / _COUNT_NORM

        # The roster the memory blocks are keyed on plus the per-tick episodic
        # last-seen map, both from the shared :func:`slot_roster` derivation (Task
        # 18.22 extracted this so the v3 slot blocks and the per-target head key on
        # the SAME lexically-sorted roster the v2 blocks do). ``episodic_last_seen``
        # is returned alongside so encode() computes it once, exactly as before.
        roster, episodic_last_seen = _roster_and_last_seen(packet, memory)
        # Per-player last-seen (tick, room), taken from the FRESHER of the per-tick
        # episodic sighting and the render-time ``WorkingMemory.last_seen`` cache
        # (the latter is only written at meeting-render time, so the episodic log
        # is what keeps the signal fresh between meetings).
        last_seen_map: dict[str, tuple[int, str]] = {}
        for player_id in roster:
            combined = _combined_last_seen(
                player_id, episodic_last_seen, memory.working
            )
            if combined is not None:
                last_seen_map[player_id] = combined

        lastseen_by_room = _block(num_rooms)
        for player_id in roster:
            seen = last_seen_map.get(player_id)
            if seen is None:
                continue
            tick, room = seen
            age = packet.tick - tick
            if 0 <= age <= self._recency_window:
                room_idx = room_index.get(room)
                if room_idx is not None:
                    lastseen_by_room[room_idx] += 1.0 / _COUNT_NORM

        scalars = self._scalar_features(packet, memory, roster)
        belief_slots, lastseen_slots = self._roster_slot_features(
            packet, roster, last_seen_map, memory
        )

        return tuple(
            self_room
            + players_by_room
            + bodies_by_room
            + lastseen_by_room
            + scalars
            + belief_slots
            + lastseen_slots
        )

    def _scalar_features(
        self,
        packet: ObservationPacket,
        memory: AgentMemory,
        roster: Sequence[str],
    ) -> list[float]:
        cooldown = packet.cooldown
        cooldown_norm = (
            0.0 if cooldown is None else _clamp_unit(float(cooldown) / _COOLDOWN_NORM)
        )
        global_state = packet.global_state
        heard_sabotage = any(
            event.kind == "sabotage_alarm" for event in packet.audible_events
        )

        # Belief aggregates — computed on the QUANTIZED grid (integers), then
        # divided back onto [0, 1] for the feature. ``count_over_gate`` is an
        # integer comparison against the quantized gate, never a raw-float ``>=``.
        max_susp_quantum = 0
        count_over_gate = 0
        for player_id in roster:
            susp_quantum = quantize_unit_interval(beliefs_suspicion(memory, player_id))
            if susp_quantum > max_susp_quantum:
                max_susp_quantum = susp_quantum
            if susp_quantum >= _SUSPICION_GATE_QUANTUM:
                count_over_gate += 1

        recent_events = memory.episodic.recent(
            since_tick=max(0, packet.tick - self._recency_window)
        )

        return [
            cooldown_norm,
            0.0 if cooldown is None else 1.0,
            1.0 if packet.self_state.in_vent else 0.0,
            1.0 if packet.self_state.role == "IMPOSTOR" else 0.0,
            _clamp_unit(float(global_state.task_completion_percent)),
            1.0 if global_state.sabotage_active else 0.0,
            1.0 if global_state.sabotage_is_gating else 0.0,
            _clamp_unit(len(packet.visible_players) / _COUNT_NORM),
            _clamp_unit(len(packet.visible_bodies) / _COUNT_NORM),
            _clamp_unit(len(packet.moved_players) / _COUNT_NORM),
            0.0,  # Reserved historical heard_vent_use position; preserve weights.
            1.0 if heard_sabotage else 0.0,
            _clamp_unit(len(roster) / self._roster_slots),
            max_susp_quantum / BELIEF_QUANT_LEVELS,
            _clamp_unit(count_over_gate / self._roster_slots),
            _clamp_unit(len(recent_events) / _EVENT_COUNT_NORM),
            _clamp_unit(len(memory.episodic) / _EVENT_COUNT_NORM),
        ]

    def _roster_slot_features(
        self,
        packet: ObservationPacket,
        roster: Sequence[str],
        last_seen_map: dict[str, tuple[int, str]],
        memory: AgentMemory,
    ) -> tuple[list[float], list[float]]:
        belief_slots: list[float] = []
        lastseen_slots: list[float] = []
        for slot in range(self._roster_slots):
            if slot < len(roster):
                player_id = roster[slot]
                susp_quantum = quantize_unit_interval(
                    beliefs_suspicion(memory, player_id)
                )
                trust_quantum = quantize_unit_interval(beliefs_trust(memory, player_id))
                belief_slots.extend(
                    (
                        susp_quantum / BELIEF_QUANT_LEVELS,
                        trust_quantum / BELIEF_QUANT_LEVELS,
                        1.0 if susp_quantum >= _SUSPICION_GATE_QUANTUM else 0.0,
                        1.0,  # filled
                    )
                )
                seen = last_seen_map.get(player_id)
                if seen is None:
                    lastseen_slots.extend((0.0, 0.0))
                else:
                    age = max(0, packet.tick - seen[0])
                    lastseen_slots.extend((_clamp_unit(age / _LASTSEEN_AGE_NORM), 1.0))
            else:
                belief_slots.extend((0.0, 0.0, 0.0, 0.0))
                lastseen_slots.extend((0.0, 0.0))
        return belief_slots, lastseen_slots


def _block(size: int) -> list[float]:
    return [0.0] * size


def _episodic_last_seen(episodic: MemoryStore) -> dict[str, tuple[int, str]]:
    """Per-player most-recent (tick, room) from the agent's OWN episodic sightings.

    Scans the agent's ``saw_player`` / ``saw_player_move`` rows — appended
    per-tick by :func:`agents.perception.ingest_packet` for every visible /
    witnessed-moving player — and keeps the latest sighting per player. Events
    are stored in non-decreasing tick order, so iterating in append order and
    overwriting leaves the freshest sighting; a ``saw_player_move`` records the
    player's CURRENT room (``to_room``). This is the per-tick source of the
    last-seen signal that ``WorkingMemory.last_seen`` only caches at render time,
    and it covers EVERY seen player, not just the ones perception minted a belief
    row for. Reads only the agent's own memory — no leak.
    """

    last_seen: dict[str, tuple[int, str]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type == EVENT_SAW_PLAYER:
            player_id = event.payload.get("player_id")
            room = event.payload.get("room")
        elif event.type == EVENT_SAW_PLAYER_MOVE:
            player_id = event.payload.get("player_id")
            room = event.payload.get("to_room")
        else:
            continue
        if isinstance(player_id, str) and isinstance(room, str):
            last_seen[player_id] = (event.tick, room)
    return last_seen


def _combined_last_seen(
    player_id: str,
    episodic_last_seen: dict[str, tuple[int, str]],
    working: WorkingMemory,
) -> tuple[int, str] | None:
    """The fresher of the episodic-derived and render-cached last-seen (tick, room).

    Consumes both the per-tick episodic sighting and the contract's
    ``WorkingMemory.last_seen`` cache, keeping whichever is more recent (the
    episodic-derived is always at least as fresh, since the cache is derived from
    the same log at render time, but merging honors both sources deterministically
    — the episodic value wins a tie).
    """

    candidates: list[tuple[int, str]] = []
    episodic = episodic_last_seen.get(player_id)
    if episodic is not None:
        candidates.append(episodic)
    cached = working.last_seen(player_id)
    if cached is not None:
        candidates.append((cached.tick, cached.room))
    if not candidates:
        return None
    return max(candidates, key=lambda entry: entry[0])


def _roster_and_last_seen(
    packet: ObservationPacket, memory: AgentMemory
) -> tuple[tuple[str, ...], dict[str, tuple[int, str]]]:
    """The lexical slot roster and the per-tick episodic last-seen map together.

    The roster the memory blocks are keyed on: every OTHER player the agent has
    memory of, sorted lexically. It is the union of belief-known players and
    players the agent has SEEN (from the per-tick episodic log), so a neutral
    player the agent merely saw — one perception never minted a belief row for —
    still gets a slot (it would otherwise be dropped, blinding the vector to
    routine movement history). The agent's OWN id is excluded: an impostor's own
    move can pass the movement-witness gate (its departure room is adjacent to
    its arrival), minting a ``saw_player_move`` row for itself — the store render
    self-suppresses for the same reason. A self belief/last-seen slot is
    meaningless (no agent suspects itself) and would skew the roster aggregates.

    Returns the ``episodic_last_seen`` map alongside the roster so a single caller
    (``encode``) derives it exactly once; :func:`slot_roster` drops it. Extracted
    at Task 18.22 so the v2 slot blocks, the v3 witness/recency slots, and the
    per-target KILL head all key on ONE roster derivation — the v2 bytes are
    unchanged because the computation is identical, only relocated.
    """

    beliefs = memory.beliefs
    episodic_last_seen = _episodic_last_seen(memory.episodic)
    roster = tuple(
        sorted(
            (set(beliefs.known_players()) | set(episodic_last_seen)) - {packet.agent_id}
        )
    )
    return roster, episodic_last_seen


def slot_roster(packet: ObservationPacket, memory: AgentMemory) -> tuple[str, ...]:
    """Lexically-sorted per-player slot roster shared by the v2/v3 slot blocks
    and the 18.22 per-target head: (belief-known ∪ episodic-seen) − self.

    The public projection of :func:`_roster_and_last_seen` (the last-seen map is
    an internal by-product). ``training.bakeoff.policy_es`` imports this to key
    the per-target KILL head on the SAME roster ordering the encoder's belief
    slots use, so a head logit for slot ``i`` scores the exact player the
    encoder's slot ``i`` describes.
    """

    return _roster_and_last_seen(packet, memory)[0]


def beliefs_suspicion(memory: AgentMemory, player_id: str) -> float:
    """The agent's own suspicion float for ``player_id`` (0.5 default when unknown)."""

    return memory.beliefs.view(player_id).suspicion


def beliefs_trust(memory: AgentMemory, player_id: str) -> float:
    """The agent's own trust float for ``player_id`` (0.5 default when unknown)."""

    return memory.beliefs.view(player_id).trust


# --------------------------------------------------------------------------- #
# Encoder v3 — the meeting-history + witness/recency widening (Task 18.22).
#
# Additive and versioned: every v3 block is APPENDED below the v2 layout, so the
# v2 vector is a strict prefix of v3 and the v2 golden bytes are untouched (only
# an ENCODER_VERSION bump legalizes a layout change, and v3 carries its own
# stamp). The three new blocks give the per-target KILL head (18.22) the signal
# the v2 encoder cannot: which meetings the agent has survived, which roster
# players are co-located witnesses of a candidate kill, and a short-horizon
# recency the v2 50-tick age normalizer cannot resolve. Every block reads only
# the agent's OWN packet + OWN memory — see the module docstring's v3 firewall
# note (the single leak-review locus).
# --------------------------------------------------------------------------- #

# The v3 encoder-layout version stamp (see :data:`ENCODER_VERSION`). A separate
# identity so a recorded game attributes v3 features to v3 and the golden test
# pins each layout to its own version.
ENCODER_VERSION_V3: Final[str] = "v3"

# The v3 meeting-history scalar block, in order. Named here so the layout has one
# source of truth (mirroring ``_SCALAR_FEATURE_NAMES`` for the v2 scalar block).
_V3_MEETING_FEATURE_NAMES: Final[tuple[str, ...]] = (
    "meetings_survived_norm",
    "meeting_ejections_norm",
    "meeting_skips_norm",
)

# Normalizer for the meeting-history counts (~meetings-per-game): keeps the
# survived / ejection / skip counts in ~[0, 1] without a raw-float comparison in
# the belief path (these normalize meeting COUNTS, not beliefs).
_MEETING_COUNT_NORM: Final[float] = 8.0

# Per-slot feature counts for the two v3 roster-slot blocks (the golden layout
# pins them, mirroring the v2 ``_BELIEF_FEATURES_PER_SLOT`` idiom).
_WITNESS_FEATURES_PER_SLOT: Final[int] = 3  # visible, co_located, witnesses_norm
_RECENCY_FEATURES_PER_SLOT: Final[int] = 1  # short-horizon recency


class TacticalFeatureEncoderV3(TacticalFeatureEncoder):
    """Encoder v2 plus the Task-18.22 meeting-history + witness/recency blocks.

    Subclasses :class:`TacticalFeatureEncoder` so the entire v2 layout and
    computation are inherited byte-for-byte: :meth:`feature_layout` and
    :meth:`encode` call ``super()`` and APPEND the three v3 blocks, so the v2
    vector is a strict prefix of the v3 vector. Same doctrine as v2 (firewall-
    legal, pure-Python, deterministic, total) — every v3 value that is
    belief/ratio-derived goes through :func:`quantize_unit_interval` on the
    :data:`BELIEF_QUANT_LEVELS` grid before it lands in the vector (the §6.3
    integer-grid discipline), and booleans are plain ``1.0`` / ``0.0``.

    The v3 blocks, in appended order:

    * **meeting_history_scalars** (3) — the agent's survived / ejection / skip
      meeting counts from its OWN ``memory.meeting_history`` channel;
    * **witness_slots** (``roster_slots`` × 3) — per lexical roster slot, whether
      the agent can currently see that player, whether it is co-located, and how
      many other visible players would witness a kill of it;
    * **lastseen_recency_slots** (``roster_slots`` × 1) — per roster slot, a
      short-horizon last-seen recency the v2 slots' 50-tick age cannot resolve.
    """

    version: ClassVar[str] = ENCODER_VERSION_V3

    def feature_layout(self, public_map: PublicMapView) -> tuple[FeatureSegment, ...]:
        """The v2 segment tuple plus the three v3 segments, in appended order.

        The v3 segments follow the full v2 layout, so the v2 prefix is unchanged
        and the total dimension is the v2 dimension plus ``3 + roster_slots * 3 +
        roster_slots * 1``. The golden test pins this tuple against the v3 stamp.
        """

        return super().feature_layout(public_map) + (
            FeatureSegment("meeting_history_scalars", len(_V3_MEETING_FEATURE_NAMES)),
            FeatureSegment(
                "witness_slots", self._roster_slots * _WITNESS_FEATURES_PER_SLOT
            ),
            FeatureSegment(
                "lastseen_recency_slots",
                self._roster_slots * _RECENCY_FEATURES_PER_SLOT,
            ),
        )

    def encode(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
    ) -> tuple[float, ...]:
        """Encode one decision into the v2 vector plus the three v3 blocks.

        The v2 vector (``super().encode``) is a strict prefix; the three v3 blocks
        are appended in layout order. Reads only ``packet``, the static
        ``public_map``, and the agent's OWN ``memory`` — no engine, no other
        agent's state (the meeting-history channel is hook-fed PUBLIC facts). The
        roster is re-derived from the shared :func:`_roster_and_last_seen`, so the
        v3 slots key on the SAME lexical roster as the inherited v2 slot blocks.
        """

        base = super().encode(packet, public_map, memory)
        roster, episodic_last_seen = _roster_and_last_seen(packet, memory)

        meeting_scalars = self._meeting_history_scalars(memory)
        witness_slots = self._witness_slots(packet, roster)
        recency_slots = self._lastseen_recency_slots(
            packet, roster, episodic_last_seen, memory
        )
        return base + tuple(meeting_scalars + witness_slots + recency_slots)

    def _meeting_history_scalars(self, memory: AgentMemory) -> list[float]:
        """The three meeting-history counts, each normalized + quantized (18.22).

        Reads the agent's OWN ``memory.meeting_history``. The hook reaches LIVING
        agents only, so ``len(history)`` IS the number of meetings this agent
        survived; the ejection / skip counts partition those by outcome. Each is
        normalized by :data:`_MEETING_COUNT_NORM` and quantized onto the
        :data:`BELIEF_QUANT_LEVELS` grid (the §6.3 integer-grid discipline).
        """

        history = memory.meeting_history
        return [
            quantize_unit_interval(len(history) / _MEETING_COUNT_NORM)
            / BELIEF_QUANT_LEVELS,
            quantize_unit_interval(history.ejection_count() / _MEETING_COUNT_NORM)
            / BELIEF_QUANT_LEVELS,
            quantize_unit_interval(history.skip_count() / _MEETING_COUNT_NORM)
            / BELIEF_QUANT_LEVELS,
        ]

    def _witness_slots(
        self, packet: ObservationPacket, roster: Sequence[str]
    ) -> list[float]:
        """Per roster slot: ``(visible, co_located, witnesses_norm)`` (18.22).

        From the agent's OWN packet only. A slot player is ``visible`` when it is
        in ``packet.visible_players``; ``co_located`` when its room is the agent's
        own room; ``witnesses`` is the count of OTHER visible players in that same
        room who would witness a kill of the slot player — self is never in
        ``visible_players``, and the agent's own fellow impostors are excluded
        (``packet.self_state.fellow_impostor_ids``, the identical privileged
        self channel the post-meeting belief fold reads: a teammate poses no
        report/testimony risk, matching the FSM ``co_present`` kill-gate
        semantics the head refines) — normalized by :data:`_COUNT_NORM` and
        quantized onto the grid. A slot player the agent cannot see, and every
        slot past the roster, zero-fills ``(0.0, 0.0, 0.0)``.
        """

        # First occurrence wins (ids are unique in practice); the room a slot
        # player is visible in.
        visible_room: dict[str, str] = {}
        for view in packet.visible_players:
            if view.id not in visible_room:
                visible_room[view.id] = view.room
        self_room = packet.self_state.room
        fellows = frozenset(packet.self_state.fellow_impostor_ids)

        slots: list[float] = []
        for slot in range(self._roster_slots):
            if slot < len(roster):
                player_id = roster[slot]
                room = visible_room.get(player_id)
                if room is None:
                    slots.extend((0.0, 0.0, 0.0))
                else:
                    co_located = 1.0 if room == self_room else 0.0
                    witnesses = sum(
                        1
                        for view in packet.visible_players
                        if view.room == room
                        and view.id != player_id
                        and view.id not in fellows
                    )
                    witnesses_norm = (
                        quantize_unit_interval(witnesses / _COUNT_NORM)
                        / BELIEF_QUANT_LEVELS
                    )
                    slots.extend((1.0, co_located, witnesses_norm))
            else:
                slots.extend((0.0, 0.0, 0.0))
        return slots

    def _lastseen_recency_slots(
        self,
        packet: ObservationPacket,
        roster: Sequence[str],
        episodic_last_seen: dict[str, tuple[int, str]],
        memory: AgentMemory,
    ) -> list[float]:
        """Per roster slot: one short-horizon last-seen recency value (18.22).

        The short-horizon signal the v2 slots' 50-tick-normalized age cannot
        resolve. Source is the SAME :func:`_combined_last_seen` merge v2 uses (own
        episodic sighting + own render cache). Unseen zero-fills. For a slot seen
        at tick ``t``: ``age = max(0, packet.tick - t)``; when the recency window
        is non-positive or ``age`` exceeds it the value is ``0.0`` (out of
        horizon), else ``(window - age) / window`` quantized onto the grid — 1.0
        at ``age == 0`` decaying to the window edge. Slots past the roster
        zero-fill.
        """

        window = self._recency_window
        slots: list[float] = []
        for slot in range(self._roster_slots):
            value = 0.0
            if slot < len(roster) and window > 0:
                player_id = roster[slot]
                combined = _combined_last_seen(
                    player_id, episodic_last_seen, memory.working
                )
                if combined is not None:
                    age = max(0, packet.tick - combined[0])
                    if age <= window:
                        value = (
                            quantize_unit_interval((window - age) / window)
                            / BELIEF_QUANT_LEVELS
                        )
            slots.append(value)
        return slots


def encode_features_v3(
    packet: ObservationPacket,
    public_map: PublicMapView,
    memory: AgentMemory,
    *,
    roster_slots: int = DEFAULT_ROSTER_SLOTS,
    recency_window: int = DEFAULT_RECENCY_WINDOW,
) -> tuple[float, ...]:
    """Encode one decision with :class:`TacticalFeatureEncoderV3` (Task 18.22).

    Additive and versioned: the returned vector is the v2 vector (byte-identical
    prefix) followed by the three v3 blocks (meeting-history scalars, witness
    slots, last-seen recency slots). Firewall doctrine is the v2 doctrine
    unchanged — it reads ONLY the agent's own ``packet`` and own ``memory``, and
    the meeting-history channel it consumes is fed exclusively from the
    ``note_meeting_concluded`` hook's PUBLIC payload (the module docstring's v3
    firewall note is the single leak-review locus). Every belief/ratio-derived v3
    value is quantized onto the :data:`BELIEF_QUANT_LEVELS` integer grid (the §6.3
    residue-flips-argmax discipline) before it lands in the vector.

    Constructs a fresh encoder per call (no shared state; the encoder is a thin
    stateless wrapper over ``roster_slots`` / ``recency_window``), mirroring how
    a caller would build :class:`TacticalFeatureEncoder` directly.
    """

    encoder = TacticalFeatureEncoderV3(
        roster_slots=roster_slots, recency_window=recency_window
    )
    return encoder.encode(packet, public_map, memory)


# --------------------------------------------------------------------------- #
# Pure-Python inference kernel + Wave-1 float64-hex weight serialization.
#
# A learned tactical policy composes this encoder with a small MLP head; the head
# lives here (under ``agents/``) so the WHOLE inference path is pure-Python and
# firewall-legal, ready to deploy without touching ``training/``. The genome is a
# flat list of float64 weights, serialized as float-hex JSON (Wave-1 posture; the
# int-quantized format is a PAUSE decision).
# --------------------------------------------------------------------------- #


def mlp_genome_length(*, input_dim: int, hidden: int, output: int) -> int:
    """Flat genome length for a one-hidden-layer MLP (W1, b1, W2, b2)."""

    return input_dim * hidden + hidden + hidden * output + output


def mlp_forward(
    genome: Sequence[float],
    features: Sequence[float],
    *,
    input_dim: int,
    hidden: int,
    output: int,
) -> tuple[float, ...]:
    """Pure-Python forward pass of a one-hidden-layer ``tanh`` MLP.

    ``genome`` is a flat ``[W1 | b1 | W2 | b2]`` of length
    :func:`mlp_genome_length`. Deterministic (fixed accumulation order, stdlib
    ``math.tanh`` only), so two runs on the same genome + features produce
    bit-identical logits — the property the determinism harness hashes.
    """

    if len(features) != input_dim:
        raise ValueError(
            f"feature vector length {len(features)} != input_dim {input_dim}"
        )
    expected = mlp_genome_length(input_dim=input_dim, hidden=hidden, output=output)
    if len(genome) != expected:
        raise ValueError(f"genome length {len(genome)} != expected {expected}")

    w2_offset = input_dim * hidden
    b1_offset = w2_offset
    w2_start = b1_offset + hidden
    b2_start = w2_start + hidden * output

    hidden_activations = [0.0] * hidden
    for j in range(hidden):
        total = genome[b1_offset + j]
        base = j * input_dim
        for i in range(input_dim):
            total += genome[base + i] * features[i]
        hidden_activations[j] = math.tanh(total)

    logits = [0.0] * output
    for k in range(output):
        total = genome[b2_start + k]
        base = w2_start + k * hidden
        for j in range(hidden):
            total += genome[base + j] * hidden_activations[j]
        logits[k] = total
    return tuple(logits)


def weights_to_hex_json(weights: Sequence[float]) -> str:
    """Serialize float64 weights to a lossless float-hex JSON string (Wave-1 posture).

    Each weight is written with :meth:`float.hex`, which is EXACT for float64, so
    :func:`weights_from_hex_json` round-trips the genome bit-for-bit. This is the
    Wave-1 weight format; the int-quantized format is a PAUSE decision (Task
    15.18) — see the module docstring.
    """

    return json.dumps([float(weight).hex() for weight in weights])


def weights_from_hex_json(data: str) -> tuple[float, ...]:
    """Deserialize a :func:`weights_to_hex_json` string back to exact float64 weights."""

    raw = json.loads(data)
    if not isinstance(raw, list):
        raise ValueError("weights JSON must be a list of float-hex strings")
    return tuple(float.fromhex(item) for item in raw)


__all__ = [
    "BELIEF_QUANT_LEVELS",
    "DEFAULT_RECENCY_WINDOW",
    "DEFAULT_ROSTER_SLOTS",
    "ENCODER_VERSION",
    "ENCODER_VERSION_V3",
    "FeatureSegment",
    "TacticalFeatureEncoder",
    "TacticalFeatureEncoderV3",
    "beliefs_suspicion",
    "beliefs_trust",
    "encode_features_v3",
    "mlp_forward",
    "mlp_genome_length",
    "quantize_unit_interval",
    "slot_roster",
    "weights_from_hex_json",
    "weights_to_hex_json",
]
