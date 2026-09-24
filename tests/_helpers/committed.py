"""The one home for walks over the committed replay sets, each computed once.

The five instruments below — the assembled eval report, the information funnel,
the kill-craft, deception and solvability folds — are the suite's most expensive
fixtures: each re-seeds every game in a set, replays every recorded action
through the engine and verifies every state hash. The sixth walk,
:func:`committed_meetings`, rebuilds every speaker's memory through the real
perception path and projects the three private channels the meeting layer reads.
Each is a pure deterministic function of frozen committed bytes, so computing
one twice is repeated work and nothing else. Every test-side walk over a
committed set goes through this module.

One instance is shared by every reader on a worker, and two mechanisms — not a
promise — keep that from coupling them: the reports and meeting records are
frozen, so no field can be rebound, and every collection they expose is
annotated ``Mapping``/``Sequence``, which has no ``__setitem__``, so
``uv run mypy .`` rejects an in-place mutation where it is written.
``tests/_helpers/test_committed_single_home.py`` walks the cached value graphs
and fails if either property is ever dropped.

``functools.cache`` rather than a session fixture: the sharing has to reach
plain helper functions and class bodies that cannot request a fixture, and under
``pytest-xdist`` a session fixture is session-scoped *per worker* anyway — so a
process-level cache is the same lifetime with a wider reach.

A few call sites deliberately walk a set WITHOUT this cache — because a second
independent computation is what they assert, or because the walker itself is the
subject under test. ``tests/_helpers/test_committed_single_home.py`` holds that
allow-list with the reason for each, and pins every other call site here.
"""

from __future__ import annotations

import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Final, Protocol, TypeVar

if TYPE_CHECKING:
    from agents.memory.episodic import MemoryStore
    from eval.deception_instruments import DeceptionInstrumentsReport
    from eval.funnel import InformationFunnelReport
    from eval.kill_craft import KillCraftReport
    from eval.meeting_quality import TournamentEvalReport
    from eval.replay_walk import MeetingOpened
    from eval.solvability import SolvabilityReport
    from meetings.schemas import (
        ContradictionRef,
        MoveWitnessRecord,
        PlayerId,
        SightingRecord,
        VentWitnessRecord,
    )
    from meetings.transcript import MeetingTriggerKind
    from orchestrator.replay import MeetingReplayEntry

_Row = TypeVar("_Row")

#: The checkout root, derived from this file rather than the process working
#: directory: a test that builds a fixture path from the cwd only passes when
#: pytest happens to be invoked from the repo root.
repo_root: Final[Path] = Path(__file__).resolve().parents[2]

#: The four committed replay sets the pins walk, named once so new callers do not
#: have to spell the layout again. Cache entries are keyed by path VALUE, so a
#: module that builds the same absolute path shares the entry either way.
SAMPLES_9P2I: Final[Path] = repo_root / "replays" / "samples" / "9p2i"
SAMPLES_4P1I: Final[Path] = repo_root / "replays" / "samples" / "4p1i"
CORPUS_9P2I: Final[Path] = repo_root / "replays" / "ml_corpus" / "9p2i"
CORPUS_4P1I: Final[Path] = repo_root / "replays" / "ml_corpus" / "4p1i"

#: The four sets in the order every all-sets reader walks them.
COMMITTED_SETS: Final[tuple[Path, ...]] = (
    SAMPLES_9P2I,
    SAMPLES_4P1I,
    CORPUS_9P2I,
    CORPUS_4P1I,
)

#: Recorded meetings frozen out of the baseline-8 sets the baseline-9 re-record
#: replaced, for tests whose exhibit shape no committed set carries any more.
#: Each file's source, transform and sha256 are in the README beside them.
BASELINE8_EXHIBITS: Final[Path] = (
    repo_root / "tests" / "fixtures" / "baseline8_exhibits"
)


def frozen_meetings(name: str) -> tuple[MeetingReplayEntry, ...]:
    """Every meeting line of the frozen exhibit file ``name``, in file order.

    Raises when the file holds anything but meeting lines, so an exhibit cannot
    quietly grow a row the tests reading it never looked at.
    """

    from orchestrator.replay import MeetingReplayEntry, read_all_entries

    entries = read_all_entries(BASELINE8_EXHIBITS / name)
    meetings = tuple(
        entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    )
    if len(meetings) != len(entries):
        raise ValueError(f"{name}: a frozen exhibit holds meeting lines only")
    return meetings


