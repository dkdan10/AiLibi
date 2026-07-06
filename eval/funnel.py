"""Information-funnel diagnostics — the oracle / possession / transmission folds.

Task 15.3 (tasks/phase-15.md; tasks/post-phase-14-clean-up.md §2, H3) promotes the
clean-up charter's three-stage information measurement into committed, reusable
``eval/`` folds, so Wave 0's effect on the meeting layer is measured by the SAME
instrument before and after, forever. The charter's baseline-2 9p2i table is this
module's reproduction gate (see :func:`compute_information_funnel` and the pins in
``tests/eval/test_funnel.py``).

The reconstruction MIRRORS ``api/replay_loader.py::_walk`` (the loader is API-tier
and carries serving concerns, so the seed/advance/apply/hash-verify loop is
mirrored directly against :mod:`orchestrator.seeder` + :mod:`engine.tick` +
:func:`orchestrator.game.apply_meeting_result`, NOT imported). Every recorded
``state_hash`` (per tick) and ``state_hash_after`` (per meeting) is verified during
the walk, so a corrupted or drifted set fails loud
(:class:`FunnelReconstructionError`) rather than silently mis-measuring.

Three stages, each a fold over the game's BODY-REPORT meetings (emergency meetings
carry no body and are excluded):

* **Stage 1 — EXISTENCE (the pooled-testimony oracle).** At each body-report
  meeting, the killer-candidate set under PERFECT sharing of every living crew
  member's legitimate same-room sightings, with alibi-elimination at the kill
  tick. Crew vision is same-room-only (:mod:`engine.visibility`), so a sighting
  is a co-location between a living crew member and another player in the recorded
  per-tick state. A living suspect is ELIMINATED when pooled crew sightings place
  them only in rooms other than the kill room at the kill tick. The reported base
  set uses the exact kill tick; a ``±1``-tick window variant additionally admits
  adjacent-tick sightings under one-hop room reachability.

* **Stage 2 — POSSESSION (the held-clue census).** Per meeting, whether at least
  one living-at-meeting crew member HOLDS hard evidence: an impostor vent
  witnessed (role-proving — vents are impostor-only), the victim last-seen-with
  the killer, the killer placed at the scene, or the kill itself witnessed.

* **Stage 3 — TRANSMISSION (what reached the meeting).** Per meeting: structured
  killer-placement observations, vent mentions in the free-text turns, whether the
  killer was accused, speakers-vs-holders, votes landing inside/outside the oracle
  candidate set, and the reporter-ejection census (the meeting ejecting its own —
  always innocent — reporter).

Oracle assumptions (this is a DIAGNOSTIC CEILING, an upper bound on what pooled
crew testimony could resolve — NOT a claim about achievable play):

* **Honest pooling.** Every living crew member's sightings are shared perfectly and
  truthfully; no crew lies, forgets, or withholds. Real meetings share far less.
* **Kill-time knowledge.** The exact kill tick + kill room are taken as known
  (from the recorded ``KilledEvent`` / ``BodyState``); real crew must INFER them.
* **Crew-only witnesses.** Only living crew members testify; impostor "sightings"
  never enter the pool.

Known method artifact — the **same-tick move+kill frame**: sightings are read from
the recorded per-tick (post-advance) positions while the kill room comes from the
``KilledEvent``. When a body is reported long after its kill, the killer may have
been ejected in an earlier meeting, so it is dead at the report meeting and drops
out of the (living-at-meeting) candidate universe — the killer then sits OUTSIDE
the reconstructed set. On the committed baseline-2 9p2i bytes this leaves the
killer inside the candidate set in 122/129 meetings (7 such late-report frames).
The artifact is a property of the reconstruction frame, not of the play.

Reproduction status (committed baseline-2 9p2i — see ``tests/eval/test_funnel.py``
and the Task-15.3 PR ``## Questions``): this instrument reproduces the charter §2
figures EXACTLY for report-meeting count (129), the exact-tick candidate set
(median 3, mean 2.86, killer-in-set 122), kill-witnessed (6), vent-witnessed (74),
**killer-at-scene (32)**, **last-seen-with-killer (37)**, vent-mentioned (36/74),
and the reporter-ejection census (22/106, all innocent). Three charter §2 figures do
NOT reproduce, and the evidence is that the charter's own rows are MUTUALLY
INCONSISTENT: (1) the ±1-window aggregates (this oracle mean 2.29 / unique 38 / ≤2 84
vs charter 2.0 / 45 / 85) — two independent exhaustive reconstructions found the
charter's row is only reachable from a move-augmented base whose OWN exact-tick set
is not 369, so no single oracle produces both the exact-tick row it reproduces and
the ±1 row; (2) hard-clue-held (98 vs 94) — with the exactly-reproduced scene 32 and
last-seen 37 the union's proven floor is 95, so 94 is below what its own component
figures allow; (3) votes-outside-a-≤3-set (37/68 vs 42/73). These are surfaced for
owner review rather than reverse-fit to an incoherent instrument; the per-meeting
rows expose the raw inputs so the figures can be re-derived under any definition.

JSON report schema (``InformationFunnelReport.model_dump()`` / the
``scripts/measure_baseline.py --funnel`` ``--json`` rows), consumed by Task 15.7
for the before/after close finding — STABLE::

    {
      "replay_set_dir": str,
      "num_players": int, "num_impostors": int, "tasks_per_crewmate": int,
      "games_total": int,
      "report_meetings": int,                 # body-report meetings folded
      # -- Stage 1 (over report_meetings) --
      "candidate_set_median": float | null,
      "candidate_set_mean": float | null,
      "candidate_set_pm1_mean": float | null,
      "unique_killer_pm1": int,               # |set|==1 under the ±1 window
      "candidate_le2_pm1": int,               # |set|<=2 under the ±1 window
      "killer_in_set": int,
      # -- Stage 2 (over report_meetings) --
      "hard_clue_held": int,
      "vent_witnessed": int, "last_seen_with_killer": int,
      "killer_at_scene": int, "kill_witnessed": int,
      # -- Stage 3 --
      "vent_mentioned": int, "vent_meetings": int,          # e.g. 36 / 74
      "killer_placement_observed": int,   # structured saw_player places killer at scene
      "killer_accused": int,              # an accusation names the killer
      "votes_outside_small_set": int, "small_set_ejections": int,  # e.g. 42 / 73
      "reporter_ejected": int, "reporter_ejected_innocent": int,   # e.g. 22 / 22
      "report_ejections": int,                                     # e.g. 106
      "per_meeting": [ MeetingFunnelRow, ... ]
    }

Pure + offline: no network, no ``AILIBI_*`` env, no LLM. The public surface
(stable — downstream tasks import these): :func:`compute_information_funnel`,
:class:`InformationFunnelReport`, :class:`MeetingFunnelRow`.
"""

