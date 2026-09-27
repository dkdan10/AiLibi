"""The regroup relevance window: a sighting there neither clears nor convicts.

Under ``meeting_reset = "hub_with_grace"`` every survivor stands in the meeting
room at the resume tick ``R`` and at most one hop out at ``R + 1``, the shape of
the spawn window. :func:`meetings.transcript.in_regroup_window` marks those two
ticks, and every relevance-gated reader of a transcript takes the same window
from the public regroup ticks it is handed (``regroup_ticks``, empty by
default): the corroboration pairs, the claim-stated and grounded vouches, the
voice backing, the stated paths behind the physical detector, the absent set and
the testimony ledger, and -- the symmetric half -- ``alibi_vs_sighting``
prosecution. The ballot's own-sighting rows leave the window out too. Every case
states the twin with no regroup ticks, where the same sighting still counts, so
each exclusion is shown to bite.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any, Final

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

from meetings.corroboration import build_testimony_ledger
from meetings.manager import (
    MAX_EVIDENCE_ROWS_PER_SUBJECT,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    build_evidence_rows,
    derive_belief_evidence,
    extract_belief_evidence,
)
from meetings.render_contract import EvidenceRow
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    Claim,
    ContradictionRef,
    CorroborationClaim,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VentWitnessRecord,
    VoteBallot,
)
from meetings.transcript import (
    SPAWN_WINDOW_LAST_TICK,
    absent_players,
    detect_contradictions,
    detect_corroborations,
    grounded_vouch_subjects,
    in_regroup_window,
    independent_voices,
    is_relevant_sighting,
    reconstruct_stated_paths,
)
from tests.meetings._manager_helpers import (
    _extract_marker,
    _make_manager,
    _participant,
    _run,
    _ScriptedLLMClient,
    _turn_json,
    _vote_json,
    _vote_prompt,
)

#: A meeting held at tick 11 resumed play at tick 12, so 12 is its regroup tick.
REGROUP: Final[int] = 12
WINDOW: Final[frozenset[int]] = frozenset({REGROUP})
ROSTER: Final[frozenset[str]] = frozenset({"p-1", "p-2", "p-3", "p-4", "p-5"})


def _saw(
    subject: str,
    *,
    tick: int,
    room: str = "CAFETERIA",
    co_present: tuple[str, ...] = (),
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room, co_present=co_present
    )


def _alibi(subject: str, *, room: str, from_tick: int, to_tick: int) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        route=(AlibiSegment(room=room, from_tick=from_tick, to_tick=to_tick),),
    )


def _accuse(target: str) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=target, confidence=0.7, reason="where they stood"
    )


def _turn(
    index: int,
    speaker: str,
    *,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
    kind: str | None = None,
) -> MeetingTurn:
    turn_kind = kind if kind is not None else "opening" if index == 0 else "reply"
    return MeetingTurn(
        turn_id=f"m-1:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
        observations=observations,
        claims=claims,
        free_text=f"turn {index} from {speaker}",
    )


def _transcript(*turns: MeetingTurn) -> MeetingTranscript:
    return MeetingTranscript(turns=turns)


# --------------------------------------------------------------------------- #
# The window and the gate, as properties                                      #
# --------------------------------------------------------------------------- #

_TICKS = st.integers(min_value=0, max_value=60)
_TICK_SETS = st.frozensets(_TICKS, max_size=6)
_ROOMS = st.frozensets(st.sampled_from(("CAFETERIA", "ADMIN", "MEDBAY")), max_size=2)


@settings(deadline=None)
@given(tick=_TICKS, regroup_ticks=_TICK_SETS)
def test_the_window_is_each_regroup_tick_and_the_tick_after(
    tick: int, regroup_ticks: frozenset[int]
) -> None:
    expected = any(tick in (regroup, regroup + 1) for regroup in regroup_ticks)
    assert in_regroup_window(tick, regroup_ticks=regroup_ticks) is expected


@settings(deadline=None)
@given(tick=_TICKS, rooms=_ROOMS, body_rooms=_ROOMS, regroup_ticks=_TICK_SETS)
def test_the_relevance_gate_adds_the_window_and_changes_nothing_else(
    tick: int,
    rooms: frozenset[str],
    body_rooms: frozenset[str],
    regroup_ticks: frozenset[int],
) -> None:
    legacy = tick > SPAWN_WINDOW_LAST_TICK and not (rooms & body_rooms)
    assert (
        is_relevant_sighting(tick=tick, rooms=rooms, triggering_body_rooms=body_rooms)
        is legacy
    )
    windowed = is_relevant_sighting(
        tick=tick,
        rooms=rooms,
        triggering_body_rooms=body_rooms,
        regroup_ticks=regroup_ticks,
    )
    assert windowed is (
        legacy and not in_regroup_window(tick, regroup_ticks=regroup_ticks)
    )


@pytest.mark.parametrize("tick", [0, SPAWN_WINDOW_LAST_TICK])
def test_the_spawn_window_is_unchanged_by_regroup_ticks(tick: int) -> None:
    for regroup_ticks in (frozenset(), WINDOW):
        assert not is_relevant_sighting(
            tick=tick,
            rooms=frozenset({"ADMIN"}),
            triggering_body_rooms=frozenset(),
            regroup_ticks=regroup_ticks,
        )


# --------------------------------------------------------------------------- #
# Corroboration, the vouches and the voices                                   #
# --------------------------------------------------------------------------- #


def _corroborated_alibi(sighting_tick: int) -> MeetingTranscript:
    """``p-2`` stays in CAFETERIA across the regroup; ``p-3`` saw them there."""

    return _transcript(
        _turn(
            0,
            "p-2",
            claims=(
                _alibi(
                    "p-2", room="CAFETERIA", from_tick=REGROUP - 1, to_tick=REGROUP + 2
                ),
            ),
        ),
        _turn(1, "p-3", observations=(_saw("p-2", tick=sighting_tick),)),
    )


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_co_presence_sighting_in_the_window_does_not_corroborate(tick: int) -> None:
    transcript = _corroborated_alibi(tick)
    assert detect_corroborations(transcript, roster=ROSTER, regroup_ticks=WINDOW) == ()
    assert [
        pair.subject for pair in detect_corroborations(transcript, roster=ROSTER)
    ] == ["p-2"]
    windowed = derive_belief_evidence(
        transcript, contradictions=(), roster=ROSTER, regroup_ticks=WINDOW
    )
    plain = derive_belief_evidence(transcript, contradictions=(), roster=ROSTER)
    assert windowed.corroborated == ()
    assert plain.corroborated == ("p-2",)


@pytest.mark.parametrize("tick", [REGROUP - 1, REGROUP + 2])
def test_a_sighting_just_outside_the_window_still_corroborates(tick: int) -> None:
    transcript = _corroborated_alibi(tick)
    assert [
        pair.subject
        for pair in detect_corroborations(
            transcript, roster=ROSTER, regroup_ticks=WINDOW
        )
    ] == ["p-2"]


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_claim_stated_vouch_in_the_window_exculpates_nobody(tick: int) -> None:
    result = MeetingResult(
        meeting_id="m-1",
        triggered_by="p-1",
        trigger_tick=REGROUP + 5,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.5,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            )
            for voter in sorted(ROSTER)
        ),
        transcript=_transcript(
            _turn(
                0,
                "p-3",
                claims=(
                    CorroborationClaim(
                        type="corroboration",
                        supports="p-2",
                        on_tick=tick,
                        reason="with me",
                    ),
                ),
            )
        ),
    )
    assert extract_belief_evidence(result, regroup_ticks=WINDOW).corroborated == ()
    assert extract_belief_evidence(result).corroborated == ("p-2",)


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_grounded_vouch_in_the_window_grounds_nothing(tick: int) -> None:
    transcript = _transcript(_turn(0, "p-3", observations=(_saw("p-2", tick=tick),)))
    records = {"p-3": (SightingRecord(subject="p-2", room="CAFETERIA", tick=tick),)}
    assert (
        grounded_vouch_subjects(
            transcript, sighting_records=records, roster=ROSTER, regroup_ticks=WINDOW
        )
        == frozenset()
    )
    assert grounded_vouch_subjects(
        transcript, sighting_records=records, roster=ROSTER
    ) == frozenset({"p-2"})
    windowed = derive_belief_evidence(
        transcript,
        contradictions=(),
        roster=ROSTER,
        sighting_records=records,
        regroup_ticks=WINDOW,
    )
    plain = derive_belief_evidence(
        transcript, contradictions=(), roster=ROSTER, sighting_records=records
    )
    assert "p-2" not in windowed.corroborated
    assert "p-2" in plain.corroborated


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_sighting_in_the_window_backs_no_voice(tick: int) -> None:
    transcript = _transcript(
        _turn(
            0,
            "p-1",
            observations=(_saw("p-4", tick=tick, room="ADMIN"),),
            claims=(_accuse("p-2"),),
        )
    )
    assert independent_voices(transcript, roster=ROSTER, regroup_ticks=WINDOW) == {}
    assert independent_voices(transcript, roster=ROSTER) == {"p-2": ("p-1",)}
    assert (
        derive_belief_evidence(
            transcript, contradictions=(), roster=ROSTER, regroup_ticks=WINDOW
        ).pre_vote_informed
        == ()
    )
    assert derive_belief_evidence(
        transcript, contradictions=(), roster=ROSTER
    ).pre_vote_informed == ("p-2",)


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_witnessed_vent_in_the_window_still_backs_a_voice(tick: int) -> None:
    # A vent is witness-gated when it happens, so the regroup after it cannot
    # empty it: the vent branch keeps the spawn test only.
    transcript = _transcript(
        _turn(
            0,
            "p-1",
            observations=(
                SawVentObservation(
                    type="saw_vent", tick=tick, subject="p-2", room="ADMIN"
                ),
            ),
            claims=(_accuse("p-2"),),
        )
    )
    assert independent_voices(transcript, roster=ROSTER, regroup_ticks=WINDOW) == {
        "p-2": ("p-1",)
    }


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_a_placement_in_the_window_places_nobody(tick: int) -> None:
    transcript = _transcript(_turn(0, "p-1", observations=(_saw("p-2", tick=tick),)))
    assert "p-2" in absent_players(transcript, roster=ROSTER, regroup_ticks=WINDOW)
    assert "p-2" not in absent_players(transcript, roster=ROSTER)
    assert (
        reconstruct_stated_paths(transcript, roster=ROSTER, regroup_ticks=WINDOW) == {}
    )
    assert "p-2" in reconstruct_stated_paths(transcript, roster=ROSTER)
    windowed = derive_belief_evidence(
        transcript, contradictions=(), roster=ROSTER, regroup_ticks=WINDOW
    )
    plain = derive_belief_evidence(transcript, contradictions=(), roster=ROSTER)
    assert "p-2" in windowed.absent
    assert "p-2" not in plain.absent


# --------------------------------------------------------------------------- #
# The symmetric half: prosecution                                             #
# --------------------------------------------------------------------------- #


def _envelope_alibi_contradicted_at(tick: int) -> MeetingTranscript:
    """``p-2`` claims ADMIN across the regroup; ``p-3`` saw them in CAFETERIA."""

    return _transcript(
        _turn(
            0,
            "p-2",
            claims=(
                _alibi("p-2", room="ADMIN", from_tick=REGROUP - 3, to_tick=REGROUP + 3),
            ),
        ),
        _turn(1, "p-3", observations=(_saw("p-2", tick=tick),)),
    )


def _kinds(flags: tuple[object, ...]) -> list[str]:
    return [getattr(flag, "kind") for flag in flags]


@pytest.mark.parametrize("tick", [REGROUP, REGROUP + 1])
def test_an_envelope_alibi_spanning_a_regroup_is_not_prosecuted_in_the_window(
    tick: int,
) -> None:
    transcript = _envelope_alibi_contradicted_at(tick)
    windowed = detect_contradictions(transcript, roster=ROSTER, regroup_ticks=WINDOW)
    plain = detect_contradictions(transcript, roster=ROSTER)
    assert "alibi_vs_sighting" not in _kinds(windowed)
    assert _kinds(plain) == ["alibi_vs_sighting"]


def test_a_contradiction_outside_the_window_is_still_prosecuted() -> None:
    transcript = _envelope_alibi_contradicted_at(REGROUP + 2)
    assert _kinds(
        detect_contradictions(transcript, roster=ROSTER, regroup_ticks=WINDOW)
    ) == ["alibi_vs_sighting"]


def test_a_proxy_retarget_is_not_minted_from_a_window_sighting() -> None:
    # A proxy alibi about p-2, the sighting at R, and p-2's own account agreeing
    # with the sighting: outside the window this re-targets a weak flag at the
    # proxy speaker; inside it nothing is minted at all.
    transcript = _transcript(
        _turn(
            0,
            "p-4",
            claims=(
                _alibi("p-2", room="ADMIN", from_tick=REGROUP - 3, to_tick=REGROUP + 3),
            ),
        ),
        _turn(1, "p-3", observations=(_saw("p-2", tick=REGROUP),)),
        _turn(
            2,
            "p-2",
            claims=(
                _alibi("p-2", room="CAFETERIA", from_tick=REGROUP, to_tick=REGROUP),
            ),
        ),
    )
    assert "alibi_vs_sighting" in _kinds(
        detect_contradictions(transcript, roster=ROSTER)
    )
    assert "alibi_vs_sighting" not in _kinds(
        detect_contradictions(transcript, roster=ROSTER, regroup_ticks=WINDOW)
    )


def test_co_presence_in_the_window_cannot_physically_contradict_an_alibi() -> None:
    # Two independent speakers each place p-2 in their company in CAFETERIA at
    # R, against p-2's own ADMIN account: the physical detector's two-source
    # conjunction outside the window, nothing inside it.
    transcript = _transcript(
        _turn(
            0,
            "p-2",
            claims=(
                _alibi("p-2", room="ADMIN", from_tick=REGROUP - 3, to_tick=REGROUP + 3),
            ),
        ),
        _turn(
            1,
            "p-3",
            observations=(_saw("p-4", tick=REGROUP, co_present=("p-2",)),),
        ),
        _turn(
            2,
            "p-5",
            observations=(_saw("p-1", tick=REGROUP, co_present=("p-2",)),),
        ),
    )
    assert "alibi_vs_physical" in _kinds(
        detect_contradictions(transcript, roster=ROSTER)
    )
    assert "alibi_vs_physical" not in _kinds(
        detect_contradictions(transcript, roster=ROSTER, regroup_ticks=WINDOW)
    )


def test_a_kill_scene_co_presence_in_the_window_contradicts_nothing() -> None:
    # A report meeting: the opener found a body in CAFETERIA. The kill-scene
    # reconstruction recovers co-presence at the body's room to contradict an
    # alibi placed elsewhere -- but not a placement the regroup made.
    from meetings.schemas import FoundBodyObservation

    transcript = _transcript(
        _turn(
            0,
            "p-1",
            observations=(
                FoundBodyObservation(
                    type="found_body", tick=REGROUP + 1, body_of="p-9", room="CAFETERIA"
                ),
            ),
        ),
        _turn(
            1,
            "p-2",
            claims=(
                _alibi("p-2", room="ADMIN", from_tick=REGROUP - 3, to_tick=REGROUP + 3),
            ),
        ),
        _turn(
            2,
            "p-3",
            observations=(_saw("p-4", tick=REGROUP, co_present=("p-2",)),),
        ),
        _turn(
            3,
            "p-5",
            observations=(_saw("p-1", tick=REGROUP, co_present=("p-2",)),),
        ),
    )
    assert "alibi_vs_physical" in _kinds(
        detect_contradictions(transcript, roster=ROSTER, trigger_kind="report")
    )
    assert "alibi_vs_physical" not in _kinds(
        detect_contradictions(
            transcript, roster=ROSTER, trigger_kind="report", regroup_ticks=WINDOW
        )
    )


def test_the_testimony_ledger_walks_no_transit_through_the_window() -> None:
    transcript = _transcript(
        _turn(0, "p-1", claims=(_accuse("p-2"),)),
        _turn(
            1, "p-3", observations=(_saw("p-2", tick=REGROUP + 1, room="UPPER_HALL"),)
        ),
        _turn(2, "p-4", observations=(_saw("p-2", tick=REGROUP + 2, room="ADMIN"),)),
    )

    def _transits(regroup_ticks: frozenset[int]) -> tuple[tuple[str, str], ...]:
        ledger = build_testimony_ledger(
            transcript,
            contradictions=(),
            sighting_records={},
            move_witness_records={},
            opener="p-1",
            roster=ROSTER,
            regroup_ticks=regroup_ticks,
        )
        (row,) = [row for row in ledger.rows if row.subject == "p-2"]
        return row.walkable_transits

    assert _transits(frozenset()) == (("UPPER_HALL", "ADMIN"),)
    assert _transits(WINDOW) == ()


# --------------------------------------------------------------------------- #
# The ballot's own rows                                                       #
# --------------------------------------------------------------------------- #


def _voter_with_an_early_vent_row() -> MeetingParticipant:
    """``p-1`` saw ``p-2`` vent at tick 5, then saw them seven times, then the regroup."""

    ordinary = tuple(
        SightingRecord(
            subject="p-2", room="ADMIN", tick=tick, observation_id=f"p-1:{tick}:0"
        )
        for tick in range(6, 13)
    )
    regroup_sightings = tuple(
        SightingRecord(
            subject="p-2",
            room="CAFETERIA",
            tick=tick,
            observation_id=f"p-1:{tick}:0",
        )
        for tick in (20, 21)
    )
    return replace(
        _participant("p-1"),
        vent_witness_records=(
            VentWitnessRecord(
                subject="p-2", room="ADMIN", tick=5, observation_id="p-1:5:0"
            ),
        ),
        sighting_records=ordinary + regroup_sightings,
    )


def _own_rows(regroup_ticks: frozenset[int]) -> tuple[EvidenceRow, ...]:
    return build_evidence_rows(
        voter=_voter_with_an_early_vent_row(),
        candidate_targets=("p-2", "p-3"),
        contradictions=(),
        transcript=MeetingTranscript(),
        regroup_ticks=regroup_ticks,
    )


def test_an_early_vent_row_survives_the_budget_past_a_regroup() -> None:
    rows = _own_rows(frozenset({20}))
    kinds = [row.kind for row in rows if row.subject == "p-2"]
    assert kinds.count("own_vent") == 1
    assert kinds.count("own_sighting") == 7
    assert len(kinds) == MAX_EVIDENCE_ROWS_PER_SUBJECT
    assert not any(
        "tick 20" in row.description or "tick 21" in row.description for row in rows
    )


def test_without_the_exclusion_the_regroup_sightings_push_the_vent_row_out() -> None:
    rows = _own_rows(frozenset())
    kinds = [row.kind for row in rows if row.subject == "p-2"]
    assert "own_vent" not in kinds
    assert len(kinds) == MAX_EVIDENCE_ROWS_PER_SUBJECT


def test_a_spawn_window_sighting_row_is_unchanged() -> None:
    voter = replace(
        _participant("p-1"),
        sighting_records=(SightingRecord(subject="p-2", room="CAFETERIA", tick=0),),
    )
    for regroup_ticks in (frozenset(), WINDOW):
        rows = build_evidence_rows(
            voter=voter,
            candidate_targets=("p-2",),
            contradictions=(),
            transcript=MeetingTranscript(),
            regroup_ticks=regroup_ticks,
        )
        assert [row.kind for row in rows] == ["own_sighting"]


# --------------------------------------------------------------------------- #
# The manager threads the window everywhere it detects                        #
# --------------------------------------------------------------------------- #


def _trigger() -> MeetingTrigger:
    return MeetingTrigger(
        triggered_by="p-1",
        trigger_tick=REGROUP + 5,
        description="p-1 called an emergency meeting at tick 17",
        kind="emergency",
    )


class _CapturedVotes:
    """The manager's vote render inputs, captured per voter."""

    def __init__(self) -> None:
        self.evidence_rows: dict[str, tuple[EvidenceRow, ...]] = {}
        self.flags: dict[str, int] = {}

    def __call__(self, **kwargs: object) -> str:
        voter = str(kwargs["voter_id"])
        rows = kwargs.get("evidence_rows", ())
        assert isinstance(rows, tuple)
        self.evidence_rows[voter] = rows
        flags = kwargs["contradiction_flags"]
        assert isinstance(flags, tuple)
        self.flags[voter] = len(flags)
        return _vote_prompt(**kwargs)  # type: ignore[arg-type]