@cache
def report_9p2i() -> TournamentEvalReport:
    """The committed 9p2i set's eval report, assembled once.

    ``build_report`` re-derives roles from the seeds, folds the 50 recorded
    replays through the one operator assembly (``scripts/build_sample_report.py``)
    and runs the state-hash-verified kill-craft walk over the whole directory.

    Imports lazily: ``build_sample_report`` pulls in the api/engine/eval stack,
    which does not belong in the import time of tests that never read a report.
    """

    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from build_sample_report import build_report

    return build_report(SAMPLES_9P2I)


@cache
def funnel_report(sample_dir: Path) -> InformationFunnelReport:
    """``sample_dir``'s three-stage information funnel, folded once."""

    from eval.funnel import compute_information_funnel

    return compute_information_funnel(sample_dir)


def funnel_9p2i() -> InformationFunnelReport:
    """The committed 9p2i set's information funnel — the cross-package reader."""

    return funnel_report(SAMPLES_9P2I)


@cache
def kill_craft_report(sample_dir: Path) -> KillCraftReport:
    """``sample_dir``'s kill-craft report, walked once."""

    from eval.kill_craft import compute_kill_craft_report

    return compute_kill_craft_report(sample_dir)


@cache
def deception_instruments_report(sample_dir: Path) -> DeceptionInstrumentsReport:
    """``sample_dir``'s Tier-A deception instruments, folded once."""

    from eval.deception_instruments import compute_deception_instruments

    return compute_deception_instruments(sample_dir)


@cache
def solvability_report(sample_dir: Path) -> SolvabilityReport:
    """``sample_dir``'s solvability ceiling, walked once."""

    from eval.solvability import compute_solvability_report

    return compute_solvability_report(sample_dir)


def sighting_records_from_recorded_flags(
    entry: MeetingReplayEntry,
) -> dict[PlayerId, tuple[SightingRecord, ...]]:
    """Invert one meeting's sighting channel out of its RECORDED flags.

    Records-free by design, and for frozen exhibits and transcript-level re-runs
    only. A frozen baseline-8 exhibit line (:func:`frozen_meetings`) carries no
    tick rows, so no replay walk can rebuild its speakers' memories; a recorded
    flag carrying :data:`WEAK_REASON_UNGROUNDED_SIGHTING` says the speaker's own
    record did NOT back that sighting, and every other spoken sighting was
    grounded at record time, so the inversion re-grounds what the recording
    grounded. A committed meeting's true channels come from
    :func:`committed_meetings` instead: the inversion knows nothing of the
    movement channel, and an all-ungrounded meeting inverts to an empty mapping,
    which drops the detector back to its pre-grounding rules.
    """

    from meetings.schemas import SawPlayerObservation, SightingRecord
    from meetings.transcript import WEAK_REASON_UNGROUNDED_SIGHTING

    ungrounded = {
        event_id
        for flag in entry.contradictions
        if WEAK_REASON_UNGROUNDED_SIGHTING in flag.description
        for event_id in (flag.event_a_id, flag.event_b_id)
    }
    records: dict[PlayerId, list[SightingRecord]] = {}
    for turn in entry.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawPlayerObservation):
                continue
            if f"turn:{turn.turn_id}:obs:{index}" in ungrounded:
                continue
            records.setdefault(turn.speaker, []).append(
                SightingRecord(
                    subject=observation.subject,
                    room=observation.room,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}


# --------------------------------------------------------------------------- #
# The committed meetings, with the private channels production threaded.       #
# --------------------------------------------------------------------------- #
#
# The meeting layer reads three per-speaker channels the transcript does not
# carry: witnessed vents, witnessed room-to-room moves and first-hand sightings.
# The replay persists none of them as rows, but each is a projection of the
# speaker's episodic memory, and the replay walk rebuilds that memory through
# the real perception path. The builders project it field for field the way the
# live accessors do, and the walk threads the result the way the meeting manager
# does, so re-running the detector over a committed meeting re-runs production.
# ``tests/meetings/test_contradictions.py`` gates that claim on every committed
# meeting.


def _fellow_impostors(
    holder: PlayerId, roles: Mapping[PlayerId, str]
) -> frozenset[PlayerId]:
    """The holder's fellow impostors: empty for a crewmate and a sole impostor."""

    if roles.get(holder) != "IMPOSTOR":
        return frozenset()
    return frozenset(
        pid for pid, role in roles.items() if role == "IMPOSTOR" and pid != holder
    )


def vent_witness_records_for_meeting(
    memory: MemoryStore,
) -> tuple[VentWitnessRecord, ...]:
    """The holder's witnessed vents, as ``TacticalAgent`` reads them.

    ``orchestrator.game.TacticalAgent.vent_witness_records_for_meeting``:
    first-hand ``saw_player`` rows stamped with the vent action. Neither the
    accessor nor the manager applies a teammate guard to this channel.
    """

    from agents.memory.beliefs import OBSERVED_VENT_ACTION
    from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED
    from meetings.schemas import VentWitnessRecord

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
                VentWitnessRecord(
                    subject=subject,
                    room=room,
                    tick=event.tick,
                    observation_id=event.observation_id,
                )
            )
    return tuple(records)


