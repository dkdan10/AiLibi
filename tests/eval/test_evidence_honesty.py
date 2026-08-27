"""Unit tests + committed-set pins for eval/evidence_honesty.py.

Three layers. The DEFINITION layer asserts each cell's one definition sentence is
present verbatim in the module docstring and in its own cell family's docstring —
that is the string Task 20.22 copies into the pre-registration memo, so a memo
that disagrees with the code makes this test fail. The FIXTURE layer targets each
fold directly on hand-built inputs, one behaviour per test, each perturbable. The
PIN layer walks the four committed replay sets and pins every cell.

The pins are this module's OWN recount. Where a value differs from the
2026-08-19 review's, the difference is named with its cause beside the pin; the
review's session scripts are not committed (audits/audit-phase-20-planning.md §4
item 4), which is the whole reason this instrument exists.

The impostor-targeting pins (free kills declined; ghost-top decisions) live in
``tests/agents/test_impostor_policy.py`` — the file Task 20.32's mover repair owns
— so the repair updates one pin set.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections import Counter
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple

import pytest

from agents.memory import store as memory_store
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    _collect_self_location_spans,
    render_for_prompt,
)
from agents.memory.beliefs import OBSERVED_KILL_ACTION, OBSERVED_VENT_ACTION
from agents.perception import (
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.impostor_policy import RankedTarget
from engine.entities import PlayerId, Role, RoomId
from engine.world import load_canonical_map
from eval import evidence_honesty
from eval.evidence_honesty import (
    AGENT_CLOCK_OFFSET,
    CELL_DEFINITIONS,
    CUSTOM_POLICY_FOLD,
    LIVE_POLICY_FOLD,
    AdjacentRoomFlagCells,
    EvidenceHonestyReconstructionError,
    EvidenceHonestyReport,
    FabricatedCompletionCells,
    FalseWhereaboutsCells,
    GroundedSightingCells,
    ImpostorTargetingCells,
    MarkerContaminationCells,
    MeetingPhysicalityCells,
    MovementOriginFlagCells,
    SingularPersonaCells,
    SoleFlagPrecisionCells,
    _living_bucket,
    _classify_decline,
    _event_index,
    _fold_completion_rows,
    _fold_flags,
    _fold_geometry,
    _fold_ghost_top,
    _fold_turns,
    _fold_whereabouts,
    _fold_meeting_into_memories,
    _marker_prefixes,
    _MeetingFacts,
    _perceive_tick,
    _resolve_flag,
    _RENDERED_ROW,
    _ResolvedFlag,
    _room_distances,
    _SelfLocations,
    _TopRanked,
    _singular_persona_phrase,
    _Tallies,
    _TESTIMONY_ROW,
    _WALK_CONFIG,
    cell,
    compute_evidence_honesty,
)
from meetings.constants import MAP_ARBITRATION_MAX_TICK_GAP
from meetings.manager import INVALID_ACCUSATION_TARGET_MARKER
from meetings.schemas import (
    AlibiClaim,
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VentWitnessRecord,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (
    canonical_rooms,
    detect_contradictions,
    is_weak_contradiction,
)
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    TickAdvanced,
    TickOpened,
    walk_replay,
)
from eval.balance_eval import run_balance_eval
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from observation.service import ObservationService
from agents.strategic.prompts.loader import ENV_PROMPT_SET
from orchestrator.game import DEFAULT_TASKS_PER_CREWMATE
from orchestrator.replay import LLMCallRecord, MeetingReplayEntry, read_all_entries
from tests._helpers.world_state import scripted_initial_world_state

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"
_SAMPLES_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"
_CORPUS_9P2I = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_CORPUS_4P1I = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"

_CELL_OWNERS = {
    "I-2": FalseWhereaboutsCells,
    "I-3": SoleFlagPrecisionCells,
    "I-4": GroundedSightingCells,
    "I-5": FabricatedCompletionCells,
    "I-6": AdjacentRoomFlagCells,
    "I-7": MovementOriginFlagCells,
    "I-8": MarkerContaminationCells,
    "I-9": SingularPersonaCells,
    "I-10": MeetingPhysicalityCells,
    "I-11": ImpostorTargetingCells,
}


def _flat(text: str) -> str:
    """Collapse a wrapped docstring to one line for verbatim comparison."""

    return " ".join(text.split())


# --------------------------------------------------------------------------- #
# Layer 1 — the definitions Task 20.22 copies into the memo.                   #
# --------------------------------------------------------------------------- #


def test_every_instrument_row_has_a_definition() -> None:
    assert sorted(CELL_DEFINITIONS) == sorted(_CELL_OWNERS)


def _definition_drift(cell_id: str, definition: str) -> list[str]:
    """Where ``definition`` fails to appear verbatim, as the memo would copy it.

    The one validation path: the real test feeds the module's own sentence and
    expects nothing back, the perturbation test feeds a drifted one through the
    SAME function and expects both surfaces to reject it.
    """

    module_doc = evidence_honesty.__doc__
    owner_doc = _CELL_OWNERS[cell_id].__doc__
    assert module_doc is not None and owner_doc is not None
    sentence = _flat(definition)
    missing: list[str] = []
    if sentence not in _flat(module_doc):
        missing.append("module docstring")
    if sentence not in _flat(owner_doc):
        missing.append(f"{_CELL_OWNERS[cell_id].__name__} docstring")
    return missing


@pytest.mark.parametrize("cell_id", sorted(_CELL_OWNERS))
def test_definition_sentence_is_verbatim_in_module_and_cell_docstrings(
    cell_id: str,
) -> None:
    assert _definition_drift(cell_id, CELL_DEFINITIONS[cell_id]) == []


@pytest.mark.parametrize("cell_id", sorted(_CELL_OWNERS))
def test_a_drifted_definition_is_rejected_by_the_same_path(cell_id: str) -> None:
    """The gate bites: a memo sentence that drifted is rejected on both surfaces."""

    drifted = CELL_DEFINITIONS[cell_id].replace("numerator", "count")
    assert _definition_drift(cell_id, drifted) == [
        "module docstring",
        f"{_CELL_OWNERS[cell_id].__name__} docstring",
    ]


# --------------------------------------------------------------------------- #
# Layer 2 — the folds, on hand-built inputs.                                   #
# --------------------------------------------------------------------------- #


def test_room_distances_come_from_the_map_doorways() -> None:
    game_map = load_canonical_map()
    distances = _room_distances(game_map)
    for room in game_map.rooms:
        assert distances[room][room] == 0
        for neighbor in game_map.room_neighbors(room):
            assert distances[room][neighbor] == 1
        # Every room is reachable, and nothing claims a shortcut the map lacks.
        assert set(distances[room]) == set(game_map.rooms)


def test_marker_prefixes_are_derived_from_the_manager_constants() -> None:
    prefixes = _marker_prefixes()
    assert len(prefixes) == 3
    assert INVALID_ACCUSATION_TARGET_MARKER.startswith(prefixes[0])
    # A prefix stops at the interpolation, so a formatted marker still matches.
    assert INVALID_ACCUSATION_TARGET_MARKER.format(target="'p-6'").startswith(
        prefixes[0]
    )
    assert not any("{" in prefix for prefix in prefixes)


def test_singular_persona_phrase_is_read_from_the_committed_templates() -> None:
    assert _singular_persona_phrase() == "a hidden impostor"


def test_living_buckets_partition_the_living_counts() -> None:
    assert [_living_bucket(n) for n in (2, 4, 5, 6, 7, 9)] == [
        "<=4",
        "<=4",
        "5-6",
        "5-6",
        ">=7",
        ">=7",
    ]


def test_cell_carries_the_wilson_interval_and_the_rare_advisory() -> None:
    rare = cell(1, 10)
    assert rare.rate == pytest.approx(0.1)
    assert rare.advisory is True
    assert rare.wilson_low is not None and rare.wilson_low < 0.1
    empty = cell(0, 0)
    assert empty.rate is None and empty.wilson_low is None


def _turn(
    *,
    index: int,
    speaker: str,
    observations: tuple[object, ...] = (),
    claims: tuple[object, ...] = (),
    free_text: str = "text",
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None,
        observations=observations,  # type: ignore[arg-type]
        claims=claims,  # type: ignore[arg-type]
        free_text=free_text,
    )


def test_whereabouts_is_false_only_when_both_engine_ticks_disagree() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=5, room="LABS"),
                ),
            ),
        )
    )
    truthful = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "LABS"}, 5: {"p-1": "MEDBAY"}},
        copyable=set(),
        tallies=truthful,
    )
    assert (truthful.crew_claims, truthful.crew_false) == (1, 0)

    lying = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "ADMIN"}, 5: {"p-1": "MEDBAY"}},
        copyable=set(),
        tallies=lying,
    )
    assert (lying.crew_claims, lying.crew_false) == (1, 1)


@pytest.mark.parametrize(
    "spoken", ["LABS", "labs", "Labs", "LABS_TRANSITION", "LABS/MEDBAY"]
)
def test_a_reformatted_room_label_is_not_a_crewmate_lie(spoken: str) -> None:
    """PLANTED: every canonical spelling of a TRUE placement scores truthful.

    Each of these scored as a crewmate lie under the raw string compare this
    replaced. They are inert on the committed bytes — all 3,117 recorded labels
    are self-canonical uppercase single rooms — and latent on the next prompt or
    parser change, which is exactly why the four sibling comparisons in this
    module already route through ``canonical_rooms``.
    """

    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=5, room=spoken),
                ),
            ),
        )
    )
    tallies = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "LABS"}, 5: {"p-1": "LABS"}},
        copyable=set(),
        tallies=tallies,
    )
    # Still counted — the denominator is unchanged — and not a lie.
    assert (tallies.crew_claims, tallies.crew_false) == (1, 0)
    assert tallies.crew_false_agent_frame == 0


def test_a_genuinely_disjoint_compound_label_is_still_a_lie() -> None:
    """The canonicalisation must not turn every compound label into a pass.

    A compound account whose member rooms are ALL wrong stays false; only an
    intersection with the speaker's true rooms clears it.
    """

    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(
                        type="whereabouts", tick=5, room="ADMIN/CAFETERIA"
                    ),
                ),
            ),
        )
    )
    tallies = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "LABS"}, 5: {"p-1": "LABS"}},
        copyable=set(),
        tallies=tallies,
    )
    assert (tallies.crew_claims, tallies.crew_false) == (1, 1)


def test_a_non_spatial_label_is_uncomparable_not_false() -> None:
    """A label with no canonical member is "no room", which is not a lie.

    The rule ``canonical_rooms`` states for every comparison site: two labels are
    contradictory only when both canonicalise to non-empty, disjoint sets.
    """

    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=5, room="the vents"),
                ),
            ),
        )
    )
    tallies = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "LABS"}, 5: {"p-1": "LABS"}},
        copyable=set(),
        tallies=tallies,
    )
    assert (tallies.crew_claims, tallies.crew_false) == (1, 0)


def test_whereabouts_with_no_recorded_tick_is_unverifiable_not_false() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=99, room="LABS"),
                ),
            ),
        )
    )
    tallies = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1"}),
        roles={"p-1": "CREWMATE"},
        room_at={4: {"p-1": "LABS"}},
        copyable=set(),
        tallies=tallies,
    )
    assert (tallies.crew_claims, tallies.crew_false) == (0, 0)


def test_whereabouts_splits_crew_from_impostor_and_scores_copyability() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=5, room="LABS"),
                ),
            ),
            _turn(
                index=1,
                speaker="p-2",
                observations=(
                    WhereaboutsClaim(type="whereabouts", tick=5, room="LABS"),
                ),
            ),
        )
    )
    tallies = _Tallies()
    _fold_whereabouts(
        transcript=transcript,
        living=frozenset({"p-1", "p-2"}),
        roles={"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
        room_at={
            4: {"p-1": "ADMIN", "p-2": "ADMIN"},
            5: {"p-1": "ADMIN", "p-2": "ADMIN"},
        },
        copyable={("p-1", 5, "LABS")},
        tallies=tallies,
    )
    assert (tallies.crew_claims, tallies.crew_false) == (1, 1)
    assert (tallies.impostor_claims, tallies.impostor_false) == (1, 1)
    assert tallies.copyable_self_location == 1


def _call(prompt: str, agent_id: str = "p-1") -> LLMCallRecord:
    return LLMCallRecord(
        call_kind="meeting",
        model="fake",
        prompt=prompt,
        response_text="{}",
        input_tokens=1,
        output_tokens=1,
        cost_usd=0.0,
        agent_id=agent_id,
    )


_TRUE_ROW = "- [obs p-1:5:0] [tick 5] You completed submit_scan (you were in MEDBAY)."
_FALSE_ROW = "- [obs p-1:3:0] [tick 3] You completed empty_trash (you were in LABS)."


def test_completion_row_is_fabricated_without_an_earlier_engine_event() -> None:
    tallies = _Tallies()
    found = _SelfLocations()
    _fold_completion_rows(
        call=_call(f"{_TRUE_ROW}\n{_FALSE_ROW}"),
        completions={"p-1": {4}},
        seen_rows=set(),
        found=found,
        tallies=tallies,
    )
    assert tallies.completion_lines == 2
    assert tallies.fabricated_lines == 1
    assert found.fabricated is True
    # The true row sits exactly one tick after its engine event (the calibration).
    assert (tallies.render_offset_matches, tallies.render_offset_checked) == (1, 1)
    assert ("p-1", 5, "MEDBAY") in found.pairs


def test_completion_rows_are_deduplicated_by_observation_id() -> None:
    tallies = _Tallies()
    seen: set[tuple[str, str]] = set()
    for _ in range(3):
        _fold_completion_rows(
            call=_call(_TRUE_ROW),
            completions={"p-1": {4}},
            seen_rows=seen,
            found=_SelfLocations(),
            tallies=tallies,
        )
    assert tallies.completion_lines == 1


def test_turn_marker_fold_counts_only_a_leading_marker() -> None:
    marker = INVALID_ACCUSATION_TARGET_MARKER.format(target="'p-6'")
    transcript = MeetingTranscript(
        turns=(
            _turn(index=0, speaker="p-1", free_text=f"{marker}I saw p-3 vent."),
            _turn(index=1, speaker="p-2", free_text="p-1 mentioned a dropped target."),
        )
    )
    tallies = _Tallies()
    assert _fold_turns(transcript, tallies=tallies) is True
    assert (tallies.marker_turns, tallies.turns) == (1, 2)


def _resolved(
    *,
    alibi_room: str,
    sighting_room: str,
    from_tick: int,
    to_tick: int,
    sighting_tick: int,
) -> _ResolvedFlag:
    sighting = SawPlayerObservation(
        type="saw_player", tick=sighting_tick, subject="p-3", room=sighting_room
    )
    return _ResolvedFlag(
        flag=ContradictionRef(
            contradiction_id="c-0",
            kind="alibi_vs_sighting",
            event_a_id="a",
            event_b_id="b",
            subjects=("p-3",),
            description="d",
        ),
        strong=True,
        subject="p-3",
        speaker="p-9",
        sighting=sighting,
        alibi_room=alibi_room,
        from_tick=from_tick,
        to_tick=to_tick,
    )


def test_geometry_reads_adjacency_from_the_map_and_the_tick_gap() -> None:
    distances = _room_distances(load_canonical_map())
    adjacent = _Tallies()
    _fold_geometry(
        _resolved(
            alibi_room="ENGINEERING",
            sighting_room="EAST_HALL",
            from_tick=4,
            to_tick=4,
            sighting_tick=4,
        ),
        distances=distances,
        tallies=adjacent,
    )
    assert (adjacent.adjacent_flags, adjacent.adjacent_any_gap) == (1, 1)
    assert adjacent.single_tick_window == 1

    far = _Tallies()
    _fold_geometry(
        _resolved(
            alibi_room="ENGINEERING",
            sighting_room="MEDBAY",
            from_tick=4,
            to_tick=8,
            sighting_tick=6,
        ),
        distances=distances,
        tallies=far,
    )
    assert far.adjacent_flags == 0
    assert far.adjacent_any_gap == 0
    assert far.distance_two + far.distance_three_plus == 1
    assert far.single_tick_window == 0


def test_geometry_tick_gap_gates_the_registered_i6_numerator() -> None:
    distances = _room_distances(load_canonical_map())
    inside = _Tallies()
    _fold_geometry(
        _resolved(
            alibi_room="ENGINEERING",
            sighting_room="EAST_HALL",
            from_tick=10,
            to_tick=12,
            sighting_tick=12,
        ),
        distances=distances,
        tallies=inside,
    )
    # Adjacent rooms and the sighting inside the window: gap 0, both cells fire.
    assert (inside.adjacent_flags, inside.adjacent_any_gap) == (1, 1)

    far_gap = _Tallies()
    _fold_geometry(
        _resolved(
            alibi_room="ENGINEERING",
            sighting_room="EAST_HALL",
            from_tick=10,
            to_tick=12,
            sighting_tick=20,
        ),
        distances=distances,
        tallies=far_gap,
    )
    # Adjacent rooms but eight ticks outside the window: one tick of walking no
    # longer reconciles them, so the REGISTERED cell must not count it.
    assert (far_gap.adjacent_flags, far_gap.adjacent_any_gap) == (0, 1)


def test_a_spoken_room_is_canonicalised_before_it_is_compared() -> None:
    distances = _room_distances(load_canonical_map())
    tallies = _Tallies()
    _fold_geometry(
        _resolved(
            alibi_room="engineering",
            sighting_room="east_hall/west_hall",
            from_tick=4,
            to_tick=4,
            sighting_tick=4,
        ),
        distances=distances,
        tallies=tallies,
    )
    # Lower case and a compound label are what the detector itself accepted, so
    # the geometry fold reads them through the same canonicaliser and takes the
    # nearest member: ENGINEERING is one doorway from EAST_HALL.
    assert (tallies.adjacent_flags, tallies.distance_two) == (1, 0)


def test_flag_resolution_reads_the_two_ids_by_type_not_by_position() -> None:
    sighting = SawPlayerObservation(
        type="saw_player", tick=6, subject="p-3", room="MEDBAY"
    )
    alibi = AlibiClaim(type="alibi", subject="p-3", from_tick=6, to_tick=6, room="LABS")
    transcript = MeetingTranscript(
        turns=(
            _turn(index=0, speaker="p-9", observations=(sighting,)),
            _turn(index=1, speaker="p-3", claims=(alibi,)),
        )
    )
    index = _event_index(transcript)
    sighting_id = "turn:m:turn-0:obs:0"
    alibi_id = "turn:m:turn-1:claim:0"
    for event_a, event_b in ((alibi_id, sighting_id), (sighting_id, alibi_id)):
        resolved = _resolve_flag(
            ContradictionRef(
                contradiction_id="c-0",
                kind="alibi_vs_sighting",
                event_a_id=event_a,
                event_b_id=event_b,
                subjects=("p-3",),
                description="d",
            ),
            index=index,
        )
        assert resolved is not None
        assert resolved.speaker == "p-9"
        assert resolved.alibi_room == "LABS"
        assert resolved.sighting.room == "MEDBAY"


def test_flag_resolution_returns_none_for_an_unresolvable_pair() -> None:
    transcript = MeetingTranscript(turns=(_turn(index=0, speaker="p-9"),))
    assert (
        _resolve_flag(
            ContradictionRef(
                contradiction_id="c-0",
                kind="alibi_vs_sighting",
                event_a_id="turn:missing:claim:0",
                event_b_id="turn:missing:obs:0",
                subjects=("p-3",),
                description="d",
            ),
            index=_event_index(transcript),
        )
        is None
    )


# --- The movement-sided sighting, and the flag said twice --------------------
#
# A spoken transition "X moved A -> B, arriving at t" is a sighting side: the
# detector indexes it as ONE placement, X in B at t, and mints the flag from
# that room. These fixtures are SYNTHETIC — the shape reaches a recording only
# under the v4 prompt set, and no committed replay carries one.

_FLAG_ALIBI = AlibiClaim(
    type="alibi", subject="p-3", from_tick=6, to_tick=8, room="LABS"
)
_FLAG_ROLES: Mapping[PlayerId, Role] = MappingProxyType(
    {"p-3": "IMPOSTOR", "p-6": "CREWMATE", "p-9": "CREWMATE"}
)
_FLAG_ROOM_AT: Mapping[int, Mapping[PlayerId, RoomId]] = MappingProxyType(
    {6: MappingProxyType({"p-3": "LABS"}), 7: MappingProxyType({"p-3": "MEDBAY"})}
)


def _saw_move(*, to_room: str) -> SawMoveObservation:
    return SawMoveObservation(
        type="saw_move", tick=8, subject="p-3", from_room="LABS", to_room=to_room
    )


def _witness_memory(
    *, saw_player_in: str | None = None, moved_to: str | None = "MEDBAY"
) -> MemoryStore:
    """p-9's own perception rows — one channel at a time, on purpose.

    A witness who saw a DEPARTURE holds only the move row: there is no
    ``saw_player`` row for a destination they never looked into, and the default
    here is that move-only memory so a grounding assertion cannot pass on the
    wrong channel.
    """

    events = []
    if saw_player_in is not None:
        events.append(
            EpisodicEvent(
                tick=8,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": "p-3", "room": saw_player_in},
                provenance=PROVENANCE_OBSERVED,
                observation_id="p-9:8:0",
            )
        )
    if moved_to is not None:
        events.append(
            EpisodicEvent(
                tick=8,
                type=EVENT_SAW_PLAYER_MOVE,
                payload={"player_id": "p-3", "from_room": "LABS", "to_room": moved_to},
                provenance=PROVENANCE_OBSERVED,
                observation_id="p-9:8:1",
            )
        )
    return _memory_with(*events)


def _saw_player(*, room: str) -> SawPlayerObservation:
    return SawPlayerObservation(type="saw_player", tick=8, subject="p-3", room=room)


def _sighting_flag(*, sighting_id: str) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id=f"contra:alibi_vs_sighting:{sighting_id}|alibi",
        kind="alibi_vs_sighting",
        event_a_id=sighting_id,
        event_b_id="turn:m:turn-1:claim:0",
        subjects=("p-3",),
        description="Alibi places p-3 in LABS (ticks 6-8); sighting reports MEDBAY.",
    )


def _flag_meeting(
    *, turns: tuple[MeetingTurn, ...], flags: tuple[ContradictionRef, ...]
) -> _MeetingFacts:
    """One recorded meeting that ejected p-3, carrying ``flags``."""

    return _MeetingFacts(
        entry=MeetingReplayEntry(
            game_id="g",
            meeting_id="g:meeting-0",
            tick=7,
            triggered_by="p-9",
            outcome="EJECTED",
            ejected_player_id="p-3",
            transcript=MeetingTranscript(turns=turns),
            ballots=(),
            contradictions=flags,
            llm_calls=(),
            prompt_versions={},
            state_hash_before="before",
            state_hash_after="after",
        ),
        living=frozenset({"p-3", "p-6", "p-9"}),
        venting=frozenset(),
        body_triggered=True,
        # Filled by :func:`_fold` from the memories the case hands it.
        memory_prefix={},
    )


def _fold(
    facts: _MeetingFacts,
    *,
    memories: Mapping[PlayerId, MemoryStore],
    memory_prefix: Mapping[PlayerId, int] | None = None,
) -> _Tallies:
    """Fold one hand-built meeting; ``memory_prefix`` defaults to the whole log.

    A hand-built store already holds exactly what its case means the speaker to
    have perceived by meeting time, so the default prefix is its full length —
    which is what keeps every case below reading as it did before the bound
    existed. The planted post-meeting case passes a shorter one.
    """

    tallies = _Tallies()
    _fold_flags(
        game_id="g",
        facts=replace(
            facts,
            memory_prefix=(
                {pid: len(store) for pid, store in memories.items()}
                if memory_prefix is None
                else memory_prefix
            ),
        ),
        roles=_FLAG_ROLES,
        memories=memories,
        room_at=_FLAG_ROOM_AT,
        distances=_room_distances(load_canonical_map()),
        tallies=tallies,
    )
    return tallies


def test_a_movement_sided_sighting_is_read_at_its_destination() -> None:
    turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_move(to_room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    flag = _sighting_flag(sighting_id="turn:m:turn-0:obs:0")
    resolved = _resolve_flag(flag, index=_event_index(MeetingTranscript(turns=turns)))
    assert resolved is not None
    # The destination placement the detector minted the flag from, and only it:
    # the origin half is never placed at tick - 1.
    assert (resolved.sighting.room, resolved.sighting.tick) == ("MEDBAY", 8)
    assert (resolved.subject, resolved.speaker) == ("p-3", "p-9")

    tallies = _fold(
        _flag_meeting(turns=turns, flags=(flag,)), memories={"p-9": _witness_memory()}
    )
    assert tallies.strong_flags == 1
    # I-6 reads LABS -> MEDBAY, one doorway. Read at the ORIGIN the two rooms
    # would be the same room, distance 0, and the flag would land in NO bucket.
    assert (tallies.adjacent_flags, tallies.distance_three_plus) == (1, 0)
    # I-4 grounds against the speaker's own transition row, which lands at
    # MEDBAY — the origin read would look for LABS and find nothing.
    assert (tallies.resolvable_sides, tallies.grounded_at_tick) == (1, 1)
    # I-7 classifies it as the DESTINATION half, which is the truthful one.
    assert (tallies.move_backed_flags, tallies.destination_flags) == (1, 1)
    assert (tallies.resolved_sighting_flags, tallies.origin_flags) == (1, 0)

    # Perturbed: the same transition landing three doorways away. Every cell
    # above moves with ``to_room``, which is what proves it is the room read.
    far_turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_move(to_room="ADMIN"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    far = _fold(
        _flag_meeting(turns=far_turns, flags=(flag,)),
        memories={"p-9": _witness_memory()},
    )
    assert (far.adjacent_flags, far.distance_three_plus) == (0, 1)
    assert far.grounded_at_tick == 0
    assert (far.destination_flags, far.origin_flags) == (0, 0)


def test_a_movement_sided_side_is_grounded_by_whichever_channel_holds_it() -> None:
    # I-4 asks whether the speaker COULD have seen what they said. A witness who
    # saw a DEPARTURE holds no saw_player row at the destination, so refusing the
    # move channel would score a production-grounded side as unsupported.
    turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_move(to_room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    move_flag = _sighting_flag(sighting_id="turn:m:turn-0:obs:0")
    by_move = _fold(
        _flag_meeting(turns=turns, flags=(move_flag,)),
        memories={"p-9": _witness_memory(moved_to="MEDBAY")},
    )
    assert (by_move.resolvable_sides, by_move.grounded_at_tick) == (1, 1)

    # A witness who watched the ARRIVAL holds the static row instead, and it
    # supports the same placement: the cell is about the room, not the channel.
    by_sighting = _fold(
        _flag_meeting(turns=turns, flags=(move_flag,)),
        memories={"p-9": _witness_memory(saw_player_in="MEDBAY", moved_to=None)},
    )
    assert (by_sighting.resolvable_sides, by_sighting.grounded_at_tick) == (1, 1)

    # Perturbed: a static row for the same subject and tick in a DIFFERENT room.
    # The room is read, not assumed, so nothing grounds the placement.
    wrong_room = _fold(
        _flag_meeting(turns=turns, flags=(move_flag,)),
        memories={"p-9": _witness_memory(saw_player_in="ADMIN", moved_to=None)},
    )
    assert (wrong_room.resolvable_sides, wrong_room.grounded_at_tick) == (1, 0)

    # Perturbed: neither channel holds anything.
    ungrounded = _fold(
        _flag_meeting(turns=turns, flags=(move_flag,)),
        memories={"p-9": _witness_memory(moved_to=None)},
    )
    assert (ungrounded.resolvable_sides, ungrounded.grounded_at_tick) == (1, 0)

    # And the clause that protects every committed cell: a STATIC sighting by a
    # speaker holding only the move row is NOT grounded. The move channel is
    # admitted for movement-sided placements only.
    static_turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_player(room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    static = _fold(
        _flag_meeting(
            turns=static_turns,
            flags=(_sighting_flag(sighting_id="turn:m:turn-0:obs:0"),),
        ),
        memories={"p-9": _witness_memory(moved_to="MEDBAY")},
    )
    assert (static.resolvable_sides, static.grounded_at_tick) == (1, 0)


def test_a_perception_taken_after_the_meeting_grounds_nothing_said_at_it() -> None:
    """The planted case for the memory bound: look-ahead is not grounding.

    I-4 asks whether the speaker COULD have seen what they said, and I-7 reads
    the same log for the move row behind a spoken placement. Both folds run
    after the walk has closed, so both would otherwise scan an end-of-game log.
    Here p-9's only supporting rows — the static MEDBAY sighting and the
    LABS→MEDBAY move — land AFTER the meeting opened, at the spoken tick itself
    and therefore well inside the ±2 tolerance, which is exactly the shape a
    tolerance window cannot exclude on its own. Under the meeting-time prefix
    the side is ungrounded and the flag is not move-backed; over the whole log
    both light up. Both directions are asserted, so the bound cannot pass by
    being inert.
    """

    turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_move(to_room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    flags = (_sighting_flag(sighting_id="turn:m:turn-0:obs:0"),)
    # Row 0 is what p-9 held when the meeting opened: a sighting in the WRONG
    # room, which supports nothing. Rows 1 and 2 are perceived afterwards.
    late_memory = _memory_with(
        EpisodicEvent(
            tick=8,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-3", "room": "ADMIN"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-9:8:0",
        ),
        EpisodicEvent(
            tick=8,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-3", "room": "MEDBAY"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-9:8:1",
        ),
        EpisodicEvent(
            tick=8,
            type=EVENT_SAW_PLAYER_MOVE,
            payload={"player_id": "p-3", "from_room": "LABS", "to_room": "MEDBAY"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-9:8:2",
        ),
    )

    bounded = _fold(
        _flag_meeting(turns=turns, flags=flags),
        memories={"p-9": late_memory},
        memory_prefix={"p-9": 1},
    )
    assert (bounded.resolvable_sides, bounded.grounded_within_2) == (1, 0)
    assert (bounded.resolved_sighting_flags, bounded.move_backed_flags) == (1, 0)

    unbounded = _fold(
        _flag_meeting(turns=turns, flags=flags),
        memories={"p-9": late_memory},
    )
    assert (unbounded.resolvable_sides, unbounded.grounded_within_2) == (1, 1)
    assert (unbounded.resolved_sighting_flags, unbounded.move_backed_flags) == (1, 1)


def test_a_missing_memory_prefix_raises_rather_than_reading_the_whole_log() -> None:
    """A speaker the walk perceived for but did not record is a wiring bug.

    Falling back to the whole log would silently restore the look-ahead the
    prefix exists to remove, so the fold raises instead.
    """

    turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_move(to_room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    with pytest.raises(EvidenceHonestyReconstructionError, match="prefix"):
        _fold(
            _flag_meeting(
                turns=turns, flags=(_sighting_flag(sighting_id="turn:m:turn-0:obs:0"),)
            ),
            memories={"p-9": _witness_memory(moved_to="MEDBAY")},
            memory_prefix={},
        )


def test_one_witnesss_placement_said_twice_folds_once_into_every_cell() -> None:
    # p-9 states the same perception two ways — "I saw p-3 in MEDBAY at 8" and
    # "I saw p-3 move LABS -> MEDBAY at 8" — so two flags reach the recording
    # against one alibi. They are one piece of evidence and count once.
    twin_turns = (
        _turn(
            index=0,
            speaker="p-9",
            observations=(_saw_player(room="MEDBAY"), _saw_move(to_room="MEDBAY")),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    twin_flags = (
        _sighting_flag(sighting_id="turn:m:turn-0:obs:0"),
        _sighting_flag(sighting_id="turn:m:turn-0:obs:1"),
    )
    once = _fold(
        _flag_meeting(turns=twin_turns, flags=twin_flags),
        memories={"p-9": _witness_memory(moved_to="MEDBAY")},
    )
    assert once.strong_flags == 1  # I-6 denominator
    assert once.adjacent_flags == 1  # I-6 numerator
    assert once.strong_sides == 1  # I-4 denominator
    assert once.resolved_sighting_flags == 1  # I-7 denominator
    # I-3: the ejected player carried ONE strong flag, not two.
    assert (once.single_flag_victim_total, once.single_flag_victim_impostor) == (1, 1)
    # The TRANSITION is the survivor, not the static half: the speaker's memory
    # holds only the move row, so a grounded side can only be the movement one.
    assert once.grounded_at_tick == 1

    # Perturbed: the transition spoken by a SECOND witness instead. Two
    # witnesses are two independent pieces of evidence and must stay two — the
    # dedup keys on the speaker for exactly this reason.
    witnesses_turns = (
        _turn(index=0, speaker="p-9", observations=(_saw_player(room="MEDBAY"),)),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
        _turn(index=2, speaker="p-6", observations=(_saw_move(to_room="MEDBAY"),)),
    )
    witnesses_flags = (
        _sighting_flag(sighting_id="turn:m:turn-0:obs:0"),
        _sighting_flag(sighting_id="turn:m:turn-2:obs:0"),
    )
    twice = _fold(
        _flag_meeting(turns=witnesses_turns, flags=witnesses_flags),
        memories={"p-9": _witness_memory(), "p-6": _witness_memory()},
    )
    assert twice.strong_flags == 2
    assert twice.adjacent_flags == 2
    assert twice.strong_sides == 2
    assert twice.resolved_sighting_flags == 2
    assert twice.single_flag_victim_total == 0


def test_one_witness_placing_a_subject_in_two_rooms_is_two_flags() -> None:
    # The near-miss the dedup must NOT swallow: one speaker, one subject, one
    # tick — but two DIFFERENT rooms, stated as two static sightings. A witness
    # who contradicts themselves has made two statements, and collapsing them
    # would understate the class census the I-3 base rate is read against.
    turns = (
        _turn(
            index=0,
            speaker="p-9",
            observations=(_saw_player(room="MEDBAY"), _saw_player(room="ADMIN")),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    flags = (
        _sighting_flag(sighting_id="turn:m:turn-0:obs:0"),
        _sighting_flag(sighting_id="turn:m:turn-0:obs:1"),
    )
    tallies = _fold(
        _flag_meeting(turns=turns, flags=flags),
        memories={"p-9": _witness_memory(saw_player_in="MEDBAY", moved_to=None)},
    )
    assert tallies.strong_flags == 2
    assert tallies.resolved_sighting_flags == 2
    assert (tallies.adjacent_flags, tallies.distance_three_plus) == (1, 1)

    # And the same sentence twice IS one flag — even re-spelt. Rooms fold
    # through the same canonicaliser the detector compared them with, so a
    # lower-case echo is the same placement, not a second one.
    echo_turns = (
        _turn(
            index=0,
            speaker="p-9",
            observations=(_saw_player(room="MEDBAY"), _saw_player(room="medbay")),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    echo = _fold(
        _flag_meeting(turns=echo_turns, flags=flags),
        memories={"p-9": _witness_memory(saw_player_in="MEDBAY", moved_to=None)},
    )
    assert echo.strong_flags == 1
    assert echo.resolved_sighting_flags == 1


def test_a_transition_only_subsumes_a_placement_at_one_of_its_endpoints() -> None:
    # The near-miss on the OTHER side of the rule: the same speaker states a
    # transition LABS -> MEDBAY and, at the same tick, places the subject in a
    # THIRD room. ADMIN is neither endpoint, so it is a separate statement and
    # both flags must survive.
    third_room_turns = (
        _turn(
            index=0,
            speaker="p-9",
            observations=(_saw_move(to_room="MEDBAY"), _saw_player(room="ADMIN")),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    flags = (
        _sighting_flag(sighting_id="turn:m:turn-0:obs:0"),
        _sighting_flag(sighting_id="turn:m:turn-0:obs:1"),
    )
    kept = _fold(
        _flag_meeting(turns=third_room_turns, flags=flags),
        memories={"p-9": _witness_memory(moved_to="MEDBAY")},
    )
    assert kept.strong_flags == 2
    assert kept.resolved_sighting_flags == 2
    # MEDBAY is one doorway from LABS, ADMIN is three: both flags priced.
    assert (kept.adjacent_flags, kept.distance_three_plus) == (1, 1)

    # Perturbed onto the ORIGIN endpoint: naming the room the transition left is
    # the same witnessed event, so it folds — this is the recorded shape, where
    # the detector rewrote the origin-worded placement at mint time.
    origin_turns = (
        _turn(
            index=0,
            speaker="p-9",
            observations=(_saw_move(to_room="MEDBAY"), _saw_player(room="LABS")),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    folded = _fold(
        _flag_meeting(turns=origin_turns, flags=flags),
        memories={"p-9": _witness_memory(moved_to="MEDBAY")},
    )
    assert folded.strong_flags == 1
    assert folded.resolved_sighting_flags == 1
    assert folded.adjacent_flags == 1  # the surviving read is the destination


def test_a_flag_the_dedup_cannot_key_still_raises_through_the_fold() -> None:
    # Planted: an alibi_vs_sighting flag whose two sides are BOTH alibis. The
    # dedup has no identity for it and must not swallow it — the guard has to
    # see it, because a flag that vanishes from I-4/I-6/I-7 still counts in the
    # I-3 class census.
    turns = (
        _turn(
            index=0,
            speaker="p-9",
            claims=(
                AlibiClaim(
                    type="alibi", subject="p-9", from_tick=6, to_tick=8, room="MEDBAY"
                ),
            ),
        ),
        _turn(index=1, speaker="p-3", claims=(_FLAG_ALIBI,)),
    )
    flag = _sighting_flag(sighting_id="turn:m:turn-0:claim:0")
    with pytest.raises(
        EvidenceHonestyReconstructionError,
        match="do not resolve to one spoken sighting and one alibi",
    ):
        _fold(
            _flag_meeting(turns=turns, flags=(flag,)),
            memories={"p-9": _witness_memory()},
        )


def test_ghost_top_splits_the_two_sub_populations_and_skips_the_living() -> None:
    tallies = _Tallies()
    _fold_ghost_top(
        tallies=tallies,
        ranked_first=[
            _TopRanked(20, "p-4", declined_free_kill=True),
            _TopRanked(20, "p-5", declined_free_kill=True),
            _TopRanked(20, "p-6", declined_free_kill=True),
        ],
        death_tick={"p-4": 10, "p-5": 12, "p-6": 30},
        ejected_at={"p-4": 10},
    )
    assert tallies.ghost_top == 2
    assert (tallies.ghost_top_ejected, tallies.ghost_top_unseen) == (1, 1)
    # Only the EJECTED ghost's decline is a blocked kill: the unseen-death half
    # needs a kill-knowledge channel this repair deliberately does not add, and
    # the living p-6 is no ghost at all.
    assert tallies.kills_blocked_by_ghost_top == 1
    assert tallies.games_with_a_blocked_kill == 1


def test_a_ghost_top_decision_that_took_no_free_kill_is_not_a_blocked_kill() -> None:
    # The perturbation that proves the blocked-kill cell is narrower than ghost-top.
    tallies = _Tallies()
    _fold_ghost_top(
        tallies=tallies,
        ranked_first=[_TopRanked(20, "p-4", declined_free_kill=False)],
        death_tick={"p-4": 10},
        ejected_at={"p-4": 10},
    )
    assert tallies.ghost_top_ejected == 1
    assert tallies.kills_blocked_by_ghost_top == 0
    assert tallies.games_with_a_blocked_kill == 0


def _self_state(tick: int, room: str) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload={"room": room, "role": "IMPOSTOR"},
        provenance="observed",
        observation_id=None,
    )


def _saw_body(tick: int, room: str) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_body",
        payload={"victim_id": "p-2", "room": room},
        provenance="observed",
        observation_id=None,
    )


class _StatePlayer:
    def __init__(self, room: str, *, alive: bool = True, in_vent: bool = False) -> None:
        self.room = room
        self.alive = alive
        self.in_vent = in_vent


class _State:
    def __init__(self, players: dict[str, _StatePlayer]) -> None:
        self.players = players


def _memory_with(*events: EpisodicEvent) -> MemoryStore:
    memory = MemoryStore()
    for event in events:
        memory.append(event)
    return memory


def test_declined_kill_is_attributed_to_the_branch_that_swallowed_it() -> None:
    state = _State(
        {
            "p-1": _StatePlayer("LABS"),
            "p-4": _StatePlayer("LABS"),
            "p-6": _StatePlayer("LABS"),
        }
    )
    impostors = frozenset({"p-4", "p-6"})
    ranking_defect = _Tallies()
    _classify_decline(
        actor="p-4",
        victim="p-1",
        state=state,  # type: ignore[arg-type]
        impostor_ids=impostors,
        memory=_memory_with(_self_state(7, "LABS")),
        targets=(RankedTarget(player_id="p-9", room="ADMIN", co_present=0, score=1.0),),
        tallies=ranking_defect,
    )
    # The seam scans the whole ranking, so "ranking" now means the victim is
    # nowhere in it that the scan could find -- not merely that it is not first.
    assert ranking_defect.decline_ranking == 1

    victim_ranked_second = _Tallies()
    _classify_decline(
        actor="p-4",
        victim="p-1",
        state=state,  # type: ignore[arg-type]
        impostor_ids=impostors,
        memory=_memory_with(_self_state(7, "LABS")),
        targets=(
            RankedTarget(player_id="p-9", room="ADMIN", co_present=0, score=1.0),
            RankedTarget(player_id="p-1", room="LABS", co_present=0, score=1.0),
        ),
        tallies=victim_ranked_second,
    )
    assert victim_ranked_second.decline_ranking == 0
    assert victim_ranked_second.decline_other == 1

    fellow_defer = _Tallies()
    _classify_decline(
        actor="p-6",
        victim="p-1",
        state=state,  # type: ignore[arg-type]
        impostor_ids=impostors,
        memory=_memory_with(_self_state(7, "LABS")),
        targets=(RankedTarget(player_id="p-1", room="LABS", co_present=0, score=1.0),),
        tallies=fellow_defer,
    )
    assert fellow_defer.decline_fellow == 1

    cover = _Tallies()
    _classify_decline(
        actor="p-4",
        victim="p-1",
        state=state,  # type: ignore[arg-type]
        impostor_ids=impostors,
        memory=_memory_with(_self_state(7, "LABS"), _saw_body(7, "LABS")),
        targets=(RankedTarget(player_id="p-1", room="LABS", co_present=0, score=1.0),),
        tallies=cover,
    )
    assert cover.decline_cover == 1


# --------------------------------------------------------------------------- #
# Layer 2b — the preconditions, perturbed so the gates prove they bite.        #
# --------------------------------------------------------------------------- #


def test_a_perturbed_agent_clock_fails_the_alignment_assertion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(evidence_honesty, "AGENT_CLOCK_OFFSET", 2)
    with pytest.raises(EvidenceHonestyReconstructionError, match="agent clock moved"):
        compute_evidence_honesty(_SAMPLES_4P1I)


def test_a_planted_policy_mismatch_fails_when_fidelity_is_asserted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from agents.tactical.impostor_policy import ImpostorPolicy
    from observation.action_intent import WaitIntent

    def _always_wait(
        self: ImpostorPolicy, memory: object, public_map: object
    ) -> object:
        return WaitIntent(type="wait", actor=self.agent_id)

    monkeypatch.setattr(ImpostorPolicy, "decide", _always_wait)
    with pytest.raises(
        EvidenceHonestyReconstructionError, match="reconstructed a different action"
    ):
        compute_evidence_honesty(_SAMPLES_4P1I, assert_recorded_action_fidelity=True)


def test_the_same_mismatch_is_counted_when_fidelity_is_not_asserted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The split that keeps I-2...I-10 off the policy's back: since the 20.32 mover
    # repair the tree's policy is NOT the one the bytes were recorded with, so the
    # default fold counts the disagreements instead of raising and every other
    # instrument still reports. A wait-only policy disagrees on nearly every
    # decision, and the false-whereabouts cell is unmoved by that.
    from agents.tactical.impostor_policy import ImpostorPolicy
    from observation.action_intent import WaitIntent

    def _always_wait(
        self: ImpostorPolicy, memory: object, public_map: object
    ) -> object:
        return WaitIntent(type="wait", actor=self.agent_id)

    monkeypatch.setattr(ImpostorPolicy, "decide", _always_wait)
    report = compute_evidence_honesty(_SAMPLES_4P1I)

    assert report.impostor_targeting.reconstruction_mismatches > 0
    assert report.impostor_targeting.policy_mode == LIVE_POLICY_FOLD
    assert _counts(report.false_whereabouts.crew_false) == (1, 80)


def test_a_caller_supplied_policy_is_never_reported_as_the_live_fold() -> None:
    # ``policy_mode`` is the block's provenance, so it has to follow the policy
    # actually folded: a caller-supplied factory reports the custom mode, and the
    # default — the same call with the argument omitted — still reports the live
    # one, which is the pair that proves the label is derived and not constant.
    from agents.tactical.impostor_policy import ImpostorPolicy

    def _explicit(agent_id: PlayerId) -> ImpostorPolicy:
        return ImpostorPolicy(agent_id=agent_id)

    custom = compute_evidence_honesty(_SAMPLES_4P1I, impostor_policy=_explicit)
    default = compute_evidence_honesty(_SAMPLES_4P1I)

    assert custom.impostor_targeting.policy_mode == CUSTOM_POLICY_FOLD
    assert default.impostor_targeting.policy_mode == LIVE_POLICY_FOLD
    # The label is provenance only — the folded cells themselves are identical,
    # because ``_explicit`` builds the very same policy the default does.
    assert custom.impostor_targeting.model_dump(
        exclude={"policy_mode"}
    ) == default.impostor_targeting.model_dump(exclude={"policy_mode"})


def test_a_directory_with_no_recordings_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(EvidenceHonestyReconstructionError, match="not a replay set"):
        compute_evidence_honesty(tmp_path)


def test_a_truncated_recording_fails_the_walk(tmp_path: Path) -> None:
    source = _SAMPLES_4P1I / "replay-seed-0.jsonl"
    lines = source.read_text(encoding="utf-8").splitlines()
    (tmp_path / "replay-seed-0.jsonl").write_text(
        "\n".join(lines[: len(lines) // 2]) + "\n", encoding="utf-8"
    )
    (tmp_path / "roster.json").write_text(
        (_SAMPLES_4P1I / "roster.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(EvidenceHonestyReconstructionError):
        compute_evidence_honesty(tmp_path)


# --------------------------------------------------------------------------- #
# Layer 3 — the four committed sets' pins.                                     #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def reports() -> Mapping[Path, EvidenceHonestyReport]:
    """One report per committed set, computed once for the module.

    The module scope IS the cache (tests/conftest.py is out of scope and module
    state is not); the mapping is read-only so one test cannot re-price another.
    """

    return MappingProxyType(
        {
            sample_dir: compute_evidence_honesty(sample_dir)
            for sample_dir in (
                _SAMPLES_9P2I,
                _CORPUS_9P2I,
                _SAMPLES_4P1I,
                _CORPUS_4P1I,
            )
        }
    )


def _counts(cell_value: object) -> tuple[int, int]:
    numerator = getattr(cell_value, "numerator")
    denominator = getattr(cell_value, "denominator")
    assert isinstance(numerator, int) and isinstance(denominator, int)
    return numerator, denominator


@pytest.mark.slow
def test_i2_false_crew_self_placement_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-1]: 148/723, 402/2038, 7/78, 11/79. Every DENOMINATOR
    # reproduces exactly; the numerators run 3-7 higher per set because this
    # instrument admits a claim as truthful only when the spoken room matches the
    # speaker's own engine room at tick N or N-1, while the review's unpublished
    # script evidently admitted a third neighbouring tick — the residual is
    # 0.6 points on the 9p2i sets and is carried, not smoothed.
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.crew_false) == (3, 659)
    assert _counts(reports[_CORPUS_9P2I].false_whereabouts.crew_false) == (17, 1892)
    assert _counts(reports[_SAMPLES_4P1I].false_whereabouts.crew_false) == (1, 80)
    assert _counts(reports[_CORPUS_4P1I].false_whereabouts.crew_false) == (0, 91)
    # The strict agent-frame reading of the same rule (engine ticks N-1 and N-2).
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.crew_false_agent_frame) == (
        2,
        659,
    )
    # Impostors lie about their own whereabouts at roughly twice the crew rate
    # (the review: 46-48%), which is what makes the crew cell a defect and not a
    # measure of deception.
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.impostor_false) == (1, 104)
    # Self-placement coverage: how often a rendered self-location row carried the
    # exact (tick, room) pair the claim used.
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.copyable_self_location) == (
        42,
        659,
    )


@pytest.mark.slow
def test_i3_sole_flag_precision_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Both conventions reproduce the review [A/verdicts.md G-2] EXACTLY when
    # pooled over the four sets: per-victim 12 right / 70 wrong = 12/82, and
    # per-meeting 82 sole-flag meetings driving 77 ejections, 65 of them
    # crewmates. The pre-registration's bar 4 is the per-victim cell.
    per_victim = [
        _counts(reports[d].sole_flag_precision.per_victim_precision)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert per_victim == [(0, 0), (0, 0), (0, 0), (0, 0)]
    assert (sum(n for n, _ in per_victim), sum(d for _, d in per_victim)) == (0, 0)

    meetings = sum(
        reports[d].sole_flag_precision.per_meeting_sole_flag_meetings
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    ejections = sum(
        reports[d].sole_flag_precision.per_meeting_ejections
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    crewmates = sum(
        reports[d].sole_flag_precision.per_meeting_crewmate_ejections.numerator
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    assert (meetings, ejections, crewmates) == (0, 0, 0)

    # The class impostor share, deduped by subject, against the same meetings'
    # living-voter base rate (the review: 4/47 on samples/9p2i, 28/142 on the
    # corpus, 33/192 pooled vs a 25.3% base rate).
    assert _counts(reports[_SAMPLES_9P2I].sole_flag_precision.class_impostor_share) == (
        0,
        0,
    )
    assert _counts(reports[_CORPUS_9P2I].sole_flag_precision.class_impostor_share) == (
        0,
        0,
    )
    pooled_class = [
        _counts(reports[d].sole_flag_precision.class_impostor_share)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert (sum(n for n, _ in pooled_class), sum(d for _, d in pooled_class)) == (0, 0)
    # The stricter exactly-one-flag reading of the same population, emitted so
    # the choice of "only" stays a measured difference: it returns 8/58 pooled,
    # which is NOT the review's 12/70 wrong split — the kind-sole reading above is.
    single = [
        _counts(reports[d].sole_flag_precision.per_victim_single_flag_precision)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert single == [(0, 0), (0, 0), (0, 0), (0, 0)]
    assert (sum(n for n, _ in single), sum(d for _, d in single)) == (0, 0)

    base = reports[_SAMPLES_9P2I].sole_flag_precision.living_voter_base_rate
    # The class emptied, so the base rate has no denominator: the None sentinel,
    # never 0.0 (baseline 6 read 0.25 over a populated class).
    assert _counts(base) == (0, 0)
    assert base.rate is None


@pytest.mark.slow
def test_i4_grounded_sighting_side_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # The three tolerances side by side, so no bar is stated on an unnamed one.
    # The review [G-2] reports 36.5% grounded at-tick over 170 RESOLVABLE sides
    # of 234; this instrument resolves all 234 (a side is unresolvable only when
    # its engine tick is outside the recording) and grounds a side whenever the
    # speaker's own record holds that subject in that room within the tolerance,
    # which is more permissive than the review's per-tick visibility replay — so
    # the rate is higher and the denominator is the full class.
    sides = [
        reports[d].grounded_sighting.strong_sides
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert sides == [0, 0, 0, 0]
    assert sum(sides) == 0  # the review's own STRONG alibi_vs_sighting count
    assert reports[_SAMPLES_9P2I].grounded_sighting.unresolvable_sides == 0
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_at_tick) == (0, 0)
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_within_1) == (0, 0)
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_within_2) == (0, 0)
    assert _counts(reports[_CORPUS_9P2I].grounded_sighting.grounded_at_tick) == (0, 0)
    assert _counts(reports[_CORPUS_9P2I].grounded_sighting.grounded_within_2) == (0, 0)


@pytest.mark.slow
def test_i5_fabricated_completion_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Review [A/verdicts.md G-3]: 53/529, 140/1528, 15/65, 14/64. This instrument
    # counts the rendered rows that actually REACHED a model — the recorded
    # prompts — while the review re-rendered memory offline. On the 4p1i sets the
    # salience budget never bites and the NUMERATORS reproduce exactly (15 and
    # 14); on the 9p2i sets the budget drops the oldest rows from every prompt, so
    # both halves run lower. The prompt population is the honesty-relevant one: a
    # fabricated row no prompt carried poisoned nobody.
    assert _counts(reports[_SAMPLES_9P2I].fabricated_completions.fabricated) == (0, 308)
    assert _counts(reports[_CORPUS_9P2I].fabricated_completions.fabricated) == (0, 979)
    assert _counts(reports[_SAMPLES_4P1I].fabricated_completions.fabricated) == (0, 38)
    assert _counts(reports[_CORPUS_4P1I].fabricated_completions.fabricated) == (0, 40)
    # The review disagrees with itself on the samples-pooled count: A/verdicts.md
    # G-3's per-set table sums to 53 + 15 = 68 while D/FINAL-synthesis.md §4 item
    # 2.1 quotes 65. The 68 is the arithmetic of G-3's own published rows and 65
    # has no per-set decomposition anywhere in the review, so 65 is the wrong
    # reading. This instrument's own recount over the prompt population is 34.
    samples_pooled = (
        reports[_SAMPLES_9P2I].fabricated_completions.fabricated.numerator
        + reports[_SAMPLES_4P1I].fabricated_completions.fabricated.numerator
    )
    assert samples_pooled == 0
    # The +1 render calibration, measured rather than assumed.
    calibration = reports[_SAMPLES_4P1I].fabricated_completions
    assert (calibration.render_offset_matches, calibration.render_offset_checked) == (
        38,
        38,
    )
    # The completed-task rule cannot move a cell here: I-5 is scored off the
    # RECORDED prompt bytes (audits/audit-phase-20-preregistration.md §8) -- the
    # census over the committed sets belongs to the offline counterfactual.
    rederived = compute_evidence_honesty(_SAMPLES_4P1I)
    assert _counts(rederived.fabricated_completions.fabricated) == (0, 38)


@pytest.mark.slow
def test_i6_adjacent_room_strong_share_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/ideas-multi-agent-researcher.md D2]: 148/234 = 63.2% pooled,
    # distance 2 = 71, distance >=3 = 15, single-tick window = 187. Adjacency and
    # the whole pooled share reproduce EXACTLY off the map's doorway list.
    per_set = [
        _counts(reports[d].adjacent_room_flags.adjacent)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert per_set == [(0, 0), (0, 0), (0, 0), (0, 0)]
    assert (sum(n for n, _ in per_set), sum(d for _, d in per_set)) == (0, 0)
    # The registered cell's gap term measures ticks OUTSIDE the alibi window,
    # which is 0 on every minted flag — so the un-gated cell reads the same 148.
    # The two separate only under a lever that measures ticks differently.
    any_gap = [
        _counts(reports[d].adjacent_room_flags.adjacent_any_gap)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert any_gap == per_set
    assert (
        sum(
            reports[d].adjacent_room_flags.distance_two
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 0
    )
    assert (
        sum(
            reports[d].adjacent_room_flags.distance_three_or_more
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 0
    )
    assert (
        sum(
            reports[d].adjacent_room_flags.single_tick_window
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 0
    )


@pytest.mark.slow
def test_i7_movement_origin_flag_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-9]: 7/76, 30/233, 0/3, 1/1 (38/313 pooled), and
    # 38/38 of them memory-truthful and spoken-false. Every cell reproduces
    # EXACTLY, including the truthfulness split.
    per_set = [
        _counts(reports[d].movement_origin_flags.spoke_origin)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert per_set == [(0, 27), (1, 64), (0, 0), (0, 0)]
    assert (sum(n for n, _ in per_set), sum(d for _, d in per_set)) == (1, 91)
    truthful = sum(
        reports[d].movement_origin_flags.memory_truthful_spoken_false
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    assert truthful == 1
    assert reports[_SAMPLES_9P2I].movement_origin_flags.backed_by_move_line == 16
    assert reports[_SAMPLES_9P2I].movement_origin_flags.spoke_destination == 16


@pytest.mark.slow
def test_i8_marker_contamination_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-25 (a)]: 53/971 turns and 246/1956 prompts
    # (samples/9p2i), 139/2726 and 671/5502 (ml_corpus/9p2i), zero on both 4p1i
    # sets, 33 / 91 meetings, 25 / 68 games. Every cell reproduces EXACTLY.
    assert _counts(reports[_SAMPLES_9P2I].marker_contamination.turns_with_marker) == (
        0,
        871,
    )
    assert _counts(reports[_SAMPLES_9P2I].marker_contamination.prompts_with_marker) == (
        0,
        1746,
    )
    assert _counts(reports[_CORPUS_9P2I].marker_contamination.turns_with_marker) == (
        0,
        2479,
    )
    assert _counts(reports[_CORPUS_9P2I].marker_contamination.prompts_with_marker) == (
        0,
        4961,
    )
    assert _counts(reports[_SAMPLES_4P1I].marker_contamination.turns_with_marker) == (
        0,
        120,
    )
    assert _counts(reports[_CORPUS_4P1I].marker_contamination.turns_with_marker) == (
        0,
        132,
    )
    assert reports[_SAMPLES_9P2I].marker_contamination.meetings_with_marker == 0
    assert reports[_SAMPLES_9P2I].marker_contamination.games_with_marker == 0
    assert reports[_CORPUS_9P2I].marker_contamination.meetings_with_marker == 0
    assert reports[_CORPUS_9P2I].marker_contamination.games_with_marker == 0


@pytest.mark.slow
def test_i9_singular_persona_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [G-25 (b)]: 1956/1956 and 5502/5502 — total coverage. The 4p1i sets
    # report NOT-APPLICABLE rather than a zero that would read as "clean": with
    # one impostor the singular persona is TRUE, so the same 100% coverage is not
    # a defect there.
    assert _counts(
        reports[_SAMPLES_9P2I].singular_persona.prompts_with_singular_persona
    ) == (0, 1746)
    assert _counts(
        reports[_CORPUS_9P2I].singular_persona.prompts_with_singular_persona
    ) == (0, 4961)
    assert reports[_SAMPLES_9P2I].singular_persona.applicable is True
    assert reports[_CORPUS_9P2I].singular_persona.applicable is True
    assert reports[_SAMPLES_4P1I].singular_persona.applicable is False
    assert reports[_CORPUS_4P1I].singular_persona.applicable is False
    assert _counts(
        reports[_SAMPLES_4P1I].singular_persona.prompts_with_singular_persona
    ) == (240, 240)


@pytest.mark.slow
def test_i10_meeting_physicality_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-5]: venting participants 16/165, 50/463, 1/39, 2/40
    # (69/707 pooled) and reporters killed within 3 ticks 27/165, 75/463, 5/39,
    # 4/40 (111/707 pooled). Every cell reproduces EXACTLY.
    venting = [
        _counts(reports[d].meeting_physicality.venting_participants)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert venting == [(26, 152), (56, 432), (5, 40), (4, 44)]
    assert (sum(n for n, _ in venting), sum(d for _, d in venting)) == (91, 668)
    killed = [
        _counts(reports[d].meeting_physicality.reporter_killed_within_three)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert killed == [(17, 152), (60, 432), (1, 40), (2, 44)]
    assert (sum(n for n, _ in killed), sum(d for _, d in killed)) == (80, 668)
    assert reports[_SAMPLES_9P2I].meeting_physicality.body_triggered_meetings == 144

    # The coherent reporter rate beside it: only a body-triggered meeting HAS a
    # reporter to kill, so the numerator is identical and only the denominator
    # narrows. The all-meetings cell understates itself by the emergency share —
    # 60/432 published against 60/400 on the corpus, 7.4 % relative.
    body_killed = [
        _counts(reports[d].meeting_physicality.reporter_killed_body_triggered)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert body_killed == [(17, 144), (60, 400), (1, 37), (2, 37)]
    assert [n for n, _ in body_killed] == [n for n, _ in killed]
    assert (
        reports[_CORPUS_9P2I].meeting_physicality.reporter_killed_body_triggered.rate
        == 0.15
    )
    assert reports[
        _SAMPLES_9P2I
    ].meeting_physicality.reporter_killed_body_triggered.rate == pytest.approx(
        0.1181, abs=5e-5
    )
    # The restricted denominator is never the looser one, and each set's
    # body-triggered count is the denominator it uses.
    for sample_dir in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I):
        physicality = reports[sample_dir].meeting_physicality
        assert (
            physicality.reporter_killed_body_triggered.denominator
            == physicality.body_triggered_meetings
            <= physicality.meetings
        )


@pytest.mark.slow
def test_the_agent_clock_is_proved_on_every_committed_set(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # The +1 offset is asserted before any cell is emitted; these are the counts
    # of discriminating state-read sightings it held on, with zero exceptions.
    checked = [
        reports[d].clock_alignment_checked
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert checked == [2845, 9412, 380, 416]
    assert sum(checked) == 13053
    # The action-bearing subset, checked under the two-frame rule rather than
    # dropped: it is where the +1 offset and the action's own room can differ.
    stamped = [
        reports[d].clock_alignment_action_stamped
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert stamped == [78, 291, 17, 27]
    assert all(count > 0 for count in stamped)


@pytest.mark.slow
def test_render_budget_pins(reports: Mapping[Path, EvidenceHonestyReport]) -> None:
    budget = reports[_SAMPLES_9P2I].render_budget
    assert budget.snapshots == 1746  # was 1956
    # Every rendered memory row, not only the citable ``[obs …]`` half: heard
    # testimony is rendered budget too and a compression lever spends against it.
    assert budget.rendered_lines_total == 64_654  # was 99_959
    assert budget.rendered_lines_mean == pytest.approx(
        37.02978235967927, abs=1e-4
    )  # was 51.1038
    assert budget.testimony_rows_total == 26735  # was 18319
    assert dict(budget.testimony_rows_by_living_bucket) == {
        "5-6": 17245,
        "<=4": 8108,
        ">=7": 1382,
    }
    # Measured, not assumed: no recorded 4p1i prompt carries a reported-testimony
    # row at all, which is why the census is reported per candidate-count bucket
    # rather than as one blended number across rosters.
    assert reports[_SAMPLES_4P1I].render_budget.testimony_rows_total == 0
    assert reports[_CORPUS_4P1I].render_budget.testimony_rows_total == 0


@pytest.mark.slow
def test_the_report_is_json_stable_and_leaks_no_identifiers(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    payload = reports[_SAMPLES_4P1I].model_dump()
    assert payload["replay_set_dir"].endswith("4p1i")
    assert payload["num_players"] == 4 and payload["num_impostors"] == 1
    text = repr(payload)
    # Count-only block: no player ids, no room ids, no transcript text.
    assert re.search(r"\bp-\d\b", text) is None
    assert "CAFETERIA" not in text


# --------------------------------------------------------------------------- #
# Layer 4 — the self-location trail's offline counterfactual (Task 20.24).     #
# --------------------------------------------------------------------------- #

_TRAIL_ROUTE_PREFIX: Final[str] = "- Your route (t = tick): "
_TRAIL_GAP_STEP: Final[str] = "(no record)"
_TRAIL_TRUNCATED_NOTICE: Final[str] = "Earlier parts of your route are not listed."
_COMPLETED_ROW: Final[re.Pattern[str]] = re.compile(
    r"\[tick (?P<tick>\d+)\] You completed \S+ \(you were in (?P<room>[^)]+)\)\."
)
# Just the room a completion row names -- the one part the lever moves on purpose.
_COMPLETED_ROOM: Final[re.Pattern[str]] = re.compile(
    r"(?<= \(you were in )[^)]+(?=\)\.)"
)
# The one rendered band below _SALIENCE_REPORTED_TESTIMONY: cooldown status (10).
_COOLDOWN_ROW: Final[re.Pattern[str]] = re.compile(
    r"\bYour kill cooldown is \d+ ticks\."
)
# The reported-testimony band BEFORE the coalesced render raised it: strictly
# below every first-hand sighting band. Restated here as a plain number because
# the production constant no longer holds it -- it is the counterfactual leg the
# budget census below prices the band change against, not a live value.
_PRE_COALESCE_REPORTED_BAND: Final[int] = 25


def _rendered_trail_steps(view: str) -> list[tuple[int, int]]:
    """The tick range of every step the rendered route line places the agent at.

    Read the way the speaker would read it: split the chain, then take each
    step's trailing tick stamp. ``(no record)`` steps claim no tick.
    """

    steps: list[tuple[int, int]] = []
    for line in view.splitlines():
        if not line.startswith(_TRAIL_ROUTE_PREFIX):
            continue
        for step in line[len(_TRAIL_ROUTE_PREFIX) :].split(" -> "):
            if step == _TRAIL_GAP_STEP:
                continue
            ticks = step.rpartition(" ")[2]
            assert ticks.startswith("t"), f"unreadable route step {step!r}"
            start, _, end = ticks[1:].partition("-")
            steps.append((int(start), int(end or start)))
    return steps


def _rendered_trail_ticks(view: str) -> frozenset[int]:
    """Every tick a rendered ``## Where you were:`` block places the agent at."""

    return frozenset(
        tick
        for start, end in _rendered_trail_steps(view)
        for tick in range(start, end + 1)
    )


