"""Information-funnel diagnostics — the oracle / possession / transmission folds.

Task 15.3 (tasks/phase-15.md; tasks/post-phase-14-clean-up.md §2, H3) promotes the
clean-up charter's three-stage information measurement into committed, reusable
``eval/`` folds, so Wave 0's effect on the meeting layer is measured by the SAME
instrument before and after, forever. The charter's baseline-2 9p2i table is this
module's reproduction gate (see :func:`compute_information_funnel` and the pins in
``tests/eval/test_funnel.py``).

The reconstruction runs on :func:`eval.replay_walk.walk_replay` under the named
``funnel-instrument`` profile (Task 19.25 consolidated the formerly mirrored
seed/advance/apply/hash-verify loop; the loader stays API-tier and separate).
Every recorded state hash is verified during the walk — the per-tick
``state_hash`` and each meeting row's ``state_hash_before`` /
``state_hash_after`` — so a corrupted or drifted set fails loud
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
  killer-placement observations, vent mentions in the free-text turns, structured
  ``SawVentObservation`` uptake (the H4 gauge — 0 on the v4 baselines that predate
  the type), whether the killer was accused, votes landing inside/outside the
  oracle candidate set, and the reporter-ejection census (the meeting ejecting its
  own — always innocent — reporter).

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

Reproduction status (committed baseline-2 9p2i — pinned in
``tests/eval/test_funnel.py``): this instrument reproduces every charter §2 figure
EXACTLY — report-meeting count (129), the exact-tick candidate set (median 3, mean
2.86, killer-in-set 122), the ±1-window aggregates (mean 2.29, singleton 38 of which killer-unique 36, ≤2 84),
kill-witnessed (6), vent-witnessed (74), killer-at-scene (32),
last-seen-with-killer (37), hard-clue-held (98), vent-mentioned (36/74),
votes-outside-a-≤3-set (37/68), and the reporter-ejection census (22/106, all
innocent). Provenance note: the charter's ±1-window / hard-clue-union /
votes-outside cells were CORRECTED to these values (owner decision, 2026-07-07 —
see the charter §2 preamble) after two independent exhaustive reconstructions
proved the 2026-07-05 one-off script's cells (2.0 / 45 / 85, 94, 42/73) mutually
inconsistent with its own exact-tick row — e.g. the only ±1 rule reaching mean 2.0
wrongly alibis a killer in transit (killer-in-set 122 → 110). The committed
instrument is authoritative; the per-meeting rows expose the raw inputs so any
figure can be re-derived under an alternative definition without another walk.

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
      "candidate_singleton_pm1": int,         # |set|==1 under the ±1 window
      "unique_killer_pm1": int,               # |set|=={killer} under the ±1 window
      "candidate_le2_pm1": int,               # |set|<=2 under the ±1 window
      "killer_in_set": int,
      # -- Stage 2 (over report_meetings) --
      "hard_clue_held": int,
      "vent_witnessed": int, "last_seen_with_killer": int,
      "killer_at_scene": int, "kill_witnessed": int,
      # -- Stage 3 --
      "vent_mentioned": int, "vent_meetings": int,          # e.g. 36 / 74
      "structured_vent_observed": int,    # witnessed-vent meetings w/ a structured
                                          # SawVentObservation (H4 uptake; 0 on v4)
      "killer_placement_observed": int,   # structured saw_player places killer at
                                          # scene within [kill_tick-1, meeting tick]
      "killer_accused": int,              # an accusation names the killer
      "votes_outside_small_set": int, "small_set_ejections": int,  # e.g. 42 / 73
      "reporter_ejected": int, "reporter_ejected_innocent": int,   # e.g. 22 / 22
      "report_ejections": int,                                     # e.g. 106
      "killer_self_reported": int,        # messenger-innocent-prior tripwire (0 on
                                          # baseline 2; non-zero => do not read the
                                          # Stage-1 rows naively)
      "per_meeting": [ MeetingFunnelRow, ... ]
    }

Pure + offline: no network, no ``AILIBI_*`` env, no LLM. The public surface
(stable — downstream tasks import these): :func:`compute_information_funnel`,
:class:`InformationFunnelReport`, :class:`MeetingFunnelRow`.
"""

from __future__ import annotations

import re
import statistics
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from pydantic import BaseModel, ConfigDict

from agents.perception import ingest_packet
from engine.entities import PlayerId, Role, RoomId
from engine.events import (
    KilledEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.world import Map, WorldState, load_canonical_map
from observation.service import ObservationService
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkViolation,
    walk_replay,
)
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.manager import derive_reported_testimony, extract_belief_evidence
from meetings.render_contract import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    TurnKind,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (
    MeetingTriggerKind,
    grounded_vouch_subjects,
    reconstruct_stated_paths,
)
from orchestrator.game import TacticalAgent, build_default_agent_factory
from orchestrator.replay import LLMCallRecord

# The candidate-set band the "votes landing outside the pooled-knowledge set"
# transmission leak is measured over (charter §2 Stage 3: "when that set was <=3").
_SMALL_SET_BAR = 3

# A vent MENTION is a word starting with "vent" (vent / vents / vented / venting),
# never a mere substring hit inside "event" / "prevent" / "eventually" — those
# would overstate the transmission metric on corpora that phrase around the word.
_VENT_MENTION_RE = re.compile(r"\bvent", re.IGNORECASE)


class FunnelReconstructionError(RuntimeError):
    """The recording does not reconstruct here — corrupt, drifted, or off-substrate.

    Raised during the walk when a per-tick ``state_hash`` or a meeting's
    ``state_hash_after`` disagrees with the engine reconstruction, when a MEETING
    tick carries no meeting row, or when the recording's ``game_over`` stamp
    names a graduated lever OFF — so a drifted, corrupted or earlier-substrate
    replay set fails loud rather than silently mis-measuring (AGENTS.md "no
    silent fallbacks").
    """