def sighting_records_for_meeting(
    memory: MemoryStore, *, holder: PlayerId, roles: Mapping[PlayerId, str]
) -> tuple[SightingRecord, ...]:
    """The holder's first-hand sightings, as the prosecution channel gets them.

    ``orchestrator.game.TacticalAgent.sighting_records_for_meeting``: first-hand
    ``saw_player`` rows minus the incriminating vent and kill actions, each with
    its co-presence projection. Then the teammate guard
    :class:`meetings.manager.MeetingManager` applies when it builds the
    detector's mapping: an impostor's rows naming a fellow impostor are dropped,
    and the co-presence tuples are left as the accessor built them.
    """

    from agents.memory.beliefs import OBSERVED_KILL_ACTION, OBSERVED_VENT_ACTION
    from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED
    from meetings.schemas import SightingRecord

    fellows = _fellow_impostors(holder, roles)
    rows: list[tuple[str, str, int, str | None]] = []
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
        rows.append((subject, room, event.tick, event.observation_id))
        co_present.setdefault((event.tick, room), set()).add(subject)
    return tuple(
        SightingRecord(
            subject=subject,
            room=room,
            tick=tick,
            co_present=tuple(sorted(co_present.get((tick, room), set()) - {subject})),
            observation_id=observation_id,
        )
        for subject, room, tick, observation_id in rows
        if subject not in fellows
    )


def move_witness_records_for_meeting(
    memory: MemoryStore,
    *,
    holder: PlayerId,
    roles: Mapping[PlayerId, str],
    keep_holder_rows: bool = False,
) -> tuple[MoveWitnessRecord, ...]:
    """The holder's witnessed transitions, as ``TacticalAgent`` reads them.

    ``orchestrator.game.TacticalAgent.move_witness_records_for_meeting``:
    first-hand ``saw_player_move`` rows, minus every row naming a fellow
    impostor and every row naming the holder themself. ``keep_holder_rows`` is a
    planted control's switch, which the live accessor does not have: it plants
    the self-row drift so the gate can be shown to catch it.
    """

    from agents.perception import EVENT_SAW_PLAYER_MOVE, PROVENANCE_OBSERVED
    from meetings.schemas import MoveWitnessRecord

    fellows = _fellow_impostors(holder, roles)
    records: list[MoveWitnessRecord] = []
    for event in memory.recent(since_tick=0):
        if (
            event.type != EVENT_SAW_PLAYER_MOVE
            or event.provenance != PROVENANCE_OBSERVED
        ):
            continue
        subject = event.payload.get("player_id")
        if subject in fellows or (subject == holder and not keep_holder_rows):
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
                    observation_id=event.observation_id,
                )
            )
    return tuple(records)


