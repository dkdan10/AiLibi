"""The Phase-20 offline counterfactual: the whole lever slate over frozen bytes.

One command, one shipping slate, one table. It re-runs the eight Phase-20
detector and render levers over the reconstructed inputs of the 300 committed
games and prints, per set and pooled, every pre-registered cell an instrument can
compute without spending the record
(``audits/audit-phase-20-preregistration.md`` §8).

Three columns, in this order, because the third is only worth reading once the
first two agree:

* **RECORDED-OFF** — the committed instrument (``eval.evidence_honesty``,
  ``eval.solvability``) reading the recorded bytes. This IS the ratified §3
  baseline.
* **RECONSTRUCTED-OFF** — the same cell folded from re-derived inputs with all
  eight levers OFF. A cell whose two OFF readings disagree prints no ON value:
  the counterfactual would be measuring the reconstruction, not the lever.
* **ON** — the same reconstruction with all eight levers ON, toggled through each
  resolver's ``env`` parameter. The process environment is never written.

Detector-and-render only, by construction. The scripted-mover repair (Task 20.32)
is a declared co-intervention of the record and is deliberately absent here, which
is exactly what makes this table a clean attribution instrument (synthesis ruling
R3): the model, the mover, the seeds and the recorded bytes are held constant and
only the detector and render rules move.

Cell definitions are imported, never re-stated. Every fold below routes through
``eval.evidence_honesty``'s own fold functions, so a cell this table prints is the
cell that module defines; the reconstruction supplies inputs, not meanings.

Scope, stated before any number:

* **I-11 is excluded.** The ratified cells are the frozen
  ``eval.evidence_honesty.RATIFIED_I11_CELLS``; the policy that produced them left
  the tree at the mover repair, so a live-policy fold reports mismatches by
  construction. No ratified bar rides I-11 (memo §11, 2026-08-20).
* **I-1 and I-2 carry no ON column.** A flag that stops being minted is not a vote
  that changes, and the false-self-placement cell measures what the model says
  once it can read a trail it never had. §8 names both as not predictable offline.
* **I-3 is ``sole_flag_precision.per_victim_precision``** (every STRONG flag on the
  ejectee is ``alibi_vs_sighting``, however many), not the exactly-one-flag
  companion; **I-6 is ``adjacent_room_flags.adjacent``** with the un-gated
  ``adjacent_any_gap`` reported beside it, never in place of it (memo §10).

Purity: offline, no network, no LLM call, no replay written, no ``os.environ``
assignment.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal, TextIO

# Allow `uv run python scripts/counterfactual_phase20.py ...` to find top-level
# packages (mirrors scripts/measure_baseline.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agents.memory.episodic import MemoryStore  # noqa: E402
from agents.memory.store import (  # noqa: E402
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    render_for_prompt,
)
from agents.memory.beliefs import OBSERVED_KILL_ACTION, OBSERVED_VENT_ACTION  # noqa: E402
from agents.perception import (  # noqa: E402
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from api.replay_loader import _parse_turn_annotations  # noqa: E402
from engine.entities import PlayerId, Role, RoomId  # noqa: E402
from engine.events import TaskCompletedEvent  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from eval.deduction_metrics import WilsonRateCell, classify_flag  # noqa: E402
from eval.evidence_honesty import (  # noqa: E402
    _MARKER_PREFIXES,
    _RENDERED_ROW,
    _TESTIMONY_ROW,
    _WALK_CONFIG,
    EvidenceHonestyReport,
    _fold_completion_rows,
    _fold_flags,
    _MeetingFacts,
    _report,
    _room_distances,
    _SelfLocations,
    _Tallies,
    compute_evidence_honesty,
)
from eval.replay_walk import (  # noqa: E402
    MeetingApplied,
    MeetingOpened,
    TickAdvanced,
    TickOpened,
    walk_replay,
)
from eval.solvability import SolvabilityReport, compute_solvability_report  # noqa: E402
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk  # noqa: E402
from meetings.manager import derive_reported_testimony, extract_belief_evidence  # noqa: E402
from meetings.schemas import (  # noqa: E402
    ContradictionRef,
    MoveWitnessRecord,
    SightingRecord,
    VentWitnessRecord,
)
from meetings.transcript import detect_contradictions, is_weak_contradiction  # noqa: E402
from observation.service import ObservationService  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    LLMCallRecord,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    env_var_for_lever,
    fold_meeting_outcome_into_memories,
    substrate_flag_snapshot,
)

# The four committed sets, in the record order §9 fixes.
CANONICAL_SETS: Final[tuple[str, ...]] = (
    "samples/9p2i",
    "ml_corpus/9p2i",
    "samples/4p1i",
    "ml_corpus/4p1i",
)

# The one lever the Phase-20 slate does NOT turn on: the impostor-answer template
# arm, which §9 pins OFF for the record.
NON_PHASE_20_LEVER: Final[str] = "impostor_roll_call"

# The eight Phase-20 levers, read off the substrate registry rather than listed
# here: a lever registered at 20.33 and forgotten here would silently drop out of
# the slate this memo predicts for.
PHASE_20_LEVERS: Final[tuple[str, ...]] = tuple(
    key for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS if key != NON_PHASE_20_LEVER
)

# The three levers that move a flag. The other five move a rendered line.
DETECTOR_LEVERS: Final[tuple[str, ...]] = (
    "movement_claim_shape",
    "grounded_prosecution",
    "map_aware_arbitration",
)

SLATE_OFF: Final[Mapping[str, str]] = MappingProxyType({})
SLATE_ON: Final[Mapping[str, str]] = MappingProxyType(
    {env_var_for_lever(key): "1" for key in PHASE_20_LEVERS}
)

# The render census's ON slate, and the reason it is not the full one.
# ``meeting_outcome_memory`` ON re-tags a rendered testimony frame ``[meeting N]``
# (agents/memory/store.py::_render_reported_testimony), which the instrument's
# OFF-shaped ``_TESTIMONY_ROW`` / ``_RENDERED_ROW`` patterns do not match. Counting
# that render with a widened pattern would put a second definition of the render
# cell in this script, so the census runs on the seven-lever slate the committed
# patterns can read and the full-slate figure is declared unmeasurable and ROUTED
# rather than recounted here.
RENDER_CENSUS_SLATE: Final[Mapping[str, str]] = MappingProxyType(
    {
        env_var_for_lever(key): "1"
        for key in PHASE_20_LEVERS
        if key != "meeting_outcome_memory"
    }
)
RENDER_CENSUS_SLATE_LABEL: Final[str] = "seven-ON (less meeting_outcome_memory)"
FULL_SLATE_LABEL: Final[str] = "all-eight-ON"

# The leave-one-out legs: the full slate with one detector lever withheld. A
# render lever takes no leg here — it moves no flag, so its leave-one-out on every
# flag cell is the slate itself.
LEAVE_ONE_OUT: Final[Mapping[str, Mapping[str, str]]] = MappingProxyType(
    {
        f"-{lever}": MappingProxyType(
            {env_var_for_lever(key): "1" for key in PHASE_20_LEVERS if key != lever}
        )
        for lever in DETECTOR_LEVERS
    }
)

# The committed 19.14 non-direct innocent split the 79-meeting enumeration must
# reproduce before any surviving-flag number is believed
# (tests/eval/test_deduction_metrics.py:179-182, :257, :296-297, :310-311).
COMMITTED_INNOCENT_EJECTIONS: Final[Mapping[str, int]] = MappingProxyType(
    {
        "samples/9p2i": 23,
        "ml_corpus/9p2i": 54,
        "samples/4p1i": 2,
        "ml_corpus/4p1i": 0,
    }
)

Population = Literal["flag", "turn", "render", "prompt", "oracle"]

# How a cell's RECONSTRUCTED-OFF reading relates to its RECORDED-OFF one, and
# therefore whether an ON column may be printed for it.
#
# ``flag`` / ``turn``   the reconstruction reproduces the recorded artefact
#                       exactly; the two OFF readings must be EQUAL or the ON
#                       column is withheld and the run fails.
# ``render``            the recorded population is LLM calls and the reconstructed
#                       one is meeting-agent memory renders; the two cannot be
#                       equal by construction, so the OFF readings are reported
#                       side by side and the ON column rides the reconstruction.
# ``prompt``            the cell reads whole prompt bytes, which re-render only
#                       under a Jinja prompt set; the default set at HEAD is not
#                       the set the bytes were recorded with, so the cell is
#                       PROMPT-SET-COUPLED: RECORDED only, no ON.
# ``oracle``            the cell's inputs (the engine's kill/visibility record and
#                       the recorded ballots) are untouched by every lever, so ON
#                       equals OFF by construction and the instrument is the only
#                       reading needed.
_EXACT_POPULATIONS: Final[frozenset[str]] = frozenset({"flag", "turn"})


class SlateFlagCounts:
    """Mutable per-leg tallies. One instance per lever slate per set."""

    def __init__(self) -> None:
        self.tallies = _Tallies()
        # The innocent-ejection census: how many of the 79 still carry a STRONG
        # flag naming the ejectee, and how many lose a kind-sole conviction.
        self.innocent_any_strong = 0
        self.innocent_sole_kind = 0
        self.strong_alibi_vs_sighting = 0


@dataclass
class _SetWalk:
    """Everything one committed set's single walk produced."""

    set_name: str
    games: int
    meetings: int
    off_flags_match_recorded: int
    innocent_ejections: int
    legs: dict[str, SlateFlagCounts] = field(default_factory=dict)
    # Turn-population cells (I-8's turn half), OFF and ON.
    turns: int = 0
    marker_turns_off: int = 0
    marker_turns_on: int = 0
    # Render-population cells (I-5 and the render census), OFF and ON.
    snapshots: int = 0
    rendered_rows_off: int = 0
    rendered_rows_on: int = 0
    testimony_rows_off: int = 0
    testimony_rows_on: int = 0
    completion_rows_off: int = 0
    completion_rows_on: int = 0
    fabricated_rows_off: int = 0
    fabricated_rows_on: int = 0
    # The render census's own ON leg: the seven-lever, pattern-readable slate.
    rendered_rows_census_on: int = 0
    testimony_rows_census_on: int = 0


