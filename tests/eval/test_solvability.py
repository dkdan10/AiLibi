"""Unit tests + reproduction pins for eval/solvability.py.

Two layers. The fixture layer targets :func:`candidate_set_for_body_meeting`
directly — one behaviour per test, each built so that perturbing the rule flips
it (the clearing sighting removed, the witness turned impostor, the witness
killed, the witness moved into the body's room, the subject vented). The census
layer walks the four committed replay sets and pins every cell.

The census pins are this module's OWN recount, not the review's numbers. The
review (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1) reports
containment 581/626, singleton 109/626 with 103/109 correct, ≤2 208/626, and
61/354 ejections on an already-cleared player; those values are quoted beside
each pooled pin below with the definitional cause of the difference. The
headline cause is the kill anchor: re-scored under the review's "last kill
before the meeting" anchor this module returns containment 581/626 exactly,
which is what ``killer_in_set_last_kill_anchor`` carries.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from engine.entities import PlayerState, Role, SabotageState
from engine.rng import EngineRng
from engine.world import WorldState, load_canonical_map
from eval.replay_walk import MeetingOpened, walk_replay
from eval.solvability import (
    _WALK_CONFIG,
    SolvabilityReconstructionError,
    SolvabilityReport,
    _walk_game,
    candidate_set_for_body_meeting,
    compute_solvability_report,
)
from eval.validity import resolve_roster_knobs, roles_by_seed
from tests._helpers.committed import solvability_report

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"
_SAMPLES_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"
_CORPUS_9P2I = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_CORPUS_4P1I = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"

# The body's room, and a room that is not it. Both are canonical-map rooms.
_BODY_ROOM = "ADMIN"
_ELSEWHERE = "EAST_HALL"


# --------------------------------------------------------------------------- #
# Hand-built fixtures for the set logic.                                       #
# --------------------------------------------------------------------------- #


def _player(
    player_id: str,
    room: str,
    *,
    role: Role = "CREWMATE",
    alive: bool = True,
    in_vent: bool = False,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role=role,
        alive=alive,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=in_vent,
    )


def _kill_state(
    *players: PlayerState, sabotage: SabotageState | None = None
) -> WorldState:
    """A PRE-advance world state of the kill tick holding exactly ``players``."""

    game_map = load_canonical_map()
    return WorldState(
        tick=7,
        phase="PLAY",
        map=game_map.id,
        players={player.id: player for player in players},
        bodies={},
        tasks={},
        sabotage=sabotage,
        cooldowns={},
        emergency_uses={},
        rng_state=EngineRng.from_seed(1).snapshot(),
        seed=1,
    )


def _lights_sabotage() -> SabotageState:
    """An ACTIVE lights sabotage — the degrade that applies to everyone alike."""

    return SabotageState(
        kind="lights",
        remaining_ticks=90,
        affected_rooms=(_BODY_ROOM,),
        active=True,
    )


_ROLES: dict[str, Role] = {
    "p-suspect": "CREWMATE",
    "p-witness": "CREWMATE",
    "p-impostor": "IMPOSTOR",
    "p-in-room": "CREWMATE",
    "p-victim": "CREWMATE",
}


def _candidates(
    state: WorldState, living: set[str], *, victim: str = "p-victim"
) -> frozenset[str]:
    return candidate_set_for_body_meeting(
        kill_state=state,
        game_map=load_canonical_map(),
        roles=_ROLES,
        body_room=_BODY_ROOM,
        victim=victim,
        living_at_meeting=frozenset(living),
    )


def test_a_crewmate_sighting_clears_the_player_it_saw() -> None:
    """Two crewmates together outside the body's room clear each other."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE),
        _player("p-in-room", _BODY_ROOM),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect", "p-witness", "p-in-room"}) == frozenset(
        {"p-in-room"}
    )


def test_a_lone_impostor_witness_clears_nobody() -> None:
    """Same geometry, witness turned IMPOSTOR: the suspect stays a candidate.

    The crew cannot honestly pool the killer's own testimony, so an impostor
    never observes here — flipping this one role flips the cell.
    """

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-impostor", _ELSEWHERE, role="IMPOSTOR"),
        _player("p-victim", _BODY_ROOM),
    )

    assert "p-suspect" in _candidates(state, {"p-suspect", "p-impostor"})