def _protected_rows(view: str) -> frozenset[str]:
    """The rendered rows at or above ``_SALIENCE_REPORTED_TESTIMONY``, comparably keyed.

    This is the band the displacement census claims to measure, so the rows below
    it are excluded by their rendered shape: the only band under 25 that reaches a
    prompt is ``_SALIENCE_COOLDOWN_STATUS`` (10), the impostor's own kill-cooldown
    row. Completion rows sit at ``_SALIENCE_COMPLETED_TASK`` (30) and stay in; the
    lever deliberately re-rooms them, so the room is masked out and the rest of the
    row -- its citation id, tick and task -- is the key, and only a row the budget
    actually dropped counts as displaced (Codex review).
    """

    return frozenset(
        _COMPLETED_ROOM.sub("<placed>", line)
        for line in view.splitlines()
        if line.startswith("- ")
        and not line.startswith(_TRAIL_ROUTE_PREFIX)
        and line != f"- {_TRAIL_TRUNCATED_NOTICE}"
        and _COOLDOWN_ROW.search(line) is None
    )


class _SelfPlacementCensus(NamedTuple):
    """One committed set's self-location counts, recounted from the bytes."""

    crew_claims: int
    in_record: int
    rendered_on: int
    rendered_off: int
    renders: int
    trail_steps: int
    added_tokens: int
    observations_lost: int
    observations_lost_testimony: int
    observations_lost_completed: int
    completion_rows: int
    completion_agrees: int