@dataclass(frozen=True)
class Row:
    """One printed cell: the label, the three columns and the reading rule."""

    cell_id: str
    label: str
    population: Population
    recorded_off: tuple[int, int] | None
    reconstructed_off: tuple[int, int] | None
    on: tuple[int, int] | None
    note: str = ""
    # ``rate`` prints a percentage, ``mean`` prints rows-per-snapshot. A mean has
    # no percentage reading, and printing one would invite a nonsense comparison.
    display: Literal["rate", "mean"] = "rate"
    # The slate the ON column was computed under. Every row is the full eight
    # except the render census, which states its own.
    on_slate: str = FULL_SLATE_LABEL

    @property
    def agrees(self) -> bool:
        """Whether the two OFF readings agree well enough to print an ON."""

        if self.population not in _EXACT_POPULATIONS:
            return True
        return self.recorded_off == self.reconstructed_off

    def payload(self) -> dict[str, object]:
        """This row as JSON the record audit can consume."""

        return {
            "cell": self.cell_id,
            "label": self.label,
            "population": self.population,
            "recorded_off": list(self.recorded_off) if self.recorded_off else None,
            "reconstructed_off": (
                list(self.reconstructed_off) if self.reconstructed_off else None
            ),
            "on": list(self.on) if self.on else None,
            "off_readings_agree": self.agrees,
            "display": self.display,
            "on_slate": self.on_slate,
            "note": self.note,
        }