def test_a_witness_killed_before_the_meeting_clears_nobody() -> None:
    """The witness saw it, then died: it is not there to say so."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect", "p-witness"}) == frozenset()
    # The same state, with the witness absent from the meeting's living roster.
    assert _candidates(state, {"p-suspect"}) == frozenset({"p-suspect"})


def test_a_witness_standing_in_the_body_room_clears_nobody() -> None:
    """Being seen IN the body's room is not an alibi — it is the opposite."""

    state = _kill_state(
        _player("p-suspect", _BODY_ROOM),
        _player("p-witness", _BODY_ROOM),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect", "p-witness"}) == frozenset(
        {"p-suspect", "p-witness"}
    )


def test_a_vented_player_is_never_cleared() -> None:
    """A vented player is visible to nobody, so no sighting can clear it."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE, in_vent=True),
        _player("p-witness", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect", "p-witness"}) == frozenset({"p-suspect"})


def test_self_placement_never_clears() -> None:
    """A lone crewmate outside the body's room does not clear itself."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect"}) == frozenset({"p-suspect"})


def test_an_observer_dead_at_the_kill_tick_clears_nobody() -> None:
    """Observers must be alive at the kill tick as well as at the meeting."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE, alive=False),
        _player("p-victim", _BODY_ROOM),
    )

    assert _candidates(state, {"p-suspect", "p-witness"}) == frozenset(
        {"p-suspect", "p-witness"}
    )


def test_a_lights_sabotage_tick_leaves_the_crew_rule_unchanged() -> None:
    """The degrade applies to everyone, and crew are same-room-only either way."""

    players = (
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE),
        _player("p-in-room", _BODY_ROOM),
        _player("p-victim", _BODY_ROOM),
    )
    living = {"p-suspect", "p-witness", "p-in-room"}

    lit = _candidates(_kill_state(*players), living)
    dark = _candidates(_kill_state(*players, sabotage=_lights_sabotage()), living)

    assert lit == dark == frozenset({"p-in-room"})


def test_a_victim_alive_at_its_own_meeting_is_a_reconstruction_breach() -> None:
    """A mis-anchored meeting fails loud rather than quietly scoring a ghost."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )

    with pytest.raises(SolvabilityReconstructionError, match="mis-anchored"):
        _candidates(state, {"p-suspect", "p-victim"})


def test_an_incomplete_role_map_is_a_reconstruction_breach() -> None:
    """A missing role would silently demote a crewmate out of the witness pool.

    The perturbation is the point: with ``p-witness`` present in ``roles`` the
    sighting clears ``p-suspect``; drop that one entry and, without this guard,
    the candidate set would quietly grow instead of failing.
    """

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )
    assert _candidates(state, {"p-suspect", "p-witness"}) == frozenset()

    with pytest.raises(SolvabilityReconstructionError, match="no role for"):
        candidate_set_for_body_meeting(
            kill_state=state,
            game_map=load_canonical_map(),
            roles={"p-suspect": "CREWMATE", "p-victim": "CREWMATE"},
            body_room=_BODY_ROOM,
            victim="p-victim",
            living_at_meeting=frozenset({"p-suspect", "p-witness"}),
        )


def test_a_living_player_absent_from_the_kill_state_is_a_breach() -> None:
    """Nobody joins mid-game, so a missing kill-tick entry is disagreeing input."""

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-victim", _BODY_ROOM),
    )

    with pytest.raises(SolvabilityReconstructionError, match="absent from the kill"):
        _candidates(state, {"p-suspect", "p-witness"})


def test_a_role_disagreeing_with_the_kill_state_is_a_breach() -> None:
    """Sight comes from the world state's role; the crew filter from ``roles``.

    An observer mapped CREWMATE but stored IMPOSTOR would enter the honest pool
    carrying adjacent-room vision and clear players no crewmate could see.
    """

    state = _kill_state(
        _player("p-suspect", _ELSEWHERE),
        _player("p-witness", _ELSEWHERE, role="IMPOSTOR"),
        _player("p-victim", _BODY_ROOM),
    )

    with pytest.raises(SolvabilityReconstructionError, match="disagrees with the kill"):
        _candidates(state, {"p-suspect", "p-witness"})