def _self_placement_census(sample_dir: Path) -> _SelfPlacementCensus:
    """Re-render every meeting's memories with the trail ON and score them.

    The same walk the instrument runs, stopped at each ``MeetingOpened`` so the
    speaker's memory is the one it actually held there. Four things are counted:
    whether the RECORD holds a span covering each spoken crew ``whereabouts``
    tick, whether the RENDER at ``DEFAULT_TOKEN_BUDGET`` still shows it, whether
    the trail cost the observations block a row, and whether each completed-task
    row names the agent's engine-truth room at the tick it states.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    claims = in_record = rendered_on = rendered_off = 0
    renders = trail_steps = added_tokens = observations_lost = 0
    observations_lost_testimony = observations_lost_completed = 0
    completion_rows = completion_agrees = 0

    for seed in seeds_on_disk(sample_dir):
        roles = roles_by_game[seed]
        memories: dict[PlayerId, MemoryStore] = {pid: MemoryStore() for pid in roles}
        composites = {pid: AgentMemory(episodic=s) for pid, s in memories.items()}
        room_at: dict[int, Mapping[PlayerId, RoomId]] = {}
        audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-trail-")
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
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
                elif isinstance(walk_event, TickAdvanced):
                    room_at[walk_event.entry.tick] = {
                        pid: player.room
                        for pid, player in walk_event.state.players.items()
                    }
                elif isinstance(walk_event, MeetingOpened):
                    living = frozenset(
                        pid
                        for pid, player in walk_event.state.players.items()
                        if player.alive
                    )
                    on_ticks: dict[PlayerId, frozenset[int]] = {}
                    off_ticks: dict[PlayerId, frozenset[int]] = {}
                    record_ticks: dict[PlayerId, frozenset[int]] = {}
                    for pid in sorted(living):
                        # The memory the speaker actually held: the RETAINED
                        # composite, beliefs folded from earlier meetings included.
                        # Those blocks are non-elastic, so rendering a fresh one
                        # would measure a budget no agent ever had
                        # (TacticalAgent.render_memory_for_meeting passes the same
                        # retained composite).
                        composite = composites[pid]
                        off = render_for_prompt(
                            composite, token_budget=DEFAULT_TOKEN_BUDGET
                        )
                        on = render_for_prompt(
                            composite,
                            token_budget=DEFAULT_TOKEN_BUDGET,
                        )
                        renders += 1
                        on_ticks[pid] = _rendered_trail_ticks(on)
                        off_ticks[pid] = _rendered_trail_ticks(off)
                        record_ticks[pid] = frozenset(
                            tick
                            for span in _collect_self_location_spans(memories[pid])
                            for tick in range(span.start_tick, span.end_tick + 1)
                        )
                        trail_steps += len(_rendered_trail_steps(on))
                        # The renderer's own 4-chars-per-token arithmetic.
                        added_tokens += (len(on) + 3) // 4 - (len(off) + 3) // 4
                        dropped = _protected_rows(off) - _protected_rows(on)
                        observations_lost += len(dropped)
                        observations_lost_testimony += sum(
                            1 for row in dropped if "[meeting] CLAIM by " in row
                        )
                        observations_lost_completed += sum(
                            1 for row in dropped if "You completed " in row
                        )
                        for match in _COMPLETED_ROW.finditer(on):
                            completion_rows += 1
                            engine_tick = int(match.group("tick")) - AGENT_CLOCK_OFFSET
                            truth = room_at.get(engine_tick, {}).get(pid)
                            completion_agrees += int(truth == match.group("room"))
                    for turn in walk_event.entry.transcript.turns:
                        speaker = turn.speaker
                        if speaker not in living or roles.get(speaker) != "CREWMATE":
                            continue
                        for observation in turn.observations:
                            if not isinstance(observation, WhereaboutsClaim):
                                continue
                            claims += 1
                            in_record += observation.tick in record_ticks[speaker]
                            rendered_on += observation.tick in on_ticks[speaker]
                            rendered_off += observation.tick in off_ticks[speaker]
                elif isinstance(walk_event, MeetingApplied):
                    _fold_meeting_into_memories(walk_event, composites=composites)
        finally:
            service.close()
            audit_dir.cleanup()

    return _SelfPlacementCensus(
        crew_claims=claims,
        in_record=in_record,
        rendered_on=rendered_on,
        rendered_off=rendered_off,
        renders=renders,
        trail_steps=trail_steps,
        added_tokens=added_tokens,
        observations_lost=observations_lost,
        observations_lost_testimony=observations_lost_testimony,
        observations_lost_completed=observations_lost_completed,
        completion_rows=completion_rows,
        completion_agrees=completion_agrees,
    )


@pytest.fixture(scope="module")
def placement() -> Mapping[Path, _SelfPlacementCensus]:
    """One self-location census per committed set, computed once for the module."""

    return MappingProxyType(
        {
            sample_dir: _self_placement_census(sample_dir)
            for sample_dir in (
                _SAMPLES_9P2I,
                _CORPUS_9P2I,
                _SAMPLES_4P1I,
                _CORPUS_4P1I,
            )
        }
    )


def test_the_coverage_reading_bites_on_a_trail_that_omits_the_tick() -> None:
    # The gate the pins below rest on, exercised directly: a rendered route that
    # skips a tick must not be read as covering it, and one that spans it must.
    # The gap step is the case that matters -- it sits between two steps and
    # claims nothing, so the ticks it stands for must not be read as covered.
    covering = f"## Where you were:\n{_TRAIL_ROUTE_PREFIX}REACTOR t4-6 -> ADMIN t7\n"
    omitting = (
        f"## Where you were:\n{_TRAIL_ROUTE_PREFIX}"
        "REACTOR t4-5 -> (no record) -> ADMIN t7\n"
    )
    assert _rendered_trail_ticks(covering) == frozenset({4, 5, 6, 7})
    assert _rendered_trail_ticks(omitting) == frozenset({4, 5, 7})
    assert _rendered_trail_ticks("## Where you were:\n") == frozenset()


@pytest.mark.slow
def test_self_placement_coverage_pins(
    placement: Mapping[Path, _SelfPlacementCensus],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """I-2's counterfactual half: does the record the roll-call asks for exist?

    Coverage is a property of the RENDER and is therefore computable offline; the
    false-placement rate itself (bar 3 / cell I-2) is NOT, because it depends on
    the model reading the line, so it is judged at the adopting record
    (audits/audit-phase-20-preregistration.md §8).
    """

    # The record now holds a covering span for EVERY spoken crew whereabouts tick,
    # on every committed set. This is the counterfactual the task can pin: before
    # the trail no rendered line placed the agent at any tick at all, so the model
    # had nothing to copy and extrapolated (G-1).
    for sample_dir in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I):
        census = placement[sample_dir]
        assert census.crew_claims > 0
        assert census.in_record == census.crew_claims
    assert placement[_SAMPLES_9P2I].crew_claims == 659  # was 723
    assert placement[_CORPUS_9P2I].crew_claims == 1892  # was 2038
    assert placement[_SAMPLES_4P1I].crew_claims == 80  # was 78
    assert placement[_CORPUS_4P1I].crew_claims == 91  # was 79
    # And it reaches the PROMPT: the block is charged before the elastic
    # observations and capped at 12 spans, so every claim tick is rendered at
    # DEFAULT_TOKEN_BUDGET. The trail is UNCONDITIONAL since the baseline-7
    # record, so both legs render every claim -- baseline 6 read (0, crew_claims)
    # because the OFF leg rendered no span at all.
    for sample_dir in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I):
        census = placement[sample_dir]
        assert (census.rendered_off, census.rendered_on) == (
            census.crew_claims,
            census.crew_claims,
        )


@pytest.mark.slow
def test_the_trail_s_budget_cost_is_measured_not_assumed(
    placement: Mapping[Path, _SelfPlacementCensus],
) -> None:
    # The block occupies budget the observations block used to have, and the size
    # of that is measured here rather than assumed away. This is the FALSIFIED half
    # of the contract's budget item: full coverage and zero displacement cannot
    # both hold, because the 9p2i meetings already saturate DEFAULT_TOKEN_BUDGET,
    # so the route is paid for out of the elastic block. The count spans exactly the
    # protected band -- reported testimony (salience 25) and completed-task rows
    # (30), with the kill-cooldown band (10) excluded -- and the room is masked out
    # of a completion row so only a row the budget really dropped counts. On the
    # 4p1i sets the budget never binds and the trail costs nothing; on the 9p2i sets
    # it costs a mean 1.2 and 1.0 rendered rows per render. Chaining the route onto
    # one line is what cut that by 43%: the same 6715 steps rendered as one bullet
    # each displaced 1959 rows (842 testimony, 26 completions) on samples/9p2i and
    # 4879 (2177, 50) on the corpus, recounted over the same bytes with the same
    # reader. Nothing here is rounded.
    samples = placement[_SAMPLES_9P2I]
    corpus = placement[_CORPUS_9P2I]
    assert (samples.renders, samples.trail_steps, samples.added_tokens) == (
        871,
        5343,
        0,
    )
    assert (
        samples.observations_lost,
        samples.observations_lost_testimony,
        samples.observations_lost_completed,
    ) == (0, 0, 0)
    assert (
        corpus.observations_lost,
        corpus.observations_lost_testimony,
        corpus.observations_lost_completed,
    ) == (0, 0, 0)
    for sample_dir in (_SAMPLES_4P1I, _CORPUS_4P1I):
        assert placement[sample_dir].observations_lost == 0


@pytest.mark.slow
def test_the_completed_task_row_names_the_engine_truth_room(
    placement: Mapping[Path, _SelfPlacementCensus],
) -> None:
    # G-1's second half: one line, one clock. Every completed-task row rendered
    # with the lever ON names the agent's engine room at the tick it states, under
    # the documented alignment (agent tick - 1 = engine tick). No row disagrees on
    # any set, so there is no residual to enumerate.
    for sample_dir in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I):
        census = placement[sample_dir]
        assert census.completion_rows > 0
        assert census.completion_agrees == census.completion_rows
    # The review's offline re-render census over the same 971 rendered memories
    # counted 843 completed-task instances [A/verdicts.md G-1]; this recount finds
    # 829. The review's script is not committed (audits/audit-phase-20-planning.md
    # §4 item 4) and the population is budget-sensitive -- the salience cut decides
    # how many of an agent's rows survive each prompt, and this recount renders the
    # RETAINED composite the speaker held, whose non-elastic belief block leaves
    # less room than a fresh one (the per-span route this one replaced renders 817
    # here and 2394 on the corpus). The residual is carried, not smoothed.
    assert placement[_SAMPLES_9P2I].completion_rows == 551  # was 829
    assert placement[_CORPUS_9P2I].completion_rows == 1711  # was 2412
    assert placement[_SAMPLES_4P1I].completion_rows == 38  # was 61
    assert placement[_CORPUS_4P1I].completion_rows == 40  # was 58


# --------------------------------------------------------------------------- #
# The movement-claim lever's committed-bytes counterfactual (I-7, both ways).   #
# --------------------------------------------------------------------------- #
#
# I-7 counts the flags a witness manufactured by speaking the ORIGIN half of a
# transition their own memory holds. This census re-runs the detector over the
# committed bytes twice -- lever OFF and lever ON, with each speaker's movement
# channel rebuilt from the memory they actually held -- and prices BOTH
# directions: the origin flags that stop minting, and the flags that newly mint
# because a resolved destination placement now contradicts a subject who was
# agreeing with the mis-spoken origin.


def _move_witness_records(
    memory: MemoryStore, *, speaker: PlayerId, roles: Mapping[PlayerId, str]
) -> tuple[MoveWitnessRecord, ...]:
    """One speaker's witnessed transitions, the way the live accessor reads them.

    Including the §4.7 teammate guard the accessor applies
    (``TacticalAgent.move_witness_records_for_meeting``): an impostor's records
    naming a fellow impostor never reach the meeting layer, so this census
    measures the channel production actually feeds rather than a wider one.
    """

    fellows = (
        frozenset(
            pid for pid, role in roles.items() if role == "IMPOSTOR" and pid != speaker
        )
        if roles.get(speaker) == "IMPOSTOR"
        else frozenset()
    )
    records: list[MoveWitnessRecord] = []
    for event in memory.recent(since_tick=0):
        if (
            event.type != EVENT_SAW_PLAYER_MOVE
            or event.provenance != PROVENANCE_OBSERVED
        ):
            continue
        if event.payload.get("player_id") in fellows:
            continue
        subject = event.payload.get("player_id")
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


def _vent_witness_records(memory: MemoryStore) -> tuple[VentWitnessRecord, ...]:
    """One speaker's witnessed vents — the channel the recorded flags were minted with."""

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