class MoveRecordBuilder(Protocol):
    """The shape of :func:`move_witness_records_for_meeting`."""

    def __call__(
        self, memory: MemoryStore, *, holder: PlayerId, roles: Mapping[PlayerId, str]
    ) -> tuple[MoveWitnessRecord, ...]: ...


def meeting_trigger_kind(walk_event: MeetingOpened) -> MeetingTriggerKind:
    """The trigger kind the meeting manager threads into detection.

    The orchestrator renders the engine's trigger event into a meeting trigger
    (``orchestrator.game._build_meeting_trigger``), and the manager reads the kind
    back off its description (``meetings.manager._trigger_is_emergency``). Both
    steps are called here rather than restated.
    """

    from meetings.manager import _trigger_is_emergency
    from orchestrator.game import _build_meeting_trigger

    trigger, _body_id, _engine_kind = _build_meeting_trigger(
        state=walk_event.state, events=walk_event.events
    )
    return "emergency" if _trigger_is_emergency(trigger) else "report"


@dataclass(frozen=True)
class CommittedMeeting:
    """One committed meeting, with the arguments production detected it with.

    ``roster`` is the living participants, ``trigger_kind`` is derived as the
    manager derives it, and each channel omits a participant with no rows, as
    ``meetings.manager.MeetingManager`` builds its mappings.
    """

    set_name: str
    seed: int
    entry: MeetingReplayEntry
    roster: frozenset[PlayerId]
    trigger_kind: MeetingTriggerKind
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]]
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]]

    @property
    def name(self) -> str:
        """``set:seed:meeting_id``, the key the named-meeting pins use."""

        return f"{self.set_name}:{self.seed}:{self.entry.meeting_id}"

    def rederive(self) -> tuple[ContradictionRef, ...]:
        """The detector over this meeting, with every argument production passed.

        A control drops a channel with ``dataclasses.replace`` first.
        """

        from meetings.transcript import detect_contradictions

        return detect_contradictions(
            self.entry.transcript,
            roster=self.roster,
            trigger_kind=self.trigger_kind,
            vent_witness_records=self.vent_witness_records,
            move_witness_records=self.move_witness_records,
            sighting_records=self.sighting_records,
        )


def _non_empty(
    rows_by_holder: Mapping[PlayerId, tuple[_Row, ...]],
) -> Mapping[PlayerId, tuple[_Row, ...]]:
    """A read-only mapping without the holders who have no rows."""

    return MappingProxyType(
        {holder: rows for holder, rows in rows_by_holder.items() if rows}
    )