def test_a_replay_set_with_no_recordings_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(SolvabilityReconstructionError, match="no replay-seed"):
        compute_solvability_report(tmp_path)


# --------------------------------------------------------------------------- #
# The walk profile's integrity checks bite, through this module's error type.   #
# --------------------------------------------------------------------------- #


def _corrupted_set(tmp_path: Path, mutate: Callable[[list[str]], list[str]]) -> Path:
    """A one-game replay set copied from samples/4p1i, with ``mutate`` applied."""

    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    lines = (
        (_SAMPLES_4P1I / "replay-seed-0.jsonl").read_text(encoding="utf-8").splitlines()
    )
    (tmp_path / "replay-seed-0.jsonl").write_text(
        "\n".join(mutate(lines)) + "\n", encoding="utf-8"
    )
    return tmp_path


def test_the_profile_verifies_tick_hashes(tmp_path: Path) -> None:
    def flip_first_tick_hash(lines: list[str]) -> list[str]:
        first = json.loads(lines[0])
        assert first["kind"] == "tick"
        recorded = first["state_hash"]
        first["state_hash"] = ("0" if recorded[0] != "0" else "f") + recorded[1:]
        return [json.dumps(first), *lines[1:]]

    with pytest.raises(SolvabilityReconstructionError, match="tick 0 reconstructed"):
        compute_solvability_report(_corrupted_set(tmp_path, flip_first_tick_hash))


def test_the_profile_rejects_a_truncated_recording(tmp_path: Path) -> None:
    """An EOF-truncated recording would silently shrink the body-meeting count."""

    with pytest.raises(SolvabilityReconstructionError, match="without reaching"):
        compute_solvability_report(_corrupted_set(tmp_path, lambda lines: lines[:1]))


def test_a_relabelled_tick_row_is_rejected(tmp_path: Path) -> None:
    """Tick LABELS are outside the hash chain, so the fold binds them itself.

    Swapping two labels leaves row order, actions and every ``state_hash``
    intact — the whole profile passes — but files each pre-state under the
    other's tick, which is the state kills and meetings then resolve against.
    """

    def swap_the_first_two_tick_labels(lines: list[str]) -> list[str]:
        first, second = json.loads(lines[0]), json.loads(lines[1])
        assert first["kind"] == second["kind"] == "tick"
        first["tick"], second["tick"] = second["tick"], first["tick"]
        return [json.dumps(first), json.dumps(second), *lines[2:]]

    with pytest.raises(SolvabilityReconstructionError, match="reconstructs tick"):
        compute_solvability_report(
            _corrupted_set(tmp_path, swap_the_first_two_tick_labels)
        )


def test_the_profile_rejects_a_doubled_meeting_row(tmp_path: Path) -> None:
    def double_the_first_meeting(lines: list[str]) -> list[str]:
        index = next(
            i for i, line in enumerate(lines) if json.loads(line)["kind"] == "meeting"
        )
        return [*lines[: index + 1], lines[index], *lines[index + 1 :]]

    with pytest.raises(SolvabilityReconstructionError, match="duplicate meeting rows"):
        compute_solvability_report(_corrupted_set(tmp_path, double_the_first_meeting))


# --------------------------------------------------------------------------- #
# Emergency meetings are excluded entirely.                                    #
# --------------------------------------------------------------------------- #


def test_emergency_meetings_are_excluded_from_the_census() -> None:
    """Seed 0 of samples/9p2i holds 2 body meetings and 1 emergency meeting."""

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(_SAMPLES_9P2I)
    game_map = load_canonical_map()
    replay_path = _SAMPLES_9P2I / "replay-seed-0.jsonl"

    opened = [
        event
        for event in walk_replay(
            replay_path,
            seed=0,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=_WALK_CONFIG,
        )
        if isinstance(event, MeetingOpened)
    ]
    # Non-vacuity: the game really does carry a meeting with no reported body.
    assert sum(1 for event in opened if event.body_id is None) == 1
    assert sum(1 for event in opened if event.body_id is not None) == 2

    roles = roles_by_seed(
        _SAMPLES_9P2I,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )[0]
    fold = _walk_game(
        replay_path,
        seed=0,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        roles=roles,
        game_map=game_map,
    )

    assert len(fold.rows) == 2