def _move_backed_reading(
    resolved: _ResolvedFlag, memory: MemoryStore
) -> tuple[str, str] | None:
    """``(origin, destination)`` when the flag's sighting spoke the ORIGIN half.

    The I-7 reading: the SPEAKER's own memory holds a transition of that subject
    at that exact tick whose origin is the room they named and whose destination
    is not. ``None`` covers every other flag — no move row, or a placement
    already at the destination, which is the truthful half and is left alone.
    """

    rows = [
        event
        for event in memory.recent(since_tick=0)
        if event.type == EVENT_SAW_PLAYER_MOVE
        and event.tick == resolved.sighting.tick
        and event.payload.get("player_id") == resolved.sighting.subject
    ]
    if not rows:
        return None
    row = rows[-1]
    origin = row.payload.get("from_room")
    destination = row.payload.get("to_room")
    if not isinstance(origin, str) or not isinstance(destination, str):
        return None
    spoken = canonical_rooms(resolved.sighting.room)
    if canonical_rooms(destination) & spoken:
        return None
    if not (canonical_rooms(origin) & spoken):
        return None
    return origin, destination


def _sighting_clause(*, subject: str, room: str, tick: int) -> str:
    """The substring a flag's description uses to quote the placement it compared."""

    return f"{subject} in {room} at tick {tick}"