# --------------------------------------------------------------------------- #
# The reconstruction (one walk per game, every slate folded from it).          #
# --------------------------------------------------------------------------- #


def _sighting_channel(
    memory: MemoryStore, *, speaker: PlayerId, roles: Mapping[PlayerId, Role]
) -> tuple[SightingRecord, ...]:
    """One speaker's first-hand sightings, as the prosecution channel gets them.

    The shape ``TacticalAgent.sighting_records_for_meeting`` produces, with the
    §4.7 teammate filter ``meetings.manager`` applies when it builds the mapping:
    first-hand ``saw_player`` rows minus the incriminating actions, minus (for an
    impostor) the rows naming a fellow impostor, carrying the co-presence
    projection. Reconstruction plumbing, not a cell — its correctness is proven by
    the OFF leg reproducing the recorded flags, which is asserted per meeting.
    """

    fellows = _fellows(speaker=speaker, roles=roles)
    rows: list[tuple[str, str, int]] = []
    co_present: dict[tuple[int, str], set[str]] = {}
    for event in memory.recent(since_tick=0):
        if event.type != EVENT_SAW_PLAYER or event.provenance != PROVENANCE_OBSERVED:
            continue
        if event.payload.get("action") in (OBSERVED_VENT_ACTION, OBSERVED_KILL_ACTION):
            continue
        subject = event.payload.get("player_id")
        room = event.payload.get("room")
        if not isinstance(subject, str) or not isinstance(room, str):
            continue
        rows.append((subject, room, event.tick))
        co_present.setdefault((event.tick, room), set()).add(subject)
    return tuple(
        SightingRecord(
            subject=subject,
            room=room,
            tick=tick,
            co_present=tuple(sorted(co_present.get((tick, room), set()) - {subject})),
        )
        for subject, room, tick in rows
        if subject not in fellows
    )


def _move_channel(
    memory: MemoryStore, *, speaker: PlayerId, roles: Mapping[PlayerId, Role]
) -> tuple[MoveWitnessRecord, ...]:
    """One speaker's witnessed transitions, with the accessor's teammate guard."""

    fellows = _fellows(speaker=speaker, roles=roles)
    records: list[MoveWitnessRecord] = []
    for event in memory.recent(since_tick=0):
        if (
            event.type != EVENT_SAW_PLAYER_MOVE
            or event.provenance != PROVENANCE_OBSERVED
        ):
            continue
        subject = event.payload.get("player_id")
        if subject in fellows or subject == speaker:
            continue
        from_room = event.payload.get("from_room")
        to_room = event.payload.get("to_room")
        if (
            isinstance(subject, str)
            and isinstance(from_room, str)
            and isinstance(to_room, str)
        ):
            records.append(
                MoveWitnessRecord(
                    subject=subject,
                    from_room=from_room,
                    to_room=to_room,
                    tick=event.tick,
                )
            )
    return tuple(records)


def _vent_channel(memory: MemoryStore) -> tuple[VentWitnessRecord, ...]:
    """One speaker's witnessed vents — the channel the recorded flags used."""

    records: list[VentWitnessRecord] = []
    for event in memory.recent(since_tick=0):
        if event.type != EVENT_SAW_PLAYER or event.provenance != PROVENANCE_OBSERVED:
            continue
        if event.payload.get("action") != OBSERVED_VENT_ACTION:
            continue
        subject = event.payload.get("player_id")
        room = event.payload.get("room")
        if isinstance(subject, str) and isinstance(room, str):
            records.append(
                VentWitnessRecord(subject=subject, room=room, tick=event.tick)
            )
    return tuple(records)


def _fellows(
    *, speaker: PlayerId, roles: Mapping[PlayerId, Role]
) -> frozenset[PlayerId]:
    """The speaker's own fellow-impostor set — empty for every crewmate."""

    if roles.get(speaker) != "IMPOSTOR":
        return frozenset()
    return frozenset(
        pid for pid, role in roles.items() if role == "IMPOSTOR" and pid != speaker
    )


def _fold_meeting_both_ways(
    walk_event: MeetingApplied,
    *,
    off: Mapping[PlayerId, AgentMemory],
    on: Mapping[PlayerId, AgentMemory],
) -> None:
    """Land one applied meeting in both memory lineages, each at its own slate.

    The two lineages diverge at exactly one seam: ``meeting_outcome_memory`` keeps
    a spoken vent sighting as reported CONTENT, so the ON store carries testimony
    rows the OFF store drops. Everything else — the belief evidence, the meeting
    boundary, and the shared meeting-outcome fold — is lever-independent at write
    time and is folded identically through the same production helpers.
    """

    evidence = extract_belief_evidence(walk_event.result)
    statements = derive_reported_testimony(walk_event.result)
    for pid in sorted(walk_event.state.players):
        if not walk_event.state.players[pid].alive:
            continue
        for lineage, slate in ((off, SLATE_OFF), (on, SLATE_ON)):
            absorb_meeting_evidence(
                lineage[pid],
                accused=evidence.accused,
                corroborated=evidence.corroborated,
                contradicted=evidence.contradicted,
            )
            absorb_reported_testimony(lineage[pid], statements=statements, env=slate)
    for lineage in (off, on):
        fold_meeting_outcome_into_memories(
            walk_event.result, state=walk_event.state, memories=lineage
        )


