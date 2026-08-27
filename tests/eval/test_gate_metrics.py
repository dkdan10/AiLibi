"""Tests for the Task 10.4 Phase-10 gate metrics (DESIGN.md §11.3; gp-7).

Three layers, mirroring the module split:

* **Genuine-class conversion** (:mod:`eval.vote_correctness`) — the phase's
  PRIMARY progress gate. Synthetic fixtures pin the CANON-class definition
  over each meeting's RECORDED ``ContradictionRef`` rows
  (:func:`eval.meeting_quality.recorded_contradiction_flags`): the endpoint
  band disqualifies, the self-stated weak band does NOT (audit D-D-3: a
  fabricated alibi is self-stated by construction), and supplied pairs are
  deduped per (meeting, impostor). ``_meeting`` records what the detector
  emitted over each fixture's transcript, so a fixture is a faithful
  recording unless it deliberately plants otherwise.

* **Gate surface** (:mod:`eval.meeting_quality.GateMetricsReport`) — lost
  opening accusations counted separately from cap-defaulted turns (H-H-5 vs
  H-H-2), and the D-D-2 deception-control survival partition (met /
  sheltered / unevidenced) over the rendered §6.6 suspicion-graph rows.

* **Committed regression pins** — the regenerated reports for BOTH committed
  sets carry the audited values exactly. These pin the e750b40 set (the Task
  9.11 re-record the 2026-06-10 close audit measured) and are NOT immutable:
  Task 10.5's combined re-record regenerates the reports and updates these
  pins, the standard re-record pattern.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.meeting_quality import (
    GateMetricsReport,
    TournamentEvalReport,
    build_tournament_eval_report,
    compute_gate_metrics,
    recorded_contradiction_flags,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from eval.vote_correctness import (
    GENUINE_CLASS_GATE_NOTE,
    SUPPLIED_CHANNEL_GATE_NOTE,
    GenuineClassConversionReport,
    SuppliedChannelConversionReport,
    compute_genuine_class_conversion,
    compute_supplied_channel_conversion,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)
from meetings.transcript import detect_contradictions
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord

# Default roster: p-3 is the impostor, the rest crewmates.
_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_IMPOSTOR: PlayerId = "p-3"
_CREWMATE: PlayerId = "p-1"
_VOTERS: tuple[PlayerId, ...] = ("p-0", "p-1", "p-2", "p-3")


# ---------------------------------------------------------------------------
# Fixture builders — minimal, focused on what the gate metrics actually read
# ---------------------------------------------------------------------------


def _turn(
    *,
    speaker: PlayerId,
    index: int = 0,
    kind: str = "opening",
    observations: tuple[SawPlayerObservation, ...] = (),
    claims: tuple[AlibiClaim | AccusationClaim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-0:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind=kind,  # type: ignore[arg-type]
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text="",
    )


def _alibi(
    *, subject: PlayerId, room: str = "CAFETERIA", from_tick: int = 2, to_tick: int = 8
) -> AlibiClaim:
    return AlibiClaim(
        type="alibi", subject=subject, from_tick=from_tick, to_tick=to_tick, room=room
    )


def _sighting(
    *, subject: PlayerId, room: str = "STORAGE", tick: int = 5
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", subject=subject, tick=tick, room=room
    )


def _accusation(*, against: PlayerId) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=0.9, reason="looked guilty"
    )


def _ballot(*, voter: PlayerId) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target="SKIP",
        confidence=0.5,
        primary_reason_id=None,
        rationale_text="",
    )


def _graph_call(*, agent_id: PlayerId, rows: Mapping[PlayerId, float]) -> LLMCallRecord:
    """A vote-prompt LLM call carrying a rendered §6.6 suspicion graph.

    The prompt body mirrors the committed ``vote_ballot.j2`` render (the
    ``## Your suspicion graph`` header, one backticked row per player, the
    block ending at the next ``## `` header) so the test exercises the same
    parse the committed replays do.
    """

    graph_rows = "".join(
        f"- `{pid}`: suspicion {suspicion:.2f}, trust 0.50\n"
        for pid, suspicion in rows.items()
    )
    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=(f"## Your suspicion graph\n{graph_rows}\n## Decision rules\n"),
        response_text="{}",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _genuine_flag_turns() -> tuple[MeetingTurn, ...]:
    """A transcript the repaired detector flags as genuine CANON-interior.

    The impostor's self-stated alibi (CAFETERIA ticks 2-8) against a
    crewmate's sighting in a disjoint canonical room at an INTERIOR tick (5).
    The flag is weak (self-stated — the D-D-3 band every fabricated alibi
    rides) but carries no endpoint band, so it is exactly the genuine class
    the gate counts.
    """

    return (
        _turn(
            speaker=_IMPOSTOR,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_IMPOSTOR),),
        ),
        _turn(
            speaker=_CREWMATE,
            index=1,
            kind="reply",
            observations=(_sighting(subject=_IMPOSTOR, tick=5),),
        ),
    )


def _meeting(
    *,
    outcome: MeetingOutcome = "SKIPPED",
    ejected: PlayerId | None = None,
    turns: tuple[MeetingTurn, ...] = (),
    voters: tuple[PlayerId, ...] = _VOTERS,
    contradictions: tuple[ContradictionRef, ...] | None = None,
    llm_calls: tuple[LLMCallRecord, ...] = (),
    meeting_id: str = "m-0",
) -> MeetingReport:
    """A resolved meeting whose recorded flags are what the detector emitted.

    The instruments read the RECORDED array, so a fixture that leaves it empty
    while the transcript carries a contradiction is not a recording of anything
    — it is a meeting the record says had no evidence. Recording the detector's
    own output here keeps every fixture a faithful recording of its transcript.
    Pass ``contradictions`` explicitly to record something the transcript alone
    cannot mint (a grounded ``vent_sighting``) or to plant a row that disagrees
    with it.
    """

    ballots = tuple(_ballot(voter=voter) for voter in voters)
    transcript = MeetingTranscript(turns=turns)
    recorded = (
        detect_contradictions(
            transcript, roster=frozenset(ballot.voter for ballot in ballots)
        )
        if contradictions is None
        else contradictions
    )
    return MeetingReport(
        meeting_id=meeting_id,
        tick=40,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=transcript,
        ballots=ballots,
        contradictions=recorded,
        llm_calls=llm_calls,
    )


def _game(
    *,
    meetings: tuple[MeetingReport, ...],
    roles: Mapping[PlayerId, Role] = _ROLES,
    failed_calls: tuple[FailedCallReplayEntry, ...] = (),
    game_id: str = "g-0",
    seed: int = 1,
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=None,
        reason="fixture",
        final_tick=100,
        roles=roles,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=failed_calls,
        prompt_versions={},
        cost=GameCostSummary(
            total_cost_usd=0.0,
            total_input_tokens=0,
            total_output_tokens=0,
            by_model={},
        ),
    )


def _tournament(*games: GameReport) -> TournamentReport:
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=games,
        seeds_used=tuple(game.seed for game in games),
    )


def _failed_call(
    *,
    error_type: str = "deadline_default",
    error_message: str,
    meeting_id: str = "m-0",
) -> FailedCallReplayEntry:
    return FailedCallReplayEntry(
        game_id="g-0",
        meeting_id=meeting_id,
        tick=40,
        model="fixture-model",
        prompt_length=0,
        raw_response="",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        error_type=error_type,
        error_message=error_message,
    )


_DEFAULTED_TURN_MESSAGE = (
    "opening turn (turn 0) defaulted (validation); p-1 submitted no turn "
    "after the in-turn retry"
)
_DEFAULTED_VOTE_MESSAGE = "vote defaulted (validation); p-1 submitted no ballot"


# ---------------------------------------------------------------------------
# Genuine-class conversion: the CANON-class definition (Task 10.1 import)
# ---------------------------------------------------------------------------


def test_genuine_interior_flag_naming_impostor_is_supplied_not_converted() -> None:
    """A re-derived CANON-interior impostor flag supplies; a SKIP converts nothing.

    The flag is weak (self-stated — every fabricated alibi is, audit D-D-3),
    which must NOT disqualify it: requiring an unmarked strong flag would
    define the phase gate to zero.
    """

    report = _tournament(_game(meetings=(_meeting(turns=_genuine_flag_turns()),)))

    result = compute_genuine_class_conversion(report)

    assert result.supplied == 1
    assert result.converted == 0
    assert result.conversion_rate == 0.0
    assert result.note == GENUINE_CLASS_GATE_NOTE


def test_genuine_flag_converts_when_that_impostor_is_ejected() -> None:
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    outcome="EJECTED", ejected=_IMPOSTOR, turns=_genuine_flag_turns()
                ),
            )
        )
    )

    result = compute_genuine_class_conversion(report)

    assert result.supplied == 1
    assert result.converted == 1
    assert result.conversion_rate == 1.0


def test_ejecting_someone_else_does_not_convert() -> None:
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    outcome="EJECTED", ejected=_CREWMATE, turns=_genuine_flag_turns()
                ),
            )
        )
    )

    result = compute_genuine_class_conversion(report)

    assert result.supplied == 1
    assert result.converted == 0


def test_malformed_ejected_meeting_cannot_convert() -> None:
    # MeetingReport does not enforce the EJECTED <-> non-None coupling; a
    # malformed EJECTED row with no ejected player supplies but never converts
    # (the vote-correctness partial-replay rule).
    report = _tournament(
        _game(
            meetings=(
                _meeting(outcome="EJECTED", ejected=None, turns=_genuine_flag_turns()),
            )
        )
    )

    result = compute_genuine_class_conversion(report)

    assert result.supplied == 1
    assert result.converted == 0


def test_endpoint_tick_sighting_is_not_genuine_class() -> None:
    """An edge-tick sighting is the endpoint-banded fuzz class, never supplied."""

    turns = (
        _turn(
            speaker=_IMPOSTOR,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_IMPOSTOR, from_tick=2, to_tick=8),),
        ),
        _turn(
            speaker=_CREWMATE,
            index=1,
            kind="reply",
            observations=(_sighting(subject=_IMPOSTOR, tick=8),),
        ),
    )
    report = _tournament(_game(meetings=(_meeting(turns=turns),)))

    result = compute_genuine_class_conversion(report)

    assert result.supplied == 0
    assert result.conversion_rate is None


def test_genuine_flag_naming_a_crewmate_is_not_supplied() -> None:
    """The gate counts impostor-naming flags only (roles ground truth)."""

    turns = (
        _turn(
            speaker=_CREWMATE,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_CREWMATE),),
        ),
        _turn(
            speaker="p-2",
            index=1,
            kind="reply",
            observations=(_sighting(subject=_CREWMATE, tick=5),),
        ),
    )
    report = _tournament(_game(meetings=(_meeting(turns=turns),)))

    assert compute_genuine_class_conversion(report).supplied == 0


def test_supplied_is_deduped_per_meeting_impostor_pair() -> None:
    """N interior sightings against one alibi supply ONCE, not N times.

    The gp-2 flag-fountain lesson applied to the gate's own denominator: a
    verbose meeting must not inflate `supplied` by flag volume.
    """

    turns = (
        _turn(
            speaker=_IMPOSTOR,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_IMPOSTOR),),
        ),
        _turn(
            speaker=_CREWMATE,
            index=1,
            kind="reply",
            observations=(
                _sighting(subject=_IMPOSTOR, tick=4),
                _sighting(subject=_IMPOSTOR, tick=5, room="ADMIN"),
            ),
        ),
    )
    report = _tournament(_game(meetings=(_meeting(turns=turns),)))

    assert compute_genuine_class_conversion(report).supplied == 1


def test_a_recorded_flag_supplies_even_when_the_transcript_cannot_mint_it() -> None:
    """PLANTED: the census is the RECORD, not a re-derivation of the transcript.

    The recording-time detector held the meeting's trigger kind and its three
    private grounding channels; none of them survive into the transcript, so a
    recorded flag whose transcript re-derives to nothing is the common case the
    gate must count — on ``replays/ml_corpus/9p2i`` the re-derivation loses 43
    of the 120 recorded non-vent flags. This meeting records exactly one such
    flag over an empty transcript: it supplies iff the reader is the record.
    """

    grounded = ContradictionRef(
        contradiction_id="c-grounded",
        kind="alibi_vs_sighting",
        event_a_id="alibi:x",
        event_b_id="saw:x",
        subjects=(_IMPOSTOR,),
        description="recorded against the speaker's private sighting record",
    )
    report = _tournament(
        _game(meetings=(_meeting(turns=(), contradictions=(grounded,)),))
    )

    assert compute_genuine_class_conversion(report).supplied == 1


def test_a_recorded_vent_flag_never_enters_the_transcript_census() -> None:
    """PLANTED: the vent class rides its own term and is filtered out here.

    Dropping the ``vent_sighting`` filter from the shared reader would double
    count every vent flag wherever a consumer merges the two terms, so the
    filter is asserted at the reader's own boundary, not only downstream.
    """

    vent = ContradictionRef(
        contradiction_id="c-vent",
        kind="vent_sighting",
        event_a_id="vent:x",
        event_b_id="vent:x",
        subjects=(_IMPOSTOR,),
        description="witnessed vent, grounded by the speaker's vent record",
    )
    meeting = _meeting(turns=(), contradictions=(vent,))

    assert recorded_contradiction_flags(meeting) == ()
    assert (
        compute_genuine_class_conversion(
            _tournament(_game(meetings=(meeting,)))
        ).supplied
        == 0
    )


def test_strong_alibi_conflict_is_not_the_genuine_class() -> None:
    """The gate is the CANON-interior SIGHTING channel (audit C-C-6).

    Two independent speakers stating irreconcilable alibis about the impostor
    re-derive a strong ``alibi_conflict`` — a different evidence channel that
    never produced a genuine impostor flag in either audited era, so it does
    not feed the supplied denominator (see the PR's ## Decisions block).
    """

    turns = (
        _turn(
            speaker=_CREWMATE,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_IMPOSTOR, room="CAFETERIA"),),
        ),
        _turn(
            speaker="p-2",
            index=1,
            kind="reply",
            claims=(_alibi(subject=_IMPOSTOR, room="STORAGE"),),
        ),
    )
    report = _tournament(_game(meetings=(_meeting(turns=turns),)))

    assert compute_genuine_class_conversion(report).supplied == 0


def test_meeting_with_no_ballots_supplies_nothing() -> None:
    """No ballots == an explicitly-empty living roster: the detector indexes
    nothing (the recording path always writes one ballot per living
    participant, so this arises only on hand-built partial data)."""

    report = _tournament(
        _game(meetings=(_meeting(turns=_genuine_flag_turns(), voters=()),))
    )

    assert compute_genuine_class_conversion(report).supplied == 0


def test_genuine_class_model_validators_fail_loud() -> None:
    with pytest.raises(ValidationError, match="non-negative"):
        GenuineClassConversionReport(supplied=-1, converted=0, conversion_rate=None)
    with pytest.raises(ValidationError, match="cannot exceed supplied"):
        GenuineClassConversionReport(supplied=1, converted=2, conversion_rate=1.0)
    with pytest.raises(ValidationError, match="undefined, not 0.0"):
        GenuineClassConversionReport(supplied=0, converted=0, conversion_rate=0.0)
    with pytest.raises(ValidationError, match="must be set"):
        GenuineClassConversionReport(supplied=1, converted=0, conversion_rate=None)
    with pytest.raises(ValidationError, match="in \\[0.0, 1.0\\]"):
        GenuineClassConversionReport(supplied=1, converted=1, conversion_rate=1.5)


# ---------------------------------------------------------------------------
# Lost opening accusations vs cap-defaulted turns (H-H-5 vs H-H-2)
# ---------------------------------------------------------------------------


def test_opening_without_accusation_counts_as_lost() -> None:
    with_accusation = _meeting(
        turns=(
            _turn(speaker="p-0", index=0, claims=(_accusation(against=_IMPOSTOR),)),
        ),
        meeting_id="m-0",
    )
    without_accusation = _meeting(
        turns=(_turn(speaker="p-0", index=0),), meeting_id="m-1"
    )
    empty_transcript = _meeting(turns=(), meeting_id="m-2")
    report = _tournament(
        _game(meetings=(with_accusation, without_accusation, empty_transcript))
    )

    result = compute_gate_metrics(report)

    # The accusation-bearing opening is not lost; the bare opening and the
    # empty transcript both are (an absent opening vacuously supplied no
    # accusation — the chain died on turn 0 either way).
    assert result.lost_opening_accusations == 2


def test_accusation_on_a_later_turn_does_not_save_the_opening() -> None:
    """Lost-opening reads turn 0 only: a later reply's accusation is a
    different (chain-recovery) event, not an opening accusation."""

    meeting = _meeting(
        turns=(
            _turn(speaker="p-0", index=0),
            _turn(
                speaker="p-1",
                index=1,
                kind="reply",
                claims=(_accusation(against=_IMPOSTOR),),
            ),
        )
    )
    report = _tournament(_game(meetings=(meeting,)))

    assert compute_gate_metrics(report).lost_opening_accusations == 1


def test_cap_defaults_count_distinct_turn_defaults_only() -> None:
    """Turn defaults count once per coordinate; vote defaults are not turns."""

    failed_calls = (
        _failed_call(error_message=_DEFAULTED_TURN_MESSAGE),
        # A byte-identical second row for the same defaulted turn (the
        # pre-9.10 duplicate shape, or one row per burned parse-failure
        # call) must not double-count.
        _failed_call(error_message=_DEFAULTED_TURN_MESSAGE),
        _failed_call(error_message=_DEFAULTED_VOTE_MESSAGE),
        # Non-default failure kinds (e.g. a schema-validation abort) are not
        # cap-defaults at all.
        _failed_call(error_type="ValidationError", error_message="bad payload"),
    )
    report = _tournament(_game(meetings=(), failed_calls=failed_calls))

    result = compute_gate_metrics(report)

    assert result.cap_defaulted_turns == 1


def test_unclassifiable_deadline_default_row_fails_loud() -> None:
    report = _tournament(
        _game(
            meetings=(),
            failed_calls=(_failed_call(error_message="some foreign message shape"),),
        )
    )

    with pytest.raises(ValueError, match="unclassifiable deadline_default"):
        compute_gate_metrics(report)


# ---------------------------------------------------------------------------
# Accused-impostor survival: the D-D-2 deception-control partition
# ---------------------------------------------------------------------------


def _accused_meeting(
    *,
    outcome: MeetingOutcome = "SKIPPED",
    ejected: PlayerId | None = None,
    extra_turns: tuple[MeetingTurn, ...] = (),
    llm_calls: tuple[LLMCallRecord, ...] = (),
) -> MeetingReport:
    """A meeting where a crewmate accuses the impostor on the opening turn."""

    turns = (
        _turn(speaker="p-0", index=0, claims=(_accusation(against=_IMPOSTOR),)),
        *extra_turns,
    )
    return _meeting(outcome=outcome, ejected=ejected, turns=turns, llm_calls=llm_calls)


def test_accused_impostor_ejection_is_an_event_but_not_a_survival() -> None:
    report = _tournament(
        _game(meetings=(_accused_meeting(outcome="EJECTED", ejected=_IMPOSTOR),))
    )

    result = compute_gate_metrics(report)

    assert result.accused_impostor_events == 1
    assert result.accused_impostor_survivals == 0


def test_self_accusation_is_not_crew_pressure() -> None:
    """An impostor naming themselves is excluded from the deception-control
    denominator (stricter than the recall lead's self-inclusive convention —
    the audited 55-event denominator)."""

    meeting = _meeting(
        turns=(
            _turn(speaker=_IMPOSTOR, index=0, claims=(_accusation(against=_IMPOSTOR),)),
        )
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.accused_impostor_events == 0
    assert result.accused_impostor_survivals == 0


def test_accused_crewmate_is_not_an_event() -> None:
    meeting = _meeting(
        turns=(_turn(speaker="p-0", index=0, claims=(_accusation(against=_CREWMATE),)),)
    )
    report = _tournament(_game(meetings=(meeting,)))

    assert compute_gate_metrics(report).accused_impostor_events == 0


def test_survivor_rendered_over_gate_is_under_conversion_not_deception() -> None:
    """A met-threshold render on a survivor is a CREW conversion failure —
    counting it as deception is the exact misread D-D-2 warns against."""

    meeting = _accused_meeting(
        llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.70}),)
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.accused_impostor_survivals == 1
    assert result.survivals_rendered_met == 1
    assert result.survivals_sheltered_sub_gate == 0
    assert result.survivals_unevidenced == 0


def test_met_threshold_wins_over_the_shelter_test() -> None:
    """An over-gate survivor with flags is still under-conversion: the table
    was handed a met verdict AND a flag and converted neither (the audit's
    (a)-bucket gate-crossers)."""

    meeting = _accused_meeting(
        extra_turns=_genuine_flag_turns(),
        llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.78}),),
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.survivals_rendered_met == 1
    assert result.survivals_sheltered_sub_gate == 0


def test_sub_gate_survivor_with_rederived_flag_is_sheltered() -> None:
    """Rendered below the gate AND actively flagged == the weak band genuinely
    sheltered them — the conversion-controlled deception-credit count."""

    meeting = _accused_meeting(
        extra_turns=_genuine_flag_turns(),
        llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.58}),),
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.accused_impostor_survivals == 1
    assert result.survivals_rendered_met == 0
    assert result.survivals_sheltered_sub_gate == 1
    assert result.survivals_unevidenced == 0


def test_sub_gate_survivor_without_flags_is_unevidenced() -> None:
    """Sub-gate with no detector challenge is evidence starvation, not
    deception (the audit's accusation-bump-only survivors, seeds 6/10)."""

    meeting = _accused_meeting(
        llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.55}),)
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.survivals_unevidenced == 1
    assert result.survivals_sheltered_sub_gate == 0


def test_unrendered_survivor_is_unevidenced_even_with_flags() -> None:
    """No rendered row at all == nobody held a verdict to act on; a flag
    cannot shelter a verdict that was never rendered."""

    meeting = _accused_meeting(extra_turns=_genuine_flag_turns())
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.accused_impostor_survivals == 1
    assert result.survivals_unevidenced == 1
    assert result.survivals_sheltered_sub_gate == 0


def test_a_voters_own_graph_row_never_renders_them() -> None:
    """The rendered value comes from OTHER voters' prompts: a row about the
    impostor inside the impostor's OWN prompt contributes nothing (a voter
    holds no row about itself in production; the parse enforces it)."""

    meeting = _accused_meeting(
        llm_calls=(_graph_call(agent_id=_IMPOSTOR, rows={_IMPOSTOR: 0.95}),)
    )
    report = _tournament(_game(meetings=(meeting,)))

    result = compute_gate_metrics(report)

    assert result.survivals_rendered_met == 0
    assert result.survivals_unevidenced == 1


def test_gate_metrics_model_validators_fail_loud() -> None:
    genuine = GenuineClassConversionReport(
        supplied=0, converted=0, conversion_rate=None
    )
    # The Task-19.5 successor cell, all-zero. ``note`` / ``legacy_note`` are
    # omitted on purpose so the pinned documentation strings stay one-home on
    # the model's defaults rather than being restated here.
    supplied_channel = SuppliedChannelConversionReport(
        supplied=0,
        converted=0,
        conversion_rate=None,
        witnessed_vent_supplied=0,
        witnessed_vent_converted=0,
        sighting_contradiction_supplied=0,
        sighting_contradiction_converted=0,
        whereabouts_lie_supplied=0,
        whereabouts_lie_converted=0,
        legacy_alibi_supplied=0,
        legacy_alibi_converted=0,
        legacy_alibi_conversion_rate=None,
    )
    with pytest.raises(ValidationError, match="non-negative"):
        GateMetricsReport(
            genuine_class_conversion=genuine,
            supplied_channel_conversion=supplied_channel,
            lost_opening_accusations=-1,
            cap_defaulted_turns=0,
            accused_impostor_events=0,
            accused_impostor_survivals=0,
            survivals_rendered_met=0,
            survivals_sheltered_sub_gate=0,
            survivals_unevidenced=0,
        )
    with pytest.raises(ValidationError, match="cannot exceed accused_impostor_events"):
        GateMetricsReport(
            genuine_class_conversion=genuine,
            supplied_channel_conversion=supplied_channel,
            lost_opening_accusations=0,
            cap_defaulted_turns=0,
            accused_impostor_events=1,
            accused_impostor_survivals=2,
            survivals_rendered_met=2,
            survivals_sheltered_sub_gate=0,
            survivals_unevidenced=0,
        )
    with pytest.raises(
        ValidationError, match="must equal\\s+accused_impostor_survivals"
    ):
        GateMetricsReport(
            genuine_class_conversion=genuine,
            supplied_channel_conversion=supplied_channel,
            lost_opening_accusations=0,
            cap_defaulted_turns=0,
            accused_impostor_events=3,
            accused_impostor_survivals=3,
            survivals_rendered_met=1,
            survivals_sheltered_sub_gate=0,
            survivals_unevidenced=1,
        )


def test_wrapper_packs_gate_metrics_from_the_owning_analyzers() -> None:
    """``build_tournament_eval_report`` bundles the gate block (no inline math)
    and the result round-trips through JSON like every other wrapper field."""

    report = _tournament(
        _game(
            meetings=(
                _accused_meeting(
                    extra_turns=_genuine_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.58}),),
                ),
            )
        )
    )

    evaluated = build_tournament_eval_report(report)

    assert evaluated.gate_metrics == compute_gate_metrics(report)
    assert evaluated.gate_metrics.genuine_class_conversion == (
        compute_genuine_class_conversion(report)
    )
    # Task 19.5: the successor cell is packed from its owning analyzer too —
    # one home, no inline re-derivation inside the wrapper.
    assert evaluated.gate_metrics.supplied_channel_conversion == (
        compute_supplied_channel_conversion(report)
    )
    restored = TournamentEvalReport.model_validate_json(evaluated.model_dump_json())
    assert restored == evaluated