def _responder() -> Callable[[str, type[BaseModel] | None], str]:
    """p-1 opens unsure, p-2 gives an envelope alibi, p-3 saw p-2 at R."""

    def _respond(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=VOTE" in prompt:
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        speaker = _extract_marker(prompt, "agent_id=")
        if speaker == "p-2":
            return _turn_json(
                speaker=speaker,
                claims=(
                    _alibi(
                        "p-2", room="ADMIN", from_tick=REGROUP - 3, to_tick=REGROUP + 3
                    ),
                ),
            )
        if speaker == "p-3":
            return _turn_json(
                speaker=speaker, observations=(_saw("p-2", tick=REGROUP),)
            )
        return _turn_json(speaker=speaker)

    return _respond


def _run_with(
    regroup_ticks: frozenset[int],
) -> tuple[MeetingResult, _CapturedVotes, _ScriptedLLMClient]:
    captured = _CapturedVotes()
    client = _ScriptedLLMClient(responder=_responder())
    manager = _make_manager(llm_client=client, vote_prompt=captured)
    participants = tuple(
        replace(
            _participant(agent_id),
            sighting_records=(
                SightingRecord(subject=other, room="CAFETERIA", tick=REGROUP),
            ),
        )
        for agent_id, other in (
            ("p-1", "p-2"),
            ("p-2", "p-3"),
            ("p-3", "p-2"),
            ("p-4", "p-2"),
        )
    )
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=_trigger(),
            participants=participants,
            regroup_ticks=regroup_ticks,
        )
    )
    return result, captured, client