def walk_set(sample_dir: Path, *, set_name: str) -> _SetWalk:
    """Reconstruct one committed set once and fold every lever slate from it.

    One walk per game: the observation packet is built once and ingested into both
    memory lineages, the detector is re-run per meeting on every slate, and each
    living agent's memory is rendered twice. Nothing is re-simulated and no byte on
    disk is read as anything but committed.
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
    if not seeds:
        raise SystemExit(
            f"{sample_dir}: no replay-seed-*.jsonl files found — not a replay set"
        )
    distances = _room_distances(game_map)
    walk = _SetWalk(
        set_name=set_name,
        games=len(seeds),
        meetings=0,
        off_flags_match_recorded=0,
        innocent_ejections=0,
    )
    legs: dict[str, Mapping[str, str]] = {"off": SLATE_OFF, "on": SLATE_ON}
    legs.update(LEAVE_ONE_OUT)
    walk.legs = {name: SlateFlagCounts() for name in legs}

    for seed in seeds:
        _walk_game(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            set_name=set_name,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            distances=distances,
            legs=legs,
            walk=walk,
        )
    return walk


def _walk_game(
    replay_path: Path,
    *,
    seed: int,
    set_name: str,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    legs: Mapping[str, Mapping[str, str]],
    walk: _SetWalk,
) -> None:
    """Walk one recording once and fold every slate's cells from it."""

    game_id = f"headless-seed-{seed}"
    game_map = load_canonical_map()
    off_stores = {pid: MemoryStore() for pid in roles}
    on_stores = {pid: MemoryStore() for pid in roles}
    off_memories = {pid: AgentMemory(episodic=s) for pid, s in off_stores.items()}
    on_memories = {pid: AgentMemory(episodic=s) for pid, s in on_stores.items()}
    room_at: dict[int, Mapping[PlayerId, RoomId]] = {}
    completions: dict[PlayerId, set[int]] = {pid: set() for pid in roles}
    seen_rows: dict[str, set[tuple[PlayerId, str]]] = {"off": set(), "on": set()}
    pending: list[tuple[_MeetingFacts, frozenset[PlayerId]]] = []

    audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-counterfactual-")
    service = ObservationService(
        game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
    )
    try:
        for walk_event in walk_replay(
            replay_path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=_WALK_CONFIG,
        ):
            if isinstance(walk_event, TickOpened):
                state = walk_event.state
                for pid in sorted(state.players):
                    if not state.players[pid].alive:
                        continue
                    packet = service.build_packet(
                        world_state=state,
                        agent_id=pid,
                        engine_events=walk_event.last_events,
                    )
                    ingest_packet(packet=packet, memory=off_stores[pid])
                    ingest_packet(packet=packet, memory=on_stores[pid])
            elif isinstance(walk_event, TickAdvanced):
                room_at[walk_event.entry.tick] = {
                    pid: player.room for pid, player in walk_event.state.players.items()
                }
                for event in walk_event.events:
                    if isinstance(event, TaskCompletedEvent):
                        completions[event.actor].add(event.tick)
            elif isinstance(walk_event, MeetingOpened):
                state = walk_event.state
                living = frozenset(
                    pid for pid, player in state.players.items() if player.alive
                )
                facts = _MeetingFacts(
                    entry=walk_event.entry,
                    living=living,
                    venting=frozenset(
                        pid for pid, p in state.players.items() if p.alive and p.in_vent
                    ),
                    body_triggered=walk_event.body_id is not None,
                )
                roster = frozenset(ballot.voter for ballot in walk_event.entry.ballots)
                _fold_one_meeting(
                    facts=facts,
                    roster=roster,
                    game_id=game_id,
                    roles=roles,
                    off_stores=off_stores,
                    room_at=room_at,
                    distances=distances,
                    legs=legs,
                    walk=walk,
                )
                _render_one_meeting(
                    living=living,
                    off_memories=off_memories,
                    on_memories=on_memories,
                    completions=completions,
                    seen_rows=seen_rows,
                    walk=walk,
                )
                pending.append((facts, roster))
            elif isinstance(walk_event, MeetingApplied):
                _fold_meeting_both_ways(walk_event, off=off_memories, on=on_memories)
    finally:
        service.close()
        audit_dir.cleanup()


def _fold_one_meeting(
    *,
    facts: _MeetingFacts,
    roster: frozenset[PlayerId],
    game_id: str,
    roles: Mapping[PlayerId, Role],
    off_stores: Mapping[PlayerId, MemoryStore],
    room_at: Mapping[int, Mapping[PlayerId, RoomId]],
    distances: Mapping[RoomId, Mapping[RoomId, int]],
    legs: Mapping[str, Mapping[str, str]],
    walk: _SetWalk,
) -> None:
    """Re-detect one meeting's flags on every slate and fold each leg's cells.

    The detector channels are built from the OFF lineage: they read first-hand
    ``saw_player`` / ``saw_player_move`` rows, which the render levers never write
    and the testimony seam never touches, so both lineages hand the detector the
    same inputs.
    """

    entry = facts.entry
    walk.meetings += 1
    vents = {pid: _vent_channel(off_stores[pid]) for pid in facts.living}
    moves = {
        pid: _move_channel(off_stores[pid], speaker=pid, roles=roles)
        for pid in facts.living
    }
    sightings = {
        pid: _sighting_channel(off_stores[pid], speaker=pid, roles=roles)
        for pid in facts.living
    }
    vents = {pid: rows for pid, rows in vents.items() if rows}
    moves = {pid: rows for pid, rows in moves.items() if rows}
    sightings = {pid: rows for pid, rows in sightings.items() if rows}

    innocent_ejection = _is_innocent_ejection(entry, roles=roles)
    if innocent_ejection:
        walk.innocent_ejections += 1

    # I-8's turn half: the recorded free_text, and the same turns with their audit
    # markers parsed back out — which IS the structured-turn-markers ON shape over
    # frozen bytes, read through the loader's own repr-aware parser.
    for turn in entry.transcript.turns:
        walk.turns += 1
        if turn.free_text.startswith(_MARKER_PREFIXES):
            walk.marker_turns_off += 1
        _labels, clean = _parse_turn_annotations(turn)
        if clean.startswith(_MARKER_PREFIXES):
            walk.marker_turns_on += 1

    for name, slate in legs.items():
        flags = detect_contradictions(
            entry.transcript,
            roster=roster,
            vent_witness_records=vents,
            move_witness_records=moves,
            sighting_records=sightings,
            env=slate,
        )
        if name == "off" and tuple(flags) == tuple(entry.contradictions):
            walk.off_flags_match_recorded += 1
        counts = walk.legs[name]
        _fold_flags(
            game_id=game_id,
            facts=_MeetingFacts(
                entry=entry.model_copy(update={"contradictions": flags}),
                living=facts.living,
                venting=facts.venting,
                body_triggered=facts.body_triggered,
            ),
            roles=roles,
            memories=off_stores,
            room_at=room_at,
            distances=distances,
            tallies=counts.tallies,
        )
        counts.strong_alibi_vs_sighting += sum(
            1
            for flag in flags
            if flag.kind == "alibi_vs_sighting" and not is_weak_contradiction(flag)
        )
        if innocent_ejection:
            _fold_innocent_census(flags, ejectee=entry.ejected_player_id, counts=counts)