# ---------------------------------------------------------------------------
# Committed regression pins — the e750b40 set; Task 10.5's re-record updates
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).resolve().parents[2] / "replays" / "samples"
# The flat 4p1i report now lives under replays/samples/4p1i/ (Task 12.12).
_COMMITTED_FLAT_REPORT = _SAMPLES_DIR / "4p1i" / "tournament-eval-report.json"
_COMMITTED_9P2I_REPORT = _SAMPLES_DIR / "9p2i" / "tournament-eval-report.json"


def _load_committed(path: Path) -> TournamentEvalReport:
    return TournamentEvalReport.model_validate_json(path.read_text(encoding="utf-8"))


def test_committed_9p2i_report_pins_the_audited_gate_metrics() -> None:
    """The shipped 9p/2i report carries the recorded gp-7 gate values exactly.

    These pin the baseline-6 Qwen/Qwen3.6-27B (prompt set qwen3_6_27b.v3, all
    four templates, the substrate levers ON) re-record and are NOT
    immutable — the next re-record regenerates the report and updates these
    pins, the standard re-record pattern.

    Recorded values: genuine-class 3 converted / 4 supplied — on the baseline-6
    model/set the genuine (interior, non-proxy) impostor-subject flag class has
    instances again (the transcript contradiction channel is live), so the
    PRIMARY gate reads 0.75; lost openings 0 against 0 cap-defaulted turns;
    accused-impostor survival 70/148 with the partition 34 rendered-met + 0
    sheltered + 36 unevidenced.

    Task 19.5 wires the Task-17.6 successor onto the same surface, so this also
    pins the CANARY cell ``supplied_channel_conversion``: 70 converted / 79
    supplied (rate ~0.8861), the union of witnessed vents (76/68), sighting
    contradictions (2/2) and whereabouts-lies (7/5), with the starved legacy
    alibi-anchored column riding along at 3/4.
    """

    report = _load_committed(_COMMITTED_9P2I_REPORT)
    gate = report.gate_metrics
    genuine = gate.genuine_class_conversion

    assert genuine.supplied == 1  # was 4
    assert genuine.converted == 0  # was 3
    assert genuine.conversion_rate == 0.0  # was 0.75
    assert genuine.note == GENUINE_CLASS_GATE_NOTE

    # The Task-19.5 canary cell: the successor instrument the canary bands read.
    supplied_channel = gate.supplied_channel_conversion
    assert supplied_channel.supplied == 76  # was 79
    assert supplied_channel.converted == 69  # was 70
    assert supplied_channel.conversion_rate == pytest.approx(69 / 76)  # was 70 / 79
    assert supplied_channel.witnessed_vent_supplied == 74  # was 76
    assert supplied_channel.witnessed_vent_converted == 69  # was 68
    assert supplied_channel.sighting_contradiction_supplied == 0  # was 2
    assert supplied_channel.sighting_contradiction_converted == 0  # was 2
    assert supplied_channel.whereabouts_lie_supplied == 5  # was 7
    assert supplied_channel.whereabouts_lie_converted == 2  # was 5
    # The preserved legacy column mirrors the genuine-class cell above.
    assert supplied_channel.legacy_alibi_supplied == 1  # was 4
    assert supplied_channel.legacy_alibi_converted == 0  # was 3
    assert supplied_channel.legacy_alibi_conversion_rate == pytest.approx(
        0.0
    )  # was 0.75
    assert supplied_channel.note == SUPPLIED_CHANNEL_GATE_NOTE

    assert gate.lost_opening_accusations == 0
    assert gate.cap_defaulted_turns == 0

    assert gate.accused_impostor_events == 137  # was 148
    assert gate.accused_impostor_survivals == 52  # was 70
    # The 70 accused-impostor survivals partition into rendered-met (voters saw a
    # §4.6-gate-meeting suspicion yet the impostor survived), sheltered sub-gate,
    # and unevidenced. On the baseline-6 re-record the sheltered class is empty, so
    # survivors split rendered-met (34), sheltered (0), and unevidenced (36), the
    # largest share still unevidenced.
    assert gate.survivals_rendered_met == 18  # was 34
    assert gate.survivals_sheltered_sub_gate == 0
    assert gate.survivals_unevidenced == 34  # was 36

    # Per-seed identities RE-DERIVED from the same committed games. Everything
    # above is read from the committed sidecar, which was built by the old
    # record-free census and is not rebuilt here (Task 21.15 rebuilds it), so
    # the two sides no longer agree and the fold is the corrected reading: the
    # sidecar's one genuine-class supply was a flag the transcript-only
    # re-derivation minted and the record never carried, so on the recorded
    # census no seed supplies at all. There are no lost openings and no
    # sheltered survivals on these bytes either, so those fold to empty too.
    supplied_seeds = {
        game.seed
        for game in report.report.games
        if compute_genuine_class_conversion((game,)).supplied > 0
    }
    assert supplied_seeds == set()  # was {26} — the sidecar's re-derived flag
    converted_seeds = {
        game.seed
        for game in report.report.games
        if compute_genuine_class_conversion((game,)).converted > 0
    }
    assert converted_seeds == set()
    lost_opening_seeds = {
        game.seed
        for game in report.report.games
        if compute_gate_metrics((game,)).lost_opening_accusations > 0
    }
    assert lost_opening_seeds == set()
    sheltered_seeds = {
        game.seed
        for game in report.report.games
        if compute_gate_metrics((game,)).survivals_sheltered_sub_gate > 0
    }
    assert sheltered_seeds == set()

    # JSON-level guard: the committed file itself serves the gate surface and
    # the era-invalidity note (a reader pulling the raw report sees the
    # PRIMARY gate and the warning, the gp-7 ask).
    raw = json.loads(_COMMITTED_9P2I_REPORT.read_text(encoding="utf-8"))
    assert raw["gate_metrics"]["genuine_class_conversion"]["supplied"] == 1
    assert raw["gate_metrics"]["genuine_class_conversion"]["converted"] == 0
    assert (
        "ejection_accuracy" in raw["gate_metrics"]["genuine_class_conversion"]["note"]
    )
    assert "INVALID" in raw["gate_metrics"]["genuine_class_conversion"]["note"]
    # ... and the Task-19.5 successor beside it, carrying its canary label.
    assert raw["gate_metrics"]["supplied_channel_conversion"]["supplied"] == 76
    assert (
        "canary-eligible" in raw["gate_metrics"]["supplied_channel_conversion"]["note"]
    )