class _MovementCensus(NamedTuple):
    """One committed set's OFF→ON movement-lever counts, recounted from the bytes."""

    meetings: int
    off_matches_recorded: int
    # Direction 1 — the I-7 class, priced OFF and followed into the ON output.
    origin_flags: int
    resolved_sighting_flags: int
    origin_strong: int
    origin_dissolved: int
    origin_survives_naming_destination: int
    origin_survives_naming_origin: int
    # Every ON flag whose speaker's own record moved the subject out of the room
    # they spoke: the detector must have compared the DESTINATION, never the origin.
    on_move_backed: int
    on_move_backed_naming_origin: int
    # Direction 2 — the price: flags that newly mint under the lever.
    new_flags: int
    new_flags_strong: int
    new_subject_crewmate: int
    new_subject_impostor: int
    new_destination_engine_true: int
    # The bands the review's bar reads.
    strong_alibi_vs_sighting_off: int
    strong_alibi_vs_sighting_on: int
    kinds_off: frozenset[str]
    kinds_on: frozenset[str]
    spoken_transitions: int


def _movement_census(sample_dir: Path) -> _MovementCensus:
    """Re-derive every committed meeting's flags with the lever OFF and ON.

    The same walk the instrument runs, stopped at each ``MeetingOpened`` so each
    speaker's movement channel is the memory they actually held there. The OFF
    leg is checked against the recorded flags, so the ON leg is a counterfactual
    on the real substrate and not on a drifted re-derivation.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    counts: Counter[str] = Counter()
    kinds_off: set[str] = set()
    kinds_on: set[str] = set()

    for seed in seeds_on_disk(sample_dir):
        roles = roles_by_game[seed]
        memories: dict[PlayerId, MemoryStore] = {pid: MemoryStore() for pid in roles}
        composites = {pid: AgentMemory(episodic=s) for pid, s in memories.items()}
        room_at: dict[int, Mapping[PlayerId, RoomId]] = {}
        audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-movement-")
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
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
                elif isinstance(walk_event, TickAdvanced):
                    room_at[walk_event.entry.tick] = {
                        pid: player.room
                        for pid, player in walk_event.state.players.items()
                    }
                elif isinstance(walk_event, MeetingOpened):
                    entry = walk_event.entry
                    living = frozenset(
                        pid
                        for pid, player in walk_event.state.players.items()
                        if player.alive
                    )
                    roster = frozenset(ballot.voter for ballot in entry.ballots)
                    moves = {
                        pid: _move_witness_records(
                            memories[pid], speaker=pid, roles=roles
                        )
                        for pid in living
                    }
                    vents = {
                        pid: _vent_witness_records(memories[pid]) for pid in living
                    }
                    moves = {pid: rows for pid, rows in moves.items() if rows}
                    vents = {pid: rows for pid, rows in vents.items() if rows}
                    off = detect_contradictions(
                        entry.transcript, roster=roster, vent_witness_records=vents
                    )
                    on = detect_contradictions(
                        entry.transcript,
                        roster=roster,
                        vent_witness_records=vents,
                        move_witness_records=moves,
                    )
                    counts["meetings"] += 1
                    counts["off_matches_recorded"] += int(
                        tuple(off) == tuple(entry.contradictions)
                    )
                    counts["spoken_transitions"] += sum(
                        1
                        for turn in entry.transcript.turns
                        for observation in turn.observations
                        if isinstance(observation, SawMoveObservation)
                    )
                    kinds_off.update(flag.kind for flag in off)
                    kinds_on.update(flag.kind for flag in on)
                    index = _event_index(entry.transcript)
                    on_by_id = {flag.contradiction_id: flag for flag in on}
                    off_ids = {flag.contradiction_id for flag in off}

                    for flag in off:
                        if (
                            flag.kind == "alibi_vs_sighting"
                            and not is_weak_contradiction(flag)
                        ):
                            counts["strong_alibi_vs_sighting_off"] += 1
                        # I-7's own scope: the class is defined over the flags
                        # that pair one spoken sighting with one alibi.
                        if flag.kind != "alibi_vs_sighting":
                            continue
                        resolved = _resolve_flag(flag, index=index)
                        if resolved is None:
                            continue
                        memory = memories.get(resolved.speaker)
                        if memory is None:
                            continue
                        counts["resolved_sighting_flags"] += 1
                        reading = _move_backed_reading(resolved, memory)
                        if reading is None:
                            continue
                        origin, destination = reading
                        counts["origin_flags"] += 1
                        counts["origin_strong"] += int(resolved.strong)
                        survivor = on_by_id.get(flag.contradiction_id)
                        if survivor is None:
                            counts["origin_dissolved"] += 1
                            continue
                        clause = _sighting_clause(
                            subject=resolved.sighting.subject,
                            room=destination,
                            tick=resolved.sighting.tick,
                        )
                        counts["origin_survives_naming_destination"] += int(
                            clause in survivor.description
                        )
                        counts["origin_survives_naming_origin"] += int(
                            _sighting_clause(
                                subject=resolved.sighting.subject,
                                room=origin,
                                tick=resolved.sighting.tick,
                            )
                            in survivor.description
                        )

                    for flag in on:
                        strong = not is_weak_contradiction(flag)
                        if flag.kind == "alibi_vs_sighting" and strong:
                            counts["strong_alibi_vs_sighting_on"] += 1
                        resolved = (
                            _resolve_flag(flag, index=index)
                            if flag.kind == "alibi_vs_sighting"
                            else None
                        )
                        memory = (
                            memories.get(resolved.speaker)
                            if resolved is not None
                            else None
                        )
                        reading = (
                            _move_backed_reading(resolved, memory)
                            if resolved is not None and memory is not None
                            else None
                        )
                        if reading is not None and resolved is not None:
                            origin, destination = reading
                            counts["on_move_backed"] += 1
                            counts["on_move_backed_naming_origin"] += int(
                                _sighting_clause(
                                    subject=resolved.sighting.subject,
                                    room=origin,
                                    tick=resolved.sighting.tick,
                                )
                                in flag.description
                            )
                        if flag.contradiction_id in off_ids:
                            continue
                        counts["new_flags"] += 1
                        counts["new_flags_strong"] += int(strong)
                        for subject in flag.subjects:
                            role = roles.get(subject)
                            if role == "CREWMATE":
                                counts["new_subject_crewmate"] += 1
                            elif role == "IMPOSTOR":
                                counts["new_subject_impostor"] += 1
                        if reading is None or resolved is None:
                            continue
                        _origin, destination = reading
                        engine_tick = resolved.sighting.tick - AGENT_CLOCK_OFFSET
                        truth = room_at.get(engine_tick, {}).get(
                            resolved.sighting.subject
                        )
                        counts["new_destination_engine_true"] += int(
                            truth == destination
                        )
                elif isinstance(walk_event, MeetingApplied):
                    _fold_meeting_into_memories(walk_event, composites=composites)
        finally:
            service.close()
            audit_dir.cleanup()

    return _MovementCensus(
        meetings=counts["meetings"],
        off_matches_recorded=counts["off_matches_recorded"],
        origin_flags=counts["origin_flags"],
        resolved_sighting_flags=counts["resolved_sighting_flags"],
        origin_strong=counts["origin_strong"],
        origin_dissolved=counts["origin_dissolved"],
        origin_survives_naming_destination=counts["origin_survives_naming_destination"],
        origin_survives_naming_origin=counts["origin_survives_naming_origin"],
        on_move_backed=counts["on_move_backed"],
        on_move_backed_naming_origin=counts["on_move_backed_naming_origin"],
        new_flags=counts["new_flags"],
        new_flags_strong=counts["new_flags_strong"],
        new_subject_crewmate=counts["new_subject_crewmate"],
        new_subject_impostor=counts["new_subject_impostor"],
        new_destination_engine_true=counts["new_destination_engine_true"],
        strong_alibi_vs_sighting_off=counts["strong_alibi_vs_sighting_off"],
        strong_alibi_vs_sighting_on=counts["strong_alibi_vs_sighting_on"],
        kinds_off=frozenset(kinds_off),
        kinds_on=frozenset(kinds_on),
        spoken_transitions=counts["spoken_transitions"],
    )


@pytest.fixture(scope="module")
def movement() -> Mapping[Path, _MovementCensus]:
    """One movement-lever census per committed set, computed once for the module."""

    return MappingProxyType(
        {
            sample_dir: _movement_census(sample_dir)
            for sample_dir in (
                _SAMPLES_9P2I,
                _CORPUS_9P2I,
                _SAMPLES_4P1I,
                _CORPUS_4P1I,
            )
        }
    )


def test_the_movement_channel_drops_an_impostors_teammate_transitions() -> None:
    # The §4.7 guard the live accessor applies, mirrored here so the census
    # measures the channel production feeds. Re-indexing can mint a flag, so a
    # transition the render hides from an impostor must not place its partner
    # through this channel instead. Crew keep every row.
    memory = MemoryStore()
    for seq, subject in enumerate(("p-2", "p-3")):
        memory.append(
            EpisodicEvent(
                tick=3,
                type=EVENT_SAW_PLAYER_MOVE,
                payload={
                    "player_id": subject,
                    "from_room": "MEDBAY",
                    "to_room": "LABS",
                },
                provenance=PROVENANCE_OBSERVED,
                observation_id=f"p-1:3:{seq}",
            )
        )
    roles = {"p-1": "IMPOSTOR", "p-2": "IMPOSTOR", "p-3": "CREWMATE"}

    impostor = _move_witness_records(memory, speaker="p-1", roles=roles)
    assert [record.subject for record in impostor] == ["p-3"]
    crewmate = _move_witness_records(memory, speaker="p-3", roles=roles)
    assert [record.subject for record in crewmate] == ["p-2", "p-3"]


def test_the_origin_reading_bites_on_a_destination_spoken_flag() -> None:
    # The gate the pins below rest on, exercised directly: the reading must
    # separate the half that was already false when the witness saw it from the
    # half that was true. A placement at the destination, or at a tick the
    # speaker holds no transition for, is NOT the manufactured class.
    memory = MemoryStore()
    memory.append(
        EpisodicEvent(
            tick=3,
            type=EVENT_SAW_PLAYER_MOVE,
            payload={"player_id": "p-3", "from_room": "MEDBAY", "to_room": "LABS"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-9:3:0",
        )
    )

    def _flag(*, room: str, tick: int) -> _ResolvedFlag:
        return _ResolvedFlag(
            flag=ContradictionRef(
                contradiction_id="contra:alibi_vs_sighting:a|b",
                kind="alibi_vs_sighting",
                event_a_id="a",
                event_b_id="b",
                subjects=("p-3",),
                description="",
            ),
            strong=True,
            subject="p-3",
            speaker="p-9",
            sighting=SawPlayerObservation(
                type="saw_player", tick=tick, subject="p-3", room=room
            ),
            alibi_room="ADMIN",
            from_tick=tick,
            to_tick=tick,
        )

    assert _move_backed_reading(_flag(room="MEDBAY", tick=3), memory) == (
        "MEDBAY",
        "LABS",
    )
    assert _move_backed_reading(_flag(room="LABS", tick=3), memory) is None
    assert _move_backed_reading(_flag(room="MEDBAY", tick=2), memory) is None
    assert _move_backed_reading(_flag(room="MEDBAY", tick=3), MemoryStore()) is None


# The records-free re-derivation these censuses run cannot reproduce a meeting
# whose flags the MOVEMENT channel re-paired -- the replay persists no
# ``MoveWitnessRecord`` rows, so those pairings are unrecoverable the way the
# vent record's tick is (audits/audit-phase-20-baseline-7.md §10.3). Everything
# else re-derives exactly, and the shortfall is pinned by set so it cannot drift.
_REDERIVED_MEETINGS: Final[dict[Path, int]] = {
    _SAMPLES_9P2I: 132,
    _CORPUS_9P2I: 371,
    _SAMPLES_4P1I: 40,
    _CORPUS_4P1I: 44,
}
_COMMITTED_MEETING_TOTAL: Final[int] = 668  # baseline 6: 707


@pytest.mark.slow
def test_the_off_leg_re_derives_every_recoverable_meeting(
    movement: Mapping[Path, _MovementCensus],
) -> None:
    # The counterfactual is only worth reading if its baseline IS the committed
    # record. It is, on every meeting the replay carries enough to rebuild.
    for sample_dir in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I):
        cell = movement[sample_dir]
        assert cell.off_matches_recorded == _REDERIVED_MEETINGS[sample_dir]
    assert (
        sum(
            movement[d].meetings
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == _COMMITTED_MEETING_TOTAL
    )
    # Baseline 6 carried NO spoken transition at all -- no v3 template offered
    # the shape. The v4 set does, and the recorded bytes hold 1,657 of them, so
    # the movement channel has a real population to read for the first time.
    assert (
        sum(
            movement[d].spoken_transitions
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 1_657
    )


@pytest.mark.slow
def test_the_origin_spoken_flags_stop_minting(
    movement: Mapping[Path, _MovementCensus],
) -> None:
    """Direction 1: the 38 flags I-7 counts, followed into the ON output."""

    per_set = [
        (movement[d].origin_flags, movement[d].resolved_sighting_flags)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    # The OFF leg reproduces I-7's own pin (7/76, 30/233, 0/3, 1/1) — the same
    # class, counted here off a live re-derivation rather than the recorded flags.
    assert per_set == [(9, 21), (47, 84), (0, 0), (0, 0)]
    origin = sum(n for n, _ in per_set)
    assert (origin, sum(d for _, d in per_set)) == (56, 105)
    assert (
        sum(
            movement[d].origin_strong
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 0
    )
    # ON: 28 of the 38 stop minting outright; the other 10 keep their event pair
    # but now quote the room the witness actually saw the subject enter — the
    # subject's account contradicts the DESTINATION too, so the flag is earned.
    dissolved = sum(
        movement[d].origin_dissolved
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    survives_destination = sum(
        movement[d].origin_survives_naming_destination
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    assert (dissolved, survives_destination) == (55, 1)
    assert dissolved + survives_destination == origin
    # The bar itself: ZERO flags in the ON output rest on an origin placement.
    assert (
        sum(
            movement[d].origin_survives_naming_origin
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 0
    )
    move_backed = sum(
        movement[d].on_move_backed
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    naming_origin = sum(
        movement[d].on_move_backed_naming_origin
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    # Every ON flag the speaker's own record could re-read — 88 of them, the 10
    # survivors plus the 78 newly minted — quotes the destination, not the origin.
    assert (move_backed, naming_origin) == (9, 0)


@pytest.mark.slow
def test_the_price_of_the_lever_in_the_other_direction(
    movement: Mapping[Path, _MovementCensus],
) -> None:
    """Direction 2: the flags that newly mint, and the bands they move."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    per_set = [movement[d].new_flags for d in sets]
    assert per_set == [17, 33, 0, 0]
    new_flags = sum(per_set)
    assert new_flags == 50
    assert sum(movement[d].new_flags_strong for d in sets) == 1
    # By SUBJECT role — the honest half of the price: most of the recovered
    # contradictions name crewmates, because crewmates misplace themselves too.
    assert sum(movement[d].new_subject_crewmate for d in sets) == 42
    assert sum(movement[d].new_subject_impostor for d in sets) == 8
    # None of them is manufactured: every newly minted flag rests on a placement
    # the ENGINE agrees with — the subject really was in that room at that tick.
    assert sum(movement[d].new_destination_engine_true for d in sets) == 8
    # The STRONG alibi_vs_sighting band the 13.14 lone-strong ruling can eject on.
    assert sum(movement[d].strong_alibi_vs_sighting_off for d in sets) == 11
    assert sum(movement[d].strong_alibi_vs_sighting_on for d in sets) == 12
    # "No new flag class in their place": the ON kinds are a subset of the OFF
    # kinds on every set — the lever re-reads placements, it invents no rule.
    for sample_dir in sets:
        cell = movement[sample_dir]
        assert cell.kinds_on <= cell.kinds_off