def _is_innocent_ejection(entry: object, *, roles: Mapping[PlayerId, Role]) -> bool:
    """Whether this meeting is one of the 79: a non-direct CREWMATE ejection.

    The 19.14 partition, re-derived: an ejection is PROOF-PRESENT when the ejected
    player is a subject of a ``role_proof`` flag in the meeting that ejected them,
    and the innocent cell is every OTHER ejection whose victim was a crewmate. The
    per-set totals are cross-checked against the committed pins before any
    surviving-flag number is printed.
    """

    outcome = getattr(entry, "outcome", None)
    ejectee = getattr(entry, "ejected_player_id", None)
    if outcome != "EJECTED" or not isinstance(ejectee, str):
        return False
    if roles.get(ejectee) != "CREWMATE":
        return False
    contradictions = getattr(entry, "contradictions", ())
    proven = {
        subject
        for flag in contradictions
        if classify_flag(flag) == "role_proof"
        for subject in flag.subjects
    }
    return ejectee not in proven


def _fold_innocent_census(
    flags: Sequence[ContradictionRef],
    *,
    ejectee: PlayerId | None,
    counts: SlateFlagCounts,
) -> None:
    """Follow one wrongful ejection's conviction evidence into this slate."""

    if ejectee is None:
        return
    on_victim = [
        flag
        for flag in flags
        if not is_weak_contradiction(flag) and ejectee in flag.subjects
    ]
    if on_victim:
        counts.innocent_any_strong += 1
        if all(flag.kind == "alibi_vs_sighting" for flag in on_victim):
            counts.innocent_sole_kind += 1


def _render_one_meeting(
    *,
    living: frozenset[PlayerId],
    off_memories: Mapping[PlayerId, AgentMemory],
    on_memories: Mapping[PlayerId, AgentMemory],
    completions: Mapping[PlayerId, set[int]],
    seen_rows: Mapping[str, set[tuple[PlayerId, str]]],
    walk: _SetWalk,
) -> None:
    """Render every living agent's memory twice and fold the render cells.

    Both legs pass an explicit mapping: the counterfactual must not read whatever
    the process environment happens to export. Rows are counted with the
    instrument's own patterns and the completion rows through the instrument's own
    fold, so the OFF leg is directly comparable to the recorded-prompt cell.
    """

    for pid in sorted(living):
        walk.snapshots += 1
        for leg, memories, budget in (
            ("off", off_memories, SLATE_OFF),
            ("on", on_memories, SLATE_ON),
            ("census_on", on_memories, RENDER_CENSUS_SLATE),
        ):
            view = render_for_prompt(
                memories[pid], token_budget=DEFAULT_TOKEN_BUDGET, env=budget
            )
            rows = len(_RENDERED_ROW.findall(view))
            testimony = sum(
                1
                for line in view.splitlines()
                if _TESTIMONY_ROW.match(line) is not None
            )
            if leg == "census_on":
                # The render census only: no completion fold, no dedup state.
                walk.rendered_rows_census_on += rows
                walk.testimony_rows_census_on += testimony
                continue
            tallies = _Tallies()
            _fold_completion_rows(
                call=LLMCallRecord(
                    call_kind="meeting",
                    model="offline-counterfactual",
                    prompt=view,
                    response_text="",
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    agent_id=pid,
                ),
                completions=completions,
                seen_rows=seen_rows[leg],
                found=_SelfLocations(),
                tallies=tallies,
            )
            if leg == "off":
                walk.rendered_rows_off += rows
                walk.testimony_rows_off += testimony
                walk.completion_rows_off += tallies.completion_lines
                walk.fabricated_rows_off += tallies.fabricated_lines
            else:
                walk.rendered_rows_on += rows
                walk.testimony_rows_on += testimony
                walk.completion_rows_on += tallies.completion_lines
                walk.fabricated_rows_on += tallies.fabricated_lines


# --------------------------------------------------------------------------- #
# The table.                                                                   #
# --------------------------------------------------------------------------- #


def _pair(rate_cell: WilsonRateCell) -> tuple[int, int]:
    """``(numerator, denominator)`` off a Wilson rate cell."""

    return (rate_cell.numerator, rate_cell.denominator)


