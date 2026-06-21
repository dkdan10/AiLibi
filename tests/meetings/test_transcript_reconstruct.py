"""Tests for :func:`meetings.transcript.reconstruct_stated_paths` (Task 13.2).

The helper promotes ``inference_feasibility_probe.py::reconstruct`` from
engine truth onto the PUBLIC meeting transcript: it rebuilds each subject's
STATED room-by-tick path from the transcript's ``saw_player`` observations
ONLY (DESIGN.md §5.4; experiments/lab/report-phase-b-plan.md). The contract:

* every ``saw_player`` observation places its ``subject`` and each
  ``co_present`` player in the sighting's canonical room(s) at its tick,
  traceable to that observation's id;
* which sightings count is the §6.3 relevance gate
  (:func:`meetings.transcript.is_relevant_sighting`) -- spawn-window and
  kill-scene sightings reconstruct no position -- plus a spatial-room check;
* the roster filter mirrors :func:`detect_contradictions`;
* the function is pure and replay-deterministic (run twice -> byte-identical);
* it imports nothing from ``engine`` / ``observation`` / perception (the
  §1.3 firewall: ``meetings`` stays engine-free).
"""

from __future__ import annotations

import ast
import inspect
import json
from collections.abc import Mapping

import meetings.transcript as transcript_module
from meetings.schemas import (
    AccusationClaim,
    Claim,
    CompletedTaskObservation,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
)
from meetings.transcript import StatedPlacement, reconstruct_stated_paths


# --- Builders --------------------------------------------------------------


def _saw(
    *, tick: int, subject: str, room: str, co_present: tuple[str, ...] = ()
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player",
        tick=tick,
        subject=subject,
        room=room,
        co_present=co_present,
    )


def _found_body(*, tick: int, body_of: str, room: str) -> FoundBodyObservation:
    return FoundBodyObservation(
        type="found_body", tick=tick, body_of=body_of, room=room
    )


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "opening",
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=f"turn {turn_index} from {speaker}",
    )


def _placement(*, tick: int, room: str, speaker: str, event_id: str) -> StatedPlacement:
    return StatedPlacement(
        tick=tick, rooms=frozenset({room}), speaker=speaker, event_id=event_id
    )


# --- Empty / no-sighting transcripts ---------------------------------------


class TestEmptyAndIrrelevantInput:
    def test_empty_transcript_returns_empty_mapping(self) -> None:
        assert reconstruct_stated_paths(MeetingTranscript()) == {}

    def test_transcript_with_no_sightings_returns_empty_mapping(self) -> None:
        # An opening turn carrying only an accusation + a found_body + a
        # completed_task contributes no `saw_player`, so nothing is placed.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-5",
                    confidence=0.7,
                    reason="suspicious",
                ),
            ),
            observations=(
                _found_body(tick=40, body_of="p-2", room="MEDBAY"),
                CompletedTaskObservation(
                    type="completed_task", tick=30, task_id="wiring", room="ADMIN"
                ),
            ),
        )
        assert reconstruct_stated_paths(MeetingTranscript(turns=(turn,))) == {}

    def test_only_saw_player_observations_are_read(self) -> None:
        # A found_body places the body, not a living subject's path; only the
        # saw_player on the same turn reconstructs a position.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(
                _found_body(tick=40, body_of="p-2", room="MEDBAY"),
                _saw(tick=30, subject="p-3", room="STORAGE"),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert paths == {
            "p-3": (
                _placement(
                    tick=30,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:1",
                ),
            )
        }


# --- Single-subject reconstruction -----------------------------------------