# --------------------------------------------------------------------------- #
# Census pins over the four committed sets — one walk each, per worker.       #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def samples_9p2i() -> SolvabilityReport:
    return solvability_report(_SAMPLES_9P2I)


@pytest.fixture(scope="session")
def samples_4p1i() -> SolvabilityReport:
    return solvability_report(_SAMPLES_4P1I)


@pytest.fixture(scope="session")
def corpus_9p2i() -> SolvabilityReport:
    return solvability_report(_CORPUS_9P2I)


@pytest.fixture(scope="session")
def corpus_4p1i() -> SolvabilityReport:
    return solvability_report(_CORPUS_4P1I)


def _counts(report: SolvabilityReport) -> dict[str, tuple[int, int]]:
    return {
        name: (cell.numerator, cell.denominator)
        for name, cell in (
            ("killer_in_set", report.killer_in_set),
            ("singleton_sets", report.singleton_sets),
            ("singleton_correct", report.singleton_correct),
            ("at_most_two_sets", report.at_most_two_sets),
            ("at_most_two_contains_killer", report.at_most_two_contains_killer),
            ("cleared_player_ejections", report.cleared_player_ejections),
            (
                "killer_in_set_last_kill_anchor",
                report.killer_in_set_last_kill_anchor,
            ),
        )
    }


def test_samples_9p2i_cells(samples_9p2i: SolvabilityReport) -> None:
    assert samples_9p2i.games_total == 50
    assert samples_9p2i.body_meetings == 144  # of 165 recorded meetings  # was 151
    assert samples_9p2i.ejections_at_body_meetings == 91  # was 87
    assert _counts(samples_9p2i) == {
        "killer_in_set": (126, 144),
        "singleton_sets": (20, 144),
        "singleton_correct": (14, 20),
        "at_most_two_sets": (46, 144),
        "at_most_two_contains_killer": (37, 46),
        "cleared_player_ejections": (19, 91),
        "killer_in_set_last_kill_anchor": (135, 144),
    }


def test_samples_4p1i_cells(samples_4p1i: SolvabilityReport) -> None:
    assert samples_4p1i.games_total == 50
    assert samples_4p1i.body_meetings == 37  # of 39 recorded meetings  # was 35
    assert samples_4p1i.ejections_at_body_meetings == 18  # was 8
    # One impostor and at most three living crew: nobody is ever cleared away
    # from the killer, so containment is total on both 4p1i sets.
    assert _counts(samples_4p1i) == {
        "killer_in_set": (37, 37),
        "singleton_sets": (5, 37),
        "singleton_correct": (5, 5),
        "at_most_two_sets": (5, 37),
        "at_most_two_contains_killer": (5, 5),
        "cleared_player_ejections": (0, 18),
        "killer_in_set_last_kill_anchor": (37, 37),
    }


def test_corpus_9p2i_cells(corpus_9p2i: SolvabilityReport) -> None:
    assert corpus_9p2i.games_total == 150
    assert corpus_9p2i.body_meetings == 400  # of 463 recorded meetings  # was 411
    assert corpus_9p2i.ejections_at_body_meetings == 248  # was 250
    assert _counts(corpus_9p2i) == {
        "killer_in_set": (355, 400),
        "singleton_sets": (51, 400),
        "singleton_correct": (49, 51),
        "at_most_two_sets": (133, 400),
        "at_most_two_contains_killer": (112, 133),
        "cleared_player_ejections": (49, 248),
        "killer_in_set_last_kill_anchor": (377, 400),
    }


def test_corpus_4p1i_cells(corpus_4p1i: SolvabilityReport) -> None:
    assert corpus_4p1i.games_total == 50
    assert corpus_4p1i.body_meetings == 37  # of 40 recorded meetings  # was 29
    assert corpus_4p1i.ejections_at_body_meetings == 22  # was 9
    assert _counts(corpus_4p1i) == {
        "killer_in_set": (37, 37),
        "singleton_sets": (4, 37),
        "singleton_correct": (4, 4),
        "at_most_two_sets": (4, 37),
        "at_most_two_contains_killer": (4, 4),
        "cleared_player_ejections": (0, 22),
        "killer_in_set_last_kill_anchor": (37, 37),
    }