def build_rows(
    *,
    walk: _SetWalk,
    recorded: EvidenceHonestyReport,
    solvability: SolvabilityReport,
) -> list[Row]:
    """Assemble one set's printed rows from its three readings."""

    off = walk.legs["off"].tallies
    on = walk.legs["on"].tallies
    off_report = _report(
        sample_dir=Path(recorded.replay_set_dir),
        num_players=recorded.num_players,
        num_impostors=recorded.num_impostors,
        tasks_per_crewmate=recorded.tasks_per_crewmate,
        games_total=walk.games,
        policy_mode=recorded.impostor_targeting.policy_mode,
        tallies=off,
    )
    on_report = _report(
        sample_dir=Path(recorded.replay_set_dir),
        num_players=recorded.num_players,
        num_impostors=recorded.num_impostors,
        tasks_per_crewmate=recorded.tasks_per_crewmate,
        games_total=walk.games,
        policy_mode=recorded.impostor_targeting.policy_mode,
        tallies=on,
    )
    rows: list[Row] = []

    def flag_row(cell_id: str, label: str, path: str, note: str = "") -> None:
        rows.append(
            Row(
                cell_id=cell_id,
                label=label,
                population="flag",
                recorded_off=_pair(_dig(recorded, path)),
                reconstructed_off=_pair(_dig(off_report, path)),
                on=_pair(_dig(on_report, path)),
                note=note,
            )
        )

    flag_row(
        "I-3",
        "sole-flag convicting precision (per victim)",
        "sole_flag_precision.per_victim_precision",
        "the kind-sole cell bar 4 names (memo §10), not the exactly-one-flag twin",
    )
    flag_row(
        "I-3",
        "class impostor share (STRONG alibi_vs_sighting, dedup subjects)",
        "sole_flag_precision.class_impostor_share",
    )
    flag_row(
        "I-3",
        "living-voter base rate at those meetings",
        "sole_flag_precision.living_voter_base_rate",
    )
    flag_row(
        "I-4",
        "grounded sighting side (at tick)",
        "grounded_sighting.grounded_at_tick",
        "bar 5 is the at-tick cell; a suppressed flag leaves the denominator",
    )
    flag_row(
        "I-4",
        "grounded sighting side (within +/-1 tick)",
        "grounded_sighting.grounded_within_1",
    )
    flag_row(
        "I-6",
        "adjacent-room STRONG share",
        "adjacent_room_flags.adjacent",
        "one doorway apart AND the sighting within <= 1 tick of the alibi window",
    )
    flag_row(
        "I-6",
        "adjacent-room STRONG share (un-gated adjacent_any_gap)",
        "adjacent_room_flags.adjacent_any_gap",
        "reported BESIDE the ratified numerator, never in place of it (memo §10)",
    )
    flag_row(
        "I-7",
        "movement-origin flags",
        "movement_origin_flags.spoke_origin",
    )
    rows.append(
        Row(
            cell_id="I-8",
            label="marker contamination (turns)",
            population="turn",
            recorded_off=_pair(recorded.marker_contamination.turns_with_marker),
            reconstructed_off=(walk.marker_turns_off, walk.turns),
            on=(walk.marker_turns_on, walk.turns),
            note=(
                "ON reads the same recorded turns with their audit markers parsed "
                "back into typed annotations (api.replay_loader)"
            ),
        )
    )
    rows.append(
        Row(
            cell_id="I-8",
            label="marker contamination (prompts)",
            population="prompt",
            recorded_off=_pair(recorded.marker_contamination.prompts_with_marker),
            reconstructed_off=None,
            on=None,
            note="PROMPT-SET-COUPLED: a prompt re-renders only under a Jinja set",
        )
    )
    rows.append(
        Row(
            cell_id="I-9",
            label="singular-persona prompts",
            population="prompt",
            recorded_off=_pair(recorded.singular_persona.prompts_with_singular_persona),
            reconstructed_off=None,
            on=None,
            note="PROMPT-SET-COUPLED: the persona block is template bytes",
        )
    )
    rows.append(
        Row(
            cell_id="I-5",
            label="fabricated completion lines",
            population="render",
            recorded_off=_pair(recorded.fabricated_completions.fabricated),
            reconstructed_off=(walk.fabricated_rows_off, walk.completion_rows_off),
            on=(walk.fabricated_rows_on, walk.completion_rows_on),
            note=(
                "RECORDED counts rows in recorded prompts; RECONSTRUCTED re-renders "
                "the same memories per meeting-agent — a different snapshot "
                "population, so the two OFF readings are compared as rates"
            ),
        )
    )
    rows.append(
        Row(
            cell_id="R",
            label="rendered memory rows per snapshot (mean)",
            population="render",
            recorded_off=(
                recorded.render_budget.rendered_lines_total,
                recorded.render_budget.snapshots,
            ),
            reconstructed_off=(walk.rendered_rows_off, walk.snapshots),
            on=(walk.rendered_rows_census_on, walk.snapshots),
            display="mean",
            on_slate=RENDER_CENSUS_SLATE_LABEL,
            note=(
                "the budget every render lever spends against; the ON leg drops "
                "meeting_outcome_memory because that lever re-tags the testimony "
                "frame '[meeting N]' and the instrument's row patterns are "
                "OFF-shaped - the full-slate census is ROUTED, not recounted here"
            ),
        )
    )
    rows.append(
        Row(
            cell_id="R",
            label="reported-testimony rows retained",
            population="render",
            recorded_off=(
                recorded.render_budget.testimony_rows_total,
                recorded.render_budget.rendered_lines_total,
            ),
            reconstructed_off=(walk.testimony_rows_off, walk.rendered_rows_off),
            on=(walk.testimony_rows_census_on, walk.rendered_rows_census_on),
            on_slate=RENDER_CENSUS_SLATE_LABEL,
            note=(
                "same slate caveat as the row above: the OFF-shaped testimony "
                "pattern cannot read a '[meeting N]'-tagged frame"
            ),
        )
    )
    for cell_id, label, attribute in (
        ("I-12", "containment (killer in the candidate set)", "killer_in_set"),
        ("I-12", "singleton candidate sets", "singleton_sets"),
        ("I-12", "singleton correct", "singleton_correct"),
        (
            "I-12",
            "ejections on an already-cleared player",
            "cleared_player_ejections",
        ),
    ):
        pair = _pair(getattr(solvability, attribute))
        rows.append(
            Row(
                cell_id=cell_id,
                label=label,
                population="oracle",
                recorded_off=pair,
                reconstructed_off=pair,
                on=pair,
                note=(
                    "LEVER-INVARIANT: the oracle reads the engine's kill and "
                    "visibility record and the recorded ballots; no lever moves "
                    "either offline"
                ),
            )
        )
    rows.append(
        Row(
            cell_id="E",
            label="innocent ejections still carrying a STRONG flag",
            population="flag",
            recorded_off=(
                walk.legs["off"].innocent_any_strong,
                walk.innocent_ejections,
            ),
            reconstructed_off=(
                walk.legs["off"].innocent_any_strong,
                walk.innocent_ejections,
            ),
            on=(walk.legs["on"].innocent_any_strong, walk.innocent_ejections),
            note="the 79-meeting census: a conviction that survives the slate",
        )
    )
    rows.append(
        Row(
            cell_id="E",
            label="innocent ejections whose STRONG flags were all alibi_vs_sighting",
            population="flag",
            recorded_off=(
                walk.legs["off"].innocent_sole_kind,
                walk.innocent_ejections,
            ),
            reconstructed_off=(
                walk.legs["off"].innocent_sole_kind,
                walk.innocent_ejections,
            ),
            on=(walk.legs["on"].innocent_sole_kind, walk.innocent_ejections),
            note="the kind-sole conviction bar 4 prices",
        )
    )
    return rows


