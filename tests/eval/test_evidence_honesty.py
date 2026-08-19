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

import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.tactical.impostor_policy import RankedTarget
from engine.world import load_canonical_map
from eval import evidence_honesty
from eval.evidence_honesty import (
    CELL_DEFINITIONS,
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
    _fold_geometry,
    _fold_ghost_top,
    _fold_turns,
    _fold_whereabouts,
    _marker_prefixes,
    _resolve_flag,
    _ResolvedFlag,
    _room_distances,
    _SelfLocations,
    _singular_persona_phrase,
    _Tallies,
    cell,
    compute_evidence_honesty,
)
from meetings.manager import INVALID_ACCUSATION_TARGET_MARKER
from meetings.schemas import (
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    WhereaboutsClaim,
)
from orchestrator.replay import LLMCallRecord

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


def test_ghost_top_splits_the_two_sub_populations_and_skips_the_living() -> None:
    tallies = _Tallies()
    _fold_ghost_top(
        tallies=tallies,
        ranked_first=[(20, "p-4"), (20, "p-5"), (20, "p-6")],
        death_tick={"p-4": 10, "p-5": 12, "p-6": 30},
        ejected_at={"p-4": 10},
    )
    assert tallies.ghost_top == 2
    assert (tallies.ghost_top_ejected, tallies.ghost_top_unseen) == (1, 1)


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
    assert ranking_defect.decline_ranking == 1

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


