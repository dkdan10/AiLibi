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

import dataclasses
import json
from collections.abc import Mapping, Sequence
from fractions import Fraction
from typing import get_args

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.alibi_fabrication import (
    ALIBI_CONTRADICTION_KINDS,
    compute_alibi_fabrication_rate,
)
from eval.process_scorecard import (
    ALIBI_FLAG_KINDS,
    ROLE_CORRECTNESS_NOTE,
    ROW_DEFINITIONS,
    ContextCells,
    ProcessScorecardReconstructionError,
    ProcessTally,
    RateCell,
    SetInputs,
    SetScorecard,
    _context_cells,
    _walk_config,
    fold_set,
    pool,
    scorecard_from_tally,
)
from eval.replay_walk import WalkViolation
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from eval.reporter_justice import ReporterJusticeCells
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
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
        type="alibi",
        subject=subject,
        route=(AlibiSegment(room=room, from_tick=from_tick, to_tick=to_tick),),
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


def _call(
    *, agent_id: PlayerId, prompt: str, model_body: str | None = None
) -> LLMCallRecord:
    """One recorded vote call.

    ``model_body`` is the voter's PRE-GUARD ``rationale_text``, recorded in the
    structured response the way a live vote call records it. It is the
    boundary the guard-origin cells cut along
    (``eval.deduction_metrics._split_rationale``): without it a record carrying
    a marker cannot be ATTRIBUTED to the machinery — anchoring is a shape, not a
    provenance — and the ballot lands in the published unverifiable direction
    with an empty marker region. A planted ballot that means to exercise a
    guard marker therefore has to supply the body the guard prepended to.
    """

    response = (
        json.dumps({"target": "p-3", "confidence": 0.6, "rationale_text": model_body})
        if model_body is not None
        else "{}"
    )
    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=prompt,
        response_text=response,
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


def test_a_game_with_no_reconstructed_route_is_refused_not_folded() -> None:
    """AGENTS.md rule 5 at the fold's own boundary: invalid input raises.

    ``fold_set`` used to take the route with ``.get(seed, {})``, so a game whose
    seed the route table does not carry folded against an EMPTY route: every
    alibi tick unresolvable, row 3's census silently 0, and a published number
    that looks like a measurement of nothing. It is unreachable through
    ``load_set_inputs`` — ``walk_routes`` keys every seed on disk — which is
    exactly why it has to be pinned here rather than by a figure moving.
    """

    inputs = _inputs(meetings=(_meeting(),), seed=7)
    orphaned = dataclasses.replace(inputs, routes={999: {}})
    with pytest.raises(ProcessScorecardReconstructionError) as caught:
        fold_set(orphaned)
    assert "seed 7" in str(caught.value)
    # The adverse half: the same game with its own seed keyed folds normally.
    assert fold_set(inputs).games == 1


def test_a_replay_that_does_not_reconstruct_is_refused() -> None:
    """The sibling raise: a profile violation, not a missing key."""

    violation = WalkViolation(kind="tick_hash_mismatch", game_id="planted", tick=3)
    with pytest.raises(ProcessScorecardReconstructionError) as caught:
        _walk_config().on_violation(violation)
    assert "tick_hash_mismatch" in str(caught.value)


def test_a_rate_is_none_when_its_denominator_is_zero() -> None:
    assert RateCell(numerator=0, denominator=0, not_evaluable=0, rate=None).rate is None
    with pytest.raises(ValidationError):
        RateCell(numerator=0, denominator=0, not_evaluable=0, rate=0.0)
    with pytest.raises(ValidationError):
        RateCell(numerator=3, denominator=2, not_evaluable=0, rate=1.5)