def _dig(report: object, path: str) -> WilsonRateCell:
    """Read a dotted attribute path off a report, as the rate cell it must be."""

    value: object = report
    for part in path.split("."):
        value = getattr(value, part)
    if not isinstance(value, WilsonRateCell):
        raise TypeError(f"{path} is not a WilsonRateCell on {type(report).__name__}")
    return value


def _rate(pair: tuple[int, int] | None, *, display: str = "rate") -> str:
    """One printed column: counts plus their reading, or ``--`` for no reading."""

    if pair is None:
        return "--"
    numerator, denominator = pair
    if denominator == 0:
        return f"{numerator}/{denominator} n/a"
    if display == "mean":
        return f"{numerator}/{denominator} {numerator / denominator:.4f}"
    return f"{numerator}/{denominator} {numerator / denominator:.1%}"


def leave_one_out_table(walk: _SetWalk) -> dict[str, dict[str, int]]:
    """Per-lever attribution over the innocent-ejection census and the class size."""

    return {
        name: {
            "innocent_any_strong": counts.innocent_any_strong,
            "innocent_sole_kind": counts.innocent_sole_kind,
            "strong_alibi_vs_sighting": counts.strong_alibi_vs_sighting,
        }
        for name, counts in walk.legs.items()
    }


# --------------------------------------------------------------------------- #
# The CLI.                                                                     #
# --------------------------------------------------------------------------- #


def _assert_ambient_slate_is_off(when: str) -> None:
    """Refuse to run under a stale ``AILIBI_*`` export."""

    snapshot = substrate_flag_snapshot()
    stale = sorted(key for key in PHASE_20_LEVERS if snapshot.get(key, False))
    if stale:
        raise SystemExit(
            f"the ambient process slate is not OFF {when}: "
            + ", ".join(f"{key} ({env_var_for_lever(key)})" for key in stale)
            + " — this table toggles levers through each resolver's env parameter "
            "and never reads the process environment; unset the exports and re-run"
        )


def run(set_names: Sequence[str]) -> dict[str, object]:
    """Compute the whole table for the named sets, plus the pooled column."""

    _assert_ambient_slate_is_off("at start")
    payload: dict[str, object] = {
        "slate_on": dict(SLATE_ON),
        "levers": list(PHASE_20_LEVERS),
        "sets": {},
    }
    pooled: Counter[str] = Counter()
    pooled_labels: dict[str, tuple[str, str, str, str, str, str]] = {}
    per_set: dict[str, object] = {}
    for set_name in set_names:
        sample_dir = Path("replays") / set_name
        walk = walk_set(sample_dir, set_name=set_name)
        expected = COMMITTED_INNOCENT_EJECTIONS.get(set_name)
        if expected is not None and walk.innocent_ejections != expected:
            raise SystemExit(
                f"{set_name}: the innocent-ejection enumeration reproduced "
                f"{walk.innocent_ejections}, not the committed 19.14 pin "
                f"{expected} — this is a DEFECT IN THIS SCRIPT's join, not a "
                "finding about the committed bytes; fix the enumeration before "
                "reading any ON number"
            )
        if walk.off_flags_match_recorded != walk.meetings:
            raise SystemExit(
                f"{set_name}: the OFF leg re-derived {walk.off_flags_match_recorded} "
                f"of {walk.meetings} meetings' recorded flags — the reconstruction "
                "is not the recorded substrate, so no ON column may be printed. "
                "This is a DEFECT IN THIS SCRIPT, not a finding about the bytes"
            )
        recorded = compute_evidence_honesty(sample_dir)
        solvability = compute_solvability_report(sample_dir)
        rows = build_rows(walk=walk, recorded=recorded, solvability=solvability)
        disagreeing = [row for row in rows if not row.agrees]
        if disagreeing:
            names = ", ".join(f"{row.cell_id} {row.label}" for row in disagreeing)
            raise SystemExit(
                f"{set_name}: RECORDED-OFF and RECONSTRUCTED-OFF disagree on "
                f"{names} — no ON column is printed for a cell whose baseline "
                "does not reproduce. This is a DEFECT IN THIS SCRIPT"
            )
        per_set[set_name] = {
            "games": walk.games,
            "meetings": walk.meetings,
            "innocent_ejections": walk.innocent_ejections,
            "rows": [row.payload() for row in rows],
            "leave_one_out": leave_one_out_table(walk),
        }
        for row in rows:
            key = f"{row.cell_id}|{row.label}"
            pooled_labels[key] = (
                row.cell_id,
                row.label,
                row.population,
                row.display,
                row.on_slate,
                row.note,
            )
            for column, pair in (
                ("recorded_off", row.recorded_off),
                ("reconstructed_off", row.reconstructed_off),
                ("on", row.on),
            ):
                if pair is None:
                    continue
                pooled[f"{key}|{column}|n"] += pair[0]
                pooled[f"{key}|{column}|d"] += pair[1]
    payload["sets"] = per_set
    payload["pooled"] = [
        {
            "cell": cell_id,
            "label": label,
            "population": population,
            "display": display,
            "on_slate": on_slate,
            "note": note,
            **{
                column: (
                    [pooled[f"{key}|{column}|n"], pooled[f"{key}|{column}|d"]]
                    if f"{key}|{column}|d" in pooled
                    else None
                )
                for column in ("recorded_off", "reconstructed_off", "on")
            },
        }
        for key, (
            cell_id,
            label,
            population,
            display,
            on_slate,
            note,
        ) in pooled_labels.items()
    ]
    _assert_ambient_slate_is_off("at exit")
    return payload