class TestSubjectPaths:
    def test_single_sighting_yields_one_placement(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-5",
            observations=(_saw(tick=40, subject="p-3", room="STORAGE"),),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert paths == {
            "p-3": (
                _placement(
                    tick=40,
                    room="STORAGE",
                    speaker="p-5",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
            )
        }

    def test_multiple_sightings_of_one_subject_sort_by_tick(self) -> None:
        # Two speakers place p-3 in different rooms at different ticks; the
        # path is the sorted sequence of both stated placements (a later rule
        # decides whether they are physically compatible -- 13.3 / 13.4).
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(_saw(tick=30, subject="p-3", room="ADMIN"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(_saw(tick=12, subject="p-3", room="STORAGE"),),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=turns))
        assert paths == {
            "p-3": (
                _placement(
                    tick=12,
                    room="STORAGE",
                    speaker="p-2",
                    event_id="turn:m-1:turn-1:obs:0",
                ),
                _placement(
                    tick=30,
                    room="ADMIN",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
            )
        }

    def test_self_stated_sighting_is_placed_with_speaker_recorded(self) -> None:
        # A speaker recording their own movement ("saw myself in WEST_HALL")
        # is still a stated placement; `speaker == subject` lets a consumer
        # recognise it as self-stated (vs. an independent witness).
        turn = _turn(
            turn_index=0,
            speaker="p-3",
            observations=(_saw(tick=17, subject="p-3", room="WEST_HALL"),),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert paths == {
            "p-3": (
                _placement(
                    tick=17,
                    room="WEST_HALL",
                    speaker="p-3",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
            )
        }
        assert paths["p-3"][0].speaker == "p-3"


class TestCoPresence:
    def test_co_present_players_get_their_own_placement(self) -> None:
        # "I saw p-3 in STORAGE co_present with p-7" places BOTH p-3 and p-7
        # in STORAGE at that tick, both traceable to the same observation.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(
                _saw(tick=25, subject="p-3", room="STORAGE", co_present=("p-7",)),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        shared = _placement(
            tick=25, room="STORAGE", speaker="p-1", event_id="turn:m-1:turn-0:obs:0"
        )
        assert paths == {"p-3": (shared,), "p-7": (shared,)}

    def test_subject_in_own_co_present_is_not_double_counted(self) -> None:
        # A degenerate co_present listing the subject collapses: the subject
        # is placed exactly once by the observation.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(
                _saw(tick=25, subject="p-3", room="STORAGE", co_present=("p-3", "p-3")),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert paths == {
            "p-3": (
                _placement(
                    tick=25,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
            )
        }


# --- Relevance gate (reuses is_relevant_sighting) --------------------------


class TestRelevanceGate:
    def test_spawn_window_sightings_are_excluded(self) -> None:
        # tick 0 and tick 1 are the spawn window (everyone co-spawns in
        # CAFETERIA); they reconstruct no position. tick 2 onward counts.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(
                    _saw(tick=0, subject="p-3", room="CAFETERIA"),
                    _saw(tick=1, subject="p-3", room="CAFETERIA"),
                    _saw(tick=2, subject="p-3", room="STORAGE"),
                ),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=turns))
        assert paths == {
            "p-3": (
                _placement(
                    tick=2,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:2",
                ),
            )
        }

    def test_kill_scene_sightings_are_excluded_on_a_report_meeting(self) -> None:
        # The opening found_body fixes the kill scene (MEDBAY); a sighting that
        # places the subject AT the scene must not reconstruct (presence at the
        # scene is not an exculpatory position), while an off-scene sighting does.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(_found_body(tick=40, body_of="p-2", room="MEDBAY"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(
                    _saw(tick=30, subject="p-3", room="MEDBAY"),
                    _saw(tick=32, subject="p-3", room="STORAGE"),
                ),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=turns))
        assert paths == {
            "p-3": (
                _placement(
                    tick=32,
                    room="STORAGE",
                    speaker="p-5",
                    event_id="turn:m-1:turn-1:obs:1",
                ),
            )
        }

    def test_emergency_trigger_kind_drops_the_kill_scene_exclusion(self) -> None:
        # An emergency meeting has no body by design (Task 10.11), so even a
        # found_body on the opening turn does not exclude an in-room sighting.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(_found_body(tick=40, body_of="p-2", room="MEDBAY"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=30, subject="p-3", room="MEDBAY"),),
            ),
        )
        paths = reconstruct_stated_paths(
            MeetingTranscript(turns=turns), trigger_kind="emergency"
        )
        assert paths == {
            "p-3": (
                _placement(
                    tick=30,
                    room="MEDBAY",
                    speaker="p-5",
                    event_id="turn:m-1:turn-1:obs:0",
                ),
            )
        }

    def test_non_spatial_room_label_reconstructs_no_position(self) -> None:
        # A label with no canonical map room ("SOMEWHERE") locates nobody.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(
                    _saw(tick=30, subject="p-3", room="SOMEWHERE"),
                    _saw(tick=31, subject="p-3", room="STORAGE"),
                ),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=turns))
        assert paths == {
            "p-3": (
                _placement(
                    tick=31,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:1",
                ),
            )
        }

    def test_compound_room_label_is_canonicalised(self) -> None:
        # A compound account ("LABS/MEDBAY") canonicalises to its member rooms.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(_saw(tick=30, subject="p-3", room="LABS/MEDBAY"),),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert set(paths) == {"p-3"}
        (placement,) = paths["p-3"]
        assert placement.rooms == frozenset({"LABS", "MEDBAY"})


# --- Roster filtering (mirrors detect_contradictions) ----------------------