def test_a_rate_that_contradicts_its_own_counts_is_refused() -> None:
    """The perturbed case: a cell whose published rate is not its own quotient.

    ``1/2`` with a rate of ``0.9`` is internally inconsistent, and this is the
    typed boundary every published rate crosses in both directions — the model a
    later spectator surface parses ``docs/process-scorecard.json`` with. An
    inconsistent cell must be REFUSED rather than preserved and read as a
    measurement, whether it is constructed in process or validated from JSON.
    """

    with pytest.raises(ValidationError):
        RateCell(numerator=1, denominator=2, not_evaluable=0, rate=0.9)
    with pytest.raises(ValidationError):
        RateCell.model_validate(
            json.loads(
                '{"numerator": 1, "denominator": 2, "not_evaluable": 0, "rate": 0.9}'
            )
        )
    # The honest half, to six places, in process and through JSON alike.
    assert RateCell(numerator=1, denominator=3, not_evaluable=0, rate=0.333333).rate
    assert (
        RateCell.model_validate(
            json.loads(
                '{"numerator": 1, "denominator": 3, "not_evaluable": 0, '
                '"rate": 0.333333}'
            )
        ).numerator
        == 1
    )


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


def test_the_missing_prompt_count_is_partitioned_by_ballot_kind() -> None:
    """A promptless EJECT says nothing about whether the SKIP cell measured.

    ``RateCell`` publishes ``not_evaluable`` separately so a reader can tell a
    cell that measured NOTHING from one that measured a zero. One promptless
    EJECT beside a fully recorded SKIP must therefore leave the SKIP cell's
    not-evaluable count at 0: the SKIP's prompt WAS recorded, the SKIP was
    measured, and its 0/1 is a reading. ``grounded_all`` and the unexplained row
    keep the sum, because their denominator is every ballot.
    """

    turn = _turn(speaker="p-2", claims=(_accusation_against("p-3"),))
    meeting = _meeting(
        turns=(turn,),
        ballots=(
            _ballot(voter="p-1", target="p-3"),
            _ballot(voter="p-2", target="SKIP", alternatives=("p-3",)),
        ),
        calls=(_call(agent_id="p-2", prompt=_prompt(valid=("p-3",))),),
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert (card.grounded_eject.denominator, card.grounded_eject.not_evaluable) == (
        1,
        1,
    )
    assert (card.grounded_skip.denominator, card.grounded_skip.not_evaluable) == (1, 0)
    assert card.wrong_but_believable.not_evaluable == 1
    assert card.grounded_all.not_evaluable == 1
    assert card.unexplained_decision.decisions.not_evaluable == 1


def test_the_partition_holds_with_the_kinds_swapped() -> None:
    """The adverse half: the promptless ballot is the SKIP, so the EJECT cell measures."""

    turn = _turn(speaker="p-2", claims=(_accusation_against("p-3"),))
    meeting = _meeting(
        turns=(turn,),
        ballots=(
            _ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),
            _ballot(voter="p-2", target="SKIP", alternatives=("p-3",)),
        ),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    card = _card(_inputs(meetings=(meeting,)))
    assert (card.grounded_eject.numerator, card.grounded_eject.not_evaluable) == (1, 0)
    assert (card.grounded_skip.denominator, card.grounded_skip.not_evaluable) == (1, 1)
    assert card.wrong_but_believable.not_evaluable == 0


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


def test_chance_is_measured_over_the_unambiguous_ballots_and_no_others() -> None:
    """The baseline's population is the row's own denominator, as published.

    Three crew EJECTs with DIFFERENT impostor shares, one per outcome: p-1 is
    unambiguous on a two-name list (share 1/2), p-2 ties on a three-name list
    (share 1/3) and p-0's rendered rows fall entirely outside its valid list
    (share 1/1). Only the first is in the denominator, so chance is 0.5. An
    accumulator that ran before the tie and no-row returns would publish
    (1/2 + 1/3 + 1) / 3 = 0.6111 over a denominator of 1 - a baseline no cell on
    the row accounts for, which is the defect this pins.
    """

    meeting = _meeting(
        ballots=(
            _ballot(voter="p-1", target="p-3"),
            _ballot(voter="p-2", target="p-3"),
            _ballot(voter="p-0", target="p-3"),
        ),
        calls=(
            _call(
                agent_id="p-1",
                prompt=_prompt(
                    suspicion={"p-3": 0.80, "p-0": 0.20}, valid=("p-0", "p-3")
                ),
            ),
            _call(
                agent_id="p-2",
                prompt=_prompt(
                    suspicion={"p-0": 0.60, "p-1": 0.60, "p-3": 0.10},
                    valid=("p-0", "p-1", "p-3"),
                ),
            ),
            _call(
                agent_id="p-0",
                prompt=_prompt(suspicion={"p-1": 0.90}, valid=("p-3",)),
            ),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).argmax_independence
    assert (row.unambiguous_ballots, row.ties_excluded, row.no_rendered_row) == (
        1,
        1,
        1,
    )
    assert row.chance_baseline == 0.5
    assert "SAME unambiguous ballots that form the denominator" in row.definition


def test_a_chance_population_wider_than_the_denominator_is_refused() -> None:
    """The perturbed half: one extra chance ballot and the build fails loud.

    ``scorecard_from_tally`` will not publish a baseline measured over a
    population no cell on the row accounts for, which is the shape the shipped
    accumulator had. Perturbing the tally by the single ballot a tie would have
    added is enough to turn it red.
    """

    tally = ProcessTally(
        followers=3,
        deviators=1,
        chance_share_sum=Fraction(2),
        chance_ballots=4,
    )
    assert (
        scorecard_from_tally(
            tally, label="planted", sources=("planted",)
        ).argmax_independence.chance_baseline
        == 0.5
    )

    tally.argmax_ties += 1
    tally.chance_share_sum += Fraction(1, 3)
    tally.chance_ballots += 1
    with pytest.raises(ValueError, match="must be the row's denominator"):
        scorecard_from_tally(tally, label="planted", sources=("planted",))


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


def test_a_part_true_route_is_not_evaluable_rather_than_manufactured() -> None:
    """A flag that caught a fabricated LEG is evidence, and row 3 must not claim it.

    p-1's route states CAFETERIA at agent tick 1 (true: engine tick 0) and
    STORAGE at agent tick 2 (false: p-1 is in EAST_HALL at engine tick 1). A
    fold across the whole route reads "true at some tick" off the FIRST leg and
    files the flag as schema-manufactured, although the flag may be exactly the
    one that caught the second leg. The recorded flag names the claim, not the
    leg, so the cell publishes it as not evaluable.
    """

    claim = AlibiClaim(
        type="alibi",
        subject="p-1",
        route=(
            AlibiSegment(room="CAFETERIA", from_tick=1, to_tick=1),
            AlibiSegment(room="STORAGE", from_tick=2, to_tick=2),
        ),
    )
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert (row.flags.numerator, row.flags.denominator) == (0, 1)
    assert row.flags.not_evaluable == 1
    assert "multi-leg route" in row.definition
    # The CLAIM census beside the row still reads the whole account, leg by leg:
    # the refusal is about attributing a FLAG, not about walking a route.
    assert row.self_alibi_claims == 1
    assert row.self_alibi_claims_multi_tick == 1
    assert row.self_alibi_claims_envelope_false == 1
    assert row.self_alibi_claims_strict_false == 0


def test_a_one_segment_route_is_still_scored_by_row_three() -> None:
    """The other side: the refusal is keyed on the STAY COUNT and nothing else.

    Every committed claim is a one-segment route, so this is the case that must
    not move — the same envelope as the seed-41 shape above, scored.
    """

    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=2)
    row = _card(
        _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
    ).manufactured_contradiction
    assert (row.flags.numerator, row.flags.denominator) == (1, 1)
    assert row.flags.not_evaluable == 0


def test_recutting_one_stay_does_not_change_whether_row_three_scores_a_flag() -> None:
    """Whether a flag is evaluable must not be the speaker's to choose.

    The refusal counts MAXIMAL STAYS, not the legs as stated. Counting legs
    made a PUBLISHED figure a dial the accused holds: "CAFETERIA 1-2" is
    scored, and the identical account re-cut as "CAFETERIA 1-1" plus
    "CAFETERIA 2-2" would drop out of the denominator as not evaluable — a
    caught flag quietly removed from the row that measures whether flags are
    manufactured. One continuous stay is one stay however it was narrated.
    """

    envelope = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=2)
    recut = AlibiClaim(
        type="alibi",
        subject="p-1",
        route=(
            AlibiSegment(room="CAFETERIA", from_tick=1, to_tick=1),
            AlibiSegment(room="CAFETERIA", from_tick=2, to_tick=2),
        ),
    )

    def scored(claim: AlibiClaim) -> tuple[int, int, int]:
        row = _card(
            _inputs(meetings=(_alibi_meeting(claim, "p-1"),), route=_ROUTE)
        ).manufactured_contradiction
        return (row.flags.numerator, row.flags.denominator, row.flags.not_evaluable)

    assert scored(recut) == scored(envelope) == (1, 1, 0)

    # The control: a GENUINE second stay — a different room — is the shape the
    # refusal exists for, and it is still refused.
    part_true = AlibiClaim(
        type="alibi",
        subject="p-1",
        route=(
            AlibiSegment(room="CAFETERIA", from_tick=1, to_tick=1),
            AlibiSegment(room="STORAGE", from_tick=2, to_tick=2),
        ),
    )
    assert scored(part_true) == (0, 1, 1)