def _raise_walk_violation(violation: WalkViolation) -> NoReturn:
    """The ``funnel-instrument`` profile's violation hook (both walks share it)."""

    game_id = violation.game_id
    if violation.kind == "tick_hash_mismatch":
        raise FunnelReconstructionError(
            f"{game_id}: tick {violation.tick} reconstructed {violation.actual!r} "
            f"!= recorded "
            f"{violation.expected!r} (roster mismatch or engine non-determinism)"
        )
    if violation.kind == "missing_meeting_row":
        # DELIBERATE divergence from the loader here: the loader SERVES a
        # partial replay (a run that crashed mid-meeting) by truncating the
        # timeline, but a measurement instrument must never silently
        # under-count — a MEETING tick with no (or a tick-drifted) meeting
        # row would drop every later body-report meeting from the folds
        # while the CLI exits 0. Fail loud instead.
        raise FunnelReconstructionError(
            f"{game_id}: tick {violation.tick} entered MEETING but the replay "
            "carries no meeting row for that tick (partial recording or "
            "drifted meeting tick) — refusing to silently under-measure"
        )
    if violation.kind == "meeting_pre_hash_mismatch":
        # The meeting row's OWN pre-hash must also match the reconstruction —
        # the tick row's hash does not cover it: a tampered/drifted
        # ``state_hash_before`` on the meeting row alone would otherwise pass
        # silently ("every recorded state hash is verified during the walk").
        raise FunnelReconstructionError(
            f"{game_id}: meeting at tick {violation.tick} recorded "
            f"state_hash_before {violation.expected!r} != "
            f"reconstructed pre-meeting state {violation.actual!r}"
        )
    if violation.kind == "meeting_post_hash_mismatch":
        raise FunnelReconstructionError(
            f"{game_id}: meeting at tick {violation.tick} reconstructed "
            f"{violation.actual!r} "
            f"!= recorded {violation.expected!r}"
        )
    if violation.kind == "retired_levers_stamped_off":
        # The folds re-derive rules whose env gates were deleted at the records
        # that adopted them, so bytes stamped at an earlier substrate would be
        # scored under a substrate the game never ran.
        raise FunnelReconstructionError(
            f"{game_id}: the recording stamps retired lever(s) "
            f"{list(violation.levers)} OFF — this build can only re-derive the "
            "unconditional substrate, so the funnel cells would not describe "
            "the recorded game"
        )
    raise FunnelReconstructionError(  # pragma: no cover - profile never enables it
        f"{game_id}: unexpected walk violation {violation.kind!r}"
    )