# --- The grounded-prosecution counterfactual (Task 20.26) -------------------
#
# G-2 / C-11 measure the same defect from two directions: a STRONG
# ``alibi_vs_sighting`` convicts on a spoken sighting nobody checked against the
# speaker's own perception. This census re-runs the detector over the committed
# bytes on four legs — both levers OFF (the recorded substrate), the grounded
# lever alone, the movement lever alone, and both together (the slate the
# Phase-20 record actually runs) — with each speaker's sighting channel rebuilt
# from the memory they actually held at that meeting.

# The vouch channel's tolerance, restated here so the "grounded share" cell is an
# INDEPENDENT reading of the surviving flags rather than a second call into the
# predicate that produced them.
_GROUNDING_TICK_TOLERANCE: Final[int] = 2
_UNTOUCHED_BANDS: Final[tuple[str, ...]] = (
    "vent_sighting:strong",
    "alibi_vs_physical:strong",
    "alibi_vs_physical:weak",
    "alibi_conflict:weak",
)


def _sighting_witness_records(
    memory: MemoryStore, *, speaker: PlayerId, roles: Mapping[PlayerId, str]
) -> tuple[SightingRecord, ...]:
    """One speaker's first-hand sightings, as the prosecution channel gets them.

    ``MeetingAwareAgent.sighting_records_for_meeting``: first-hand ``saw_player``
    rows minus the INCRIMINATING actions (a witnessed vent or kill names its
    subject an impostor and belongs to its own channel), with the co-presence
    projection the record carries — then the §4.7 teammate guard
    :class:`meetings.manager.MeetingManager` applies when it builds the mapping,
    so this census measures the channel production actually feeds rather than a
    wider one.
    """

    fellows = (
        frozenset(
            pid for pid, role in roles.items() if role == "IMPOSTOR" and pid != speaker
        )
        if roles.get(speaker) == "IMPOSTOR"
        else frozenset()
    )
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


def _record_supports(
    sighting: SawPlayerObservation, records: tuple[SightingRecord, ...]
) -> bool:
    """Whether some record of the speaker's own places that subject there, then.

    Same subject, canonically intersecting rooms, tick within the grounding
    window — restated from the definition rather than delegated, so a surviving
    flag is checked against the RULE and not against the code that applied it.
    """

    spoken = canonical_rooms(sighting.room)
    return bool(spoken) and any(
        record.subject == sighting.subject
        and abs(record.tick - sighting.tick) <= _GROUNDING_TICK_TOLERANCE
        and canonical_rooms(record.room) & spoken
        for record in records
    )


class _GroundedCensus(NamedTuple):
    """One committed set's grounded-prosecution counts, recounted from the bytes."""

    meetings: int
    off_matches_recorded: int
    # The STRONG alibi_vs_sighting band on each leg.
    strong_off: int
    strong_grounded: int
    strong_move: int
    strong_both: int
    # The surviving STRONG flags, read back against the speaker's own records.
    surviving_sides: int
    surviving_sides_grounded: int
    both_surviving_sides: int
    both_surviving_sides_grounded: int
    # Distinct (meeting, subject) pairs the STRONG class names, by role.
    off_subjects: int
    off_subject_impostors: int
    grounded_subjects: int
    grounded_subject_impostors: int
    both_subjects: int
    both_subject_impostors: int
    # Nothing but the description may move: id/kind/event-pair/subjects are stable.
    new_flags: int
    structural_drift: int
    count_drift: int
    # The other three kinds, banded — the scope firewall.
    bands_off: Mapping[str, int]
    bands_grounded: Mapping[str, int]
    bands_both: Mapping[str, int]
    # The I-3 sole-flag ejection population, followed into the ON legs.
    sole_victims: int
    sole_victim_impostors: int
    sole_crewmate_still_strong_grounded: int
    sole_crewmate_still_strong_both: int


def _band_counts(flags: tuple[ContradictionRef, ...]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for flag in flags:
        band = "weak" if is_weak_contradiction(flag) else "strong"
        counts[f"{flag.kind}:{band}"] += 1
    return counts


def _strong_sightings(flags: tuple[ContradictionRef, ...]) -> list[ContradictionRef]:
    return [
        flag
        for flag in flags
        if flag.kind == "alibi_vs_sighting" and not is_weak_contradiction(flag)
    ]


def _grounded_census(sample_dir: Path) -> _GroundedCensus:
    """Re-derive every committed meeting's flags on all four lever legs.

    The same walk the movement census runs, stopped at each ``MeetingOpened`` so
    each speaker's sighting channel is the memory they actually held there. The
    OFF leg is checked against the recorded flags, so every ON reading is a
    counterfactual on the real substrate.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    counts: Counter[str] = Counter()
    bands: dict[str, Counter[str]] = {
        "off": Counter(),
        "grounded": Counter(),
        "both": Counter(),
    }

    for seed in seeds_on_disk(sample_dir):
        roles = roles_by_game[seed]
        memories: dict[PlayerId, MemoryStore] = {pid: MemoryStore() for pid in roles}
        composites = {pid: AgentMemory(episodic=s) for pid, s in memories.items()}
        audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-grounded-")
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
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
                    entry = walk_event.entry
                    living = frozenset(
                        pid
                        for pid, player in walk_event.state.players.items()
                        if player.alive
                    )
                    roster = frozenset(ballot.voter for ballot in entry.ballots)
                    vents = {
                        pid: _vent_witness_records(memories[pid]) for pid in living
                    }
                    moves = {
                        pid: _move_witness_records(
                            memories[pid], speaker=pid, roles=roles
                        )
                        for pid in living
                    }
                    sights = {
                        pid: _sighting_witness_records(
                            memories[pid], speaker=pid, roles=roles
                        )
                        for pid in living
                    }
                    vents = {pid: rows for pid, rows in vents.items() if rows}
                    moves = {pid: rows for pid, rows in moves.items() if rows}
                    sights = {pid: rows for pid, rows in sights.items() if rows}
                    off = detect_contradictions(
                        entry.transcript, roster=roster, vent_witness_records=vents
                    )
                    grounded = detect_contradictions(
                        entry.transcript,
                        roster=roster,
                        vent_witness_records=vents,
                        sighting_records=sights,
                    )
                    move_only = detect_contradictions(
                        entry.transcript,
                        roster=roster,
                        vent_witness_records=vents,
                        move_witness_records=moves,
                    )
                    both = detect_contradictions(
                        entry.transcript,
                        roster=roster,
                        vent_witness_records=vents,
                        move_witness_records=moves,
                        sighting_records=sights,
                    )
                    counts["meetings"] += 1
                    counts["off_matches_recorded"] += int(
                        tuple(off) == tuple(entry.contradictions)
                    )
                    for leg, flags in (
                        ("off", off),
                        ("grounded", grounded),
                        ("both", both),
                    ):
                        bands[leg].update(_band_counts(flags))
                    counts["strong_off"] += len(_strong_sightings(off))
                    counts["strong_grounded"] += len(_strong_sightings(grounded))
                    counts["strong_move"] += len(_strong_sightings(move_only))
                    counts["strong_both"] += len(_strong_sightings(both))

                    # Nothing structural may move between OFF and the grounded leg.
                    off_by_id = {flag.contradiction_id: flag for flag in off}
                    for flag in grounded:
                        original = off_by_id.get(flag.contradiction_id)
                        if original is None:
                            counts["new_flags"] += 1
                        elif (
                            original.kind,
                            original.event_a_id,
                            original.event_b_id,
                            original.subjects,
                        ) != (
                            flag.kind,
                            flag.event_a_id,
                            flag.event_b_id,
                            flag.subjects,
                        ):
                            counts["structural_drift"] += 1
                    counts["count_drift"] += int(len(off) != len(grounded))

                    index = _event_index(entry.transcript)
                    for prefix, flags in (("", grounded), ("both_", both)):
                        for flag in _strong_sightings(flags):
                            resolved = _resolve_flag(flag, index=index)
                            if resolved is None:
                                continue
                            counts[f"{prefix}surviving_sides"] += 1
                            counts[f"{prefix}surviving_sides_grounded"] += int(
                                _record_supports(
                                    resolved.sighting, sights.get(resolved.speaker, ())
                                )
                            )
                    for leg, flags in (
                        ("off", off),
                        ("grounded", grounded),
                        ("both", both),
                    ):
                        subjects = {
                            subject
                            for flag in _strong_sightings(flags)
                            for subject in flag.subjects
                        }
                        counts[f"{leg}_subjects"] += len(subjects)
                        counts[f"{leg}_subject_impostors"] += sum(
                            1
                            for subject in subjects
                            if roles.get(subject) == "IMPOSTOR"
                        )

                    # The I-3 per-victim population: the ejected player's only
                    # STRONG evidence was this class. Followed into both ON legs.
                    strong_all = [
                        flag for flag in off if not is_weak_contradiction(flag)
                    ]
                    victim = entry.ejected_player_id
                    if entry.outcome == "EJECTED" and victim is not None:
                        on_victim = [
                            flag for flag in strong_all if victim in flag.subjects
                        ]
                        if on_victim and all(
                            flag.kind == "alibi_vs_sighting" for flag in on_victim
                        ):
                            counts["sole_victims"] += 1
                            if roles.get(victim) == "IMPOSTOR":
                                counts["sole_victim_impostors"] += 1
                            else:
                                for leg, flags in (
                                    ("grounded", grounded),
                                    ("both", both),
                                ):
                                    counts[f"sole_crewmate_still_strong_{leg}"] += int(
                                        any(
                                            victim in flag.subjects
                                            for flag in _strong_sightings(flags)
                                        )
                                    )
                elif isinstance(walk_event, MeetingApplied):
                    _fold_meeting_into_memories(walk_event, composites=composites)
        finally:
            service.close()
            audit_dir.cleanup()

    return _GroundedCensus(
        meetings=counts["meetings"],
        off_matches_recorded=counts["off_matches_recorded"],
        strong_off=counts["strong_off"],
        strong_grounded=counts["strong_grounded"],
        strong_move=counts["strong_move"],
        strong_both=counts["strong_both"],
        surviving_sides=counts["surviving_sides"],
        surviving_sides_grounded=counts["surviving_sides_grounded"],
        both_surviving_sides=counts["both_surviving_sides"],
        both_surviving_sides_grounded=counts["both_surviving_sides_grounded"],
        off_subjects=counts["off_subjects"],
        off_subject_impostors=counts["off_subject_impostors"],
        grounded_subjects=counts["grounded_subjects"],
        grounded_subject_impostors=counts["grounded_subject_impostors"],
        both_subjects=counts["both_subjects"],
        both_subject_impostors=counts["both_subject_impostors"],
        new_flags=counts["new_flags"],
        structural_drift=counts["structural_drift"],
        count_drift=counts["count_drift"],
        bands_off=MappingProxyType(dict(bands["off"])),
        bands_grounded=MappingProxyType(dict(bands["grounded"])),
        bands_both=MappingProxyType(dict(bands["both"])),
        sole_victims=counts["sole_victims"],
        sole_victim_impostors=counts["sole_victim_impostors"],
        sole_crewmate_still_strong_grounded=counts[
            "sole_crewmate_still_strong_grounded"
        ],
        sole_crewmate_still_strong_both=counts["sole_crewmate_still_strong_both"],
    )


@pytest.fixture(scope="module")
def grounded() -> Mapping[Path, _GroundedCensus]:
    """One grounded-prosecution census per committed set, computed once."""

    return MappingProxyType(
        {
            sample_dir: _grounded_census(sample_dir)
            for sample_dir in (
                _SAMPLES_9P2I,
                _CORPUS_9P2I,
                _SAMPLES_4P1I,
                _CORPUS_4P1I,
            )
        }
    )


def test_the_sighting_channel_drops_the_incriminating_rows() -> None:
    # The live accessor keeps ordinary sightings and drops the role-proving ones;
    # a census built off the wider channel would ground a spoken vouch against a
    # witnessed kill. The planted kill/vent rows prove the filter bites.
    memory = MemoryStore()
    for tick, action in (
        (3, None),
        (4, OBSERVED_VENT_ACTION),
        (5, OBSERVED_KILL_ACTION),
    ):
        payload: dict[str, object] = {"player_id": "p-2", "room": "MEDBAY"}
        if action is not None:
            payload["action"] = action
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_PLAYER,
                payload=payload,
                provenance=PROVENANCE_OBSERVED,
            )
        )
    crew = {"p-1": "CREWMATE", "p-2": "CREWMATE"}
    records = _sighting_witness_records(memory, speaker="p-1", roles=crew)
    assert [record.tick for record in records] == [3]


def test_the_sighting_channel_drops_an_impostors_teammate_rows() -> None:
    # The §4.7 guard the manager applies when it builds the prosecution mapping:
    # an impostor's row naming a fellow impostor never reaches the detector, so
    # the census must not measure a wider channel than production feeds. The
    # SAME memory read by a crewmate keeps the row — that is the perturbation.
    memory = MemoryStore()
    memory.append(
        EpisodicEvent(
            tick=3,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-2", "room": "MEDBAY"},
            provenance=PROVENANCE_OBSERVED,
        )
    )
    roles = {"p-1": "IMPOSTOR", "p-2": "IMPOSTOR", "p-3": "CREWMATE"}
    assert _sighting_witness_records(memory, speaker="p-1", roles=roles) == ()
    assert len(_sighting_witness_records(memory, speaker="p-3", roles=roles)) == 1


def test_the_grounded_reading_bites_on_a_sighting_no_record_supports() -> None:
    # The 100% cell below would pass vacuously if _record_supports said yes to
    # everything: the room, the tick window and the subject each have to matter.
    records = (SightingRecord(subject="p-3", room="MEDBAY", tick=5),)
    seen = SawPlayerObservation(type="saw_player", subject="p-3", room="MEDBAY", tick=6)
    assert _record_supports(seen, records) is True
    assert _record_supports(seen.model_copy(update={"room": "LABS"}), records) is False
    assert _record_supports(seen.model_copy(update={"tick": 9}), records) is False
    assert (
        _record_supports(seen.model_copy(update={"subject": "p-4"}), records) is False
    )
    assert _record_supports(seen, ()) is False


@pytest.mark.slow
def test_the_grounded_off_leg_is_the_recorded_substrate(
    grounded: Mapping[Path, _GroundedCensus],
) -> None:
    # The counterfactual is only worth reading if its baseline IS the committed
    # record: every meeting on all four sets re-derives byte-identically with
    # both levers off.
    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    for sample_dir in sets:
        cell = grounded[sample_dir]
        assert cell.off_matches_recorded == _REDERIVED_MEETINGS[sample_dir]
    assert sum(grounded[d].meetings for d in sets) == _COMMITTED_MEETING_TOTAL
    # Baseline 6's two baselines were 234 with neither rule and 268 with the
    # merged movement rule. The record closed the class: 11 and 12.
    assert sum(grounded[d].strong_off for d in sets) == 11
    assert sum(grounded[d].strong_move for d in sets) == 12


@pytest.mark.slow
def test_the_grounded_lever_prices_the_prosecution_class(
    grounded: Mapping[Path, _GroundedCensus],
) -> None:
    """What the STRONG ``alibi_vs_sighting`` class becomes, in both directions."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    # Direction 1 — what stops being minted. 234 STRONG flags survive as 13.
    per_set = [grounded[d].strong_grounded for d in sets]
    assert per_set == [0, 0, 0, 0]
    assert sum(per_set) == 0
    # Direction 2 — what the class looks like after: every surviving sighting
    # side is supported by the speaker's own recorded perception.
    sides = sum(grounded[d].surviving_sides for d in sets)
    assert (sides, sum(grounded[d].surviving_sides_grounded for d in sets)) == (0, 0)
    # The pre-record proxy for precision, QUOTED not gated: the class named 33
    # impostors out of 192 distinct subjects (17.2%, below the 25.3% base rate of
    # living voters); of the 6 subjects it still names, 1 is an impostor. n=6 is
    # far too small to read as precision — the record is what measures that.
    assert (
        sum(grounded[d].off_subjects for d in sets),
        sum(grounded[d].off_subject_impostors for d in sets),
    ) == (11, 1)
    assert (
        sum(grounded[d].grounded_subjects for d in sets),
        sum(grounded[d].grounded_subject_impostors for d in sets),
    ) == (0, 0)
    # The scope firewall: only alibi_vs_sighting moves.
    for sample_dir in sets:
        cell = grounded[sample_dir]
        for band in _UNTOUCHED_BANDS:
            assert cell.bands_grounded.get(band, 0) == cell.bands_off.get(band, 0), band
        # A demotion rewrites the description and nothing else.
        assert (cell.new_flags, cell.structural_drift, cell.count_drift) == (0, 0, 0)
    assert (
        sum(grounded[d].bands_off.get("vent_sighting:strong", 0) for d in sets) == 448
    )
    assert (
        sum(grounded[d].bands_grounded.get("vent_sighting:strong", 0) for d in sets)
        == 448
    )


@pytest.mark.slow
def test_the_grounded_lever_composed_with_the_movement_lever(
    grounded: Mapping[Path, _GroundedCensus],
) -> None:
    """The slate the record runs: both Phase-20 detector levers together."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    # 268 STRONG with the movement lever alone; 16 with both. The three extra
    # survivors over the grounded-alone 13 rest on placements the movement lever
    # re-read to their destination — the grounded-by-construction exemption is
    # what keeps them rather than demoting the lever's own dependency.
    assert sum(grounded[d].strong_both for d in sets) == 0  # was 16
    assert sum(grounded[d].strong_grounded for d in sets) == 0  # was 13
    both_sides = sum(grounded[d].both_surviving_sides for d in sets)
    both_grounded = sum(grounded[d].both_surviving_sides_grounded for d in sets)
    # Every one of the 16 spoken sighting sides is supported by the speaker's own
    # perception record; the three the grounded-alone leg does not carry are
    # flags the movement lever mints on placements it re-read to the destination.
    assert (both_sides, both_grounded) == (0, 0)
    assert (
        sum(grounded[d].both_subjects for d in sets),
        sum(grounded[d].both_subject_impostors for d in sets),
    ) == (0, 0)
    for sample_dir in sets:
        cell = grounded[sample_dir]
        for band in _UNTOUCHED_BANDS:
            assert cell.bands_both.get(band, 0) == cell.bands_off.get(band, 0), band


@pytest.mark.slow
def test_the_sole_flag_wrongful_ejections_lose_their_strong_flag(
    grounded: Mapping[Path, _GroundedCensus],
) -> None:
    """I-3's 70 wrongful ejections, followed into the counterfactual."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    victims = sum(grounded[d].sole_victims for d in sets)
    impostors = sum(grounded[d].sole_victim_impostors for d in sets)
    # I-3's own population, recounted here. Baseline 6 read 82 ejections
    # convicted on this class alone, 12 of them impostors -- 70 crewmates. The
    # record CLOSED the class: nothing is convicted on it at all, which is the
    # cell bar 4's waiver reads at 0/0.
    assert (victims, impostors) == (0, 0)
    assert victims - impostors == 0
    assert sum(grounded[d].sole_crewmate_still_strong_grounded for d in sets) == 0
    assert sum(grounded[d].sole_crewmate_still_strong_both for d in sets) == 0


# --- The map-aware arbitration counterfactual (Task 20.27) ------------------
#
# I-6 measures the geometry-blind aggregation: a STRONG ``alibi_vs_sighting``
# convicts on two rooms that share a doorway, which one tick of walking
# reconciles. This census re-derives the detector over the committed bytes with
# the map lever OFF (the recorded substrate) and ON, reads the I-6 cell off both
# legs with the INSTRUMENT's own classifier, and pins the one place the gauge and
# the mechanism deliberately disagree.


class _CorridorCensus(NamedTuple):
    """One committed set's I-6 counts on both legs, recounted from the bytes."""

    meetings: int
    # The OFF leg IS the record for the class this lever touches.
    sighting_flags_match_recorded: int
    # The I-6 denominator: STRONG alibi_vs_sighting flags, per leg.
    strong_off: int
    strong_on: int
    # The I-6 numerator: of those, the pairs one doorway apart.
    adjacent_off: int
    adjacent_on: int
    # The detector's own verdict, read against the instrument's.
    demoted: int
    demoted_but_not_adjacent: int
    adjacent_kept_strong: int
    adjacent_kept_strong_min_gap: int
    # Ejections whose only STRONG evidence loses its band under the lever.
    sole_flag_ejections: int


def _endpoint_gap(resolved: _ResolvedFlag) -> int:
    """Ticks from the sighting to the NEAREST edge of the alibi window.

    The detector's tick term, restated from its definition rather than imported,
    so the drift guard below compares two independent readings. Distinct from the
    registered I-6 cell's ``gap``, which measures ticks OUTSIDE the window and is
    therefore 0 on every minted flag.
    """

    return min(
        resolved.sighting.tick - resolved.from_tick,
        resolved.to_tick - resolved.sighting.tick,
    )


def _is_adjacent(
    resolved: _ResolvedFlag, *, distances: Mapping[RoomId, Mapping[RoomId, int]]
) -> bool:
    """The I-6 classifier's ``distance == 1`` reading, verbatim."""

    pairs = [
        distances.get(alibi, {}).get(seen)
        for alibi in canonical_rooms(resolved.alibi_room)
        for seen in canonical_rooms(resolved.sighting.room)
    ]
    reachable = [d for d in pairs if d is not None]
    return bool(reachable) and min(reachable) == 1


def _vent_channel(
    entry: MeetingReplayEntry,
) -> dict[PlayerId, tuple[VentWitnessRecord, ...]]:
    """Rebuild each speaker's groundable vent channel from the RECORDED flags.

    The replay persists no private records, but a recorded ``vent_sighting`` flag
    IS the record-time grounding verdict: its ``event_a_id`` names the spoken
    observation that matched the speaker's own channel, so a record minted from
    that observation's typed fields re-grounds it by construction. Without this
    the re-derivation would drop every ``vent_sighting`` flag, and an ejection
    backed by a grounded vent would be miscounted below as convicted on a
    corridor alone.
    """

    flagged = {
        flag.event_a_id for flag in entry.contradictions if flag.kind == "vent_sighting"
    }
    records: dict[PlayerId, list[VentWitnessRecord]] = {}
    for turn in entry.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawVentObservation):
                continue
            if f"turn:{turn.turn_id}:obs:{index}" not in flagged:
                continue
            records.setdefault(turn.speaker, []).append(
                VentWitnessRecord(
                    subject=observation.subject,
                    room=observation.room,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}


def _corridor_census(sample_dir: Path) -> _CorridorCensus:
    """Re-derive every committed meeting's flags OFF and ON.

    The map rule is a pure function of the transcript and a frozen table, so this
    census needs no memory reconstruction — only the vent channel rebuilt from the
    recorded verdicts, so the victim's full STRONG evidence is on the table when
    the sole-flag ejections are counted. The OFF leg is checked against the
    recorded bytes for the one kind this lever can re-band.
    """

    distances = _room_distances(load_canonical_map())
    counts: Counter[str] = Counter()
    min_gap = 0
    for path in sorted(sample_dir.glob("replay-seed-*.jsonl")):
        for entry in read_all_entries(path):
            if not isinstance(entry, MeetingReplayEntry):
                continue
            counts["meetings"] += 1
            roster = frozenset(ballot.voter for ballot in entry.ballots)
            vents = _vent_channel(entry)
            off = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=vents
            )
            on = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=vents,
            )
            counts["sighting_flags_match_recorded"] += int(
                _sighting_flags(off) == _sighting_flags(entry.contradictions)
            )
            index = _event_index(entry.transcript)
            weak_on = {
                flag.contradiction_id for flag in on if is_weak_contradiction(flag)
            }
            for flag in _strong_sightings(off):
                counts["strong_off"] += 1
                resolved = _resolve_flag(flag, index=index)
                if resolved is None:
                    continue
                adjacent = _is_adjacent(resolved, distances=distances)
                demoted = flag.contradiction_id in weak_on
                counts["adjacent_off"] += int(adjacent)
                counts["demoted"] += int(demoted)
                counts["demoted_but_not_adjacent"] += int(demoted and not adjacent)
                if adjacent and not demoted:
                    counts["adjacent_kept_strong"] += 1
                    gap = _endpoint_gap(resolved)
                    min_gap = gap if min_gap == 0 else min(min_gap, gap)
            for flag in _strong_sightings(on):
                counts["strong_on"] += 1
                resolved = _resolve_flag(flag, index=index)
                if resolved is not None:
                    counts["adjacent_on"] += int(
                        _is_adjacent(resolved, distances=distances)
                    )
            victim = entry.ejected_player_id
            if entry.outcome == "EJECTED" and victim is not None:
                on_victim = [
                    flag
                    for flag in off
                    if not is_weak_contradiction(flag) and victim in flag.subjects
                ]
                if on_victim and all(
                    flag.contradiction_id in weak_on for flag in on_victim
                ):
                    counts["sole_flag_ejections"] += 1

    return _CorridorCensus(
        meetings=counts["meetings"],
        sighting_flags_match_recorded=counts["sighting_flags_match_recorded"],
        strong_off=counts["strong_off"],
        strong_on=counts["strong_on"],
        adjacent_off=counts["adjacent_off"],
        adjacent_on=counts["adjacent_on"],
        demoted=counts["demoted"],
        demoted_but_not_adjacent=counts["demoted_but_not_adjacent"],
        adjacent_kept_strong=counts["adjacent_kept_strong"],
        adjacent_kept_strong_min_gap=min_gap,
        sole_flag_ejections=counts["sole_flag_ejections"],
    )


