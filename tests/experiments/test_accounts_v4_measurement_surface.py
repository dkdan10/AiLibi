"""What the v4 account bounds are graded by, and what the manifest may claim.

Round 1 of review on `tasks/work/accounts-prompt-set-v4.md` withdrew a sentence
the execution manifest carried: that the rationale budget and the turn bound
are measurement-neutral because "no grader reads rationale or turn prose". Half
of that is true and half of it is false, and both halves are BEHAVIOURAL facts
about the instrument's graders rather than readings of them, so they are
asserted here rather than only written down:

* a cited turn's ``free_text`` and each claim's ``reason`` decide that turn's
  relevance (:func:`_turn_bears_on` walks the dumped turn, as
  :data:`CITATION_RELEVANCE_RUBRIC` says), and ``every_citation_relevant`` is a
  conjunct of the primary outcome -- so the turn bound moves a graded input on
  the candidate arm alone, downward;
* a ballot's ``rationale_text`` decides nothing -- so the rationale budget
  moves prompt bytes and no graded input.

The manifest case is the pin that keeps the withdrawn sentence from coming
back. Every input below is hand-written: no seed of any band is read, rendered
or constructed anywhere in this file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from experiments.fresh_deduction_instrument import (
    CITATION_RELEVANCE_RUBRIC,
    EXECUTION_MANIFEST_PATH,
    grade_citation_relevance,
    grade_supported,
)
from meetings.schemas import AccusationClaim, MeetingTurn, VoteBallot

#: The player a ballot names and the grader judges relevance against.
_SUBJECT: Final[str] = "p-2"
#: The speaker of the cited turn. Not the subject, so speaker identity never
#: short-circuits :func:`_turn_bears_on` before its content walk.
_SPEAKER: Final[str] = "p-9"
_TURN_ID: Final[str] = "t-1"

#: The manifest section this card wrote, and the sentence review withdrew.
_V4_HEADING: Final[str] = "## Accounts prompt set v4 (2026-09-15)"
_WITHDRAWN_CLAIM: Final[str] = "no grader reads rationale or turn prose"


def _turn(*, free_text: str, claims: tuple[AccusationClaim, ...] = ()) -> MeetingTurn:
    return MeetingTurn(
        turn_id=_TURN_ID,
        turn_index=0,
        speaker=_SPEAKER,
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=claims,
        free_text=free_text,
    )


def _ballot(*, rationale: str = "Cited above.") -> VoteBallot:
    return VoteBallot(
        voter="p-1",
        target=_SUBJECT,
        confidence=0.6,
        primary_reason_id=_TURN_ID,
        primary_reason_observation_id=None,
        considered_alternatives=(),
        rationale_text=rationale,
    )


def _verdicts(turn: MeetingTurn) -> tuple[str, ...]:
    grades = grade_citation_relevance(
        [_ballot()],
        subject=_SUBJECT,
        turns=[turn],
        prompts_by_agent={"p-1": (f"[{_TURN_ID}] {_SPEAKER}: ...",)},
    )
    return tuple(grade.verdict for grade in grades)


def test_the_rubric_says_a_turns_free_text_and_claims_are_read() -> None:
    # The prose half of the same fact: the frozen rubric names the fields the
    # walk covers, so the manifest's declaration is not an inference from an
    # implementation detail.
    assert "its claims and its free text included" in CITATION_RELEVANCE_RUBRIC


def test_a_cited_turns_free_text_decides_whether_the_citation_is_relevant() -> None:
    # The turn bound shortens exactly this field. A reply that names the
    # ejected player makes the ballot citing it RELEVANT; the same turn with a
    # bounded reply that names nobody makes it OFF_TARGET, and
    # `every_citation_relevant` is a conjunct of `supported_correct_ejection`.
    names = _turn(free_text=f"{_SUBJECT} was in Reactor at tick 12 and never left.")
    bounded = _turn(free_text="I have nothing further.")
    assert _verdicts(names) == ("relevant",)
    assert _verdicts(bounded) == ("off_target",)


def test_a_cited_turns_claim_reason_decides_relevance_too() -> None:
    # The second field the turn bound shortens, isolated: the accusation is
    # against a THIRD player and the free text names nobody, so the only place
    # the subject can be named is the claim's `reason`.
    against_other = AccusationClaim(
        type="accusation",
        against="p-3",
        confidence=0.6,
        reason=f"{_SUBJECT} put them there at tick 12",
    )
    bounded = AccusationClaim(
        type="accusation", against="p-3", confidence=0.6, reason="unexplained gap"
    )
    assert _verdicts(
        _turn(free_text="Here is my account.", claims=(against_other,))
    ) == ("relevant",)
    assert _verdicts(_turn(free_text="Here is my account.", claims=(bounded,))) == (
        "off_target",
    )


def test_no_ballot_grader_reads_the_rationale_text() -> None:
    # The surviving half of the withdrawn claim, and the reason the rationale
    # budget is measurement-neutral: two ballots that differ ONLY in
    # `rationale_text` grade identically under both ballot graders the primary
    # outcome composes.
    turn = _turn(free_text=f"{_SUBJECT} was in Reactor at tick 12.")
    prompts = {"p-1": (f"[{_TURN_ID}] {_SPEAKER}: ...",)}
    long_rationale = _ballot(
        rationale=(
            f"I have weighed every account at this table and {_SUBJECT} is the "
            "only one whose placement cannot be reconciled with the discovery."
        )
    )
    short_rationale = _ballot(rationale="Gap at 12.")
    relevance = [
        grade_citation_relevance(
            [ballot], subject=_SUBJECT, turns=[turn], prompts_by_agent=prompts
        )[0].verdict
        for ballot in (long_rationale, short_rationale)
    ]
    supported = [
        grade_supported([ballot], prompts_by_agent=prompts)[0].verdict
        for ballot in (long_rationale, short_rationale)
    ]
    assert relevance[0] == relevance[1] == "relevant"
    assert supported[0] == supported[1]


def test_the_manifest_does_not_call_the_turn_bound_measurement_neutral() -> None:
    # The pin on the document. The v4 section once said the turn bound was
    # measurement-neutral "because no grader reads rationale or turn prose";
    # the three cases above are why that sentence may not come back, and why
    # the section has to name the path that reads a cited turn.
    manifest = Path(__file__).resolve().parents[2] / EXECUTION_MANIFEST_PATH
    text = manifest.read_text(encoding="utf-8")
    assert _V4_HEADING in text
    section = text[text.index(_V4_HEADING) :]
    section = section[: section.index("\n## ", 1)]
    assert _WITHDRAWN_CLAIM not in section
    for named in ("grade_citation_relevance", "_turn_bears_on", "OFF_TARGET"):
        assert named in section, named