def test_committed_flat_4p1i_report_pins_the_gate_metrics() -> None:
    """The flat 4p/1i set's gate block, pinned at the baseline-6 Qwen/Qwen3.6-27B
    (prompt set qwen3_6_27b.v3, all four templates, the substrate levers ON)
    re-record.

    NOT immutable — the next re-record regenerates and updates these. On the
    baseline-6 model/set the genuine (interior, non-proxy) impostor-subject flag
    class has one instance, so the set supplies 1 genuine-class flag and
    converts 1 (rate 1.0), loses 0 openings and defaults 0 turns, and its 22
    accused-impostor survivals split 3 rendered-met / 0 sheltered / 19 unevidenced.

    Task 19.5 wires the Task-17.6 successor onto the same surface, so this also
    pins the CANARY cell ``supplied_channel_conversion``: 10 converted / 11
    supplied (rate ~0.9091), the union of witnessed vents (10/9) and sighting
    contradictions (1/1) — this set supplies no whereabouts-lie (0/0) — with the
    starved legacy alibi-anchored column riding along at 1/1.
    """

    report = _load_committed(_COMMITTED_FLAT_REPORT)
    gate = report.gate_metrics
    genuine = gate.genuine_class_conversion

    assert genuine.supplied == 0  # was 1
    assert genuine.converted == 0  # was 1
    assert genuine.conversion_rate is None
    assert genuine.note == GENUINE_CLASS_GATE_NOTE

    # The Task-19.5 canary cell: the successor instrument the canary bands read.
    supplied_channel = gate.supplied_channel_conversion
    assert supplied_channel.supplied == 19
    assert supplied_channel.converted == 19
    assert supplied_channel.conversion_rate == pytest.approx(1 / 1)  # was 10 / 11
    assert supplied_channel.witnessed_vent_supplied == 19  # was 10
    assert supplied_channel.witnessed_vent_converted == 19  # was 9
    assert supplied_channel.sighting_contradiction_supplied == 0  # was 1
    assert supplied_channel.sighting_contradiction_converted == 0  # was 1
    assert supplied_channel.whereabouts_lie_supplied == 0
    assert supplied_channel.whereabouts_lie_converted == 0
    # The preserved legacy column mirrors the genuine-class cell above.
    assert supplied_channel.legacy_alibi_supplied == 0  # was 1
    assert supplied_channel.legacy_alibi_converted == 0  # was 1
    assert supplied_channel.legacy_alibi_conversion_rate == pytest.approx(None)
    assert supplied_channel.note == SUPPLIED_CHANNEL_GATE_NOTE

    assert gate.lost_opening_accusations == 0
    assert gate.cap_defaulted_turns == 0

    assert gate.accused_impostor_events == 35
    assert gate.accused_impostor_survivals == 15
    assert gate.survivals_rendered_met == 1
    assert gate.survivals_sheltered_sub_gate == 0
    assert gate.survivals_unevidenced == 14

    # JSON-level guard, mirroring the 9p2i pin above: the committed file itself
    # serves the successor cell with its canary label.
    raw = json.loads(_COMMITTED_FLAT_REPORT.read_text(encoding="utf-8"))
    assert raw["gate_metrics"]["supplied_channel_conversion"]["supplied"] == 19
    assert (
        "canary-eligible" in raw["gate_metrics"]["supplied_channel_conversion"]["note"]
    )