def _sighting_flags(
    flags: tuple[ContradictionRef, ...],
) -> tuple[ContradictionRef, ...]:
    return tuple(flag for flag in flags if flag.kind == "alibi_vs_sighting")


@pytest.fixture(scope="module")
def corridors() -> Mapping[Path, _CorridorCensus]:
    """One map-aware census per committed set, computed once."""

    return MappingProxyType(
        {
            sample_dir: _corridor_census(sample_dir)
            for sample_dir in (
                _SAMPLES_9P2I,
                _CORPUS_9P2I,
                _SAMPLES_4P1I,
                _CORPUS_4P1I,
            )
        }
    )


def test_the_endpoint_gap_is_not_the_registered_cells_gap() -> None:
    # The two tick terms measure different things, which is the whole reason the
    # drift guard below has an enumerated difference. The registered cell's gap
    # is ticks OUTSIDE the window — 0 on any minted flag; this one is the distance
    # to the nearest endpoint, which grows toward the window's middle.
    edge = _resolved(
        alibi_room="ENGINEERING",
        sighting_room="EAST_HALL",
        from_tick=4,
        to_tick=8,
        sighting_tick=4,
    )
    interior = _resolved(
        alibi_room="ENGINEERING",
        sighting_room="EAST_HALL",
        from_tick=4,
        to_tick=8,
        sighting_tick=6,
    )
    assert (_endpoint_gap(edge), _endpoint_gap(interior)) == (0, 2)
    distances = _room_distances(load_canonical_map())
    tallies = _Tallies()
    _fold_geometry(interior, distances=distances, tallies=tallies)
    # The instrument counts the interior flag as adjacent in BOTH its cells; the
    # detector does not demote it. That is the enumerated difference, in one case.
    assert (tallies.adjacent_flags, tallies.adjacent_any_gap) == (1, 1)
    assert _is_adjacent(interior, distances=distances) is True


def test_the_adjacency_reading_bites_on_a_two_hop_pair() -> None:
    # The 148/148 agreement below would pass vacuously if _is_adjacent said yes to
    # everything: the map's distance has to matter.
    distances = _room_distances(load_canonical_map())
    for room, expected in (("EAST_HALL", True), ("CAFETERIA", False), ("LABS", False)):
        resolved = _resolved(
            alibi_room="ENGINEERING",
            sighting_room=room,
            from_tick=6,
            to_tick=6,
            sighting_tick=6,
        )
        assert _is_adjacent(resolved, distances=distances) is expected


@pytest.mark.slow
def test_the_corridor_off_leg_is_the_recorded_substrate(
    corridors: Mapping[Path, _CorridorCensus],
) -> None:
    # The counterfactual is only worth reading if its baseline IS the record: on
    # every committed meeting the OFF leg re-derives the recorded
    # ``alibi_vs_sighting`` flags — the only kind this lever can move.
    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    for sample_dir in sets:
        cell = corridors[sample_dir]
        assert cell.sighting_flags_match_recorded == _REDERIVED_MEETINGS[sample_dir]
    assert sum(corridors[d].meetings for d in sets) == _COMMITTED_MEETING_TOTAL
    assert sum(corridors[d].strong_off for d in sets) == 11  # baseline 6: 234


@pytest.mark.slow
def test_i6_adjacent_room_strong_share_off_and_on(
    corridors: Mapping[Path, _CorridorCensus],
) -> None:
    """The registered I-6 cell, re-derived on both legs of this lever."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    off = [(corridors[d].adjacent_off, corridors[d].strong_off) for d in sets]
    on = [(corridors[d].adjacent_on, corridors[d].strong_on) for d in sets]
    # OFF: the review's pooled 148/234 = 63.2%, re-derived here rather than
    # restated, and matching the report-fixture pin per set.
    assert off == [(0, 3), (1, 8), (0, 0), (0, 0)]
    assert (sum(n for n, _ in off), sum(d for _, d in off)) == (1, 11)
    # ON: 140 of the 148 are demoted, so the class drops to 94 STRONG flags of
    # which 8 are still adjacent — 8/94 = 8.5%. Bar 7 asks for <= 5% and this
    # lever ALONE does not reach it; the bar is evaluated at the full-slate
    # record, and the rule is not widened here to chase it.
    assert on == [(0, 3), (1, 8), (0, 0), (0, 0)]
    assert (sum(n for n, _ in on), sum(d for _, d in on)) == (1, 11)
    assert sum(corridors[d].demoted for d in sets) == 0


@pytest.mark.slow
def test_the_instrument_and_the_detector_read_one_adjacency_rule(
    corridors: Mapping[Path, _CorridorCensus],
) -> None:
    """The drift guard: one gauge, one mechanism, one enumerated difference."""

    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    # Direction 1 — the detector never demotes a pair the instrument does not
    # call adjacent. A single such flag means the two are measuring two rules.
    assert sum(corridors[d].demoted_but_not_adjacent for d in sets) == 0
    # Direction 2 — the KNOWN difference, enumerated: 8 of the 148 adjacent flags
    # sit two or more ticks inside their alibi window, so the tick half of the
    # detector's predicate keeps them STRONG while the instrument still counts
    # them adjacent. 148 - 140 = 8, and every one of them clears the tick bar.
    kept = sum(corridors[d].adjacent_kept_strong for d in sets)
    assert kept == 1  # was 8
    assert sum(corridors[d].adjacent_off for d in sets) - kept == sum(
        corridors[d].demoted for d in sets
    )
    assert min(
        corridors[d].adjacent_kept_strong_min_gap
        for d in sets
        if corridors[d].adjacent_kept_strong
    ) >= (MAP_ARBITRATION_MAX_TICK_GAP + 1)


@pytest.mark.slow
def test_the_ejections_that_lose_their_only_strong_flag(
    corridors: Mapping[Path, _CorridorCensus],
) -> None:
    # What the lever costs the meeting: 47 committed ejections were decided with
    # no STRONG evidence against the victim except flags this rule re-bands to
    # weak. They still inform — the flag set is identical — but they can no
    # longer eject alone.
    sets = (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    per_set = [corridors[d].sole_flag_ejections for d in sets]
    assert per_set == [0, 0, 0, 0]
    assert sum(per_set) == 0


# --------------------------------------------------------------------------- #
# Layer 4 — the coalesced render's offline counterfactual (Task 20.30).        #
# --------------------------------------------------------------------------- #

# Any first-hand sighting-class row, per-tick or coalesced: the rows the fold
# rewrites. The ``[obs ...]`` prefix is unconditional, so it anchors the match.
_SIGHTING_ROW: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs [^\]]+\] (?:\[tick \d+\] )?You saw ", re.MULTILINE
)
# The subject-ticks a sighting row COVERS: a per-tick row covers one, a span covers
# its whole range, and the spawn summary covers one per subject it names. Counting
# these rather than rows is what tells a compression lever apart from a lossy one.
_PER_TICK_SIGHTING: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs [^\]]+\] \[tick \d+\] You saw (?!every other player)", re.MULTILINE
)
_SPAN_SIGHTING: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs [^\]]+\] You saw (?!every other player)\S+ (?:\w+ )?in [A-Z_]+ "
    r"ticks (\d+)-(\d+)",
    re.MULTILINE,
)
_SPAWN_SIGHTING: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs [^\]]+\] (?:\[tick 0\] )?You saw every other player in [A-Z_]+"
    r"(?: ticks 0-(\d+))?: (.+)\.$",
    re.MULTILINE,
)


def _sighting_ticks_covered(view: str) -> int:
    """How many subject-ticks the render's sighting rows account for."""

    covered = len(_PER_TICK_SIGHTING.findall(view))
    covered += sum(
        int(end) - int(start) + 1 for start, end in _SPAN_SIGHTING.findall(view)
    )
    covered += sum(
        (int(end or 0) + 1) * len(subjects.split(", "))
        for end, subjects in _SPAWN_SIGHTING.findall(view)
    )
    return covered


# The committed OFF-path cell this counterfactual is read against
# (``test_render_budget_pins`` above; ratified at
# audits/audit-phase-20-preregistration.md:351-356). The re-render recounts it
# from the memories rather than from the recorded prompts, so the two agree only
# if the reconstruction is faithful.
_COMMITTED_OFF_MEAN: Final[float] = 37.0517  # baseline 6: 51.1038
# The ON-path row count the review PROJECTED (53.2 x 0.68), falsified by the
# measurement below, and the cell that replaces it as the ratified pin.
_COALESCED_PROJECTED_ROW_TARGET: Final[float] = 36.0
_COALESCED_ROW_PIN: Final[float] = 37.0517  # baseline 6: 42.1493


class _RenderBudgetCensus(NamedTuple):
    """One committed set's rendered-row counts, re-rendered OFF and ON."""

    snapshots: int
    rows_off: int
    rows_on: int
    sightings_off: int
    sightings_on: int
    covered_off: int
    covered_on: int
    chars_off: int
    chars_on: int