def test_a_planted_policy_mismatch_fails_before_any_cell_is_emitted(
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
        compute_evidence_honesty(_SAMPLES_4P1I)


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
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.crew_false) == (152, 723)
    assert _counts(reports[_CORPUS_9P2I].false_whereabouts.crew_false) == (409, 2038)
    assert _counts(reports[_SAMPLES_4P1I].false_whereabouts.crew_false) == (10, 78)
    assert _counts(reports[_CORPUS_4P1I].false_whereabouts.crew_false) == (16, 79)
    # The strict agent-frame reading of the same rule (engine ticks N-1 and N-2).
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.crew_false_agent_frame) == (
        101,
        723,
    )
    # Impostors lie about their own whereabouts at roughly twice the crew rate
    # (the review: 46-48%), which is what makes the crew cell a defect and not a
    # measure of deception.
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.impostor_false) == (57, 120)
    # Self-placement coverage: how often a rendered self-location row carried the
    # exact (tick, room) pair the claim used.
    assert _counts(reports[_SAMPLES_9P2I].false_whereabouts.copyable_self_location) == (
        84,
        723,
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
    assert per_victim == [(2, 21), (9, 59), (1, 2), (0, 0)]
    assert (sum(n for n, _ in per_victim), sum(d for _, d in per_victim)) == (12, 82)

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
    assert (meetings, ejections, crewmates) == (82, 77, 65)

    # The class impostor share, deduped by subject, against the same meetings'
    # living-voter base rate (the review: 4/47 on samples/9p2i, 28/142 on the
    # corpus, 33/192 pooled vs a 25.3% base rate).
    assert _counts(reports[_SAMPLES_9P2I].sole_flag_precision.class_impostor_share) == (
        4,
        47,
    )
    assert _counts(reports[_CORPUS_9P2I].sole_flag_precision.class_impostor_share) == (
        28,
        142,
    )
    pooled_class = [
        _counts(reports[d].sole_flag_precision.class_impostor_share)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert (sum(n for n, _ in pooled_class), sum(d for _, d in pooled_class)) == (
        33,
        192,
    )
    # The stricter exactly-one-flag reading of the same population, emitted so
    # the choice of "only" stays a measured difference: it returns 8/58 pooled,
    # which is NOT the review's 12/70 wrong split — the kind-sole reading above is.
    single = [
        _counts(reports[d].sole_flag_precision.per_victim_single_flag_precision)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert single == [(1, 14), (6, 42), (1, 2), (0, 0)]
    assert (sum(n for n, _ in single), sum(d for _, d in single)) == (8, 58)

    base = reports[_SAMPLES_9P2I].sole_flag_precision.living_voter_base_rate
    assert _counts(base) == (65, 260)
    assert base.rate == pytest.approx(0.25)


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
    assert sides == [58, 173, 2, 1]
    assert sum(sides) == 234  # the review's own STRONG alibi_vs_sighting count
    assert reports[_SAMPLES_9P2I].grounded_sighting.unresolvable_sides == 0
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_at_tick) == (
        31,
        58,
    )
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_within_1) == (
        36,
        58,
    )
    assert _counts(reports[_SAMPLES_9P2I].grounded_sighting.grounded_within_2) == (
        36,
        58,
    )
    assert _counts(reports[_CORPUS_9P2I].grounded_sighting.grounded_at_tick) == (
        92,
        173,
    )
    assert _counts(reports[_CORPUS_9P2I].grounded_sighting.grounded_within_2) == (
        122,
        173,
    )


@pytest.mark.slow
def test_i5_fabricated_completion_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-3]: 53/529, 140/1528, 15/65, 14/64. This instrument
    # counts the rendered rows that actually REACHED a model — the recorded
    # prompts — while the review re-rendered memory offline. On the 4p1i sets the
    # salience budget never bites and the NUMERATORS reproduce exactly (15 and
    # 14); on the 9p2i sets the budget drops the oldest rows from every prompt, so
    # both halves run lower. The prompt population is the honesty-relevant one: a
    # fabricated row no prompt carried poisoned nobody.
    assert _counts(reports[_SAMPLES_9P2I].fabricated_completions.fabricated) == (
        19,
        458,
    )
    assert _counts(reports[_CORPUS_9P2I].fabricated_completions.fabricated) == (
        40,
        1311,
    )
    assert _counts(reports[_SAMPLES_4P1I].fabricated_completions.fabricated) == (15, 61)
    assert _counts(reports[_CORPUS_4P1I].fabricated_completions.fabricated) == (14, 58)
    # The review disagrees with itself on the samples-pooled count: A/verdicts.md
    # G-3's per-set table sums to 53 + 15 = 68 while D/FINAL-synthesis.md §4 item
    # 2.1 quotes 65. The 68 is the arithmetic of G-3's own published rows and 65
    # has no per-set decomposition anywhere in the review, so 65 is the wrong
    # reading. This instrument's own recount over the prompt population is 34.
    samples_pooled = (
        reports[_SAMPLES_9P2I].fabricated_completions.fabricated.numerator
        + reports[_SAMPLES_4P1I].fabricated_completions.fabricated.numerator
    )
    assert samples_pooled == 34
    # The +1 render calibration, measured rather than assumed.
    calibration = reports[_SAMPLES_4P1I].fabricated_completions
    assert (calibration.render_offset_matches, calibration.render_offset_checked) == (
        46,
        46,
    )


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
    assert per_set == [(38, 58), (108, 173), (1, 2), (1, 1)]
    assert (sum(n for n, _ in per_set), sum(d for _, d in per_set)) == (148, 234)
    assert (
        sum(
            reports[d].adjacent_room_flags.distance_two
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 71
    )
    assert (
        sum(
            reports[d].adjacent_room_flags.distance_three_or_more
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 15
    )
    assert (
        sum(
            reports[d].adjacent_room_flags.single_tick_window
            for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
        )
        == 187
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
    assert per_set == [(7, 76), (30, 233), (0, 3), (1, 1)]
    assert (sum(n for n, _ in per_set), sum(d for _, d in per_set)) == (38, 313)
    truthful = sum(
        reports[d].movement_origin_flags.memory_truthful_spoken_false
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    )
    assert truthful == 38
    assert reports[_SAMPLES_9P2I].movement_origin_flags.backed_by_move_line == 34
    assert reports[_SAMPLES_9P2I].movement_origin_flags.spoke_destination == 27


@pytest.mark.slow
def test_i8_marker_contamination_pins(
    reports: Mapping[Path, EvidenceHonestyReport],
) -> None:
    # Review [A/verdicts.md G-25 (a)]: 53/971 turns and 246/1956 prompts
    # (samples/9p2i), 139/2726 and 671/5502 (ml_corpus/9p2i), zero on both 4p1i
    # sets, 33 / 91 meetings, 25 / 68 games. Every cell reproduces EXACTLY.
    assert _counts(reports[_SAMPLES_9P2I].marker_contamination.turns_with_marker) == (
        53,
        971,
    )
    assert _counts(reports[_SAMPLES_9P2I].marker_contamination.prompts_with_marker) == (
        246,
        1956,
    )
    assert _counts(reports[_CORPUS_9P2I].marker_contamination.turns_with_marker) == (
        139,
        2726,
    )
    assert _counts(reports[_CORPUS_9P2I].marker_contamination.prompts_with_marker) == (
        671,
        5502,
    )
    assert _counts(reports[_SAMPLES_4P1I].marker_contamination.turns_with_marker) == (
        0,
        117,
    )
    assert _counts(reports[_CORPUS_4P1I].marker_contamination.turns_with_marker) == (
        0,
        120,
    )
    assert reports[_SAMPLES_9P2I].marker_contamination.meetings_with_marker == 33
    assert reports[_SAMPLES_9P2I].marker_contamination.games_with_marker == 25
    assert reports[_CORPUS_9P2I].marker_contamination.meetings_with_marker == 91
    assert reports[_CORPUS_9P2I].marker_contamination.games_with_marker == 68


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
    ) == (1956, 1956)
    assert _counts(
        reports[_CORPUS_9P2I].singular_persona.prompts_with_singular_persona
    ) == (5502, 5502)
    assert reports[_SAMPLES_9P2I].singular_persona.applicable is True
    assert reports[_CORPUS_9P2I].singular_persona.applicable is True
    assert reports[_SAMPLES_4P1I].singular_persona.applicable is False
    assert reports[_CORPUS_4P1I].singular_persona.applicable is False
    assert _counts(
        reports[_SAMPLES_4P1I].singular_persona.prompts_with_singular_persona
    ) == (234, 234)


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
    assert venting == [(16, 165), (50, 463), (1, 39), (2, 40)]
    assert (sum(n for n, _ in venting), sum(d for _, d in venting)) == (69, 707)
    killed = [
        _counts(reports[d].meeting_physicality.reporter_killed_within_three)
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert killed == [(27, 165), (75, 463), (5, 39), (4, 40)]
    assert (sum(n for n, _ in killed), sum(d for _, d in killed)) == (111, 707)
    assert reports[_SAMPLES_9P2I].meeting_physicality.body_triggered_meetings == 151


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
    assert checked == [4501, 12667, 409, 436]
    assert sum(checked) == 18_013
    # The action-bearing subset, checked under the two-frame rule rather than
    # dropped: it is where the +1 offset and the action's own room can differ.
    stamped = [
        reports[d].clock_alignment_action_stamped
        for d in (_SAMPLES_9P2I, _CORPUS_9P2I, _SAMPLES_4P1I, _CORPUS_4P1I)
    ]
    assert stamped == [93, 329, 12, 20]
    assert all(count > 0 for count in stamped)


@pytest.mark.slow
def test_render_budget_pins(reports: Mapping[Path, EvidenceHonestyReport]) -> None:
    budget = reports[_SAMPLES_9P2I].render_budget
    assert budget.snapshots == 1956
    # Every rendered memory row, not only the citable ``[obs …]`` half: heard
    # testimony is rendered budget too and a compression lever spends against it.
    assert budget.rendered_lines_total == 99_959
    assert budget.rendered_lines_mean == pytest.approx(51.1038, abs=1e-4)
    assert budget.testimony_rows_total == 18319
    assert dict(budget.testimony_rows_by_living_bucket) == {
        "<=4": 2794,
        "5-6": 11772,
        ">=7": 3753,
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