def test_pooled_denominators_and_headline_cells(
    samples_9p2i: SolvabilityReport,
    samples_4p1i: SolvabilityReport,
    corpus_9p2i: SolvabilityReport,
    corpus_4p1i: SolvabilityReport,
) -> None:
    """The pooled pin, with the review's [REVIEW-DERIVED] values beside it.

    Splits 151/87 + 35/8 + 411/250 + 29/9. Review vs this recount, and the
    definitional cause of each difference:

    * containment — review 581/626, here 544/626. Cause: the kill anchor. The
      review anchors on the last kill at or before the trigger tick; this module
      anchors on the REPORTED body's own kill. Re-scored under the review's
      anchor this module returns 581/626 exactly — the
      ``killer_in_set_last_kill_anchor`` pin below.
    * singleton — review 109/626, here 126/626; correctness review 103/109,
      here 114/126; ≤2 — review 208/626, here 246/626. Cause: the same anchor,
      plus a residual. Re-scored under the review's anchor these become
      120/626, 114/120 and 228/626, so the anchor explains most but not all of
      the set-size gap. The review's oracle is not committed; of the remaining
      definitional dimensions, taking the candidate pool at the kill tick forces
      containment to 626/626 and letting self-placement clear forces singleton
      to 522/626, and the review's figures are neither — so the residual is a
      further detail its one-sentence rule does not fix.
    * cleared-player ejections — review 61/354, here 83/354 (59/354 under the
      review's anchor). Same cause, same residual: a tighter candidate set
      clears more players, so more ejections land outside it.
    """

    reports = (samples_9p2i, samples_4p1i, corpus_9p2i, corpus_4p1i)
    pooled: dict[str, tuple[int, int]] = {}
    for report in reports:
        for name, (numerator, denominator) in _counts(report).items():
            carried = pooled.get(name, (0, 0))
            pooled[name] = (carried[0] + numerator, carried[1] + denominator)

    assert sum(report.games_total for report in reports) == 300
    assert sum(report.body_meetings for report in reports) == 618  # was 626
    assert (
        sum(report.ejections_at_body_meetings for report in reports) == 379
    )  # was 354
    assert pooled == {
        "killer_in_set": (555, 618),
        "singleton_sets": (80, 618),
        "singleton_correct": (72, 80),
        "at_most_two_sets": (188, 618),
        "at_most_two_contains_killer": (158, 188),
        "cleared_player_ejections": (68, 379),
        "killer_in_set_last_kill_anchor": (586, 618),
    }


def test_cells_carry_their_wilson_interval(samples_4p1i: SolvabilityReport) -> None:
    """The interval rides beside every rate — 35 body meetings is a small n."""

    cell = samples_4p1i.singleton_sets
    assert cell.rate is not None
    assert cell.wilson_low is not None
    assert cell.wilson_high is not None
    assert cell.rate == pytest.approx(5 / 37)  # was 6 / 35
    assert cell.wilson_low < cell.rate < cell.wilson_high
    assert cell.advisory is True  # numerator 6 is a rare-event count


def test_report_json_round_trips(samples_4p1i: SolvabilityReport) -> None:
    text = samples_4p1i.model_dump_json()
    assert SolvabilityReport.model_validate_json(text) == samples_4p1i


def test_report_carries_no_player_identifying_fields(
    samples_4p1i: SolvabilityReport,
) -> None:
    """Count-only block: no roles, ids, rooms, or transcripts leave the module."""

    payload = samples_4p1i.model_dump(mode="json")
    assert set(payload) == {
        "replay_set_dir",
        "num_players",
        "num_impostors",
        "tasks_per_crewmate",
        "games_total",
        "body_meetings",
        "ejections_at_body_meetings",
        "killer_in_set",
        "singleton_sets",
        "singleton_correct",
        "at_most_two_sets",
        "at_most_two_contains_killer",
        "cleared_player_ejections",
        "killer_in_set_last_kill_anchor",
    }
    for name in (
        "killer_in_set",
        "singleton_sets",
        "singleton_correct",
        "at_most_two_sets",
        "at_most_two_contains_killer",
        "cleared_player_ejections",
        "killer_in_set_last_kill_anchor",
    ):
        assert set(payload[name]) == {
            "numerator",
            "denominator",
            "rate",
            "wilson_low",
            "wilson_high",
            "advisory",
        }