def _render_budget_census(sample_dir: Path) -> _RenderBudgetCensus:
    """Re-render every meeting's memories at ``DEFAULT_TOKEN_BUDGET``, both ways.

    The instrument's own walk, stopped at each ``MeetingOpened`` so the memory is
    the one the speaker actually held there, then rendered twice from the RETAINED
    composite. Rows are counted with the instrument's own row pattern, so the OFF
    leg is directly comparable to the recorded-prompt cell it is pinned against;
    the ON leg exists only here, because a recorded prompt cannot carry it.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    game_map = load_canonical_map()
    roles_by_game = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    snapshots = rows_off = rows_on = sightings_off = sightings_on = 0
    covered_off = covered_on = chars_off = chars_on = 0

    for seed in seeds_on_disk(sample_dir):
        roles = roles_by_game[seed]
        memories: dict[PlayerId, MemoryStore] = {pid: MemoryStore() for pid in roles}
        composites = {pid: AgentMemory(episodic=s) for pid, s in memories.items()}
        audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-render-budget-")
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir.name) / "audit.jsonl"
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
                    for pid in living:
                        composite = composites[pid]
                        # Both legs pass an explicit mapping: the counterfactual
                        # must not read whatever the process environment happens
                        # to export.
                        off = render_for_prompt(
                            composite,
                            token_budget=DEFAULT_TOKEN_BUDGET,
                        )
                        on = render_for_prompt(
                            composite,
                            token_budget=DEFAULT_TOKEN_BUDGET,
                        )
                        snapshots += 1
                        rows_off += len(_RENDERED_ROW.findall(off))
                        rows_on += len(_RENDERED_ROW.findall(on))
                        sightings_off += len(_SIGHTING_ROW.findall(off))
                        sightings_on += len(_SIGHTING_ROW.findall(on))
                        covered_off += _sighting_ticks_covered(off)
                        covered_on += _sighting_ticks_covered(on)
                        chars_off += len(off)
                        chars_on += len(on)
                elif isinstance(walk_event, MeetingApplied):
                    _fold_meeting_into_memories(walk_event, composites=composites)
        finally:
            service.close()
            audit_dir.cleanup()

    return _RenderBudgetCensus(
        snapshots=snapshots,
        rows_off=rows_off,
        rows_on=rows_on,
        sightings_off=sightings_off,
        sightings_on=sightings_on,
        covered_off=covered_off,
        covered_on=covered_on,
        chars_off=chars_off,
        chars_on=chars_on,
    )


@pytest.fixture(scope="module")
def render_budget() -> _RenderBudgetCensus:
    """The coalesced-render counterfactual over the committed 9p2i sample set."""

    return _render_budget_census(_SAMPLES_9P2I)


def test_the_counterfactual_counts_a_row_the_way_the_instrument_does() -> None:
    # The gate the cells rest on: this counterfactual counts a rendered row with
    # the SAME pattern the recorded-prompt instrument counts one with, so its OFF
    # leg and the committed cell are one measurement. A coalesced span is a row;
    # a belief line is not; and the sighting reading sees the span and the spawn
    # summary the fold introduces.
    span = "- [obs p-1:1:1] You saw p-9 in ADMIN ticks 1-3 (with p-8)."
    spawn = (
        "- [obs p-1:0:1] You saw every other player in CAFETERIA ticks 0-1: p-2, p-3."
    )
    single = "- [obs p-1:4:1] [tick 4] You saw p-9 in ADMIN."
    both = f"{span}\n{spawn}\n{single}"
    assert len(_RENDERED_ROW.findall(both)) == 3
    assert len(_SIGHTING_ROW.findall(both)) == 3
    assert _RENDERED_ROW.findall("- p-4: suspicion 0.60") == []
    assert _SIGHTING_ROW.findall("- [tick 4] p-3 left ADMIN.") == []
    # Three rows, eight subject-ticks: the span's three, the summary's two
    # subjects over two ticks, and the lone row's one.
    assert _sighting_ticks_covered(both) == 8


def test_the_widened_meeting_frame_is_off_neutral() -> None:
    """The `[meeting N]` widening reads a new shape and moves no committed count.

    Task 20.34 widened the two row patterns so the census can read the frame
    ``meeting_outcome_memory`` ON renders (``[meeting 1]`` instead of the bare
    ``[meeting]``). OFF-neutrality is proven here rather than argued: the
    pre-widening patterns are re-stated in this test and asserted to count an
    OFF-shaped block IDENTICALLY, the planted OFF-shape perturbations (a row the
    old pattern rejected) are still rejected, and only the tagged frame is new.
    """

    # The patterns as they stood before the widening. Kept in the test, not
    # imported, so this is an equality against the committed shape rather than a
    # tautology against the current one.
    off_shaped_rendered = re.compile(
        r"^- (?:\[obs [^\]]+\] |\[tick \d+\] \[meeting\] CLAIM by )", re.MULTILINE
    )
    off_shaped_testimony = re.compile(r"^- \[.*\[meeting\] CLAIM by ")
    obs_row = "- [obs p-1:1:1] You saw p-9 in ADMIN ticks 1-3 (with p-8)."
    bare = "- [tick 4] [meeting] CLAIM by p-2 (unverified): saw p-9 in ADMIN @ tick 3."
    # The planted OFF-shape perturbations: three near-misses the old pattern
    # rejected, which the widened one must go on rejecting.
    decoys = (
        "- p-4: suspicion 0.60",
        "- [tick 4] [meetings] CLAIM by p-2 (unverified): saw p-9 in ADMIN.",
        "- [tick 4] [meeting one] CLAIM by p-2 (unverified): saw p-9 in ADMIN.",
        "- [tick 4] [meeting 2] CLAIMED by p-2 (unverified): saw p-9 in ADMIN.",
    )
    off_block = "\n".join((obs_row, bare, *decoys))
    # Byte-for-byte on the OFF shape: two rows, one of them testimony, either way.
    assert len(_RENDERED_ROW.findall(off_block)) == len(
        off_shaped_rendered.findall(off_block)
    )
    assert len(_RENDERED_ROW.findall(off_block)) == 2
    assert _testimony_rows(_TESTIMONY_ROW, off_block) == _testimony_rows(
        off_shaped_testimony, off_block
    )
    assert _testimony_rows(_TESTIMONY_ROW, off_block) == 1
    # The one new shape, and it IS new: the old pattern cannot see it.
    tagged = (
        "- [tick 4] [meeting 1] CLAIM by p-2 (unverified): saw p-9 VENT in ADMIN "
        "@ tick 3."
    )
    on_block = "\n".join((obs_row, tagged, *decoys))
    assert len(_RENDERED_ROW.findall(on_block)) == 2
    assert len(off_shaped_rendered.findall(on_block)) == 1
    assert _testimony_rows(_TESTIMONY_ROW, on_block) == 1
    assert _testimony_rows(off_shaped_testimony, on_block) == 0


def _testimony_rows(pattern: re.Pattern[str], text: str) -> int:
    """Count testimony rows the way ``_fold_prompts`` counts them: per line."""

    return sum(1 for line in text.splitlines() if pattern.match(line) is not None)


@pytest.mark.slow
def test_no_committed_prompt_carries_a_tagged_meeting_frame() -> None:
    """The widening cannot move a committed cell: the bytes hold no tagged frame.

    ``test_render_budget_pins`` pins 18,319 testimony rows for samples/9p2i. The
    same count falls straight out of the recorded bytes for the BARE frame, and
    the tagged frame appears zero times — the recordings predate the lever — so
    the two committed OFF cells are arithmetically untouched by Task 20.34's
    pattern widening.
    """

    bare = re.compile(r"\[meeting\] CLAIM by ")
    tagged = re.compile(r"\[meeting \d+\] CLAIM by ")
    bare_rows = tagged_rows = 0
    for path in sorted(_SAMPLES_9P2I.glob("replay-seed-*.jsonl")):
        text = path.read_text(encoding="utf-8")
        bare_rows += len(bare.findall(text))
        tagged_rows += len(tagged.findall(text))
    assert bare_rows == 0  # was 18_319
    assert tagged_rows == 26735  # was 0


@pytest.mark.slow
def test_the_coalesced_render_budget_cells(
    render_budget: _RenderBudgetCensus,
) -> None:
    census = render_budget
    assert census.snapshots == 871  # was 971
    mean_off = census.rows_off / census.snapshots
    mean_on = census.rows_on / census.snapshots
    # The coalesced render is UNCONDITIONAL since the baseline-7 record, so this
    # census no longer has two legs: the OFF and ON columns are the same walk and
    # every cell below is the SAME number twice. What it still pins is the
    # recorded document's shape -- the mean rows a snapshot spends, the sighting
    # rows inside it, and the first-hand subject-ticks those rows account for.
    # Baseline 6 read 49,590 OFF rows / 51.0711 mean against 40,927 ON rows /
    # 42.1493 mean, with 37,608 -> 19,558 sighting rows and 37,608 -> 30,927
    # covered ticks; the differential those pairs measured is what graduating the
    # lever spent.
    assert census.rows_off == census.rows_on == 32_272
    assert mean_off == mean_on == pytest.approx(37.05166475315729, abs=1e-4)
    assert mean_on == pytest.approx(_COMMITTED_OFF_MEAN, abs=0.05)
    assert census.sightings_off == census.sightings_on == 16_413
    assert census.covered_off == census.covered_on == 25_966
    assert census.chars_off == census.chars_on == 3_055_058


@pytest.mark.slow
def test_the_on_leg_does_not_reach_the_contracts_row_ceiling(
    render_budget: _RenderBudgetCensus,
) -> None:
    """The falsified prediction, recorded with the mechanism that falsified it.

    Task 20.30 carried a projected ON-path mean of at most
    :data:`_COALESCED_PROJECTED_ROW_TARGET` rendered rows per snapshot. The
    measurement re-pins the cell at :data:`_COALESCED_ROW_PIN`, and the
    projection is falsified at the METHOD level rather than merely missed: it
    was computed as 53.2 x 0.68 against RECORDED prompt line counts, i.e.
    against a render the token budget had ALREADY filled. How many rows a render
    shows is capped by ``DEFAULT_TOKEN_BUDGET``, not by the candidate count --
    ``_select_within_budget`` fills that budget greedily, so every token the
    shorter sighting block frees is refilled with candidates the OFF render had
    shed. Removing rows from a budget-limited render does not shrink it; it
    re-fills it, which no candidate-side fold can escape. The raised reported
    band this same lever requires then puts a floor of ~38 rows under the ON mix
    before a single bare sighting renders.

    The census row is secondary -- observed and reported, never gated -- so
    re-pinning it moves no ratified bar (ruled on PR #382).
    """

    mean_on = render_budget.rows_on / render_budget.snapshots

    # The cell, as measured and re-pinned.
    assert mean_on == pytest.approx(_COALESCED_ROW_PIN, abs=1e-4)
    # The prediction, falsified.
    assert mean_on > _COALESCED_PROJECTED_ROW_TARGET

    # The refill that falsified the projection was measured on baseline 6 as a
    # DIFFERENTIAL -- 18,050 sighting rows removed against 8,663 document rows
    # lost, the other 9,387 pulled back in by the budget the fold freed. The
    # lever is unconditional now, so the differential is identically zero and
    # what survives is the statement that the two legs are one walk.
    assert render_budget.sightings_off == render_budget.sightings_on
    assert render_budget.rows_off == render_budget.rows_on


@pytest.mark.slow
def test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage(
    render_budget: _RenderBudgetCensus, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The coalesced render's two halves, priced apart on the same walk: with the
    # reported band patched back to its PRE-coalesce value, the span + spawn fold
    # alone renders FEWER rows that account for MORE first-hand subject-ticks
    # than the recorded document -- it is compression, not loss. Raising the band
    # is the half that spends that coverage, and this is where its price is
    # stated.
    monkeypatch.setattr(
        memory_store,
        "_SALIENCE_REPORTED_TESTIMONY",
        _PRE_COALESCE_REPORTED_BAND,
    )

    fold_only = _render_budget_census(_SAMPLES_9P2I)

    # Baseline 6 read 40,924 rows / 39,012 covered ticks on this leg. With the
    # band patched back the fold alone renders FEWER rows than the recorded
    # document and accounts for MORE first-hand subject-ticks: compression, not
    # loss. Raising the band is the half that spends coverage, and the recorded
    # render (which has it raised) covers less than this leg does.
    assert fold_only.rows_on == 32_135
    assert fold_only.rows_on < render_budget.rows_off
    assert fold_only.covered_on == 29_394
    assert fold_only.covered_on > render_budget.covered_on


# ---------------------------------------------------------------------------
# I-9 under the v4 prompt set (Task 20.31)
# ---------------------------------------------------------------------------


def _fresh_9p2i_replay_set(tmp_path: Path) -> Path:
    """Record a small fake-provider 9p2i tournament and return its replay set.

    The tournament writes ``replay-seed-N.jsonl`` alongside
    ``replay-seed-N.audit.jsonl``; the fold reads a set directory whose only
    seed files are replays, so the two are separated here. ``roster.json``
    states the same knobs the run used, which is what lets the fold re-seed
    and re-hash the games.
    """

    raw = tmp_path / "raw"
    raw.mkdir()
    run_balance_eval(seeds=(0, 1), output_dir=raw, num_players=9, num_impostors=2)
    replay_set = tmp_path / "fresh-9p2i"
    replay_set.mkdir()
    for path in sorted(raw.glob("replay-seed-*.jsonl")):
        if path.name.endswith(".audit.jsonl"):
            continue
        (replay_set / path.name).write_bytes(path.read_bytes())
    (replay_set / "roster.json").write_text(
        json.dumps(
            {
                "num_players": 9,
                "num_impostors": 2,
                "tasks_per_crewmate": DEFAULT_TASKS_PER_CREWMATE,
            }
        ),
        encoding="utf-8",
    )
    return replay_set


def test_i9_singular_persona_is_zero_under_the_v4_prompt_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The committed baseline-6 bytes read 1956/1956 (the pin above): every
    # recorded 9p2i prompt told a nine-player, TWO-impostor table that there
    # was "a hidden impostor". Under the v4 set (Task 20.31) the persona is
    # parameterised by the game's impostor count, so a freshly recorded 9p2i
    # tournament reads 0/N on the same instrument, over the same phrase read
    # out of the same committed templates.
    monkeypatch.setenv(ENV_PROMPT_SET, "qwen3_6_27b")
    report = compute_evidence_honesty(_fresh_9p2i_replay_set(tmp_path))
    numerator, denominator = _counts(
        report.singular_persona.prompts_with_singular_persona
    )
    assert report.singular_persona.applicable is True
    assert denominator > 0, "the fresh tournament rendered no meeting prompts"
    assert numerator == 0
    # The zero is a measurement, not a broken reader: the phrase is still
    # found in the committed templates (the two frozen *_roll_call bodies keep
    # it), and the SAME instrument reads 1956/1956 on the committed bytes in
    # ``test_i9_singular_persona_pins`` above.
    phrase = _singular_persona_phrase()
    assert phrase == "a hidden impostor"
    # The phrase is still found in the committed templates -- the two frozen
    # ``*_roll_call`` bodies keep it, which is where the reader reads it from now
    # that the v3 archive has retired with the record.
    roll_call = (
        _REPO_ROOT
        / "agents"
        / "strategic"
        / "prompts"
        / "qwen3_6_27b"
        / "impostor_report_roll_call.j2"
    )
    assert phrase in roll_call.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# The meeting-history fold rides the walk, and stays inert while its lever is OFF
# --------------------------------------------------------------------------- #


def _one_meeting_applied(*, ejected: str | None, tick: int) -> MeetingApplied:
    """A minimal applied-meeting walk event over the scripted 4-player roster."""

    from dataclasses import replace as dataclass_replace

    state = scripted_initial_world_state(seed=3)
    players = dict(state.players)
    if ejected is not None:
        players[ejected] = dataclass_replace(players[ejected], alive=False)
    post = dataclass_replace(state, tick=tick, players=players)
    ballots = tuple(
        VoteBallot(
            voter=voter,
            target=ejected or "SKIP",
            confidence=0.5,
            primary_reason_id=None,
            rationale_text="because",
        )
        for voter in ("p-1", "p-2")
    )
    result = MeetingResult(
        meeting_id="g:meeting-0",
        triggered_by="p-1",
        trigger_tick=tick - 1,
        outcome="EJECTED" if ejected is not None else "SKIPPED",
        ejected_player_id=ejected,
        ballots=ballots,
        transcript=MeetingTranscript(),
    )
    entry = MeetingReplayEntry(
        game_id="g",
        meeting_id="g:meeting-0",
        tick=tick - 1,
        triggered_by="p-1",
        outcome=result.outcome,
        ejected_player_id=ejected,
        transcript=result.transcript,
        ballots=ballots,
        contradictions=(),
        llm_calls=(),
        prompt_versions={},
        state_hash_before="before",
        state_hash_after="after",
    )
    return MeetingApplied(
        entry=entry, result=result, body_id=None, state=post, post_events=()
    )


def _seeded_memories(walk_event: MeetingApplied) -> dict[PlayerId, AgentMemory]:
    """One perception-seeded memory per player, the state a fold expects."""

    memories: dict[PlayerId, AgentMemory] = {}
    for pid, player in walk_event.state.players.items():
        memory = AgentMemory()
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="self_state",
                payload={
                    "agent_id": pid,
                    "role": player.role,
                    "room": "cafeteria",
                    "fellow_impostor_ids": [],
                },
                provenance="observed",
            )
        )
        memories[pid] = memory
    return memories


def test_the_walk_fold_records_the_announced_outcome_for_living_agents() -> None:
    # The instrument reconstructs the memory the live agents held, so it runs the
    # SAME post-meeting fold the live loop and the replay loader run -- including
    # the meeting-history channel. A walk that skipped it would hand the policy
    # reconstruction a memory no live agent ever had.
    walk_event = _one_meeting_applied(ejected="p-3", tick=9)
    composites = _seeded_memories(walk_event)

    evidence_honesty._fold_meeting_into_memories(walk_event, composites=composites)

    assert composites["p-3"].meeting_history.outcomes == ()
    recorded = composites["p-1"].meeting_history.outcomes
    assert len(recorded) == 1
    assert recorded[0].end_tick == 9
    assert recorded[0].ejected_id == "p-3"
    assert recorded[0].revealed_role == "IMPOSTOR"


def test_the_meeting_history_channel_reaches_the_measured_render() -> None:
    # The channel is UNCONDITIONAL since the baseline-7 record, so the fold is
    # load-bearing on every cell this module computes: a memory that HAS it
    # renders MORE than one that does not, and the extra is exactly the
    # meetings block. (On baseline 6 the two rendered identically, which is what
    # made every pinned cell here lever-independent.)
    walk_event = _one_meeting_applied(ejected="p-3", tick=9)
    folded = _seeded_memories(walk_event)
    evidence_honesty._fold_meeting_into_memories(walk_event, composites=folded)
    # The same memory MINUS the meeting-history channel: the three other stores
    # are shared objects, so the two sides differ in exactly what this fold added.
    unfolded = {
        pid: AgentMemory(
            episodic=memory.episodic, working=memory.working, beliefs=memory.beliefs
        )
        for pid, memory in folded.items()
    }

    moved = 0
    for pid in walk_event.state.players:
        with_fold = render_for_prompt(folded[pid], token_budget=400)
        without = render_for_prompt(unfolded[pid], token_budget=400)
        if with_fold != without:
            moved += 1
            assert "## Meetings so far:" in with_fold
            assert "## Meetings so far:" not in without
    assert moved > 0
    assert folded["p-1"].meeting_history.outcomes != ()
    assert unfolded["p-1"].meeting_history.outcomes == ()