def test_a_vent_flag_is_outside_the_alibi_denominator() -> None:
    claim = _alibi(subject="p-1", room="CAFETERIA", from_tick=1, to_tick=3)
    meeting = _meeting(
        turns=(_turn(speaker="p-1", claims=(claim,)),),
        contradictions=(_flag(subjects=("p-1",), kind="vent_sighting"),),
    )
    row = _card(_inputs(meetings=(meeting,), route=_ROUTE)).manufactured_contradiction
    assert row.flags.denominator == 0


def test_the_alibi_kind_filter_is_the_owning_census_itself() -> None:
    """Row 3's denominator IS :mod:`eval.alibi_fabrication`'s set, not a copy.

    The scorecard's comment says the kinds are read from the census that owns
    them; identity is what makes that sentence true. A hand-written re-listing
    would still compare equal today and would drift the moment a kind is added
    or retired on one side only, so the assertion is ``is``, and the second
    half pins the shared set inside the schema Literal both modules branch on.
    """

    assert ALIBI_FLAG_KINDS is ALIBI_CONTRADICTION_KINDS
    kinds = set(get_args(ContradictionRef.model_fields["kind"].annotation))
    assert ALIBI_FLAG_KINDS <= kinds
    assert {kind for kind in kinds if kind.startswith("alibi_")} == ALIBI_FLAG_KINDS


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