def test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows() -> None:
    windowed, windowed_votes, windowed_client = _run_with(WINDOW)
    plain, plain_votes, plain_client = _run_with(frozenset())
    # The final flags, what every ballot is handed, and each mid-meeting turn's
    # flag count all read the window.
    assert "alibi_vs_sighting" not in _kinds(windowed.contradictions)
    assert "alibi_vs_sighting" in _kinds(plain.contradictions)
    assert set(windowed_votes.flags.values()) == {0}
    assert set(plain_votes.flags.values()) == {1}
    later_turns = [
        call.prompt
        for call in windowed_client.calls
        if "PHASE=TURN" in call.prompt and "TURNS_COUNT=3" in call.prompt
    ]
    assert later_turns and all("CONTRADICTIONS_COUNT=0" in p for p in later_turns)
    assert any(
        "CONTRADICTIONS_COUNT=1" in call.prompt
        for call in plain_client.calls
        if "PHASE=TURN" in call.prompt and "TURNS_COUNT=3" in call.prompt
    )
    # The voters' own co-presence sightings at R make no ballot row.
    assert not any(
        row.kind == "own_sighting"
        for rows in windowed_votes.evidence_rows.values()
        for row in rows
    )
    assert any(
        row.kind == "own_sighting"
        for rows in plain_votes.evidence_rows.values()
        for row in rows
    )