def walk_committed_meetings(
    sample_dir: Path,
    *,
    seeds: Sequence[int] | None = None,
    move_records: MoveRecordBuilder = move_witness_records_for_meeting,
) -> tuple[CommittedMeeting, ...]:
    """Walk ``sample_dir`` and project every meeting's private channels.

    The evidence-honesty instrument's walk: each tick's real observation packet
    is ingested into every living agent's memory, and the post-meeting fold runs
    after each meeting, so the memory read at a meeting's open is the one its
    speakers held. Uncached: read committed sets through
    :func:`committed_meetings`. ``seeds`` and ``move_records`` exist for planted
    controls, which walk one game with a builder production does not use.
    """

    from agents.memory.episodic import MemoryStore
    from agents.memory.store import AgentMemory
    from engine.world import load_canonical_map
    from eval.evidence_honesty import (
        _WALK_CONFIG,
        _fold_meeting_into_memories,
        _perceive_tick,
    )
    from eval.replay_walk import MeetingApplied, MeetingOpened, TickOpened, walk_replay
    from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
    from observation.service import ObservationService

    set_name = f"{sample_dir.parent.name}/{sample_dir.name}"
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    meetings: list[CommittedMeeting] = []
    for seed in seeds_on_disk(sample_dir) if seeds is None else seeds:
        roles = roles_by_game[seed]
        memories = {pid: MemoryStore() for pid in roles}
        composites = {
            pid: AgentMemory(episodic=store) for pid, store in memories.items()
        }
        with tempfile.TemporaryDirectory(prefix="ailibi-channels-") as audit_dir:
            service = ObservationService(
                game_map=game_map, audit_log_path=Path(audit_dir) / "audit.jsonl"
            )
            try:
                for walk_event in walk_replay(
                    sample_dir / f"replay-seed-{seed}.jsonl",
                    seed=seed,
                    num_players=num_players,
                    num_impostors=num_impostors,
                    tasks_per_crewmate=tasks_per_crewmate,
                    game_map=game_map,
                    config=_WALK_CONFIG,
                ):
                    if isinstance(walk_event, TickOpened):
                        _perceive_tick(walk_event, service=service, memories=memories)
                    elif isinstance(walk_event, MeetingOpened):
                        living = sorted(
                            pid
                            for pid, player in walk_event.state.players.items()
                            if player.alive
                        )
                        meetings.append(
                            CommittedMeeting(
                                set_name=set_name,
                                seed=seed,
                                entry=walk_event.entry,
                                roster=frozenset(living),
                                trigger_kind=meeting_trigger_kind(walk_event),
                                vent_witness_records=_non_empty(
                                    {
                                        pid: vent_witness_records_for_meeting(
                                            memories[pid]
                                        )
                                        for pid in living
                                    }
                                ),
                                move_witness_records=_non_empty(
                                    {
                                        pid: move_records(
                                            memories[pid], holder=pid, roles=roles
                                        )
                                        for pid in living
                                    }
                                ),
                                sighting_records=_non_empty(
                                    {
                                        pid: sighting_records_for_meeting(
                                            memories[pid], holder=pid, roles=roles
                                        )
                                        for pid in living
                                    }
                                ),
                            )
                        )
                    elif isinstance(walk_event, MeetingApplied):
                        _fold_meeting_into_memories(walk_event, composites=composites)
            finally:
                service.close()
    return tuple(meetings)


@cache
def committed_meetings(sample_dir: Path) -> tuple[CommittedMeeting, ...]:
    """``sample_dir``'s meetings with their private channels, walked once."""

    return walk_committed_meetings(sample_dir)


def all_committed_meetings() -> tuple[CommittedMeeting, ...]:
    """Every committed meeting of the four sets, in :data:`COMMITTED_SETS` order."""

    return tuple(
        meeting
        for sample_dir in COMMITTED_SETS
        for meeting in committed_meetings(sample_dir)
    )