from __future__ import annotations

import statistics
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, TypeAdapter

from engine.actions import Action
from engine.entities import PlayerId, Role, RoomId
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from observation.service import ObservationService
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.schemas import (
    AccusationClaim,
    MeetingResult,
    MeetingTurn,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# The candidate-set band the "votes landing outside the pooled-knowledge set"
# transmission leak is measured over (charter §2 Stage 3: "when that set was <=3").
_SMALL_SET_BAR = 3


class FunnelReconstructionError(RuntimeError):
    """A recorded state hash did not reconstruct — the set is corrupt/drifted.

    Raised during the walk when a per-tick ``state_hash`` or a meeting's
    ``state_hash_after`` disagrees with the engine reconstruction, so a drifted or
    corrupted replay set fails loud rather than silently mis-measuring (AGENTS.md
    "no silent fallbacks").
    """


# --------------------------------------------------------------------------- #
# Internal walk structures                                                     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Frame:
    """One recorded (post-advance) per-tick snapshot: each player's room + status."""

    room: Mapping[PlayerId, RoomId]
    alive: Mapping[PlayerId, bool]
    in_vent: Mapping[PlayerId, bool]


@dataclass(frozen=True)
class _VentSighting:
    """An impostor vent event and the living crew who witnessed it (same-room).

    ``witnesses`` is the crew-inclusive same-room witness set the engine records on
    the vent event (``source_witnesses`` at the room the impostor vents FROM ∪
    ``destination_witnesses`` at the room they surface IN — the exact pair
    :func:`observation.service._vent_observation_for_agent` surfaces to an observer).
    Vents are impostor-only, so a crew member in this set holds role-proving evidence.
    """

    tick: int
    actor: PlayerId
    witnesses: frozenset[PlayerId]


@dataclass(frozen=True)
class _ReportMeeting:
    """One reconstructed body-report meeting + its kill provenance."""

    seed: int
    meeting_id: str
    tick: int
    reporter: PlayerId
    outcome: str
    ejected: PlayerId | None
    victim: PlayerId
    killer: PlayerId
    kill_tick: int
    kill_room: RoomId
    kill_witnesses: frozenset[PlayerId]
    living_at_meeting: frozenset[PlayerId]
    turns: tuple[MeetingTurn, ...]
    ballots: tuple[VoteBallot, ...]


@dataclass(frozen=True)
class _GameWalk:
    """The funnel-relevant reconstruction of one recorded game.

    ``sight`` / ``moved`` are the per-tick crew perception the killer-at-scene fold
    reads: for each packet tick (the ``WorldState.tick`` the packet perceives),
    each living crew observer's ``visible_players`` (``{subject: room}`` — same-room
    sightings, plus witnessed vent/kill placements the observation layer folds in)
    and ``moved_players`` (``{subject: (from_room, to_room)}`` — a room transition the
    observer watched). Built through the real :class:`~observation.service.ObservationService`
    so a crew placement is exactly what the same-room-only firewall would surface.
    """

    seed: int
    roles: Mapping[PlayerId, Role]
    frames: Mapping[int, _Frame]
    vent_sightings: tuple[_VentSighting, ...]
    report_meetings: tuple[_ReportMeeting, ...]
    sight: Mapping[int, Mapping[PlayerId, Mapping[PlayerId, RoomId]]]
    moved: Mapping[int, Mapping[PlayerId, Mapping[PlayerId, tuple[RoomId, RoomId]]]]


def _deserialize_actions(raw_actions: Sequence[Mapping[str, object]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _frame_of(state: WorldState) -> _Frame:
    players = state.players
    return _Frame(
        room={pid: p.room for pid, p in players.items()},
        alive={pid: p.alive for pid, p in players.items()},
        in_vent={pid: p.in_vent for pid, p in players.items()},
    )


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
    """Re-seed + replay one game, collecting the funnel's reconstruction inputs.

    Mirrors ``api/replay_loader.py::_walk`` / ``eval.validity._reconstruct_game``:
    re-seed, feed the recorded actions through :func:`engine.tick.advance_tick`,
    verify every ``state_hash``, and on a MEETING tick rebuild the
    :class:`~meetings.schemas.MeetingResult` from the recorded entry and apply it
    via :func:`orchestrator.game.apply_meeting_result` (verifying
    ``state_hash_after``). Collects per-tick post-advance frames, impostor vent
    sightings, and the body-report meetings with their kill provenance.
    """

    game_id = f"headless-seed-{seed}"
    entries = read_all_entries(replay_path)
    tick_entries = [e for e in entries if isinstance(e, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        e.tick: e for e in entries if isinstance(e, MeetingReplayEntry)
    }

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    frames: dict[int, _Frame] = {}
    kill_by_victim: dict[
        PlayerId, tuple[int, RoomId, PlayerId, frozenset[PlayerId]]
    ] = {}
    vent_sightings: list[_VentSighting] = []
    report_meetings: list[_ReportMeeting] = []
    sight: dict[int, dict[PlayerId, dict[PlayerId, RoomId]]] = {}
    moved: dict[int, dict[PlayerId, dict[PlayerId, tuple[RoomId, RoomId]]]] = {}

    # The observation pipeline is re-run per living crew observer per tick so the
    # killer-at-scene fold reads exactly what the same-room-only firewall surfaces
    # (Task 12.3 / api/replay_loader.py::_walk collect_visibility). The audit log is
    # routed to a throwaway temp file; ``last_events`` is threaded EXACTLY as the
    # loader threads it — the previous tick's events (or, across a meeting, the
    # pre-meeting play events plus the meeting's post-events) — so witnessed vent /
    # kill / move placements land on the right frame and no stale movement leaks
    # onto a post-meeting tick.
    audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-funnel-")
    service = ObservationService(
        game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
    )
    last_events: tuple[EngineEvent, ...] = ()

    try:
        for entry in tick_entries:
            packet_tick = state.tick
            tick_sight: dict[PlayerId, dict[PlayerId, RoomId]] = {}
            tick_moved: dict[PlayerId, dict[PlayerId, tuple[RoomId, RoomId]]] = {}
            for pid, player in state.players.items():
                if not player.alive or roles.get(pid) != "CREWMATE":
                    continue
                packet = service.build_packet(
                    world_state=state, agent_id=pid, engine_events=last_events
                )
                tick_sight[pid] = {vp.id: vp.room for vp in packet.visible_players}
                tick_moved[pid] = {
                    mv.id: (mv.from_room, mv.to_room) for mv in packet.moved_players
                }
            sight[packet_tick] = tick_sight
            moved[packet_tick] = tick_moved

            actions = _deserialize_actions(entry.actions)
            state, events = advance_tick(state, actions, game_map=game_map)
            actual = _state_hash(state)
            if actual != entry.state_hash:
                raise FunnelReconstructionError(
                    f"{game_id}: tick {entry.tick} reconstructed {actual!r} != recorded "
                    f"{entry.state_hash!r} (roster mismatch or engine non-determinism)"
                )
            frames[entry.tick] = _frame_of(state)
            for event in events:
                if isinstance(event, KilledEvent):
                    kill_by_victim[event.target] = (
                        event.tick,
                        event.room,
                        event.actor,
                        frozenset(event.witnesses),
                    )
                elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                    if roles.get(event.actor) == "IMPOSTOR":
                        vent_sightings.append(
                            _VentSighting(
                                tick=event.tick,
                                actor=event.actor,
                                witnesses=frozenset(event.source_witnesses)
                                | frozenset(event.destination_witnesses),
                            )
                        )

            if state.phase == "GAME_OVER":
                break
            if state.phase != "MEETING":
                last_events = tuple(events)
                continue

            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                # Partial replay: a meeting opened but never resolved (crashed
                # mid-meeting). Stop the walk, matching the loader.
                break

            body_id = next(
                (
                    event.body_id
                    for event in events
                    if isinstance(event, MeetingTriggeredEvent)
                ),
                None,
            )
            if body_id is not None and body_id in state.bodies:
                body = state.bodies[body_id]
                victim = body.player_id
                kill = kill_by_victim.get(victim)
                if kill is not None:
                    kill_tick, kill_room, killer, kill_witnesses = kill
                    report_meetings.append(
                        _ReportMeeting(
                            seed=seed,
                            meeting_id=meeting_entry.meeting_id,
                            tick=entry.tick,
                            reporter=meeting_entry.triggered_by,
                            outcome=meeting_entry.outcome,
                            ejected=meeting_entry.ejected_player_id,
                            victim=victim,
                            killer=killer,
                            kill_tick=kill_tick,
                            kill_room=kill_room,
                            kill_witnesses=kill_witnesses,
                            living_at_meeting=frozenset(
                                pid for pid, p in state.players.items() if p.alive
                            ),
                            turns=tuple(meeting_entry.transcript.turns),
                            ballots=tuple(meeting_entry.ballots),
                        )
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
            pre_meeting_events = tuple(events)
            state, post_events = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                raise FunnelReconstructionError(
                    f"{game_id}: meeting at tick {entry.tick} reconstructed {after!r} "
                    f"!= recorded {meeting_entry.state_hash_after!r}"
                )
            last_events = pre_meeting_events + tuple(post_events)
            if state.phase == "GAME_OVER":
                break
    finally:
        audit_dir.cleanup()

    return _GameWalk(
        seed=seed,
        roles=roles,
        frames=frames,
        vent_sightings=tuple(vent_sightings),
        report_meetings=tuple(report_meetings),
        sight=sight,
        moved=moved,
    )


# --------------------------------------------------------------------------- #
# Stage 1 — the pooled-testimony oracle (EXISTENCE)                            #
# --------------------------------------------------------------------------- #


def _pooled_sightings(
    frame: _Frame, roles: Mapping[PlayerId, Role]
) -> dict[PlayerId, RoomId]:
    """Pool every living crew member's legitimate same-room sightings at one frame.

    Returns ``{player_id: room}`` for every player who is CO-LOCATED with a living
    crew member other than themselves (a genuine sighting — a crew member alone
    testifies to no one and self-alibi is not a sighting). Crew vision is
    same-room-only (:mod:`engine.visibility`), so co-location in the recorded frame
    IS the sighting; a vented player is invisible and never placed.
    """

    crew_by_room: dict[RoomId, list[PlayerId]] = {}
    for pid, room in frame.room.items():
        if frame.alive[pid] and not frame.in_vent[pid] and roles.get(pid) == "CREWMATE":
            crew_by_room.setdefault(room, []).append(pid)
    placed: dict[PlayerId, RoomId] = {}
    for pid, room in frame.room.items():
        if not frame.alive[pid] or frame.in_vent[pid]:
            continue
        if any(w != pid for w in crew_by_room.get(room, ())):
            placed[pid] = room
    return placed


def _candidate_universe(meeting: _ReportMeeting) -> frozenset[PlayerId]:
    """Living-at-meeting suspects, minus the victim and the reporter.

    The reporter is excluded because a pooled-testimony oracle does not suspect the
    messenger — the crew's failure to honour that is measured separately as the
    reporter-ejection leak (Stage 3). The victim is dead. The killer of a
    late-reported body may already be dead here (see the same-tick move+kill frame
    note in the module docstring), which is exactly why ``killer_in_set`` is
    ``122/129`` rather than ``129/129`` on baseline 2.
    """

    return meeting.living_at_meeting - {meeting.victim, meeting.reporter}


def _vented_at_kill_tick(
    meeting: _ReportMeeting, frames: Mapping[int, _Frame]
) -> frozenset[PlayerId]:
    """Suspects recorded IN A VENT at the kill tick — a vent alibi.

    A same-room kill requires the killer to be standing in the kill room; a player
    recorded in a vent at the kill tick therefore cannot have committed it and is
    eliminated. This is the one place the reconstruction reads a god's-eye position
    the crew could not see (a vented player is invisible), consistent with the
    oracle's kill-time-knowledge assumption — it never eliminates the killer (the
    killer is in the room, not a vent) and removes only the provably-elsewhere.
    """

    frame = frames.get(meeting.kill_tick)
    if frame is None:
        return frozenset()
    return frozenset(p for p in _candidate_universe(meeting) if frame.in_vent.get(p))


def _candidate_set_exact(
    meeting: _ReportMeeting,
    frames: Mapping[int, _Frame],
    roles: Mapping[PlayerId, Role],
) -> frozenset[PlayerId]:
    """The candidate set under alibi-elimination at the exact kill tick."""

    frame = frames.get(meeting.kill_tick)
    placed = _pooled_sightings(frame, roles) if frame is not None else {}
    vented = _vented_at_kill_tick(meeting, frames)
    return frozenset(
        p
        for p in _candidate_universe(meeting)
        if p not in vented and not (p in placed and placed[p] != meeting.kill_room)
    )


def _reachable(game_map: Map, room: RoomId) -> frozenset[RoomId]:
    """Rooms from which ``room`` is reachable in one tick (itself + neighbours)."""

    return frozenset({room, *game_map.room_neighbors(room)})


def _candidate_set_pm1(
    meeting: _ReportMeeting,
    frames: Mapping[int, _Frame],
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> frozenset[PlayerId]:
    """The candidate set under the ±1-tick kill-window variant.

    Pools sightings across ``[kill_tick-1, kill_tick, kill_tick+1]``: a suspect is
    alibied by an exact-tick sighting away from the kill room, OR by an adjacent-tick
    sighting in a room from which the kill room is UNREACHABLE in one hop (they could
    not have been at the scene at the kill tick). A suspect placed AT the kill room
    at the exact tick stays a candidate regardless (they were at the scene).
    """

    R = meeting.kill_room
    t = meeting.kill_tick
    reach = _reachable(game_map, R)
    vented = _vented_at_kill_tick(meeting, frames)
    placed = {
        dt: _pooled_sightings(frames[t + dt], roles)
        for dt in (-1, 0, 1)
        if (t + dt) in frames
    }
    out: set[PlayerId] = set()
    for p in _candidate_universe(meeting):
        if p in vented:
            continue
        at_scene = p in placed.get(0, {}) and placed[0][p] == R
        alibied = False
        if not at_scene:
            if p in placed.get(0, {}) and placed[0][p] != R:
                alibied = True
            if p in placed.get(-1, {}) and placed[-1][p] not in reach:
                alibied = True
            if p in placed.get(1, {}) and placed[1][p] not in reach:
                alibied = True
        if not alibied:
            out.add(p)
    return frozenset(out)


# --------------------------------------------------------------------------- #
# Stage 2 — the held-clue census (POSSESSION)                                 #
# --------------------------------------------------------------------------- #


def _living_crew(
    meeting: _ReportMeeting, roles: Mapping[PlayerId, Role]
) -> frozenset[PlayerId]:
    return frozenset(p for p in meeting.living_at_meeting if roles.get(p) == "CREWMATE")


def _holds_vent(meeting: _ReportMeeting, walk: _GameWalk) -> bool:
    """A living-at-meeting crew member witnessed an impostor vent before the meeting.

    Role-proving (vents are impostor-only). The window is STRICTLY before the
    meeting-trigger tick: a vent seen on the report tick itself is not held going
    INTO the meeting.
    """

    crew = _living_crew(meeting, walk.roles)
    return any(
        vs.tick < meeting.tick and bool(vs.witnesses & crew)
        for vs in walk.vent_sightings
    )


def _holds_kill_witnessed(
    meeting: _ReportMeeting, roles: Mapping[PlayerId, Role]
) -> bool:
    """A living-at-meeting crew member witnessed the kill itself."""

    return bool(meeting.kill_witnesses & _living_crew(meeting, roles))


def _holds_scene(meeting: _ReportMeeting, walk: _GameWalk) -> bool:
    """A living-at-meeting crew member places the killer at the scene (kill room).

    Reads the reconstructed crew perception at the kill-result frame and the one
    after (packet ticks ``kill_tick+1`` / ``+2``): a living-at-meeting crew member
    (the reporter included — they were at the body, so their placement counts) who
    SAW the killer in the kill room (``visible_players`` — co-location, or a
    witnessed vent/kill the observation layer folds into the same channel) OR who
    WATCHED the killer move into/out of the kill room (``moved_players`` — a room
    transition touching the scene). The move channel is what raw co-location misses:
    a crew member who watched the killer walk into the kill room has placed them
    there just as surely as one standing in it.

    The window is capped at the meeting-trigger tick: when the body is reported on
    the very next tick (``meeting.tick == kill_tick + 1``), the ``kill_tick + 2``
    packet is a post-meeting resumed-play frame — not evidence anyone held going
    INTO the meeting — so it must not count (Stage-2 possession is what the crew
    brought to the vote).
    """

    crew = _living_crew(meeting, walk.roles)
    killer = meeting.killer
    room = meeting.kill_room
    for packet_tick in (meeting.kill_tick + 1, meeting.kill_tick + 2):
        if packet_tick > meeting.tick:
            continue
        seen = walk.sight.get(packet_tick, {})
        transitions = walk.moved.get(packet_tick, {})
        for observer in crew:
            if seen.get(observer, {}).get(killer) == room:
                return True
            transition = transitions.get(observer, {}).get(killer)
            if transition is not None and room in transition:
                return True
    return False


def _holds_last_seen_with_killer(
    meeting: _ReportMeeting,
    frames: Mapping[int, _Frame],
    roles: Mapping[PlayerId, Role],
) -> bool:
    """Some crew member's LAST sighting of the living victim placed them with the killer.

    Per-crew (each living crew member other than the reporter, whose proximity to
    the body at report time is separately the reporter-ejection leak): walk backward
    from the kill tick to that crew member's most recent co-location with the
    still-alive victim; the clue is held iff the killer shared that room. A single
    crew member whose last look at the victim caught the killer beside them suffices.

    A killer hidden IN A VENT in that room does not count: a vented player is
    invisible to same-room observers (:mod:`engine.visibility`), so the observer
    only ever saw the victim, never the vent-concealed killer. (Only the killer can
    be vented here — vents are impostor-only and kill targets/observers are crew.)
    """

    crew = _living_crew(meeting, roles) - {meeting.reporter}
    V = meeting.victim
    K = meeting.killer
    ticks = sorted((t for t in frames if t <= meeting.kill_tick), reverse=True)
    for observer in crew:
        for t in ticks:
            frame = frames[t]
            if not (frame.alive.get(V, False) and frame.alive.get(observer, False)):
                continue
            if frame.room.get(observer) != frame.room.get(V):
                continue
            if frame.room.get(K) == frame.room.get(V) and not frame.in_vent.get(K):
                return True
            break  # only this crew member's LAST co-location with the victim counts
    return False


def _holds_hard_clue(meeting: _ReportMeeting, walk: _GameWalk) -> bool:
    return (
        _holds_vent(meeting, walk)
        or _holds_kill_witnessed(meeting, walk.roles)
        or _holds_scene(meeting, walk)
        or _holds_last_seen_with_killer(meeting, walk.frames, walk.roles)
    )


# --------------------------------------------------------------------------- #
# Stage 3 — what reached the meeting (TRANSMISSION)                            #
# --------------------------------------------------------------------------- #


def _mentions_vent(turns: Sequence[MeetingTurn]) -> bool:
    """Any turn's free text names a vent (the only channel a v4 vent claim has)."""

    return any("vent" in (turn.free_text or "").lower() for turn in turns)


def _has_killer_placement_observation(meeting: _ReportMeeting) -> bool:
    """A structured ``saw_player`` observation places the killer in the kill room."""

    return any(
        isinstance(obs, SawPlayerObservation)
        and obs.subject == meeting.killer
        and obs.room == meeting.kill_room
        for turn in meeting.turns
        for obs in turn.observations
    )


def _killer_accused(meeting: _ReportMeeting) -> bool:
    """Any accusation names the killer."""

    return any(
        isinstance(claim, AccusationClaim) and claim.against == meeting.killer
        for turn in meeting.turns
        for claim in turn.claims
    )


def _reporter_ejected(meeting: _ReportMeeting) -> bool:
    return meeting.outcome == "EJECTED" and meeting.ejected == meeting.reporter


# --------------------------------------------------------------------------- #
# Report types (public, stable)                                               #
# --------------------------------------------------------------------------- #


class MeetingFunnelRow(BaseModel):
    """The three-stage funnel measurement for ONE body-report meeting (frozen).

    Stage 1 (``candidate_*`` / ``killer_in_set*``) is the pooled-testimony oracle;
    Stage 2 (``holds_*`` / ``hard_clue_held``) the held-clue census; Stage 3 the
    rest (transmission). ``vote_outside_candidate_set`` is ``None`` unless the
    meeting ejected someone with a candidate set of size ``<= 3`` (the band the
    charter's "votes outside the set" leak is measured over).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    meeting_id: str
    tick: int
    reporter: PlayerId
    outcome: str
    ejected: PlayerId | None
    victim: PlayerId
    killer: PlayerId
    kill_tick: int
    kill_room: RoomId
    # Stage 1
    candidate_set: tuple[PlayerId, ...]
    candidate_set_size: int
    candidate_set_pm1_size: int
    killer_in_set: bool
    killer_in_set_pm1: bool
    unique_killer_pm1: bool
    # Stage 2
    holds_vent: bool
    holds_last_seen_with_killer: bool
    holds_scene: bool
    holds_kill_witnessed: bool
    hard_clue_held: bool
    # Stage 3
    vent_mentioned: bool
    killer_placement_observed: bool
    killer_accused: bool
    reporter_ejected: bool
    reporter_ejected_innocent: bool
    vote_outside_candidate_set: bool | None


class InformationFunnelReport(BaseModel):
    """The information-funnel diagnostics over one replay set (frozen value object).

    Aggregates the per-meeting rows into the charter §2 figures (see the module
    docstring JSON schema). ``candidate_set_*`` medians/means are ``None`` (not
    ``0.0``) when the set has no body-report meetings, mirroring the ``eval``
    empty-denominator convention.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    report_meetings: int
    # Stage 1
    candidate_set_median: float | None
    candidate_set_mean: float | None
    candidate_set_pm1_mean: float | None
    unique_killer_pm1: int
    candidate_le2_pm1: int
    killer_in_set: int
    # Stage 2
    hard_clue_held: int
    vent_witnessed: int
    last_seen_with_killer: int
    killer_at_scene: int
    kill_witnessed: int
    # Stage 3
    vent_mentioned: int
    vent_meetings: int
    killer_placement_observed: int
    killer_accused: int
    votes_outside_small_set: int
    small_set_ejections: int
    reporter_ejected: int
    reporter_ejected_innocent: int
    report_ejections: int
    per_meeting: tuple[MeetingFunnelRow, ...]


def _meeting_row(
    meeting: _ReportMeeting,
    walk: _GameWalk,
    game_map: Map,
) -> MeetingFunnelRow:
    frames = walk.frames
    roles = walk.roles
    exact = _candidate_set_exact(meeting, frames, roles)
    pm1 = _candidate_set_pm1(meeting, frames, roles, game_map)
    small_set = meeting.outcome == "EJECTED" and len(exact) <= _SMALL_SET_BAR
    vote_outside = (meeting.ejected not in exact) if small_set else None
    return MeetingFunnelRow(
        seed=meeting.seed,
        meeting_id=meeting.meeting_id,
        tick=meeting.tick,
        reporter=meeting.reporter,
        outcome=meeting.outcome,
        ejected=meeting.ejected,
        victim=meeting.victim,
        killer=meeting.killer,
        kill_tick=meeting.kill_tick,
        kill_room=meeting.kill_room,
        candidate_set=tuple(sorted(exact)),
        candidate_set_size=len(exact),
        candidate_set_pm1_size=len(pm1),
        killer_in_set=meeting.killer in exact,
        killer_in_set_pm1=meeting.killer in pm1,
        unique_killer_pm1=len(pm1) == 1,
        holds_vent=_holds_vent(meeting, walk),
        holds_last_seen_with_killer=_holds_last_seen_with_killer(
            meeting, frames, roles
        ),
        holds_scene=_holds_scene(meeting, walk),
        holds_kill_witnessed=_holds_kill_witnessed(meeting, roles),
        hard_clue_held=_holds_hard_clue(meeting, walk),
        vent_mentioned=_mentions_vent(meeting.turns),
        killer_placement_observed=_has_killer_placement_observation(meeting),
        killer_accused=_killer_accused(meeting),
        reporter_ejected=_reporter_ejected(meeting),
        reporter_ejected_innocent=_reporter_ejected(meeting)
        and roles.get(meeting.reporter) == "CREWMATE",
        vote_outside_candidate_set=vote_outside,
    )


def compute_information_funnel(sample_dir: Path) -> InformationFunnelReport:
    """Fold a replay set's committed bytes into the three-stage funnel diagnostics.

    Re-seeds every game from the set's roster (``roster.json`` via
    :func:`eval.validity.resolve_roster_knobs`; the flat 4p1i default otherwise),
    walks each recorded action stream through the engine with per-tick + per-meeting
    state-hash verification (:func:`_walk_game`), and folds every body-report meeting
    into the oracle / possession / transmission census. Runs on any replay-set
    directory and on both roster presets. Pure and offline.
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
        raise ValueError(f"no replay-seed-*.jsonl found under {sample_dir}")

    rows: list[MeetingFunnelRow] = []
    for seed in seeds:
        walk = _walk_game(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            game_map=game_map,
        )
        for meeting in walk.report_meetings:
            rows.append(_meeting_row(meeting, walk, game_map))

    n = len(rows)
    sizes = [r.candidate_set_size for r in rows]
    pm1_sizes = [r.candidate_set_pm1_size for r in rows]
    small_rows = [r for r in rows if r.vote_outside_candidate_set is not None]
    vent_rows = [r for r in rows if r.holds_vent]
    report_ejections = sum(1 for r in rows if r.outcome == "EJECTED")
    return InformationFunnelReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(seeds),
        report_meetings=n,
        candidate_set_median=statistics.median(sizes) if sizes else None,
        candidate_set_mean=statistics.fmean(sizes) if sizes else None,
        candidate_set_pm1_mean=statistics.fmean(pm1_sizes) if pm1_sizes else None,
        unique_killer_pm1=sum(1 for r in rows if r.unique_killer_pm1),
        candidate_le2_pm1=sum(1 for r in rows if r.candidate_set_pm1_size <= 2),
        killer_in_set=sum(1 for r in rows if r.killer_in_set),
        hard_clue_held=sum(1 for r in rows if r.hard_clue_held),
        vent_witnessed=len(vent_rows),
        last_seen_with_killer=sum(1 for r in rows if r.holds_last_seen_with_killer),
        killer_at_scene=sum(1 for r in rows if r.holds_scene),
        kill_witnessed=sum(1 for r in rows if r.holds_kill_witnessed),
        vent_mentioned=sum(1 for r in vent_rows if r.vent_mentioned),
        vent_meetings=len(vent_rows),
        killer_placement_observed=sum(1 for r in rows if r.killer_placement_observed),
        killer_accused=sum(1 for r in rows if r.killer_accused),
        votes_outside_small_set=sum(
            1 for r in small_rows if r.vote_outside_candidate_set
        ),
        small_set_ejections=len(small_rows),
        reporter_ejected=sum(1 for r in rows if r.reporter_ejected),
        reporter_ejected_innocent=sum(1 for r in rows if r.reporter_ejected_innocent),
        report_ejections=report_ejections,
        per_meeting=tuple(rows),
    )


__all__ = [
    "FunnelReconstructionError",
    "InformationFunnelReport",
    "MeetingFunnelRow",
    "compute_information_funnel",
]