class _WindowSpy(MeetingManager):
    """A manager that records the regroup ticks every detection receives."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.detections: list[frozenset[int]] = []

    def _detect_contradictions(
        self,
        transcript: MeetingTranscript,
        *,
        regroup_ticks: frozenset[int] = frozenset(),
        **kwargs: Any,
    ) -> tuple[ContradictionRef, ...]:
        self.detections.append(regroup_ticks)
        return super()._detect_contradictions(
            transcript, regroup_ticks=regroup_ticks, **kwargs
        )


def _every_phase_responder() -> Callable[[str, type[BaseModel] | None], str]:
    """p-1 accuses p-2 and places p-4 with them; p-3 charges p-2 again at the roll call.

    So the meeting runs a chain reply (p-2), an opt-in turn (p-4, placed with
    the accused), the roll call (p-3, p-5) and the bounded rebuttal (p-2).
    """

    def _respond(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=VOTE" in prompt:
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        speaker = _extract_marker(prompt, "agent_id=")
        if speaker == "p-1":
            return _turn_json(
                speaker=speaker,
                accuses="p-2",
                observations=(
                    _saw("p-4", tick=REGROUP + 2, room="ADMIN", co_present=("p-2",)),
                ),
            )
        if speaker == "p-3":
            return _turn_json(
                speaker=speaker,
                accuses="p-2",
                observations=(_saw("p-2", tick=REGROUP + 3, room="MEDBAY"),),
            )
        return _turn_json(speaker=speaker)

    return _respond


def test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import meetings.manager as manager_module
    from meetings.evidence_profile import MeetingEvidenceProfile
    from meetings.manager import MeetingConfig
    from tests.meetings._manager_helpers import (
        _crewmate_report_prompt,
        _impostor_report_prompt,
        _statement_prompt,
    )

    received: dict[str, list[frozenset[int]]] = {"evidence": [], "absent": []}

    def _spy(name: str, real: Callable[..., Any]) -> Callable[..., Any]:
        def _call(*args: Any, **kwargs: Any) -> Any:
            received[name].append(kwargs.get("regroup_ticks", frozenset()))
            return real(*args, **kwargs)

        return _call

    monkeypatch.setattr(
        manager_module,
        "derive_belief_evidence",
        _spy("evidence", manager_module.derive_belief_evidence),
    )
    # The manager's name for :func:`meetings.transcript.absent_players`.
    monkeypatch.setattr(
        manager_module, "absent_players", _spy("absent", absent_players)
    )
    manager = _WindowSpy(
        llm_client=_ScriptedLLMClient(responder=_every_phase_responder()),
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=_vote_prompt,
        config=MeetingConfig(),
        evidence_profile=MeetingEvidenceProfile(bounded_rebuttal_version=1),
    )
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=_trigger(),
            participants=tuple(_participant(pid) for pid in sorted(ROSTER)),
            regroup_ticks=WINDOW,
        )
    )
    assert [(turn.speaker, turn.turn_kind) for turn in result.transcript.turns] == [
        ("p-1", "opening"),
        ("p-2", "reply"),
        ("p-4", "opt_in"),
        ("p-3", "opt_in"),
        ("p-5", "opt_in"),
        ("p-2", "reply"),
    ]
    # Chain, opt-in, two roll-call turns, the rebuttal and the final pass.
    assert manager.detections == [WINDOW] * 6
    assert received["evidence"] and set(received["evidence"]) == {WINDOW}
    assert received["absent"] and set(received["absent"]) == {WINDOW}


def _ledger_transits(regroup_ticks: frozenset[int]) -> tuple[tuple[str, str], ...]:
    """The testimony ledger's walkable transits for ``p-2``, with the lever ON.

    ``p-1`` opens accusing ``p-2``; at the roll call ``p-3`` saw ``p-2`` in
    UPPER_HALL on the tick after the regroup and ``p-4`` saw them in ADMIN the
    tick after that.
    """

    from meetings.manager import MeetingConfig, MeetingManager
    from tests.meetings._manager_helpers import (
        _crewmate_report_prompt,
        _impostor_report_prompt,
        _statement_prompt,
    )

    ledgers: list[object] = []

    def _capture(**kwargs: object) -> str:
        ledgers.append(kwargs.get("testimony_ledger"))
        return _vote_prompt(**kwargs)  # type: ignore[arg-type]

    def _respond(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=VOTE" in prompt:
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        speaker = _extract_marker(prompt, "agent_id=")
        seen = {
            "p-3": (_saw("p-2", tick=REGROUP + 1, room="UPPER_HALL"),),
            "p-4": (_saw("p-2", tick=REGROUP + 2, room="ADMIN"),),
        }.get(speaker, ())
        return _turn_json(
            speaker=speaker,
            accuses="p-2" if speaker == "p-1" else None,
            observations=seen,
        )

    manager = MeetingManager(
        llm_client=_ScriptedLLMClient(responder=_respond),
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=_capture,
        config=MeetingConfig(),
        corroboration_discipline=True,
    )
    _run(
        manager.run(
            meeting_id="m-1",
            trigger=_trigger(),
            participants=tuple(
                _participant(pid) for pid in ("p-1", "p-2", "p-3", "p-4")
            ),
            regroup_ticks=regroup_ticks,
        )
    )
    transits: set[tuple[tuple[str, str], ...]] = set()
    for ledger in ledgers:
        assert ledger is not None
        for row in getattr(ledger, "rows"):
            if row.subject == "p-2":
                transits.add(row.walkable_transits)
    (only,) = transits
    return only


def test_the_manager_hands_the_testimony_ledger_the_window() -> None:
    assert _ledger_transits(frozenset()) == (("UPPER_HALL", "ADMIN"),)
    assert _ledger_transits(WINDOW) == ()


@pytest.mark.parametrize("bad", [frozenset({-1}), frozenset({True})])
def test_the_manager_refuses_a_tick_that_is_not_a_non_negative_integer(
    bad: frozenset[int],
) -> None:
    client = _ScriptedLLMClient(responder=_responder())
    manager = _make_manager(llm_client=client)
    with pytest.raises(ValueError, match="regroup ticks must be non-negative integers"):
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_trigger(),
                participants=(_participant("p-1"), _participant("p-2")),
                regroup_ticks=bad,
            )
        )
    assert client.calls == []


@pytest.mark.parametrize(
    ("ticks", "named"),
    [(frozenset({9, -1}), "[-1, 9]"), (frozenset({4, 2, True}), "[True, 2, 4]")],
)
def test_the_manager_refusal_names_the_ticks_it_was_handed(
    ticks: frozenset[int], named: str
) -> None:
    client = _ScriptedLLMClient(responder=_responder())
    manager = _make_manager(llm_client=client)
    with pytest.raises(ValueError) as refused:
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_trigger(),
                participants=(_participant("p-1"), _participant("p-2")),
                regroup_ticks=ticks,
            )
        )
    assert str(refused.value) == f"regroup ticks must be non-negative integers: {named}"
    assert client.calls == []