class TestRosterFilter:
    def test_roster_none_places_every_named_player(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(
                _saw(tick=30, subject="p-99", room="STORAGE", co_present=("p-98",)),
            ),
        )
        paths = reconstruct_stated_paths(MeetingTranscript(turns=(turn,)))
        assert set(paths) == {"p-98", "p-99"}

    def test_explicit_roster_drops_non_roster_subject_and_co_present(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(
                # p-3 (roster) seen with p-99 (hallucinated, off-roster).
                _saw(tick=30, subject="p-3", room="STORAGE", co_present=("p-99",)),
                # whole sighting about an off-roster subject.
                _saw(tick=31, subject="p-99", room="ADMIN"),
            ),
        )
        roster = frozenset({"p-1", "p-3"})
        paths = reconstruct_stated_paths(
            MeetingTranscript(turns=(turn,)), roster=roster
        )
        assert paths == {
            "p-3": (
                _placement(
                    tick=30,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
            )
        }

    def test_empty_roster_places_nobody(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            observations=(_saw(tick=30, subject="p-3", room="STORAGE"),),
        )
        assert (
            reconstruct_stated_paths(
                MeetingTranscript(turns=(turn,)), roster=frozenset()
            )
            == {}
        )


# --- The "expected paths" hand-built transcript ----------------------------


def _hand_built_transcript() -> MeetingTranscript:
    """A small multi-subject transcript exercising every contributing shape."""
    return MeetingTranscript(
        turns=(
            _turn(
                turn_index=0,
                speaker="p-1",
                turn_kind="opening",
                observations=(
                    _saw(tick=10, subject="p-3", room="STORAGE"),
                    _saw(tick=20, subject="p-3", room="ADMIN"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                observations=(
                    _saw(tick=15, subject="p-4", room="MEDBAY", co_present=("p-3",)),
                ),
            ),
        )
    )


class TestHandBuiltExpectedPaths:
    def test_reconstruction_matches_expected_paths(self) -> None:
        paths = reconstruct_stated_paths(_hand_built_transcript())
        assert paths == {
            "p-3": (
                _placement(
                    tick=10,
                    room="STORAGE",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:0",
                ),
                _placement(
                    tick=15,
                    room="MEDBAY",
                    speaker="p-2",
                    event_id="turn:m-1:turn-1:obs:0",
                ),
                _placement(
                    tick=20,
                    room="ADMIN",
                    speaker="p-1",
                    event_id="turn:m-1:turn-0:obs:1",
                ),
            ),
            "p-4": (
                _placement(
                    tick=15,
                    room="MEDBAY",
                    speaker="p-2",
                    event_id="turn:m-1:turn-1:obs:0",
                ),
            ),
        }

    def test_subjects_and_placements_are_sorted(self) -> None:
        paths = reconstruct_stated_paths(_hand_built_transcript())
        assert list(paths) == sorted(paths)
        for placements in paths.values():
            ticks = [placement.tick for placement in placements]
            assert ticks == sorted(ticks)

    def test_every_placement_is_traceable_to_a_transcript_saw_player(self) -> None:
        # The 13.4 firewall guarantee: each placement's event_id resolves to a
        # `saw_player` observation actually present in the transcript.
        transcript = _hand_built_transcript()
        saw_ids = {
            f"turn:{turn.turn_id}:obs:{index}"
            for turn in transcript.turns
            for index, observation in enumerate(turn.observations)
            if isinstance(observation, SawPlayerObservation)
        }
        paths = reconstruct_stated_paths(transcript)
        for placements in paths.values():
            for placement in placements:
                assert placement.event_id in saw_ids


# --- Purity / determinism --------------------------------------------------


def _canonical(paths: Mapping[str, tuple[StatedPlacement, ...]]) -> str:
    """A byte-stable serialisation independent of frozenset iteration order."""
    return json.dumps(
        {
            subject: [
                [p.tick, sorted(p.rooms), p.speaker, p.event_id] for p in placements
            ]
            for subject, placements in paths.items()
        },
        sort_keys=True,
    )


class TestPurityAndDeterminism:
    def test_running_twice_is_byte_identical(self) -> None:
        transcript = _hand_built_transcript()
        first = reconstruct_stated_paths(transcript)
        second = reconstruct_stated_paths(transcript)
        assert first == second
        assert _canonical(first) == _canonical(second)

    def test_function_does_not_mutate_the_transcript(self) -> None:
        transcript = _hand_built_transcript()
        before = transcript.model_dump(mode="json")
        reconstruct_stated_paths(transcript)
        assert transcript.model_dump(mode="json") == before

    def test_returns_plain_mapping_of_tuples_of_placements(self) -> None:
        paths = reconstruct_stated_paths(_hand_built_transcript())
        for subject, placements in paths.items():
            assert isinstance(subject, str)
            assert isinstance(placements, tuple)
            for placement in placements:
                assert isinstance(placement, StatedPlacement)
                assert isinstance(placement.rooms, frozenset)


# --- Firewall: meetings.transcript imports no engine/observation/perception -


def _imported_modules() -> set[str]:
    """Every absolute module imported by ``meetings.transcript`` (AST walk).

    Walks import statements only -- comments and string literals that mention
    "engine" (the module documents the firewall in prose) are never read.
    """
    tree = ast.parse(inspect.getsource(transcript_module))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


class TestFirewall:
    def test_transcript_module_imports_no_engine_layer(self) -> None:
        for module in _imported_modules():
            root = module.split(".")[0]
            assert root not in {"engine", "observation"}, module
            assert "perception" not in module, module
