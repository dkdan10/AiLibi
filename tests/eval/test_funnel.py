"""Unit tests for eval/funnel.py (Task 15.3).

Two layers:

* scripted-fixture unit tests over hand-built ``_Frame`` / ``_ReportMeeting`` /
  ``_GameWalk`` objects, exercising each stage's folds in isolation (the oracle's
  sighting/alibi/vent-alibi logic, the possession census, the transmission
  census), plus the walk's fail-loud state-hash verification;
* the baseline-2 REPRODUCTION PINS — ``compute_information_funnel`` over the
  committed 9p2i bytes must reproduce the clean-up charter §2 figures EXACTLY, and
  the fold must also run clean on the 4p1i preset.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from eval.funnel import (
    FunnelReconstructionError,
    InformationFunnelReport,
    _candidate_set_exact,
    _Frame,
    _GameWalk,
    _has_killer_placement_observation,
    _has_structured_vent_observation,
    _holds_kill_witnessed,
    _holds_last_seen_with_killer,
    _holds_scene,
    _holds_vent,
    _killer_accused,
    _mentions_vent,
    _pooled_sightings,
    _ReportMeeting,
    _reporter_ejected,
    _VentSighting,
    _walk_game,
    compute_information_funnel,
)
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from meetings.schemas import (
    AccusationClaim,
    Claim,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    SawVentObservation,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


# --------------------------------------------------------------------------- #
# Scripted-fixture builders                                                   #
# --------------------------------------------------------------------------- #


def _frame(
    rooms: dict[PlayerId, str],
    *,
    dead: frozenset[PlayerId] = frozenset(),
    vented: frozenset[PlayerId] = frozenset(),
) -> _Frame:
    return _Frame(
        room=dict(rooms),
        alive={pid: pid not in dead for pid in rooms},
        in_vent={pid: pid in vented for pid in rooms},
    )


def _turn(
    speaker: PlayerId,
    *,
    free_text: str = "",
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m:turn-{speaker}",
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        observations=tuple(observations),
        claims=tuple(claims),
        free_text=free_text,
    )


def _meeting(
    *,
    reporter: PlayerId = "p-1",
    outcome: str = "SKIPPED",
    ejected: PlayerId | None = None,
    victim: PlayerId = "p-9",
    killer: PlayerId = "p-2",
    kill_tick: int = 5,
    kill_room: str = "STORAGE",
    kill_witnesses: frozenset[PlayerId] = frozenset(),
    living: frozenset[PlayerId] = frozenset({"p-1", "p-2", "p-3", "p-4"}),
    turns: tuple[MeetingTurn, ...] = (),
    meeting_tick: int | None = None,
) -> _ReportMeeting:
    return _ReportMeeting(
        seed=0,
        meeting_id="m",
        tick=meeting_tick if meeting_tick is not None else kill_tick + 3,
        reporter=reporter,
        outcome=outcome,
        ejected=ejected,
        victim=victim,
        killer=killer,
        kill_tick=kill_tick,
        kill_room=kill_room,
        kill_witnesses=kill_witnesses,
        living_at_meeting=living,
        turns=turns,
        ballots=(),
    )


def _walk(
    *,
    roles: dict[PlayerId, Role],
    frames: dict[int, _Frame] | None = None,
    vents: tuple[_VentSighting, ...] = (),
    meetings: tuple[_ReportMeeting, ...] = (),
    sight: dict[int, dict[PlayerId, dict[PlayerId, str]]] | None = None,
    moved: dict[int, dict[PlayerId, dict[PlayerId, tuple[str, str]]]] | None = None,
) -> _GameWalk:
    return _GameWalk(
        seed=0,
        roles=dict(roles),
        frames=dict(frames or {}),
        vent_sightings=vents,
        report_meetings=meetings,
        sight=sight or {},
        moved=moved or {},
    )


def _vent(
    *, tick: int, actor: PlayerId, witnesses: frozenset[PlayerId]
) -> _VentSighting:
    return _VentSighting(tick=tick, actor=actor, witnesses=witnesses)


_ROLES: dict[PlayerId, Role] = {
    "p-1": "CREWMATE",
    "p-2": "IMPOSTOR",
    "p-3": "CREWMATE",
    "p-4": "CREWMATE",
    "p-9": "CREWMATE",
}


# --------------------------------------------------------------------------- #
# Stage 1 — oracle unit tests                                                 #
# --------------------------------------------------------------------------- #


def test_pooled_sightings_places_only_co_located_players() -> None:
    # A sighting is co-location with a living crew OTHER than the subject (self-alibi
    # is not a sighting): p-2 (impostor) is seen by crew p-3 in STORAGE; p-3 has no
    # OTHER crew there so is not placed; crew p-4 & p-9 in MEDBAY place each other;
    # lone crew p-1 is not placed; a vented player is never placed.
    frame = _frame(
        {
            "p-1": "CAFETERIA",
            "p-2": "STORAGE",
            "p-3": "STORAGE",
            "p-4": "MEDBAY",
            "p-9": "MEDBAY",
            "p-5": "STORAGE",
        },
        vented=frozenset({"p-5"}),
    )
    roles: dict[PlayerId, Role] = {**_ROLES, "p-5": "IMPOSTOR"}
    placed = _pooled_sightings(frame, roles)
    assert placed == {"p-2": "STORAGE", "p-4": "MEDBAY", "p-9": "MEDBAY"}


def test_candidate_set_alibis_suspects_seen_elsewhere() -> None:
    # Kill in STORAGE at t=5. p-3 (crew) is with p-4 in ADMIN => p-4 alibied.
    # p-2 (killer) alone in STORAGE => unseen => candidate. Reporter p-1 excluded.
    frames = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "STORAGE", "p-3": "ADMIN", "p-4": "ADMIN"}
        )
    }
    meeting = _meeting(
        reporter="p-1",
        killer="p-2",
        kill_room="STORAGE",
        kill_tick=5,
        living=frozenset({"p-1", "p-2", "p-3", "p-4"}),
    )
    cand = _candidate_set_exact(meeting, frames, _ROLES)
    assert "p-1" not in cand  # reporter excluded
    assert "p-2" in cand  # killer unseen at the scene => stays a candidate
    # p-3 & p-4 share ADMIN and are both crew, so each is SEEN by the other in a
    # room != STORAGE => both alibied.
    assert "p-3" not in cand
    assert "p-4" not in cand
    assert cand == frozenset({"p-2"})


def test_candidate_set_excludes_vented_suspect_at_kill_tick() -> None:
    # p-4 is in a vent at the kill tick => provably not committing the same-room kill.
    frames = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "STORAGE", "p-3": "MEDBAY", "p-4": "REACTOR"},
            vented=frozenset({"p-4"}),
        )
    }
    meeting = _meeting(reporter="p-1", killer="p-2", kill_room="STORAGE", kill_tick=5)
    cand = _candidate_set_exact(meeting, frames, _ROLES)
    assert "p-4" not in cand  # vent alibi
    assert "p-2" in cand  # killer


def test_candidate_set_keeps_killer_seen_at_scene() -> None:
    # A crew witness co-located with the killer IN the kill room does not alibi them.
    frames = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "STORAGE", "p-3": "STORAGE", "p-4": "ADMIN"}
        )
    }
    meeting = _meeting(reporter="p-1", killer="p-2", kill_room="STORAGE", kill_tick=5)
    assert "p-2" in _candidate_set_exact(meeting, frames, _ROLES)


# --------------------------------------------------------------------------- #
# Stage 2 — possession unit tests                                             #
# --------------------------------------------------------------------------- #


def test_holds_vent_requires_living_crew_witness_strictly_before_meeting() -> None:
    meeting = _meeting(kill_tick=5, killer="p-2")  # meeting.tick == 8
    roles = _ROLES
    # A crew witnessed the impostor vent at tick 6 (< 8) => held.
    walk_held = _walk(
        roles=roles,
        vents=(_vent(tick=6, actor="p-2", witnesses=frozenset({"p-3"})),),
    )
    assert _holds_vent(meeting, walk_held) is True
    # The only witness is dead at the meeting (p-9 is the victim) => not held.
    walk_dead = _walk(
        roles=roles,
        vents=(_vent(tick=6, actor="p-2", witnesses=frozenset({"p-9"})),),
    )
    assert _holds_vent(meeting, walk_dead) is False
    # A vent ON the meeting tick is not held going in.
    walk_late = _walk(
        roles=roles,
        vents=(_vent(tick=8, actor="p-2", witnesses=frozenset({"p-3"})),),
    )
    assert _holds_vent(meeting, walk_late) is False


def test_holds_kill_witnessed() -> None:
    assert (
        _holds_kill_witnessed(_meeting(kill_witnesses=frozenset({"p-3"})), _ROLES)
        is True
    )
    assert (
        _holds_kill_witnessed(_meeting(kill_witnesses=frozenset({"p-9"})), _ROLES)
        is False
    )  # victim


def test_holds_scene_by_seeing_killer_in_room() -> None:
    # Crew p-3 SAW killer p-2 in the kill room STORAGE at packet tick kill_tick+1.
    meeting = _meeting(killer="p-2", victim="p-9", kill_room="STORAGE", kill_tick=5)
    walk = _walk(
        roles=_ROLES, sight={6: {"p-3": {"p-2": "STORAGE"}}}, meetings=(meeting,)
    )
    assert _holds_scene(meeting, walk) is True
    # The same sighting placing the killer ELSEWHERE is not the scene.
    walk_elsewhere = _walk(
        roles=_ROLES, sight={6: {"p-3": {"p-2": "ADMIN"}}}, meetings=(meeting,)
    )
    assert _holds_scene(meeting, walk_elsewhere) is False


def test_holds_scene_by_witnessed_move_touching_kill_room() -> None:
    # Crew p-3 WATCHED killer p-2 move INTO the kill room (STORAGE) — a placement
    # raw co-location misses; the move channel is what lifts scene 28 -> 32 on 9p2i.
    meeting = _meeting(killer="p-2", victim="p-9", kill_room="STORAGE", kill_tick=5)
    walk = _walk(
        roles=_ROLES,
        moved={7: {"p-3": {"p-2": ("ENGINEERING", "STORAGE")}}},
        meetings=(meeting,),
    )
    assert _holds_scene(meeting, walk) is True
    # A move NOT touching the kill room is not the scene.
    walk_off = _walk(
        roles=_ROLES,
        moved={7: {"p-3": {"p-2": ("ENGINEERING", "REACTOR")}}},
        meetings=(meeting,),
    )
    assert _holds_scene(meeting, walk_off) is False


def test_holds_scene_window_capped_at_meeting_tick() -> None:
    # The body is reported immediately (meeting.tick == kill_tick + 1), so the
    # kill_tick+2 packet is a POST-meeting resumed-play frame: a sighting there is
    # not evidence held going INTO the meeting and must not count.
    meeting = _meeting(
        killer="p-2", victim="p-9", kill_room="STORAGE", kill_tick=5, meeting_tick=6
    )
    walk_post = _walk(
        roles=_ROLES, sight={7: {"p-3": {"p-2": "STORAGE"}}}, meetings=(meeting,)
    )
    assert _holds_scene(meeting, walk_post) is False
    # The kill-result frame itself (kill_tick+1 == meeting.tick) still counts.
    walk_at = _walk(
        roles=_ROLES, sight={6: {"p-3": {"p-2": "STORAGE"}}}, meetings=(meeting,)
    )
    assert _holds_scene(meeting, walk_at) is True


def test_holds_last_seen_with_killer() -> None:
    # p-3's last co-location with the still-alive victim p-9 also held the killer p-2.
    frames = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "STORAGE", "p-3": "STORAGE", "p-9": "STORAGE"}
        ),
    }
    meeting = _meeting(
        reporter="p-1", killer="p-2", victim="p-9", kill_room="STORAGE", kill_tick=5
    )
    assert _holds_last_seen_with_killer(meeting, frames, _ROLES) is True
    # If p-3 last saw the victim WITHOUT the killer present, not held.
    frames_no_killer = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "ADMIN", "p-3": "STORAGE", "p-9": "STORAGE"}
        )
    }
    assert _holds_last_seen_with_killer(meeting, frames_no_killer, _ROLES) is False
    # A killer hidden IN A VENT in the victim's room is invisible — not "seen with".
    frames_vented_killer = {
        5: _frame(
            {"p-1": "CAFETERIA", "p-2": "STORAGE", "p-3": "STORAGE", "p-9": "STORAGE"},
            vented=frozenset({"p-2"}),
        )
    }
    assert _holds_last_seen_with_killer(meeting, frames_vented_killer, _ROLES) is False


# --------------------------------------------------------------------------- #
# Stage 3 — transmission unit tests                                           #
# --------------------------------------------------------------------------- #


def test_mentions_vent_scans_free_text() -> None:
    assert (
        _mentions_vent((_turn("p-1", free_text="I saw p-2 VENT in storage"),)) is True
    )
    assert _mentions_vent((_turn("p-1", free_text="p-2 vented into medbay"),)) is True
    assert _mentions_vent((_turn("p-1", free_text="nothing suspicious"),)) is False
    # A word merely CONTAINING "vent" is not a vent mention.
    assert (
        _mentions_vent(
            (_turn("p-1", free_text="in any event, we should prevent chaos"),)
        )
        is False
    )


def test_has_killer_placement_observation() -> None:
    def obs(subject: str, room: str, tick: int = 5) -> SawPlayerObservation:
        return SawPlayerObservation(
            type="saw_player", tick=tick, subject=subject, room=room
        )

    # A structured saw_player naming the killer IN the kill room AROUND the kill
    # counts (fixture: kill_tick=5, meeting tick=8 => window [4, 8])...
    at_scene = _turn("p-3", observations=(obs("p-2", "STORAGE"),))
    assert (
        _has_killer_placement_observation(
            _meeting(killer="p-2", kill_room="STORAGE", turns=(at_scene,))
        )
        is True
    )
    # ...but the wrong subject or the wrong room does not.
    wrong_subject = _turn("p-3", observations=(obs("p-4", "STORAGE"),))
    wrong_room = _turn("p-3", observations=(obs("p-2", "ADMIN"),))
    assert (
        _has_killer_placement_observation(
            _meeting(killer="p-2", kill_room="STORAGE", turns=(wrong_subject,))
        )
        is False
    )
    assert (
        _has_killer_placement_observation(
            _meeting(killer="p-2", kill_room="STORAGE", turns=(wrong_room,))
        )
        is False
    )
    # ...and neither does an out-of-window tick: a STALE pre-kill sighting of the
    # killer in that room, or a tick after the meeting fired.
    stale = _turn("p-3", observations=(obs("p-2", "STORAGE", tick=1),))
    future = _turn("p-3", observations=(obs("p-2", "STORAGE", tick=20),))
    assert (
        _has_killer_placement_observation(
            _meeting(killer="p-2", kill_room="STORAGE", turns=(stale,))
        )
        is False
    )
    assert (
        _has_killer_placement_observation(
            _meeting(killer="p-2", kill_room="STORAGE", turns=(future,))
        )
        is False
    )


def test_has_structured_vent_observation() -> None:
    vent_turn = _turn(
        "p-3",
        observations=(
            SawVentObservation(type="saw_vent", tick=6, subject="p-2", room="STORAGE"),
        ),
    )
    assert _has_structured_vent_observation(_meeting(turns=(vent_turn,))) is True
    # A free-text vent mention alone is NOT a structured observation.
    text_only = _turn("p-3", free_text="I saw p-2 vent in storage")
    assert _has_structured_vent_observation(_meeting(turns=(text_only,))) is False


def test_killer_accused() -> None:
    accuse = _turn(
        "p-1",
        claims=(
            AccusationClaim(
                type="accusation", against="p-2", confidence=0.9, reason="x"
            ),
        ),
    )
    assert _killer_accused(_meeting(killer="p-2", turns=(accuse,))) is True
    assert _killer_accused(_meeting(killer="p-2", turns=(_turn("p-1"),))) is False


def test_reporter_ejected() -> None:
    assert (
        _reporter_ejected(_meeting(reporter="p-1", outcome="EJECTED", ejected="p-1"))
        is True
    )
    assert (
        _reporter_ejected(_meeting(reporter="p-1", outcome="EJECTED", ejected="p-2"))
        is False
    )
    assert (
        _reporter_ejected(_meeting(reporter="p-1", outcome="SKIPPED", ejected=None))
        is False
    )


# --------------------------------------------------------------------------- #
# Walk — fail-loud on a drifted state hash                                     #
# --------------------------------------------------------------------------- #


def test_walk_raises_on_corrupted_state_hash(tmp_path: Path) -> None:
    """A tampered recorded ``state_hash`` fails loud (never silently mis-measures)."""

    src = _FOUR / "replay-seed-0.jsonl"
    dst = tmp_path / "replay-seed-0.jsonl"
    lines = src.read_text(encoding="utf-8").splitlines()
    # Corrupt the first tick row's state_hash.
    import json

    first = json.loads(lines[0])
    first["state_hash"] = "0" * 64
    lines[0] = json.dumps(first)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    game_map = load_canonical_map()
    with pytest.raises(FunnelReconstructionError):
        _walk_game(
            dst,
            seed=0,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            roles={f"p-{i}": "CREWMATE" for i in range(1, 5)},
            game_map=game_map,
        )


@pytest.mark.parametrize("field", ["state_hash_before", "state_hash_after"])
def test_walk_raises_on_corrupted_meeting_hash(tmp_path: Path, field: str) -> None:
    """A tampered meeting-row hash fails loud too (both meeting-side verifies).

    Distinct from the per-tick check: ``state_hash_before`` pins the state the
    meeting resolved against (the tick row's hash does not cover the meeting
    row's own copy), and ``state_hash_after`` pins the applied outcome — a
    drifted tally/ejection rule is caught, never silently mis-measured.
    """

    import json

    seed: int | None = None
    lines: list[str] = []
    for candidate in sorted(_FOUR.glob("replay-seed-*.jsonl")):
        text = candidate.read_text(encoding="utf-8").splitlines()
        if any('"kind":"meeting"' in ln for ln in text):
            seed = int(candidate.stem.rsplit("-", 1)[1])
            lines = text
            break
    assert seed is not None, "no committed 4p1i replay carries a meeting row"
    for i, ln in enumerate(lines):
        row = json.loads(ln)
        if row.get("kind") == "meeting":
            row[field] = "0" * 64
            lines[i] = json.dumps(row)
            break
    dst = tmp_path / f"replay-seed-{seed}.jsonl"
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    game_map = load_canonical_map()
    with pytest.raises(FunnelReconstructionError):
        _walk_game(
            dst,
            seed=seed,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            roles={f"p-{i}": "CREWMATE" for i in range(1, 5)},
            game_map=game_map,
        )


def test_walk_raises_on_missing_meeting_row(tmp_path: Path) -> None:
    """A MEETING tick with no meeting row fails loud, never silently truncates.

    Deliberate divergence from the serving loader (which shows a crashed run's
    prefix): an instrument that quietly dropped every meeting after a missing /
    tick-drifted meeting row would under-count the folds while exiting 0.
    """

    seed: int | None = None
    lines: list[str] = []
    for candidate in sorted(_FOUR.glob("replay-seed-*.jsonl")):
        text = candidate.read_text(encoding="utf-8").splitlines()
        if any('"kind":"meeting"' in ln for ln in text):
            seed = int(candidate.stem.rsplit("-", 1)[1])
            lines = text
            break
    assert seed is not None, "no committed 4p1i replay carries a meeting row"
    dst = tmp_path / f"replay-seed-{seed}.jsonl"
    dst.write_text(
        "\n".join(ln for ln in lines if '"kind":"meeting"' not in ln) + "\n",
        encoding="utf-8",
    )

    game_map = load_canonical_map()
    with pytest.raises(FunnelReconstructionError, match="no meeting row"):
        _walk_game(
            dst,
            seed=seed,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            roles={f"p-{i}": "CREWMATE" for i in range(1, 5)},
            game_map=game_map,
        )


# --------------------------------------------------------------------------- #
# Baseline-2 reproduction pins (charter §2)                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def nine_funnel() -> InformationFunnelReport:
    return compute_information_funnel(_NINE)


def test_funnel_reproduces_report_meeting_count(
    nine_funnel: InformationFunnelReport,
) -> None:
    # Baseline 3 (Task 15.7 re-record); the before/after reading vs baseline 2 is
    # in audits/audit-phase-15-wave0-close.md §2.
    assert nine_funnel.games_total == 50
    assert nine_funnel.report_meetings == 124


def test_funnel_reproduces_oracle_stage(nine_funnel: InformationFunnelReport) -> None:
    # Baseline-3 committed bytes: the oracle is a diagnostic ceiling; the median
    # holds at 3, and killer-in-set is preserved via one-hop reachability (the
    # model never wrongly alibis the killer).
    assert nine_funnel.candidate_set_median == 3
    assert nine_funnel.candidate_set_mean is not None
    assert round(nine_funnel.candidate_set_mean, 2) == 2.84
    assert nine_funnel.killer_in_set == 109
    assert nine_funnel.candidate_set_pm1_mean is not None
    assert round(nine_funnel.candidate_set_pm1_mean, 2) == 2.30
    # 38 singleton ±1-window sets, of which 35 hold EXACTLY the killer — the 3
    # misses are dead-killer late reports (unique_killer never over-counts a
    # singleton that convicted the wrong player).
    assert nine_funnel.candidate_singleton_pm1 == 38
    assert nine_funnel.unique_killer_pm1 == 35
    assert nine_funnel.candidate_le2_pm1 == 76


def test_funnel_reproduces_possession_stage(
    nine_funnel: InformationFunnelReport,
) -> None:
    assert nine_funnel.vent_witnessed == 73
    assert nine_funnel.kill_witnessed == 5
    assert nine_funnel.killer_at_scene == 33
    assert nine_funnel.last_seen_with_killer == 42
    # The union vent ∪ kill-witnessed ∪ scene ∪ last-seen (baseline 3; held-clue
    # supply is unchanged from baseline 2 at 98).
    assert nine_funnel.hard_clue_held == 98


def test_funnel_reproduces_transmission_stage(
    nine_funnel: InformationFunnelReport,
) -> None:
    # The Wave-0 transmission gains (audit-phase-15-wave0-close.md §2): free-text
    # vent mentions rose 36 -> 53 of 73 held, and the reporter damp cut
    # innocent-reporter ejections 22 -> 4.
    assert nine_funnel.vent_mentioned == 53
    assert nine_funnel.vent_meetings == 73
    assert nine_funnel.reporter_ejected == 4
    assert nine_funnel.reporter_ejected_innocent == 4
    assert nine_funnel.report_ejections == 95
    # Votes outside the ≤3 exact-tick candidate set.
    assert nine_funnel.votes_outside_small_set == 30
    assert nine_funnel.small_set_ejections == 64
    # The messenger-innocent-prior tripwire: no committed killer self-reports.
    assert nine_funnel.killer_self_reported == 0
    # The Wave-0 headline: 15.4's SawVentObservation type makes held vents
    # STRUCTURALLY speakable — 55 structured vent observations on baseline 3 where
    # the v4 baselines had 0/74. Pinned so the folds cannot silently drift.
    assert nine_funnel.structured_vent_observed == 55
    assert nine_funnel.killer_placement_observed == 40
    assert nine_funnel.killer_accused == 75


def test_funnel_runs_on_4p1i_preset() -> None:
    report = compute_information_funnel(_FOUR)
    assert report.num_players == 4
    assert report.num_impostors == 1
    assert report.games_total == 50
    # 4p1i has no charter table; pin the meeting count so the roster-keyed walk
    # (flat-default knobs) cannot silently drift on the committed bytes.
    assert report.report_meetings == 35
