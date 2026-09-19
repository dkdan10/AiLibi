"""Planted cases for every row of the process scorecard.

Each row of :mod:`eval.process_scorecard` is pinned by a PAIR of planted shapes
that differ in exactly the thing the row's published definition names, so a test
that passes proves the definition is the one the code computes rather than that
some number came out. Nothing here walks a committed replay set: the fold is
pure over a :class:`~eval.process_scorecard.SetInputs`, so a two-meeting game and
a three-tick route built by hand exercise every branch at no cost. The committed
pins live in ``tests/scripts/test_process_scorecard.py``, where ``--check``
recomputes the published artifact from the recordings themselves.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.process_scorecard import (
    ROLE_CORRECTNESS_NOTE,
    ROW_DEFINITIONS,
    ContextCells,
    ProcessTally,
    RateCell,
    SetInputs,
    SetScorecard,
    fold_set,
    pool,
    scorecard_from_tally,
)
from eval.report_schema import GameCostSummary, GameReport, MeetingReport
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_REASON_ID_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    BallotTargetRewriteReason,
    ContradictionRef,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    RoomId,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.replay import LLMCallRecord

_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_ROOMS: tuple[RoomId, ...] = ("CAFETERIA", "EAST_HALL", "ENGINEERING", "STORAGE")
_EMPTY_CONTEXT = ContextCells(
    impostor_alibis=0,
    impostor_alibis_survived=0,
    impostor_alibi_survival_rate=None,
    reporter_slots=0,
    reporter_ejections=0,
    innocent_non_reporter_slots=0,
    innocent_non_reporter_ejections=0,
)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _turn(
    *,
    speaker: PlayerId,
    index: int = 0,
    observations: tuple[SawPlayerObservation, ...] = (),
    claims: tuple[AlibiClaim | AccusationClaim, ...] = (),
    free_text: str = "",
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-0:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=free_text,
    )


def _alibi(
    *, subject: PlayerId, room: RoomId, from_tick: int, to_tick: int
) -> AlibiClaim:
    return AlibiClaim(
        type="alibi", subject=subject, from_tick=from_tick, to_tick=to_tick, room=room
    )


def _flag(
    *, subjects: tuple[PlayerId, ...], kind: str = "alibi_vs_sighting"
) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id=f"c-{'-'.join(subjects)}-{kind}",
        kind=kind,  # type: ignore[arg-type]
        event_a_id="a",
        event_b_id="b",
        subjects=subjects,
        description="",
    )


def _ballot(
    *,
    voter: PlayerId,
    target: str,
    reason_id: str | None = None,
    observation_id: str | None = None,
    alternatives: tuple[PlayerId, ...] = (),
    rationale: str = "",
    rewrite_reason: BallotTargetRewriteReason | None = None,
    redirected_from: str | None = None,
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.6,
        primary_reason_id=reason_id,
        primary_reason_observation_id=observation_id,
        considered_alternatives=alternatives,
        rationale_text=rationale,
        guard_redirected_from=redirected_from,
        guard_rewrite_reason=rewrite_reason,
    )


def _prompt(
    *,
    suspicion: Mapping[PlayerId, float] = {},
    valid: Sequence[PlayerId] = (),
    memory_lines: Sequence[str] = (),
) -> str:
    """A vote prompt carrying the two blocks the offline reader parses.

    The header strings and row shapes are the committed ``vote_ballot.j2``
    literals, which is what makes a planted prompt a fair stand-in for a
    recorded one.
    """

    rows = "".join(
        f"- `{pid}`: suspicion {value:.2f}, trust 0.50\n"
        for pid, value in suspicion.items()
    )
    listed = ", ".join(f"`{pid}`" for pid in valid)
    memory = "\n".join(memory_lines)
    return (
        f"## Your memory\n{memory}\n"
        f"## Your suspicion graph\n{rows}\n"
        f'## Valid ejection targets\n{listed} — or "SKIP".\n'
        "## How to decide\n"
    )


def _call(*, agent_id: PlayerId, prompt: str) -> LLMCallRecord:
    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=prompt,
        response_text="{}",
        input_tokens=1,
        output_tokens=1,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _meeting(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    ballots: tuple[VoteBallot, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    calls: tuple[LLMCallRecord, ...] = (),
    outcome: MeetingOutcome = "SKIPPED",
    ejected: PlayerId | None = None,
    tick: int = 4,
) -> MeetingReport:
    return MeetingReport(
        meeting_id="m-0",
        tick=tick,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=MeetingTranscript(turns=turns),
        ballots=ballots,
        contradictions=contradictions,
        llm_calls=calls,
    )


def _inputs(
    *,
    meetings: tuple[MeetingReport, ...],
    route: Mapping[int, Mapping[PlayerId, RoomId]] | None = None,
    seed: int = 7,
) -> SetInputs:
    game = GameReport(
        game_id="planted",
        seed=seed,
        winner="CREWMATES",
        reason="planted",
        final_tick=9,
        roles=_ROLES,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=(),
        prompt_versions={},
        cost=GameCostSummary(
            total_cost_usd=0.0, total_input_tokens=0, total_output_tokens=0, by_model={}
        ),
    )
    return SetInputs(
        label="planted",
        source="planted",
        games=(game,),
        routes={seed: dict(route or {})},
        rooms=_ROOMS,
        context=_EMPTY_CONTEXT,
    )


def _card(inputs: SetInputs) -> SetScorecard:
    return scorecard_from_tally(fold_set(inputs), label="planted", sources=("planted",))


# ---------------------------------------------------------------------------
# The published contract
# ---------------------------------------------------------------------------


def test_every_row_publishes_its_own_definition() -> None:
    """Nine rows, nine definitions, each naming numerator and denominator."""

    assert len(ROW_DEFINITIONS) == 9
    for name, definition in ROW_DEFINITIONS.items():
        assert "Numerator" in definition or "numerator" in definition, name
        assert "Denominator" in definition or "denominator" in definition, name


def test_the_demotion_is_dated_and_names_the_decision() -> None:
    assert "2026-09-19" in ROLE_CORRECTNESS_NOTE
    assert "D1" in ROLE_CORRECTNESS_NOTE
    assert "NOT a gate" in ROLE_CORRECTNESS_NOTE


def test_a_rate_is_none_when_its_denominator_is_zero() -> None:
    assert RateCell(numerator=0, denominator=0, not_evaluable=0, rate=None).rate is None
    with pytest.raises(ValidationError):
        RateCell(numerator=0, denominator=0, not_evaluable=0, rate=0.0)
    with pytest.raises(ValidationError):
        RateCell(numerator=3, denominator=2, not_evaluable=0, rate=1.5)


# ---------------------------------------------------------------------------
# Row 1 — grounded decisions
# ---------------------------------------------------------------------------


def _skip_meeting(*, cite: bool) -> MeetingReport:
    """A SKIP weighing ``p-3``, citing the turn that names ``p-3`` — or nothing."""

    turn = _turn(speaker="p-2", claims=(_accusation_against("p-3"),))
    prompt = _prompt(valid=("p-2", "p-3"))
    return _meeting(
        turns=(turn,),
        ballots=(
            _ballot(
                voter="p-1",
                target="SKIP",
                reason_id=turn.turn_id if cite else None,
                alternatives=("p-3",),
                rationale="nothing decisive",
            ),
        ),
        calls=(_call(agent_id="p-1", prompt=prompt),),
    )


def _accusation_against(player: PlayerId) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=player, confidence=0.7, reason="odd route"
    )


def test_a_skip_citing_a_turn_about_a_named_alternative_is_grounded() -> None:
    card = _card(_inputs(meetings=(_skip_meeting(cite=True),)))
    assert (card.grounded_skip.numerator, card.grounded_skip.denominator) == (1, 1)


def test_the_same_skip_with_its_citation_nulled_is_not_grounded() -> None:
    """The adverse half: nothing else moves, so only the citation can explain it."""

    card = _card(_inputs(meetings=(_skip_meeting(cite=False),)))
    assert (card.grounded_skip.numerator, card.grounded_skip.denominator) == (0, 1)


def test_an_eject_citing_a_turn_about_somebody_else_is_not_grounded() -> None:
    """Aboutness, not mere resolution: the turn resolves and names the wrong player."""

    turn = _turn(speaker="p-2", claims=(_accusation_against("p-0"),))
    meeting = _meeting(
        turns=(turn,),
        ballots=(_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert card.grounded_eject.numerator == 0
    assert card.grounded_eject.denominator == 1


def test_a_ballot_with_no_recorded_prompt_is_not_evaluable_not_ungrounded() -> None:
    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="p-3"),),
        calls=(),
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert card.grounded_eject.not_evaluable == 1


# ---------------------------------------------------------------------------
# Row 2 — argmax independence
# ---------------------------------------------------------------------------


def test_a_follower_and_a_deviator_whose_role_correctness_differs() -> None:
    """p-1 follows its argmax onto the impostor; p-2 departs onto a crewmate."""

    prompt_follower = _prompt(
        suspicion={"p-3": 0.80, "p-0": 0.20}, valid=("p-0", "p-3")
    )
    prompt_deviator = _prompt(
        suspicion={"p-3": 0.80, "p-0": 0.20}, valid=("p-0", "p-3")
    )
    meeting = _meeting(
        ballots=(
            _ballot(voter="p-1", target="p-3"),
            _ballot(voter="p-2", target="p-0"),
        ),
        calls=(
            _call(agent_id="p-1", prompt=prompt_follower),
            _call(agent_id="p-2", prompt=prompt_deviator),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).argmax_independence
    assert (row.followers, row.deviators) == (1, 1)
    assert (row.follower_role_correct, row.deviator_role_correct) == (1, 0)
    assert row.chance_baseline == 0.5


def test_a_tie_lands_in_the_excluded_count_and_not_in_either_column() -> None:
    """Two valid targets at the same rendered row: the argmax is not a choice."""

    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="p-3"),),
        calls=(
            _call(
                agent_id="p-1",
                prompt=_prompt(
                    suspicion={"p-3": 0.60, "p-0": 0.60}, valid=("p-0", "p-3")
                ),
            ),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).argmax_independence
    assert (row.followers, row.deviators, row.ties_excluded) == (0, 0, 1)
    assert row.unambiguous_ballots == 0


def test_a_row_outside_the_valid_target_list_cannot_win_the_argmax() -> None:
    """The dead carry rendered rows; a ballot may not name them, so nor may the argmax."""

    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="p-3"),),
        calls=(
            _call(
                agent_id="p-1",
                prompt=_prompt(suspicion={"p-0": 0.95, "p-3": 0.40}, valid=("p-3",)),
            ),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).argmax_independence
    assert (row.followers, row.deviators) == (1, 0)


def test_an_impostor_voter_is_outside_the_crew_argmax_denominator() -> None:
    meeting = _meeting(
        ballots=(_ballot(voter="p-3", target="p-1"),),
        calls=(
            _call(
                agent_id="p-3",
                prompt=_prompt(suspicion={"p-1": 0.9}, valid=("p-0", "p-1")),
            ),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).argmax_independence
    assert row.unambiguous_ballots == 0


# ---------------------------------------------------------------------------
# Row 3 — manufactured contradictions
# ---------------------------------------------------------------------------

#: ``p-1`` walks CAFETERIA -> EAST_HALL -> STORAGE over engine ticks 0, 1, 2.
_ROUTE: Mapping[int, Mapping[PlayerId, RoomId]] = {
    -1: {
        "p-0": "CAFETERIA",
        "p-1": "CAFETERIA",
        "p-2": "CAFETERIA",
        "p-3": "CAFETERIA",
    },
    0: {"p-0": "CAFETERIA", "p-1": "CAFETERIA", "p-2": "CAFETERIA", "p-3": "CAFETERIA"},
    1: {"p-0": "CAFETERIA", "p-1": "EAST_HALL", "p-2": "CAFETERIA", "p-3": "CAFETERIA"},
    2: {"p-0": "CAFETERIA", "p-1": "STORAGE", "p-2": "CAFETERIA", "p-3": "CAFETERIA"},
}


def _alibi_meeting(claim: AlibiClaim, speaker: PlayerId) -> MeetingReport:
    return _meeting(
        turns=(_turn(speaker=speaker, claims=(claim,)),),
        contradictions=(_flag(subjects=(speaker,)),),
    )


def test_an_envelope_alibi_true_at_its_first_tick_mints_a_manufactured_flag() -> None:
    """The seed-41 shape: p-1 truthfully moved, and the envelope contradicts it."""

    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=3)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert (row.flags.numerator, row.flags.denominator) == (1, 1)
    assert row.manufactured_on_a_wholly_true_claim == 0
    assert row.self_alibi_claims == 1
    assert row.self_alibi_claims_envelope_false == 1
    assert row.self_alibi_claims_strict_false == 0


def test_a_flat_single_tick_lie_does_not_mint_a_manufactured_flag() -> None:
    """The adverse half: the speaker was in that room at NO tick the claim covers."""

    claim = _alibi(subject="p-1", room="ENGINEERING", from_tick=1, to_tick=1)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert (row.flags.numerator, row.flags.denominator) == (0, 1)
    assert row.self_alibi_claims_strict_false == 1
    assert row.self_alibi_claims_multi_tick == 0


def test_a_wholly_true_claim_is_manufactured_and_reported_separately() -> None:
    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=0, to_tick=1)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert row.flags.numerator == 1
    assert row.manufactured_on_a_wholly_true_claim == 1
    assert row.self_alibi_claims_envelope_false == 0


def test_a_flag_naming_no_self_alibi_speaker_is_not_evaluable() -> None:
    meeting = _meeting(contradictions=(_flag(subjects=("p-2",)),))
    row = _card(_inputs(meetings=(meeting,), route=_ROUTE)).manufactured_contradiction
    assert (row.flags.numerator, row.flags.denominator) == (0, 1)
    assert row.flags.not_evaluable == 1


def test_a_claim_reaching_past_the_walk_is_not_evaluable_rather_than_false() -> None:
    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=40)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert row.self_alibi_claims_unresolvable == 1
    assert row.self_alibi_claims_envelope_false == 0
    assert row.flags.not_evaluable == 1


def test_a_vent_flag_is_outside_the_alibi_denominator() -> None:
    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=3)
    meeting = _meeting(
        turns=(_turn(speaker="p-1", claims=(claim,)),),
        contradictions=(_flag(subjects=("p-1",), kind="vent_sighting"),),
    )
    row = _card(_inputs(meetings=(meeting,), route=_ROUTE)).manufactured_contradiction
    assert row.flags.denominator == 0


def test_an_alibi_about_another_player_is_out_of_the_self_claim_census() -> None:
    claim = _alibi(subject="p-2", room="CAFETERIA", from_tick=1, to_tick=2)
    meeting = _meeting(turns=(_turn(speaker="p-1", claims=(claim,)),))
    row = _card(_inputs(meetings=(meeting,), route=_ROUTE)).manufactured_contradiction
    assert (row.self_alibi_claims, row.other_subject_alibi_claims) == (0, 1)


def test_the_agent_clock_offset_is_what_makes_the_census_hold() -> None:
    """A claim about agent tick 1 reads engine tick 0, never engine tick 1.

    p-1 is in CAFETERIA at engine tick 0 and EAST_HALL at engine tick 1, so the
    single-tick claim below is TRUE under the +1 convention and FALSE under a
    same-frame one. The row that distinguishes them is the one the committed
    census (955 / 104 / 103 / 2) only reproduces under this convention.
    """

    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=1)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert row.self_alibi_claims_envelope_false == 0


# ---------------------------------------------------------------------------
# Row 4 — unexplained decisions
# ---------------------------------------------------------------------------


def test_a_skip_naming_no_player_anywhere_is_unexplained() -> None:
    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="SKIP", rationale="not enough to go on"),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert (row.decisions.numerator, row.skips_naming_no_player) == (1, 1)


def test_a_skip_naming_a_player_only_in_prose_is_not_unexplained() -> None:
    meeting = _meeting(
        ballots=(
            _ballot(voter="p-1", target="SKIP", rationale="p-3 worries me, but thinly"),
        ),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert row.decisions.numerator == 0
    assert row.skips_naming_a_player_in_prose == 1


def test_an_eject_whose_citation_does_not_resolve_is_unexplained() -> None:
    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="p-3", reason_id="m-0:turn-99"),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert (row.decisions.numerator, row.uncited_ejects) == (1, 1)


# ---------------------------------------------------------------------------
# Row 5 — the evidence-quality mix
# ---------------------------------------------------------------------------


def _ejection(
    *,
    contradictions: tuple[ContradictionRef, ...] = (),
    turns: tuple[MeetingTurn, ...] = (),
    ballot: VoteBallot,
    prompt: str,
) -> MeetingReport:
    return _meeting(
        turns=turns,
        contradictions=contradictions,
        ballots=(ballot,),
        calls=(_call(agent_id=ballot.voter, prompt=prompt),),
        outcome="EJECTED",
        ejected="p-3",
    )


def test_a_vent_flag_outranks_every_other_band() -> None:
    meeting = _ejection(
        contradictions=(
            _flag(subjects=("p-3",), kind="vent_sighting"),
            _flag(subjects=("p-3",)),
        ),
        ballot=_ballot(voter="p-1", target="p-3"),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"vent_flag": 1}
    assert row.band_role_correct == {"vent_flag": 1}


def test_an_unflagged_ejection_on_a_cited_observation_is_first_hand() -> None:
    meeting = _ejection(
        ballot=_ballot(voter="p-1", target="p-3", observation_id="p-1:3:0"),
        prompt=_prompt(
            valid=("p-3",),
            memory_lines=("[obs p-1:3:0] You saw p-3 leave ENGINEERING",),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"first_hand": 1}


def test_an_unflagged_ejection_on_an_accusation_turn_is_hearsay() -> None:
    turn = _turn(speaker="p-2", claims=(_accusation_against("p-3"),))
    meeting = _ejection(
        turns=(turn,),
        ballot=_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"hearsay": 1}


def test_an_unflagged_uncited_ejection_is_unevidenced() -> None:
    meeting = _ejection(
        ballot=_ballot(voter="p-1", target="p-3"),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"unevidenced": 1}


def test_the_mix_is_role_blind_and_reports_the_role_beside_it() -> None:
    """An innocent ejected on a vent flag still lands in the vent band."""

    meeting = _meeting(
        contradictions=(_flag(subjects=("p-0",), kind="vent_sighting"),),
        ballots=(_ballot(voter="p-1", target="p-0"),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-0",))),),
        outcome="EJECTED",
        ejected="p-0",
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert card.evidence_quality_mix.band_counts == {"vent_flag": 1}
    assert card.evidence_quality_mix.band_role_correct == {"vent_flag": 0}
    assert card.role_correct_ejection.numerator == 0
    assert card.role_correct_ejection.denominator == 1


# ---------------------------------------------------------------------------
# Row 6 — rationale faithfulness, and its stated limit
# ---------------------------------------------------------------------------


def _rationale_meeting(rationale: str) -> MeetingReport:
    turn = _turn(speaker="p-3", free_text="I was in CAFETERIA at tick 2")
    return _meeting(
        turns=(turn,),
        ballots=(_ballot(voter="p-1", target="p-3", rationale=rationale),),
        calls=(
            _call(
                agent_id="p-1",
                prompt=_prompt(
                    valid=("p-3",),
                    memory_lines=("[obs p-1:2:0] You saw p-3 in CAFETERIA at tick 2",),
                ),
            ),
        ),
    )


def test_a_rationale_naming_an_absent_room_fails() -> None:
    row = _card(
        _inputs(meetings=(_rationale_meeting("p-3 was in STORAGE at tick 2"),))
    ).rationale_faithfulness
    assert (row.ballots.numerator, row.ballots.denominator) == (0, 1)
    assert row.tokens_absent == 1


def test_a_rationale_whose_tokens_are_all_present_passes() -> None:
    row = _card(
        _inputs(meetings=(_rationale_meeting("p-3 was in Cafeteria at tick 2"),))
    ).rationale_faithfulness
    assert (row.ballots.numerator, row.ballots.denominator) == (1, 1)
    assert row.tokens_absent == 0


def test_a_negated_assertion_passes_which_is_the_stated_limit() -> None:
    """The row tests TOKENS, not propositions — pinned so the limit is not prose.

    "p-3 was NOT in CAFETERIA at tick 2" contradicts the line the voter held and
    still scores faithful, because every token in it is present. The published
    row says so in its own ``limits`` field, and the memo's section-3 result on
    invented facts is two-method agreement rather than this measurement.
    """

    card = _card(
        _inputs(meetings=(_rationale_meeting("p-3 was NOT in CAFETERIA at tick 2"),))
    )
    row = card.rationale_faithfulness
    assert row.ballots.numerator == 1
    assert "TOKENS, not propositions" in row.limits
    assert "TWO-METHOD AGREEMENT" in row.limits


def test_a_rationale_with_no_extractable_token_is_not_evaluable() -> None:
    row = _card(
        _inputs(meetings=(_rationale_meeting("nothing about this adds up"),))
    ).rationale_faithfulness
    assert (row.ballots.numerator, row.ballots.denominator) == (0, 0)
    assert row.ballots.not_evaluable == 1
    assert row.ballots.rate is None


# ---------------------------------------------------------------------------
# Row 7 — the agent-authored share
# ---------------------------------------------------------------------------


def _authored_meeting(ballot: VoteBallot) -> MeetingReport:
    return _meeting(
        ballots=(ballot,),
        calls=(_call(agent_id=ballot.voter, prompt=_prompt(valid=("p-3",))),),
    )


def test_a_ballot_carrying_under_gate_redirect_leaves_the_authored_share() -> None:
    marker = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-0")
    ballot = _ballot(
        voter="p-1",
        target="p-3",
        rationale=f"{marker}they looked wrong",
        rewrite_reason="under_gate_redirect",
        redirected_from="p-0",
    )
    row = _card(_inputs(meetings=(_authored_meeting(ballot),))).agent_authored_share
    assert (row.ballots.numerator, row.ballots.denominator) == (0, 1)
    assert row.rewrite_reasons == {"under_gate_redirect": 1}
    assert row.redirect_marker_ballots == 1


def test_a_ballot_carrying_only_a_nulled_citation_marker_stays_authored() -> None:
    """The adverse half: the citation moved, the TARGET did not."""

    marker = INVALID_REASON_ID_MARKER.format(reason_id="m-0:turn-99")
    ballot = _ballot(voter="p-1", target="p-3", rationale=f"{marker}they looked wrong")
    row = _card(_inputs(meetings=(_authored_meeting(ballot),))).agent_authored_share
    assert (row.ballots.numerator, row.ballots.denominator) == (1, 1)
    assert row.citation_nulled_target_intact == 1
    assert row.redirect_marker_ballots == 0


def test_a_marker_rewrite_with_no_typed_reason_still_leaves_the_share() -> None:
    """The pre-typed-field fallback meetings/schemas.py prescribes."""

    marker = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-0")
    ballot = _ballot(voter="p-1", target="p-3", rationale=f"{marker}they looked wrong")
    row = _card(_inputs(meetings=(_authored_meeting(ballot),))).agent_authored_share
    assert row.ballots.numerator == 0
    assert row.marker_unwound_without_typed_reason == 1
    assert row.rewrite_reasons == {}


def test_the_typed_layer_counts_a_rewrite_the_marker_census_cannot_see() -> None:
    """``uncited_coerced`` prepends no target repr, so only the typed field sees it."""

    ballot = _ballot(
        voter="p-1",
        target="SKIP",
        rationale="no case I can source",
        rewrite_reason="uncited_coerced",
        redirected_from="p-3",
    )
    row = _card(_inputs(meetings=(_authored_meeting(ballot),))).agent_authored_share
    assert row.ballots.numerator == 0
    assert row.rewrite_reasons == {"uncited_coerced": 1}
    assert row.redirect_marker_ballots == 0


# ---------------------------------------------------------------------------
# Row 8 — wrong but believable
# ---------------------------------------------------------------------------


def _wrong_but_believable_meeting(*, manufactured: bool) -> MeetingReport:
    """p-1 grounds an EJECT of the innocent p-0 on a turn that names p-0.

    With ``manufactured`` the meeting also carries an alibi flag against p-0
    whose own claim the route makes true, which is exactly the basis row 3
    disqualifies — so the same wrong call stops being believable.
    """

    claim = _alibi(subject="p-0", room="CAFETERIA", from_tick=1, to_tick=3)
    turn = _turn(speaker="p-0", claims=(claim,))
    return _meeting(
        turns=(turn,),
        contradictions=(_flag(subjects=("p-0",)),) if manufactured else (),
        ballots=(_ballot(voter="p-1", target="p-0", reason_id=turn.turn_id),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-0",))),),
    )


def test_a_grounded_wrong_call_is_wrong_but_believable() -> None:
    card = _card(
        _inputs(
            meetings=(_wrong_but_believable_meeting(manufactured=False),),
            route=_ROUTE,
        )
    )
    assert card.wrong_but_believable.numerator == 1
    assert card.wrong_but_believable_label == "reported, never penalised"


def test_a_wrong_call_resting_on_a_manufactured_flag_is_not_believable() -> None:
    card = _card(
        _inputs(
            meetings=(_wrong_but_believable_meeting(manufactured=True),),
            route=_ROUTE,
        )
    )
    assert card.manufactured_contradiction.flags.numerator == 1
    assert card.wrong_but_believable.numerator == 0


def test_a_role_correct_eject_is_never_wrong_but_believable() -> None:
    turn = _turn(speaker="p-3", claims=(_accusation_against("p-3"),))
    meeting = _meeting(
        turns=(turn,),
        ballots=(_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert card.grounded_eject.numerator == 1
    assert card.wrong_but_believable.numerator == 0


# ---------------------------------------------------------------------------
# Row 9 and pooling
# ---------------------------------------------------------------------------


def test_the_role_correct_row_is_labelled_as_no_gate() -> None:
    meeting = _meeting(
        ballots=(_ballot(voter="p-1", target="p-3"),),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
        outcome="EJECTED",
        ejected="p-3",
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert card.role_correct_ejection.numerator == 1
    assert card.role_correct_ejection_label == "reported beside, never a gate"


def test_pooling_adds_counts_and_recomputes_every_rate() -> None:
    """Two groups pool by addition, never by averaging their rates.

    The left group is one grounded EJECT of one; the right is one ungrounded
    EJECT of three. A mean of rates would publish 0.667; the pooled rate is
    1 of 4.
    """

    left = ProcessTally(ballots=1, eject_ballots=1, grounded_eject=1)
    right = ProcessTally(ballots=3, eject_ballots=3, grounded_eject=0)
    pooled = pool([left, right], label="pooled", sources=("a", "b"))
    assert (pooled.grounded_eject.numerator, pooled.grounded_eject.denominator) == (
        1,
        4,
    )
    assert pooled.grounded_eject.rate == 0.25


def test_pooling_the_chance_baseline_is_exact_and_order_free() -> None:
    """Carried as an exact sum of per-ballot shares, so pooling cannot drift."""

    from fractions import Fraction

    left = ProcessTally(chance_share_sum=Fraction(1, 3), chance_ballots=1)
    right = ProcessTally(chance_share_sum=Fraction(1, 2), chance_ballots=1)
    forwards = pool([left, right], label="x", sources=()).argmax_independence
    backwards = pool([right, left], label="x", sources=()).argmax_independence
    assert forwards.chance_baseline == backwards.chance_baseline
    assert forwards.chance_baseline == round(float(Fraction(5, 12)), 6)