def _print_table(
    payload: Mapping[str, object], *, stream: TextIO | None = None
) -> None:
    """Print the OFF/ON table the memo reproduces row for row."""

    out = sys.stdout if stream is None else stream
    sets = payload["sets"]
    assert isinstance(sets, dict)
    header = (
        f"{'cell':<5} {'label':<58} {'RECORDED-OFF':>20} "
        f"{'RECONSTRUCTED-OFF':>20} {'ON':>20}"
    )
    for set_name, block in sets.items():
        assert isinstance(block, dict)
        print(
            f"\n== {set_name} "
            f"({block['games']} games, {block['meetings']} meetings, "
            f"{block['innocent_ejections']} innocent ejections)",
            file=out,
        )
        print(header, file=out)
        for row in block["rows"]:
            _print_row(row, out=out)
        print(
            "   leave-one-out (innocent ejections still STRONG / kind-sole / "
            "STRONG alibi_vs_sighting):",
            file=out,
        )
        for leg, counts in block["leave_one_out"].items():
            print(
                f"     {leg:<26} {counts['innocent_any_strong']:>4} "
                f"{counts['innocent_sole_kind']:>4} "
                f"{counts['strong_alibi_vs_sighting']:>5}",
                file=out,
            )
    print("\n== POOLED", file=out)
    print(header, file=out)
    pooled = payload["pooled"]
    assert isinstance(pooled, list)
    for row in pooled:
        _print_row(row, out=out)
    _print_reading_rules(pooled, out=out)


def _print_reading_rules(pooled: Sequence[object], *, out: TextIO) -> None:
    """The footnotes a reader needs before comparing two columns.

    Every row whose ON column is missing, computed under a slate other than the
    full eight, or lever-invariant by construction says so here — so no column is
    read as something it is not.
    """

    print("\nreading rules:", file=out)
    for row in pooled:
        assert isinstance(row, dict)
        if row["population"] == "flag" or row["population"] == "turn":
            if row["on_slate"] == FULL_SLATE_LABEL:
                continue
        label = f"{row['cell']} {row['label']}"
        slate = (
            ""
            if row["on_slate"] == FULL_SLATE_LABEL
            else (f" [ON slate: {row['on_slate']}]")
        )
        print(f"  {label}{slate}: {row['note']}", file=out)
    print(
        "  I-1 (non-direct conviction accuracy, innocent ejections), I-2 (false "
        "crew self-placement), the model-dependent halves of the four I-13 "
        "fixtures and the win split carry NO ON column at all: a flag that stops "
        "being minted is not a vote that changes.",
        file=out,
    )
    print(
        "  I-11 is excluded: its ratified cells are the frozen "
        "eval.evidence_honesty.RATIFIED_I11_CELLS, never a live-policy fold.",
        file=out,
    )


def _print_row(row: Mapping[str, object], *, out: TextIO) -> None:
    def pair(key: str) -> tuple[int, int] | None:
        value = row.get(key)
        if value is None:
            return None
        assert isinstance(value, list)
        return (int(value[0]), int(value[1]))

    display = str(row.get("display", "rate"))
    print(
        f"{row['cell']:<5} {str(row['label'])[:58]:<58} "
        f"{_rate(pair('recorded_off'), display=display):>20} "
        f"{_rate(pair('reconstructed_off'), display=display):>20} "
        f"{_rate(pair('on'), display=display):>20}",
        file=out,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "The Phase-20 offline counterfactual: every predictable pre-registered "
            "cell over the committed bytes, OFF slate and ON slate, $0 and offline "
            "(audits/audit-phase-20-preregistration.md §8)."
        )
    )
    parser.add_argument(
        "--sets",
        default="all",
        help=(
            "'all' for the four committed sets in the §9 record order, or one "
            "set name under replays/ (e.g. samples/4p1i) for iteration"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the same table machine-readably for the record audit",
    )
    args = parser.parse_args(argv)
    set_names = (
        list(CANONICAL_SETS) if args.sets == "all" else [str(args.sets).strip("/")]
    )
    started = time.monotonic()
    payload = run(set_names)
    elapsed = time.monotonic() - started
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_table(payload)
        print(f"\nwall time: {elapsed:.1f}s", file=sys.stdout)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