#: MEASURED: the committed meetings whose recorded flags the movement channel
#: decides. With every other argument production passed and the move channel
#: dropped, exactly these re-derive differently from the recording. Named rather
#: than counted, so one member cannot leave while an unrelated defect takes its
#: place. The controls in tests/meetings/test_contradictions.py (all four sets)
#: and tests/meetings/test_transcript.py (samples/9p2i) both read this set.
# was 69 records-free names in test_contradictions.py, one of them (1134 m3) its own artifact
MOVEMENT_DECIDED_MEETINGS: Final[frozenset[str]] = frozenset(
    {
        "ml_corpus/9p2i:1000:headless-seed-1000:meeting-0",
        "ml_corpus/9p2i:1001:headless-seed-1001:meeting-1",
        "ml_corpus/9p2i:1003:headless-seed-1003:meeting-1",
        "ml_corpus/9p2i:1005:headless-seed-1005:meeting-0",
        "ml_corpus/9p2i:1010:headless-seed-1010:meeting-1",
        "ml_corpus/9p2i:1012:headless-seed-1012:meeting-0",
        "ml_corpus/9p2i:1013:headless-seed-1013:meeting-0",
        "ml_corpus/9p2i:1015:headless-seed-1015:meeting-1",
        "ml_corpus/9p2i:1016:headless-seed-1016:meeting-1",
        "ml_corpus/9p2i:1021:headless-seed-1021:meeting-0",
        "ml_corpus/9p2i:1023:headless-seed-1023:meeting-0",
        "ml_corpus/9p2i:1026:headless-seed-1026:meeting-0",
        "ml_corpus/9p2i:1035:headless-seed-1035:meeting-3",
        "ml_corpus/9p2i:1038:headless-seed-1038:meeting-1",
        "ml_corpus/9p2i:1038:headless-seed-1038:meeting-2",
        "ml_corpus/9p2i:1040:headless-seed-1040:meeting-0",
        "ml_corpus/9p2i:1040:headless-seed-1040:meeting-2",
        "ml_corpus/9p2i:1041:headless-seed-1041:meeting-1",
        "ml_corpus/9p2i:1042:headless-seed-1042:meeting-0",
        "ml_corpus/9p2i:1046:headless-seed-1046:meeting-0",
        "ml_corpus/9p2i:1046:headless-seed-1046:meeting-1",
        "ml_corpus/9p2i:1055:headless-seed-1055:meeting-0",
        "ml_corpus/9p2i:1078:headless-seed-1078:meeting-0",
        "ml_corpus/9p2i:1079:headless-seed-1079:meeting-0",
        "ml_corpus/9p2i:1079:headless-seed-1079:meeting-2",
        "ml_corpus/9p2i:1080:headless-seed-1080:meeting-0",
        "ml_corpus/9p2i:1083:headless-seed-1083:meeting-1",
        "ml_corpus/9p2i:1093:headless-seed-1093:meeting-0",
        "ml_corpus/9p2i:1096:headless-seed-1096:meeting-0",
        "ml_corpus/9p2i:1100:headless-seed-1100:meeting-0",
        "ml_corpus/9p2i:1101:headless-seed-1101:meeting-1",
        "ml_corpus/9p2i:1103:headless-seed-1103:meeting-0",
        "ml_corpus/9p2i:1104:headless-seed-1104:meeting-0",
        "ml_corpus/9p2i:1104:headless-seed-1104:meeting-1",
        "ml_corpus/9p2i:1112:headless-seed-1112:meeting-0",
        "ml_corpus/9p2i:1114:headless-seed-1114:meeting-0",
        "ml_corpus/9p2i:1119:headless-seed-1119:meeting-0",
        "ml_corpus/9p2i:1120:headless-seed-1120:meeting-1",
        "ml_corpus/9p2i:1123:headless-seed-1123:meeting-0",
        "ml_corpus/9p2i:1124:headless-seed-1124:meeting-0",
        "ml_corpus/9p2i:1126:headless-seed-1126:meeting-0",
        "ml_corpus/9p2i:1127:headless-seed-1127:meeting-1",
        "ml_corpus/9p2i:1131:headless-seed-1131:meeting-0",
        "ml_corpus/9p2i:1133:headless-seed-1133:meeting-1",
        "ml_corpus/9p2i:1134:headless-seed-1134:meeting-0",
        "ml_corpus/9p2i:1138:headless-seed-1138:meeting-1",
        "ml_corpus/9p2i:1139:headless-seed-1139:meeting-0",
        "ml_corpus/9p2i:1144:headless-seed-1144:meeting-2",
        "ml_corpus/9p2i:1146:headless-seed-1146:meeting-0",
        "ml_corpus/9p2i:1147:headless-seed-1147:meeting-0",
        "ml_corpus/9p2i:1149:headless-seed-1149:meeting-1",
        "samples/9p2i:11:headless-seed-11:meeting-0",
        "samples/9p2i:17:headless-seed-17:meeting-0",
        "samples/9p2i:20:headless-seed-20:meeting-0",
        "samples/9p2i:20:headless-seed-20:meeting-1",
        "samples/9p2i:22:headless-seed-22:meeting-1",
        "samples/9p2i:23:headless-seed-23:meeting-0",
        "samples/9p2i:23:headless-seed-23:meeting-1",
        "samples/9p2i:24:headless-seed-24:meeting-2",
        "samples/9p2i:26:headless-seed-26:meeting-1",
        "samples/9p2i:27:headless-seed-27:meeting-0",
        "samples/9p2i:2:headless-seed-2:meeting-0",
        "samples/9p2i:30:headless-seed-30:meeting-2",
        "samples/9p2i:32:headless-seed-32:meeting-0",
        "samples/9p2i:34:headless-seed-34:meeting-1",
        "samples/9p2i:38:headless-seed-38:meeting-1",
        "samples/9p2i:40:headless-seed-40:meeting-0",
        "samples/9p2i:7:headless-seed-7:meeting-0",
    }
)