# The named Task 19.25 profile (see eval/replay_walk.py's drift record), shared
# by BOTH funnel walks: every recorded hash verified (per-tick + meeting
# before/after), missing meeting row fail-loud, and a recording stamping a
# graduated lever OFF refused before the first advance. The vj walk's
# trigger-event and living-vs-voters checks are consumer semantics in its own
# fold.
_WALK_CONFIG: ReplayWalkConfig = ReplayWalkConfig(
    profile="funnel-instrument",
    on_violation=_raise_walk_violation,
    verify_tick_hashes=True,
    verify_action_dispositions=True,
    missing_meeting_row="violation",
    verify_meeting_pre_hashes=True,
    verify_meeting_post_hashes=True,
    reject_retired_levers_stamped_off=True,
)


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

    The engine walk is :func:`eval.replay_walk.walk_replay` under the named
    ``funnel-instrument`` profile (Task 19.25; the walker's docstring is the
    drift record): every recorded hash verified — per-tick ``state_hash`` plus
    each meeting's ``state_hash_before`` / ``state_hash_after`` — and a MEETING
    tick with no meeting row FAILS LOUD (the deliberate divergence from the
    serving loader: an instrument must never silently under-count). Collects
    per-tick post-advance frames, impostor vent sightings, and the body-report
    meetings with their kill provenance.
    """

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
    # routed to a throwaway temp file; ``last_events`` is threaded by the walker
    # EXACTLY as the loader threads it — the previous tick's events (or, across a
    # meeting, the pre-meeting play events plus the meeting's post-events) — so
    # witnessed vent / kill / move placements land on the right frame and no stale
    # movement leaks onto a post-meeting tick.
    audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-funnel-")
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
                packet_tick = state.tick
                tick_sight: dict[PlayerId, dict[PlayerId, RoomId]] = {}
                tick_moved: dict[PlayerId, dict[PlayerId, tuple[RoomId, RoomId]]] = {}
                for pid, player in state.players.items():
                    if not player.alive or roles.get(pid) != "CREWMATE":
                        continue
                    packet = service.build_packet(
                        world_state=state,
                        agent_id=pid,
                        engine_events=walk_event.last_events,
                    )
                    tick_sight[pid] = {vp.id: vp.room for vp in packet.visible_players}
                    tick_moved[pid] = {
                        mv.id: (mv.from_room, mv.to_room) for mv in packet.moved_players
                    }
                sight[packet_tick] = tick_sight
                moved[packet_tick] = tick_moved
            elif isinstance(walk_event, TickAdvanced):
                frames[walk_event.entry.tick] = _frame_of(walk_event.state)
                for event in walk_event.events:
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
            elif isinstance(walk_event, MeetingOpened):
                meeting_entry = walk_event.entry
                body_id = walk_event.body_id
                state = walk_event.state
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
                                tick=meeting_entry.tick,
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

    Witness liveness is evaluated AT THE SIGHTING FRAME, deliberately: a witness
    who saw the suspect and later died before the report meeting still contributes
    — Stage 1 measures what information EXISTED in the world (the diagnostic
    ceiling), not what survived to the vote; survival-to-meeting is exactly what
    the Stage-2 possession census filters on. This is the charter-ratified
    definition behind the pinned §2 Stage-1 figures.
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

    The messenger-innocent exclusion is a PRIOR calibrated on the measured corpus
    (impostors essentially never self-report on baseline 2 — the H5 base rate),
    not a rule of the game: the engine permits a killer to report their own
    victim, and a future learned impostor could game the prior by self-reporting
    to exit every candidate set. That failure is made LOUD, not silent — the
    ``killer_self_reported`` aggregate (0 on both committed sets) trips on any
    such meeting, and the per-meeting rows carry ``reporter``/``killer`` so every
    Stage-1 figure can be recomputed under a no-exclusion variant.
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

    The reporter exclusion is the charter-ratified definition behind the pinned
    37/129 (the reporter's evidence still counts through every OTHER possession
    channel — scene, vent, kill-witnessed): this channel isolates third-party
    "last seen with" testimony from the reporter's discovery-adjacent knowledge,
    the signal the reporter-ejection leak shows meetings already over-weight. A
    reporter-inclusive variant is recomputable from the per-meeting rows.
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
    """Any turn's free text names a vent (the only channel a v4 vent claim has).

    Word-prefix match (:data:`_VENT_MENTION_RE`): "vent" / "vents" / "vented" /
    "venting" count; a substring hit inside "event" / "prevent" never does.
    Reproduces 36/74 on the committed baseline-2 bytes identically to a raw
    substring scan (no corpus meeting turns on the difference) while staying
    robust on future recordings.
    """

    return any(_VENT_MENTION_RE.search(turn.free_text or "") for turn in turns)


def _has_structured_vent_observation(meeting: _ReportMeeting) -> bool:
    """Any turn carries a STRUCTURED :class:`SawVentObservation` (Task 15.4's type).

    The H4 uptake gauge: the charter's target is the share of witnessed-vent
    meetings carrying a structured vent observation (0% on the v4 baselines,
    which predate the type; Task 15.7 measures the v5 uptake from this fold).
    """

    return any(
        isinstance(obs, SawVentObservation)
        for turn in meeting.turns
        for obs in turn.observations
    )


def _has_killer_placement_observation(meeting: _ReportMeeting) -> bool:
    """A structured ``saw_player`` places the killer in the kill room AROUND the kill.

    The observation's spoken tick must fall in ``[kill_tick - 1, meeting tick]`` —
    at or just before the kill (the same ±1-tick kill-window knowledge the oracle's
    window variant grants) through the report. A sighting of the killer in that
    room from well BEFORE the kill is a stale placement, not scene testimony, and a
    tick after the meeting fired is not something the speaker could have seen.
    """

    return any(
        isinstance(obs, SawPlayerObservation)
        and obs.subject == meeting.killer
        and obs.room == meeting.kill_room
        and (meeting.kill_tick - 1) <= obs.tick <= meeting.tick
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
    # The ±1-window set narrowed to EXACTLY the killer (a singleton that misses
    # the killer — a dead-killer late report — is NOT unique-killer; the size-1
    # census is derivable from candidate_set_pm1_size).
    unique_killer_pm1: bool
    # Stage 2
    holds_vent: bool
    holds_last_seen_with_killer: bool
    holds_scene: bool
    holds_kill_witnessed: bool
    hard_clue_held: bool
    # Stage 3
    vent_mentioned: bool
    structured_vent_observed: bool
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
    candidate_singleton_pm1: int
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
    structured_vent_observed: int
    killer_placement_observed: int
    killer_accused: int
    votes_outside_small_set: int
    small_set_ejections: int
    reporter_ejected: int
    reporter_ejected_innocent: int
    report_ejections: int
    # Tripwire for the oracle's messenger-innocent prior (see
    # :func:`_candidate_universe`): meetings whose reporter IS the killer. 0 on
    # both committed baseline-2 sets; a non-zero reading on a future (e.g.
    # learned-policy) set means the reporter-exclusion prior is being gamed and
    # the Stage-1 rows must not be read naively.
    killer_self_reported: int
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
        unique_killer_pm1=len(pm1) == 1 and meeting.killer in pm1,
        holds_vent=_holds_vent(meeting, walk),
        holds_last_seen_with_killer=_holds_last_seen_with_killer(
            meeting, frames, roles
        ),
        holds_scene=_holds_scene(meeting, walk),
        holds_kill_witnessed=_holds_kill_witnessed(meeting, roles),
        hard_clue_held=_holds_hard_clue(meeting, walk),
        vent_mentioned=_mentions_vent(meeting.turns),
        structured_vent_observed=_has_structured_vent_observation(meeting),
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
        candidate_singleton_pm1=sum(1 for r in rows if r.candidate_set_pm1_size == 1),
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
        # The H4 uptake share's numerator: witnessed-vent meetings carrying a
        # structured SawVentObservation (denominator = vent_meetings, exactly as
        # vent_mentioned).
        structured_vent_observed=sum(
            1 for r in vent_rows if r.structured_vent_observed
        ),
        killer_placement_observed=sum(1 for r in rows if r.killer_placement_observed),
        killer_accused=sum(1 for r in rows if r.killer_accused),
        votes_outside_small_set=sum(
            1 for r in small_rows if r.vote_outside_candidate_set
        ),
        small_set_ejections=len(small_rows),
        reporter_ejected=sum(1 for r in rows if r.reporter_ejected),
        reporter_ejected_innocent=sum(1 for r in rows if r.reporter_ejected_innocent),
        report_ejections=report_ejections,
        killer_self_reported=sum(1 for r in rows if r.killer == r.reporter),
        per_meeting=tuple(rows),
    )


# --------------------------------------------------------------------------- #
# Task 16.10 pooling-folds extension region (additive — the 15.3 folds above   #
# are untouched).                                                              #
#                                                                              #
# The V&J instruments' pooling census over EVERY resolved meeting (body-report #
# AND emergency — pooling mechanisms are per-meeting, not per-body): roll-call #
# coverage, vouch + GROUNDED-vouch rates, absence-set size distribution, and   #
# the whereabouts-lie detection rate. Diagnostics the 16.17 close QUOTES —     #
# nothing here gates; the referee (eval/watchability.py) alone gates.          #
#                                                                              #
# The walk (:func:`_walk_game_vj`) extends the 15.3 replay reconstruction with #
# the ONE layer the 15.3 walk deliberately omitted: per-agent memory. It       #
# mirrors ``orchestrator.game._run_loop``'s feeding exactly — per tick, the    #
# pre-advance observation packet of every living player is ingested into a     #
# real per-agent :class:`~orchestrator.game.TacticalAgent` memory              #
# (``agents.perception.ingest_packet``, the same call ``decide()`` makes), and #
# at each meeting boundary the recorded result is absorbed through the same    #
# ``extract_belief_evidence`` / ``derive_reported_testimony`` fan-out the      #
# orchestrator runs — so the meeting-open snapshots this walk takes            #
# (suspicion graphs, sighting records, observation-id sets) are read off the   #
# PRODUCTION accessors, byte-equal to what the live meeting saw. The           #
# reconstruction fidelity is pinned by eval/vj_instruments.py's rendered-value #
# cross-check (every per-player suspicion in the committed vote prompts        #
# reproduces exactly).                                                         #
#                                                                              #
# The accessors read no environment at all: every lever they once consulted    #
# graduated, so the instrument is pure and $0 (no ``AILIBI_*`` reads) and the   #
# snapshots reproduce the baseline-7 substrate the committed sets were          #
# recorded under.                                                               #
#                                                                               #
# This walk reads the replay through ``eval.replay_walk``, which calls          #
# ``read_all_entries`` directly and performs NO substrate check — unlike the    #
# API replay loader, and unlike the audit workflows' re-extraction spine, which #
# refuses a stamp naming a retired lever OFF. Run against a recording made      #
# under an EARLIER substrate this region would therefore reconstruct current    #
# always-on memory and belief state over legacy bytes, and the divergence is    #
# NOT confined to the J1-clamped rendered scalar: retired rules (the absence    #
# prior, the evidence-quality fold) move the typed decomposition too. The vj    #
# rendered cross-check counts a rendered divergence but does not gate it, so    #
# the committed sets are the only inputs these numbers are stated for.          #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _VJMeeting:
    """One reconstructed meeting + the meeting-open agent-memory snapshots.

    The carrier the pooling folds (this region) and the judgment folds
    (:mod:`eval.vj_instruments`) both read. ``living`` is the living-player set
    at meeting open (== the recorded ballot voters — verified during the walk);
    the ``*_by_*`` mappings are the production accessor snapshots taken exactly
    where ``orchestrator.game._build_participants`` takes them.
    """

    seed: int
    meeting_id: str
    tick: int
    trigger_kind: MeetingTriggerKind
    triggered_by: PlayerId
    outcome: str
    ejected: PlayerId | None
    living: frozenset[PlayerId]
    transcript: MeetingTranscript
    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...]
    llm_calls: tuple[LLMCallRecord, ...]
    suspicion_graph_by_voter: Mapping[PlayerId, tuple[SuspicionEntry, ...]]
    sighting_records_by_speaker: Mapping[PlayerId, tuple[SightingRecord, ...]]
    observation_ids_by_voter: Mapping[PlayerId, frozenset[str]]
    fellow_impostor_ids_by_voter: Mapping[PlayerId, tuple[PlayerId, ...]]


@dataclass(frozen=True)
class _VJGameWalk:
    """The memory-augmented reconstruction of one recorded game (all meetings)."""

    seed: int
    roles: Mapping[PlayerId, Role]
    meetings: tuple[_VJMeeting, ...]


def _walk_game_vj(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    roles: Mapping[PlayerId, Role],
    game_map: Map,
) -> _VJGameWalk:
    """Re-seed + replay one game with the per-agent memory layer reconstructed.

    Shares :func:`_walk_game`'s engine walk — :func:`eval.replay_walk.walk_replay`
    under the same ``funnel-instrument`` profile (same hash verification, same
    fail-loud on a MEETING tick without a meeting row) — and adds the live
    game's memory feeding: real :class:`~orchestrator.game.TacticalAgent`
    instances (the default factory, exactly what the recorded games ran)
    ingest every living player's pre-advance packet each tick, and each
    meeting's recorded result is absorbed post-apply through the same
    ``extract_belief_evidence`` + ``derive_reported_testimony`` fan-out as
    ``orchestrator.game._absorb_meeting_beliefs`` — sorted iteration, living
    players in the post-meeting state. Collects EVERY meeting (emergency
    included) with its meeting-open accessor snapshots. Two vj-only checks are
    consumer semantics layered in this fold, not walker options: a MEETING
    transition without a :class:`~engine.events.MeetingTriggeredEvent`, and a
    reconstructed living set differing from the recorded ballot voters.
    """

    game_id = f"headless-seed-{seed}"
    factory = build_default_agent_factory()
    agents: dict[PlayerId, TacticalAgent] = {}
    for pid in sorted(roles):
        agent = factory(pid, roles[pid])
        if not isinstance(agent, TacticalAgent):  # pragma: no cover - factory pin
            raise TypeError(
                "build_default_agent_factory returned a non-TacticalAgent; the "
                "memory-augmented walk mirrors the production accessors and "
                "cannot proceed without them"
            )
        agents[pid] = agent
    impostor_ids = tuple(
        sorted(pid for pid, role in roles.items() if role == "IMPOSTOR")
    )

    meetings: list[_VJMeeting] = []
    audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-funnel-vj-")
    service = ObservationService(
        game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
    )
    trigger_kind: MeetingTriggerKind | None = None

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
                # Pre-advance packets for EVERY living player (the 15.3 walk
                # builds crew-only packets; the memory layer needs impostor
                # memories too — impostor speakers vouch and vote like anyone
                # else), ingested into each agent's own memory exactly as
                # ``TacticalAgent.decide`` does.
                state = walk_event.state
                for pid in sorted(state.players):
                    if not state.players[pid].alive:
                        continue
                    packet = service.build_packet(
                        world_state=state,
                        agent_id=pid,
                        engine_events=walk_event.last_events,
                    )
                    ingest_packet(
                        packet=packet,
                        memory=agents[pid].memory.episodic,
                        beliefs=agents[pid].memory.beliefs,
                    )
            elif isinstance(walk_event, MeetingOpened):
                meeting_entry = walk_event.entry
                state = walk_event.state
                if walk_event.trigger is None:
                    raise FunnelReconstructionError(
                        f"{game_id}: tick {meeting_entry.tick} entered MEETING "
                        "without a "
                        "MeetingTriggeredEvent (engine invariant violation)"
                    )
                trigger_kind = walk_event.trigger.trigger

                living = frozenset(
                    pid for pid, player in state.players.items() if player.alive
                )
                voters = frozenset(b.voter for b in meeting_entry.ballots)
                if living != voters:
                    # Every living participant casts exactly one ballot (defaults
                    # included) — a mismatch means the reconstruction diverged
                    # from the recorded meeting and every snapshot below would
                    # lie.
                    raise FunnelReconstructionError(
                        f"{game_id}: meeting at tick {meeting_entry.tick} "
                        f"reconstructed "
                        f"living set {sorted(living)} != recorded ballot voters "
                        f"{sorted(voters)}"
                    )

                # Meeting-open snapshots off the PRODUCTION accessors, sorted
                # like ``_build_participants``. The accessors consult no
                # environment (see the region banner).
                graph_by_voter: dict[PlayerId, tuple[SuspicionEntry, ...]] = {}
                sightings_by_speaker: dict[PlayerId, tuple[SightingRecord, ...]] = {}
                obs_ids_by_voter: dict[PlayerId, frozenset[str]] = {}
                fellows_by_voter: dict[PlayerId, tuple[PlayerId, ...]] = {}
                for pid in sorted(living):
                    agent = agents[pid]
                    graph_by_voter[pid] = agent.suspicion_graph_for_meeting()
                    sightings_by_speaker[pid] = agent.sighting_records_for_meeting()
                    obs_ids_by_voter[pid] = frozenset(
                        agent.observation_ids_for_meeting()
                    )
                    fellows_by_voter[pid] = (
                        tuple(x for x in impostor_ids if x != pid)
                        if roles[pid] == "IMPOSTOR"
                        else ()
                    )

                meetings.append(
                    _VJMeeting(
                        seed=seed,
                        meeting_id=meeting_entry.meeting_id,
                        tick=meeting_entry.tick,
                        trigger_kind=trigger_kind,
                        triggered_by=meeting_entry.triggered_by,
                        outcome=meeting_entry.outcome,
                        ejected=meeting_entry.ejected_player_id,
                        living=living,
                        transcript=meeting_entry.transcript,
                        ballots=tuple(meeting_entry.ballots),
                        contradictions=tuple(meeting_entry.contradictions),
                        llm_calls=tuple(meeting_entry.llm_calls),
                        suspicion_graph_by_voter=graph_by_voter,
                        sighting_records_by_speaker=sightings_by_speaker,
                        observation_ids_by_voter=obs_ids_by_voter,
                        fellow_impostor_ids_by_voter=fellows_by_voter,
                    )
                )
            elif isinstance(walk_event, MeetingApplied):
                # The post-meeting persistent belief fold, mirroring
                # ``orchestrator.game._absorb_meeting_beliefs``: one evidence
                # reduction + one absorb per player still alive in the
                # post-meeting state, sorted; the reported-testimony content
                # fold rides the same loop. Decay (§6.3 Rule 5) runs inside the
                # absorb, so an evidence-free meeting still decays — exactly as
                # live. ``trigger_kind`` was set on this meeting's MeetingOpened
                # (the walker always pairs them).
                if trigger_kind is None:  # pragma: no cover - walker pairing
                    raise FunnelReconstructionError(
                        f"{game_id}: MeetingApplied at tick "
                        f"{walk_event.entry.tick} arrived without a preceding "
                        "MeetingOpened trigger"
                    )
                state = walk_event.state
                evidence = extract_belief_evidence(
                    walk_event.result, trigger_kind=trigger_kind
                )
                statements = derive_reported_testimony(
                    walk_event.result, testimony_shapes=walk_event.testimony_shapes
                )
                for pid in sorted(state.players):
                    if not state.players[pid].alive:
                        continue
                    agents[pid].absorb_meeting_evidence(
                        accused=evidence.accused,
                        corroborated=evidence.corroborated,
                        contradicted=evidence.contradicted,
                    )
                    agents[pid].absorb_reported_testimony(statements=statements)
    finally:
        audit_dir.cleanup()

    return _VJGameWalk(seed=seed, roles=roles, meetings=tuple(meetings))


# --------------------------------------------------------------------------- #
# The four pooling folds (per meeting)                                        #
# --------------------------------------------------------------------------- #


def _roll_call_placed(meeting: _VJMeeting) -> frozenset[PlayerId]:
    """Living players who self-placed via a spoken :class:`WhereaboutsClaim`.

    Roll-call coverage counts ONLY the whereabouts channel (the Task 16.7
    roll-call answer shape) — NOT ``saw_player`` placements — so the fold
    reads 0 on every committed set that predates roll-call elicitation
    (16.15) and moves exactly when the mechanism does. The broader
    any-public-placement census is the absence-set fold's complement below.
    """

    return frozenset(
        turn.speaker
        for turn in meeting.transcript.turns
        if turn.speaker in meeting.living
        and any(isinstance(obs, WhereaboutsClaim) for obs in turn.observations)
    )


def _whereabouts_claim_event_ids(meeting: _VJMeeting) -> tuple[str, ...]:
    """Every living speaker's whereabouts claim, as its contradiction event id.

    Mirrors ``meetings.transcript._turn_whereabouts_id`` exactly
    (``turn:{turn_id}:whereabouts:{index}``, ``index`` = the observation's
    position in ``turn.observations``) so a recorded
    :class:`~meetings.schemas.ContradictionRef` referencing the claim is
    matched byte-for-byte.
    """

    ids: list[str] = []
    for turn in meeting.transcript.turns:
        if turn.speaker not in meeting.living:
            continue
        for index, obs in enumerate(turn.observations):
            if isinstance(obs, WhereaboutsClaim):
                ids.append(f"turn:{turn.turn_id}:whereabouts:{index}")
    return tuple(ids)


def _vouch_census(meeting: _VJMeeting) -> tuple[int, frozenset[PlayerId]]:
    """Spoken vouches: ``saw_player`` observations placing ANOTHER living player.

    Returns ``(vouch_observations, vouched_subjects)``. A vouch is a living
    speaker's spoken :class:`SawPlayerObservation` whose subject is another
    LIVING player (the pooling census places the living; testimony about the
    victim is the 15.3 transmission folds' business). Self-placements are the
    roll-call/whereabouts channel, never a vouch.
    """

    observations = 0
    subjects: set[PlayerId] = set()
    for turn in meeting.transcript.turns:
        if turn.speaker not in meeting.living:
            continue
        for obs in turn.observations:
            if (
                isinstance(obs, SawPlayerObservation)
                and obs.subject != turn.speaker
                and obs.subject in meeting.living
            ):
                observations += 1
                subjects.add(obs.subject)
    return observations, frozenset(subjects)


def _grounded_vouch_set(meeting: _VJMeeting) -> frozenset[PlayerId]:
    """Subjects of GROUNDED vouches — the 16.7 chokepoint over reconstructed records.

    Runs the production :func:`meetings.transcript.grounded_vouch_subjects`
    with each speaker's OWN reconstructed
    :class:`~meetings.schemas.SightingRecord` snapshot (the walk's
    meeting-open accessor read), the living roster, and the trigger kind —
    exactly the mapping the graduating task will feed live. Committed
    transcripts already carry speaker-groundable sightings, so this fold is
    NON-zero on committed bytes: it measures the vouch supply the inert
    channel would ground, the before-column the close reads.
    """

    return grounded_vouch_subjects(
        meeting.transcript,
        sighting_records=meeting.sighting_records_by_speaker,
        roster=meeting.living,
        trigger_kind=meeting.trigger_kind,
    )


def _absence_set(meeting: _VJMeeting) -> tuple[PlayerId, ...]:
    """Living players with NO public placement in this meeting (sorted).

    The complement of :func:`meetings.transcript.reconstruct_stated_paths`
    over the living roster — BOTH placement channels count (a ``saw_player``
    subject / co-present and a whereabouts self-placement), so on committed
    bytes the fold reads the unplaced share as-is and shrinks as pooling
    mechanisms land (the 16.8 absence prior reads the same construction).
    """

    placed = reconstruct_stated_paths(
        meeting.transcript,
        roster=meeting.living,
        trigger_kind=meeting.trigger_kind,
    )
    return tuple(sorted(meeting.living - set(placed)))


def _whereabouts_lies_detected(meeting: _VJMeeting) -> int:
    """Whereabouts claims named by a RECORDED contradiction flag.

    A lying whereabouts claim indexes as a degenerate single-tick self-alibi
    and is prosecuted by the existing alibi flag paths (its 16.7 design), so
    detection is read off the meeting's RECORDED
    :class:`~meetings.schemas.ContradictionRef` rows — the production
    detector's own output — by event id, never re-derived.
    """

    flagged_event_ids = frozenset(
        event_id
        for ref in meeting.contradictions
        for event_id in (ref.event_a_id, ref.event_b_id)
    )
    return sum(
        1
        for event_id in _whereabouts_claim_event_ids(meeting)
        if event_id in flagged_event_ids
    )


# --------------------------------------------------------------------------- #
# Task 17.4 roll-call uptake breakdown (per-role / per-surface / answered-asked)#
#                                                                              #
# These helpers DECOMPOSE the roll-call aggregate the folds above already      #
# report — they move no committed cell (the 0.363 / 0.573 coverage means are   #
# baseline-5 findings, audits/audit-phase-16-close.md §6) but answer WHY the   #
# coverage sits where it does: whether the ~⅓ answer rate is uniform silence   #
# or STRUCTURED refusal. The impostor prompt templates instruct impostors to   #
# explain nothing about their own whereabouts, so the crew-vs-impostor split   #
# is the calibration signal the §0.1.4 absence-prior re-measure needs (a rule  #
# that removes roll-call answerers from the absent set must know whether a     #
# non-answerer is crew going quiet or an impostor refusing by design); and the #
# living − asked gap separates never-took-the-mic from the asked − answered    #
# structured refusal (every speaking turn carries the 16.15 roll-call ask).    #
# --------------------------------------------------------------------------- #


def _living_speakers(meeting: _VJMeeting) -> frozenset[PlayerId]:
    """Living players who took at least one turn — the roll-call ASKED set.

    Every speaking turn carries the Task 16.15 roll-call ask, so taking a turn
    IS being asked; the answered set (:func:`_roll_call_placed`) is a subset of
    this one (self-placing requires speaking). The ``living − asked`` gap is the
    never-took-the-mic share, kept distinct from the ``asked − answered``
    structured-refusal share (audits/audit-phase-16-close.md §6).
    """

    return frozenset(
        turn.speaker
        for turn in meeting.transcript.turns
        if turn.speaker in meeting.living
    )


def _whereabouts_claims_by_surface(meeting: _VJMeeting) -> dict[TurnKind, int]:
    """Living speakers' whereabouts claims partitioned by the carrying turn kind.

    Uses the SAME living-speaker filter and per-observation count as
    :func:`_whereabouts_claim_event_ids` (a speaker with two claims contributes
    two), so the three surface cells sum to ``whereabouts_claims``. Surfaces are
    the DESIGN.md §5.2 :data:`~meetings.schemas.TurnKind` roles — ``opening``
    (the reporter / emergency caller), ``reply`` (the reactive accusation chain)
    and ``opt_in`` (the terminal info-share volunteer).
    """

    counts: dict[TurnKind, int] = {"opening": 0, "reply": 0, "opt_in": 0}
    for turn in meeting.transcript.turns:
        if turn.speaker not in meeting.living:
            continue
        for obs in turn.observations:
            if isinstance(obs, WhereaboutsClaim):
                counts[turn.turn_kind] += 1
    return counts


def _partition_living_by_role(
    players: frozenset[PlayerId], *, roles: Mapping[PlayerId, Role]
) -> tuple[int, int]:
    """Count ``(crew, impostor)`` over ``players`` against a VALIDATED role map.

    The caller (:func:`_pooling_row`) fails loud on any living player missing
    from ``roles`` before reaching here, so the lookup is total. Callers pass a
    subset of the living set (the living roster itself, or the self-placed set),
    so both partitions are exact decompositions of their aggregate.
    """

    crew = 0
    impostor = 0
    for pid in players:
        if roles[pid] == "IMPOSTOR":
            impostor += 1
        else:
            crew += 1
    return crew, impostor


# --------------------------------------------------------------------------- #
# Pooling report types (public, stable)                                       #
# --------------------------------------------------------------------------- #


class MeetingPoolingRow(BaseModel):
    """The pooling census for ONE resolved meeting (frozen).

    Rates are shares of ``living`` (the meeting's living-player count, always
    positive). ``absence_set`` exposes the raw unplaced roster so any variant
    definition can be re-derived from the rows without another walk.

    The Task 17.4 roll-call uptake breakdown (the ``living_*`` / ``roll_call_*``
    / ``whereabouts_claims_{opening,reply,opt_in}`` cells) is ADDITIVE — it
    decomposes the aggregate roll-call cells above, never moves them
    (audits/audit-phase-16-close.md §6). Its identities hold on every row:

    * ``living_crew + living_impostor == living``;
    * ``roll_call_placed_crew + roll_call_placed_impostor == roll_call_placed``;
    * ``whereabouts_claims_opening + _reply + _opt_in == whereabouts_claims``;
    * ``roll_call_answered == roll_call_placed`` (self-placing IS answering) and
      ``roll_call_answered <= roll_call_asked <= living`` (answering requires
      speaking; being asked requires taking a turn; not everyone speaks).

    ``roll_call_coverage_{crew,impostor}`` is the per-role placed / per-role
    living share, ``None`` (undefined, never ``0.0`` — the report's
    None-means-undefined convention) exactly when that role has zero living
    members. The crew-vs-impostor split is the §0.1.4 calibration signal:
    impostor prompt templates instruct impostors to explain nothing about their
    own whereabouts, so it reads whether the roll-call silence is structured
    refusal. ``roll_call_asked`` (living players who took ≥1 turn) minus
    ``roll_call_answered`` isolates that asked-but-refused share from the
    ``living − roll_call_asked`` never-took-the-mic share.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    meeting_id: str
    tick: int
    trigger_kind: MeetingTriggerKind
    outcome: str
    living: int
    whereabouts_claims: int
    roll_call_placed: int
    roll_call_coverage: float
    vouch_observations: int
    vouched_subjects: int
    vouch_rate: float
    grounded_vouch_subjects: int
    grounded_vouch_rate: float
    absence_set: tuple[PlayerId, ...]
    absence_set_size: int
    whereabouts_lies_detected: int
    # -- Task 17.4 roll-call uptake breakdown (additive; decomposes the
    #    roll-call cells above, moves none of them) --
    living_crew: int
    living_impostor: int
    roll_call_placed_crew: int
    roll_call_placed_impostor: int
    roll_call_coverage_crew: float | None
    roll_call_coverage_impostor: float | None
    whereabouts_claims_opening: int
    whereabouts_claims_reply: int
    whereabouts_claims_opt_in: int
    roll_call_asked: int
    roll_call_answered: int


class PoolingFunnelReport(BaseModel):
    """The pooling-census diagnostics over one replay set (frozen value object).

    Aggregates the per-meeting rows over EVERY resolved meeting (emergency
    included). Mean rates are ``None`` (undefined, not ``0.0``) when the set
    has no meetings; ``whereabouts_lie_detection_rate`` and
    ``grounded_vouch_share`` are ``None`` when their denominators (claims /
    vouched subjects) are zero — on committed bytes that predate roll-call,
    the lie rate is therefore ``None`` with ``whereabouts_claims_total == 0``.
    ``absence_set_size_histogram`` maps set size to meeting count. Emitted
    inside :class:`eval.vj_instruments.VJInstrumentReport` (the ``pooling``
    field of the ``--vj`` report; JSON shape documented there).

    The Task 17.4 roll-call uptake breakdown adds the ADDITIVE aggregate cells
    that decompose ``roll_call_coverage_mean`` — none of the pre-existing cells
    move (audits/audit-phase-16-close.md §6). ``roll_call_placed_{crew,
    impostor}_total`` and the surface totals are plain row sums.
    ``roll_call_coverage_{crew,impostor}_mean`` is ``statistics.fmean`` over the
    rows where that role's coverage is DEFINED (not ``None`` — i.e. the role had
    living members), and ``None`` when no row defines it (the same
    None-means-undefined convention as the means above). ``roll_call_answer_rate``
    is ``roll_call_answered_total / roll_call_asked_total`` — the set-wide share
    of asked players who answered — ``None`` when the denominator is zero. The
    per-role coverage split is the §0.1.4 absence-prior re-measure's calibration
    input (whether the roll-call silence is impostor structured refusal).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    games_total: int
    meetings_total: int
    whereabouts_claims_total: int
    roll_call_meetings: int
    roll_call_coverage_mean: float | None
    vouch_observations_total: int
    vouch_rate_mean: float | None
    grounded_vouch_rate_mean: float | None
    grounded_vouch_share: float | None
    absence_set_size_mean: float | None
    absence_set_size_median: float | None
    absence_set_size_histogram: Mapping[int, int]
    whereabouts_lies_detected: int
    whereabouts_lie_detection_rate: float | None
    # -- Task 17.4 roll-call uptake breakdown (additive; decomposes
    #    roll_call_coverage_mean, moves no cell above) --
    roll_call_placed_crew_total: int
    roll_call_placed_impostor_total: int
    roll_call_coverage_crew_mean: float | None
    roll_call_coverage_impostor_mean: float | None
    whereabouts_claims_opening_total: int
    whereabouts_claims_reply_total: int
    whereabouts_claims_opt_in_total: int
    roll_call_asked_total: int
    roll_call_answered_total: int
    roll_call_answer_rate: float | None
    per_meeting: tuple[MeetingPoolingRow, ...]


def _pooling_row(
    meeting: _VJMeeting, *, roles: Mapping[PlayerId, Role]
) -> MeetingPoolingRow:
    living = len(meeting.living)
    if living <= 0:
        raise FunnelReconstructionError(
            f"meeting {meeting.meeting_id!r} reconstructed an empty living set"
        )
    unroled = sorted(pid for pid in meeting.living if pid not in roles)
    if unroled:
        # The per-role breakdown must attribute every living player; a missing
        # role would silently under-count one partition (AGENTS.md: no silent
        # fallbacks).
        raise FunnelReconstructionError(
            f"meeting {meeting.meeting_id!r} has living player(s) {unroled} "
            "absent from the role map — the Task 17.4 per-role roll-call "
            "breakdown cannot attribute their uptake"
        )
    placed = _roll_call_placed(meeting)
    claims = _whereabouts_claim_event_ids(meeting)
    vouch_observations, vouched = _vouch_census(meeting)
    grounded = _grounded_vouch_set(meeting)
    absence = _absence_set(meeting)
    living_crew, living_impostor = _partition_living_by_role(
        meeting.living, roles=roles
    )
    placed_crew, placed_impostor = _partition_living_by_role(placed, roles=roles)
    surface = _whereabouts_claims_by_surface(meeting)
    asked = len(_living_speakers(meeting))
    answered = len(placed)
    return MeetingPoolingRow(
        seed=meeting.seed,
        meeting_id=meeting.meeting_id,
        tick=meeting.tick,
        trigger_kind=meeting.trigger_kind,
        outcome=meeting.outcome,
        living=living,
        whereabouts_claims=len(claims),
        roll_call_placed=len(placed),
        roll_call_coverage=len(placed) / living,
        vouch_observations=vouch_observations,
        vouched_subjects=len(vouched),
        vouch_rate=len(vouched) / living,
        grounded_vouch_subjects=len(grounded),
        grounded_vouch_rate=len(grounded) / living,
        absence_set=absence,
        absence_set_size=len(absence),
        whereabouts_lies_detected=_whereabouts_lies_detected(meeting),
        living_crew=living_crew,
        living_impostor=living_impostor,
        roll_call_placed_crew=placed_crew,
        roll_call_placed_impostor=placed_impostor,
        roll_call_coverage_crew=(placed_crew / living_crew if living_crew else None),
        roll_call_coverage_impostor=(
            placed_impostor / living_impostor if living_impostor else None
        ),
        whereabouts_claims_opening=surface["opening"],
        whereabouts_claims_reply=surface["reply"],
        whereabouts_claims_opt_in=surface["opt_in"],
        roll_call_asked=asked,
        roll_call_answered=answered,
    )


def _pooling_report_from_walks(
    walks: Sequence[_VJGameWalk],
    *,
    sample_dir: Path,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> PoolingFunnelReport:
    """Aggregate the pooling rows of already-walked games into the set report.

    Shared by :func:`compute_pooling_funnel` and
    :func:`eval.vj_instruments.compute_vj_instruments` so the ``--vj`` report
    embeds the pooling census off ONE walk of the set.
    """

    rows = [
        _pooling_row(meeting, roles=walk.roles)
        for walk in walks
        for meeting in walk.meetings
    ]
    sizes = [row.absence_set_size for row in rows]
    histogram: dict[int, int] = {}
    for size in sizes:
        histogram[size] = histogram.get(size, 0) + 1
    claims_total = sum(row.whereabouts_claims for row in rows)
    lies_total = sum(row.whereabouts_lies_detected for row in rows)
    vouched_total = sum(row.vouched_subjects for row in rows)
    grounded_total = sum(row.grounded_vouch_subjects for row in rows)
    # Task 17.4 per-role coverage means fold over the rows where that role's
    # coverage is DEFINED (not None — the role had living members that meeting).
    crew_coverages = [
        c for c in (row.roll_call_coverage_crew for row in rows) if c is not None
    ]
    impostor_coverages = [
        c for c in (row.roll_call_coverage_impostor for row in rows) if c is not None
    ]
    asked_total = sum(row.roll_call_asked for row in rows)
    answered_total = sum(row.roll_call_answered for row in rows)
    return PoolingFunnelReport(
        replay_set_dir=str(sample_dir),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        games_total=len(walks),
        meetings_total=len(rows),
        whereabouts_claims_total=claims_total,
        roll_call_meetings=sum(1 for row in rows if row.whereabouts_claims),
        roll_call_coverage_mean=(
            statistics.fmean(row.roll_call_coverage for row in rows) if rows else None
        ),
        vouch_observations_total=sum(row.vouch_observations for row in rows),
        vouch_rate_mean=(
            statistics.fmean(row.vouch_rate for row in rows) if rows else None
        ),
        grounded_vouch_rate_mean=(
            statistics.fmean(row.grounded_vouch_rate for row in rows) if rows else None
        ),
        grounded_vouch_share=(
            grounded_total / vouched_total if vouched_total else None
        ),
        absence_set_size_mean=statistics.fmean(sizes) if sizes else None,
        absence_set_size_median=statistics.median(sizes) if sizes else None,
        absence_set_size_histogram={
            size: histogram[size] for size in sorted(histogram)
        },
        whereabouts_lies_detected=lies_total,
        whereabouts_lie_detection_rate=(
            lies_total / claims_total if claims_total else None
        ),
        roll_call_placed_crew_total=sum(row.roll_call_placed_crew for row in rows),
        roll_call_placed_impostor_total=sum(
            row.roll_call_placed_impostor for row in rows
        ),
        roll_call_coverage_crew_mean=(
            statistics.fmean(crew_coverages) if crew_coverages else None
        ),
        roll_call_coverage_impostor_mean=(
            statistics.fmean(impostor_coverages) if impostor_coverages else None
        ),
        whereabouts_claims_opening_total=sum(
            row.whereabouts_claims_opening for row in rows
        ),
        whereabouts_claims_reply_total=sum(
            row.whereabouts_claims_reply for row in rows
        ),
        whereabouts_claims_opt_in_total=sum(
            row.whereabouts_claims_opt_in for row in rows
        ),
        roll_call_asked_total=asked_total,
        roll_call_answered_total=answered_total,
        roll_call_answer_rate=(answered_total / asked_total if asked_total else None),
        per_meeting=tuple(rows),
    )


def _walk_set_vj(sample_dir: Path) -> tuple[list[_VJGameWalk], int, int, int]:
    """Walk every game of a replay set through the memory-augmented walk."""

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
    walks = [
        _walk_game_vj(
            sample_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            game_map=game_map,
        )
        for seed in seeds
    ]
    return walks, num_players, num_impostors, tasks_per_crewmate


def compute_pooling_funnel(sample_dir: Path) -> PoolingFunnelReport:
    """Fold a replay set's committed bytes into the pooling-census diagnostics.

    The Task 16.10 pooling instrument: roll-call coverage, vouch +
    GROUNDED-vouch rates, absence-set size distribution, and the
    whereabouts-lie detection rate over every resolved meeting. Runs on any
    replay-set directory and both roster presets; pure and offline. Also
    surfaced (embedded) through ``scripts/measure_baseline.py --vj``.
    """

    walks, num_players, num_impostors, tasks_per_crewmate = _walk_set_vj(sample_dir)
    return _pooling_report_from_walks(
        walks,
        sample_dir=sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )


__all__ = [
    "FunnelReconstructionError",
    "InformationFunnelReport",
    "MeetingFunnelRow",
    "MeetingPoolingRow",
    "PoolingFunnelReport",
    "compute_information_funnel",
    "compute_pooling_funnel",
]