def test_a_coerced_skip_whose_only_player_token_is_the_guard_marker() -> None:
    """The machinery may not answer the authorship question for the voter.

    The shipped shape: the teammate firewall coerces an impostor's EJECT to
    SKIP, its marker preserves the coerced target's id, and
    ``TEAMMATE_COERCED_VOTE_RATIONALE`` replaces the model's body - so the whole
    recorded rationale is guard prose carrying ``p-3``. Reading the raw text
    scores this SKIP as one that named what it weighed; reading the
    model-authored remainder, which is what row 4's definition names, leaves
    nothing and the SKIP is unexplained.
    """

    coerced = _ballot(
        voter="p-2",
        target="SKIP",
        rationale=(
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-3")
            + TEAMMATE_COERCED_VOTE_RATIONALE
        ),
        rewrite_reason="teammate_coerced",
        redirected_from="p-3",
    )
    meeting = _meeting(
        ballots=(coerced,),
        calls=(_call(agent_id="p-2", prompt=_prompt(valid=("p-3",))),),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert (row.decisions.numerator, row.skips_naming_no_player) == (1, 1)
    assert row.skips_naming_a_player_in_prose == 0
    assert "p-3" in coerced.rationale_text  # the raw bytes DO carry the id


def test_the_same_coerced_skip_with_a_model_body_naming_a_player_is_not() -> None:
    """The half that differs in exactly one thing: a body the model wrote.

    Same marker, same coerced SKIP; the voter's own sentence survives behind it
    and names a player, so the decision is explained and the marker's own id is
    irrelevant either way.
    """

    meeting = _meeting(
        ballots=(
            _ballot(
                voter="p-2",
                target="SKIP",
                rationale=(
                    TEAMMATE_VOTE_TARGET_MARKER.format(target="p-3")
                    + "I weighed p-0 and could not get there."
                ),
                rewrite_reason="teammate_coerced",
                redirected_from="p-3",
            ),
        ),
        calls=(
            _call(
                agent_id="p-2",
                prompt=_prompt(valid=("p-3",)),
                model_body="I weighed p-0 and could not get there.",
            ),
        ),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert (row.decisions.numerator, row.skips_naming_no_player) == (0, 0)
    assert row.skips_naming_a_player_in_prose == 1


def test_a_parse_defaulted_skip_is_unexplained_however_its_head_reads() -> None:
    """A rationale that is ENTIRELY machinery leaves nothing to have named.

    ``VOTE_PARSE_DEFAULT_MARKER`` is the whole ``rationale_text`` and carries a
    bounded head of the response that would not parse. Nothing was parsed, so
    the ballot is a machine default with no basis - even when the head's bytes
    happen to contain a player id.
    """

    meeting = _meeting(
        ballots=(
            _ballot(
                voter="p-1",
                target="SKIP",
                rationale=VOTE_PARSE_DEFAULT_MARKER.format(
                    head='{"target": "p-3", "rationale_te'
                ),
            ),
        ),
        calls=(_call(agent_id="p-1", prompt=_prompt(valid=("p-3",))),),
    )
    row = _card(_inputs(meetings=(meeting,))).unexplained_decision
    assert (row.decisions.numerator, row.skips_naming_no_player) == (1, 1)


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


def test_a_cited_turn_observing_the_ejected_player_is_first_hand() -> None:
    """Half one of the pair: the turn's observation NAMES the ejected player."""

    turn = _turn(
        speaker="p-2",
        observations=(
            SawPlayerObservation(
                type="saw_player", tick=3, subject="p-3", room="ENGINEERING"
            ),
        ),
        free_text="p-3 was not where they said",
    )
    meeting = _ejection(
        turns=(turn,),
        ballot=_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"first_hand": 1}


def test_a_cited_turn_observing_somebody_else_is_not_first_hand() -> None:
    """Half two: the same turn, one field moved - the observation is about p-0.

    ``turn.observations`` is non-empty either way and the turn still bears on
    p-3 through its own sentence, so a band that asked only whether the turn
    carried SOME structured observation would read this as first-hand evidence
    about a player no observation mentions. The published definition asks for an
    observation NAMING them, and under it this ejection rests on the speaker's
    prose alone: unevidenced.
    """

    turn = _turn(
        speaker="p-2",
        observations=(
            SawPlayerObservation(
                type="saw_player", tick=3, subject="p-0", room="ENGINEERING"
            ),
        ),
        free_text="p-3 was not where they said",
    )
    meeting = _ejection(
        turns=(turn,),
        ballot=_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"unevidenced": 1}


def test_the_ejected_players_own_turn_is_not_a_first_hand_route() -> None:
    """Being the SPEAKER is not an observation about oneself.

    A turn spoken by the ejected player carrying an observation about somebody
    else is that player's own account, not a witness's account of them; it
    carries an accusation here, so the ejection is hearsay.
    """

    turn = _turn(
        speaker="p-3",
        observations=(
            SawPlayerObservation(
                type="saw_player", tick=3, subject="p-0", room="ENGINEERING"
            ),
        ),
        claims=(_accusation_against("p-0"),),
    )
    meeting = _ejection(
        turns=(turn,),
        ballot=_ballot(voter="p-1", target="p-3", reason_id=turn.turn_id),
        prompt=_prompt(valid=("p-3",)),
    )
    row = _card(_inputs(meetings=(meeting,))).evidence_quality_mix
    assert row.band_counts == {"hearsay": 1}


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


def _authored_meeting(
    ballot: VoteBallot, *, model_body: str | None = None
) -> MeetingReport:
    return _meeting(
        ballots=(ballot,),
        calls=(
            _call(
                agent_id=ballot.voter,
                prompt=_prompt(valid=("p-3",)),
                model_body=model_body,
            ),
        ),
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
    row = _card(
        _inputs(meetings=(_authored_meeting(ballot, model_body="they looked wrong"),))
    ).agent_authored_share
    assert (row.ballots.numerator, row.ballots.denominator) == (1, 1)
    assert row.citation_nulled_target_intact == 1
    assert row.redirect_marker_ballots == 0


def test_a_marker_rewrite_with_no_typed_reason_still_leaves_the_share() -> None:
    """The pre-typed-field fallback meetings/schemas.py prescribes."""

    marker = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-0")
    ballot = _ballot(voter="p-1", target="p-3", rationale=f"{marker}they looked wrong")
    row = _card(
        _inputs(meetings=(_authored_meeting(ballot, model_body="they looked wrong"),))
    ).agent_authored_share
    assert row.ballots.numerator == 0
    assert row.marker_unwound_without_typed_reason == 1
    assert row.rewrite_reasons == {}


def test_a_model_body_that_opens_with_marker_shaped_prose_stays_authored() -> None:
    """The planted legacy ballot: marker SHAPE at position 0 is not provenance.

    A pre-typed-field recording carries no ``guard_rewrite_reason``, so the
    marker chain is the only channel left — and a model that OPENS its own
    rationale by quoting the redirect literal sits at position 0 exactly where
    the guard's marker would. Scanning the WHOLE rationale reads that opening as
    a guard rewrite and takes an authored ballot out of the share. Cut along the
    provenance boundary, the model's body IS the record, the marker region is
    empty, and the ballot stays where it belongs.
    """

    quoted = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-0") + "is what I would say"
    ballot = _ballot(voter="p-1", target="p-3", rationale=quoted)
    row = _card(
        _inputs(meetings=(_authored_meeting(ballot, model_body=quoted),))
    ).agent_authored_share
    assert (row.ballots.numerator, row.ballots.denominator) == (1, 1)
    assert row.marker_unwound_without_typed_reason == 0


def test_the_same_legacy_ballot_whose_marker_the_guard_wrote_leaves_the_share() -> None:
    """The half that differs in exactly one thing: who wrote the marker.

    Same bytes ahead of the body; here the model's pre-guard body is the body
    ALONE, so the marker is the machinery's and the rewrite is real.
    """

    marker = BALLOT_TARGET_REDIRECT_MARKER.format(target="p-0")
    ballot = _ballot(
        voter="p-1", target="p-3", rationale=f"{marker}is what I would say"
    )
    row = _card(
        _inputs(meetings=(_authored_meeting(ballot, model_body="is what I would say"),))
    ).agent_authored_share
    assert row.ballots.numerator == 0
    assert row.marker_unwound_without_typed_reason == 1


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
    """Carried as an exact sum of per-ballot shares, so pooling cannot drift.

    Each side carries the follower its chance ballot came from: the baseline's
    population IS the row's denominator, and ``scorecard_from_tally`` refuses a
    tally where the two disagree
    (``test_a_chance_population_wider_than_the_denominator_is_refused``).
    """

    left = ProcessTally(chance_share_sum=Fraction(1, 3), chance_ballots=1, followers=1)
    right = ProcessTally(chance_share_sum=Fraction(1, 2), chance_ballots=1, followers=1)
    forwards = pool([left, right], label="x", sources=()).argmax_independence
    backwards = pool([right, left], label="x", sources=()).argmax_independence
    assert forwards.chance_baseline == backwards.chance_baseline
    assert forwards.chance_baseline == round(float(Fraction(5, 12)), 6)


# ---------------------------------------------------------------------------
# Round 5: the published impostor_alibis* context cells
# ---------------------------------------------------------------------------

# A zero-filled reporter half. ``_context_cells`` carries these through
# untouched and they are irrelevant to the alibi cells under test; they are
# spelled out anyway so a new reporter cell fails this construction loudly
# rather than being silently defaulted.
_ZERO_REPORTER = ReporterJusticeCells(
    set_name="planted",
    games=0,
    meetings=0,
    body_report_meetings=0,
    emergency_meetings=0,
    reporter_crewmate_meetings=0,
    reporter_impostor_meetings=0,
    ejections=0,
    innocent_ejections=0,
    impostor_ejections=0,
    reporter_slots=0,
    reporter_ejections=0,
    reporter_innocent_ejections=0,
    innocent_non_reporter_slots=0,
    innocent_non_reporter_ejections=0,
    impostor_slots=0,
    impostor_slot_ejections=0,
    crew_accusations=0,
    crew_accusations_at_reporter=0,
    impostor_accusations=0,
    impostor_accusations_at_reporter=0,
    crew_ballots=0,
    crew_ballots_at_reporter=0,
    impostor_ballots=0,
    impostor_ballots_at_reporter=0,
    ballot_rationales=0,
    ballot_rationales_mentioning_report=0,
    ballot_rationales_with_hinge=0,
    speech_turns=0,
    speech_turns_mentioning_report=0,
    speech_turns_with_hinge=0,
    speech_turns_with_hinge_by_reporter=0,
    meetings_with_co_discoverer=0,
    co_discoverer_slots_crewmate=0,
    co_discoverer_slots_impostor=0,
)


def test_recutting_a_restated_alibi_does_not_move_the_impostor_alibi_cells() -> None:
    """The scorecard's context cells adopt the fabrication metric as computed.

    ``impostor_alibis``, ``impostor_alibis_survived`` and
    ``impostor_alibi_survival_rate`` are PUBLISHED in
    ``docs/process-scorecard.{md,json}`` and pinned by
    ``scripts/publish_process_scorecard.py --check``. They are
    ``compute_alibi_fabrication_rate``'s counts, so the round-5 dedup repair --
    keying the ACCOUNT rather than the narration -- is what keeps them out of
    the accused's hands; this closes the chain from the metric to the cell.
    """

    account = (AlibiSegment(room="STORAGE", from_tick=2, to_tick=14),)
    one_tick_legs = tuple(
        AlibiSegment(room="STORAGE", from_tick=tick, to_tick=tick)
        for tick in range(2, 15)
    )

    def cells(restatement: tuple[AlibiSegment, ...]) -> ContextCells:
        turns = tuple(
            _turn(
                index=index,
                speaker="p-3",
                claims=(AlibiClaim(type="alibi", subject="p-3", route=route),),
            )
            for index, route in enumerate((account, restatement))
        )
        game = GameReport(
            game_id="planted",
            seed=7,
            winner="CREWMATES",
            reason="planted",
            final_tick=9,
            roles=_ROLES,
            replay_ref="replay-seed-7.jsonl",
            meetings=(_meeting(turns=turns),),
            failed_calls=(),
            prompt_versions={},
            cost=GameCostSummary(
                total_cost_usd=0.0,
                total_input_tokens=0,
                total_output_tokens=0,
                by_model={},
            ),
        )
        report = TournamentReport(
            format_version=CURRENT_FORMAT_VERSION, games=(game,), seeds_used=(7,)
        )
        alibi = compute_alibi_fabrication_rate(report)
        return _context_cells(
            alibi.total_impostor_alibis, alibi.survived, _ZERO_REPORTER
        )

    verbatim = cells(account)
    # Non-vacuous: the restatement really is deduped to ONE published alibi.
    assert verbatim.impostor_alibis == 1
    assert verbatim.impostor_alibi_survival_rate == 1.0
    assert cells(one_tick_legs) == verbatim
