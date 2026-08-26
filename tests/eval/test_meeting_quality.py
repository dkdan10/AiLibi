"""Unit tests for the citation-coerced SKIP bucket (Task 17.2).

The conversion report's SKIP partition learns
:data:`~meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER` as a FOURTH by-design
bucket (``citation_coerced_skip_ballots``, beside correct / missed /
unclassified). The Task 16.6 citation gate (``citation_gate_enabled`` lever ON)
rewrites an uncited zero-flag EJECT to SKIP; the gate working is never the
voter's decision, so a marker-anchored SKIP is neither a missed skip nor a §4.6
``threshold_inversions`` entry (audits/audit-phase-16-close.md §8 routed
contract (b); the 17.2 designer ruling tasks/phase-17.md). The divert is role-
and verdict-blind (the 17.10 ruling: a coerced ballot is a forced eject, not a
decision), and marker-keyed: it fires only on the anchored production literal,
never a re-spelled string.

Fixtures instantiate ``report_schema`` / ``meetings.schemas`` models directly
(no tournament run), mirroring ``tests/eval/test_vote_correctness.py``; the
marker literals come from :mod:`meetings.manager`, never re-spelled.

Task 19.5 extends this file with the ``threshold_inversions`` RE-DOCTRINE and
the fixture that grounds it (audits/audit-phase-19-triage.md §7 item 5, row
C6). Task 13.13 de-imperatived the §4.6 vote gate — ``vote_ballot.j2`` renders
the voter's max suspicion and the 0.60 reference threshold as ONE non-directive
evidence line, and only the deterministic tally floor constrains the outcome —
so a crew voter who declines over a met reference line is exercising
**sanctioned discretion**, not disobeying a gate. The bucket is a conservatism
gauge whose nonzero value is INTENDED on post-13.13 recordings; the pre-13.13
"expect ~0, a nonzero count is a gate-render/obedience bug" reading is retired.
The tests below therefore call an unmarked met-threshold SKIP a *discretionary
decline* rather than a bug, with the counts unchanged: what they still pin is
that the divert is MARKER-KEYED, so a by-design rewrite never lands in the
remainder. :func:`~eval.meeting_quality.recount_threshold_inversions` is the
by-cause table behind the re-doctrine, pinned here over the committed bytes.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.meeting_quality import (
    ConversionReport,
    ThresholdInversionRecount,
    TournamentEvalReport,
    compute_conversion_report,
    recount_threshold_inversions,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from meetings.manager import (
    INVALID_OBSERVATION_ID_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
)
from meetings.schemas import (
    MeetingOutcome,
    MeetingTranscript,
    PlayerId,
    VoteBallot,
)
from orchestrator.replay import LLMCallRecord

# Default roster: p-3 is the impostor, the rest crewmates.
_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_IMPOSTOR: PlayerId = "p-3"
_CREWMATE: PlayerId = "p-1"

# The committed sample reports (single-era until the 17.9 re-record).
_SAMPLES_DIR = Path(__file__).resolve().parents[2] / "replays" / "samples"
_COMMITTED_9P2I_REPORT = _SAMPLES_DIR / "9p2i" / "tournament-eval-report.json"
_COMMITTED_4P1I_REPORT = _SAMPLES_DIR / "4p1i" / "tournament-eval-report.json"


# ---------------------------------------------------------------------------
# Fixture builders -- minimal, focused on what the divert actually reads
# ---------------------------------------------------------------------------


def _ballot(
    *,
    target: PlayerId,
    voter: PlayerId = "p-0",
    rationale_text: str = "",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.9,
        primary_reason_id=None,
        rationale_text=rationale_text,
    )


def _vote_call(*, agent_id: PlayerId, rendered_max: float) -> LLMCallRecord:
    """A vote-prompt LLM call carrying the rendered §4.6 gate line.

    The prompt body mirrors the v5 ``vote_ballot.j2`` render (including the
    line wrap between "is" and the bolded value) so the test exercises the
    same parse the committed replays do.
    """

    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=(
            "## Decision rules\n\n"
            "1. **Gate verdict — already computed for you (DESIGN.md §4.6).**\n"
            "   Your maximum suspicion among the living ejection targets is\n"
            f"   **{rendered_max:.2f}**; the skip threshold is **0.60**.\n"
        ),
        response_text="{}",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _meeting(
    *,
    outcome: MeetingOutcome,
    ejected: PlayerId | None,
    meeting_id: str = "m-0",
    tick: int = 40,
    ballots: tuple[VoteBallot, ...] = (),
    llm_calls: tuple[LLMCallRecord, ...] = (),
) -> MeetingReport:
    return MeetingReport(
        meeting_id=meeting_id,
        tick=tick,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=MeetingTranscript(turns=()),
        ballots=ballots,
        contradictions=(),
        llm_calls=llm_calls,
    )


def _game(
    *,
    meetings: tuple[MeetingReport, ...],
    roles: Mapping[PlayerId, Role] = _ROLES,
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
        failed_calls=(),
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


def _one_meeting_report(meeting: MeetingReport) -> TournamentReport:
    return _tournament(_game(meetings=(meeting,)))


# ---------------------------------------------------------------------------
# The divert -- marker-keyed, role- and verdict-blind
# ---------------------------------------------------------------------------


def test_crew_coerced_skip_diverts_and_is_never_an_inversion() -> None:
    """A crew voter's marker-anchored SKIP is coerced, not a threshold inversion.

    The CONTROL is the same ballot WITHOUT the marker: a crew voter shown a met
    reference line who SKIPs on their own lands in the discretionary-decline
    remainder (post-13.13 the §4.6 line is advisory, so that is sanctioned
    discretion, not a bug). The only difference is the marker, so the pin proves
    the divert is marker-keyed (mirroring the defaulted-class control style) —
    a by-design rewrite must never be filed as a voter's own decline.
    """

    coerced = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2")
                    + "I found p-2 suspicious but cited nothing."
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.75),),
    )

    result = compute_conversion_report(_one_meeting_report(coerced))

    assert result.skip_ballots == 1
    assert result.citation_coerced_skip_ballots == 1
    assert result.missed_skip_ballots == 0
    assert result.threshold_inversions == 0
    assert result.correct_skip_ballots == 0
    assert result.unclassified_skip_ballots == 0

    # CONTROL: identical ballot without the marker -> the voter's own
    # discretionary decline, so it stays in the threshold_inversions remainder.
    control = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text="I found p-2 suspicious but cited nothing.",
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.75),),
    )

    control_result = compute_conversion_report(_one_meeting_report(control))

    assert control_result.threshold_inversions == 1
    assert control_result.citation_coerced_skip_ballots == 0


def test_impostor_coerced_skip_diverts_out_of_the_impostor_bucket() -> None:
    """An impostor's coerced SKIP is a forced eject, not an in-character decline."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_IMPOSTOR,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2") + "I vote p-2."
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_IMPOSTOR, rendered_max=0.80),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.skip_ballots == 1
    assert result.citation_coerced_skip_ballots == 1
    assert result.missed_skip_impostor_voters == 0
    assert result.missed_skip_teammate_coerced == 0
    assert result.missed_skip_ballots == 0


def test_stacked_marker_still_diverts() -> None:
    """The seed-48 ballot B shape: the 16.5 null rides INSIDE the coercion prefix.

    The citation gate is the LAST guard in the manager's ballot chain, so the
    coercion marker is always the OUTERMOST prefix; a stacked
    :data:`~meetings.manager.INVALID_OBSERVATION_ID_MARKER` null sits inside
    it. The anchored match reads the outermost marker and diverts.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_IMPOSTOR,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-6")
                    + INVALID_OBSERVATION_ID_MARKER.format(observation_id="obs p-7:9:4")
                    + "I found p-3. p-6 reported it."
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_IMPOSTOR, rendered_max=0.75),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 1


def test_sub_threshold_coerced_skip_is_never_a_correct_skip() -> None:
    """A forced eject under a MUST-skip render is coerced, not a chosen correct skip."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2") + "stub"
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.30),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 1
    assert result.correct_skip_ballots == 0
    assert result.skip_ballots == 1


def test_coerced_skip_without_vote_prompt_still_diverts() -> None:
    """No rendered verdict -- the marker is the only witness, and it still diverts."""

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2") + "stub"
                ),
            ),
        ),
        llm_calls=(),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 1
    assert result.unclassified_skip_ballots == 0
    assert result.skip_ballots == 1


def test_marker_inside_prose_does_not_divert() -> None:
    """The divert is anchored: a marker not at position 0 classifies normally.

    A crew voter shown a met reference line whose rationale merely mentions the
    marker mid-prose (not as the outermost prefix) was never coerced, so the
    ballot stays their own discretionary decline in the remainder.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=(
                    "quoting the log: "
                    + UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-2")
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.75),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 0
    assert result.threshold_inversions == 1


def test_unquoted_payload_does_not_divert() -> None:
    """The ``{x!r}`` shape pin: a bare (unquoted) target is not the marker.

    The production marker interpolates ``{target!r}`` -- always a quoted repr
    -- so an unquoted payload is a different string that the repr-aware pattern
    must reject, leaving the ballot as the voter's own discretionary decline.
    Built from the imported literal's head/tail, never re-spelled.
    """

    head = UNCITED_ZERO_FLAG_EJECT_MARKER.partition("{")[0]
    tail = UNCITED_ZERO_FLAG_EJECT_MARKER.partition("}")[2]
    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=head + "p-6" + tail + "x",
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.75),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 0
    assert result.threshold_inversions == 1


def test_double_quoted_repr_target_diverts() -> None:
    """The other ``{x!r}`` pin: a target whose repr is double-quoted still matches.

    ``repr("p'6")`` is ``"p'6"`` (double-quoted because the value holds a
    single quote); the repr-aware alternation matches both quote forms, so the
    coerced ballot still diverts and never pollutes the discretionary-decline
    remainder.
    """

    meeting = _meeting(
        outcome="SKIPPED",
        ejected=None,
        ballots=(
            _ballot(
                target="SKIP",
                voter=_CREWMATE,
                rationale_text=(
                    UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p'6") + "stub"
                ),
            ),
        ),
        llm_calls=(_vote_call(agent_id=_CREWMATE, rendered_max=0.75),),
    )

    result = compute_conversion_report(_one_meeting_report(meeting))

    assert result.citation_coerced_skip_ballots == 1
    assert result.threshold_inversions == 0


# ---------------------------------------------------------------------------
# The extended partition invariant (the coerced bucket joins the skip sum)
# ---------------------------------------------------------------------------


def test_conversion_model_accepts_coerced_wired_into_skip_sum() -> None:
    """correct + missed + unclassified + citation_coerced == skip_ballots."""

    report = ConversionReport(
        total_ejections=0,
        impostor_ejections=0,
        ejection_accuracy=None,
        impostor_accused_meetings=0,
        impostor_accused_conversions=0,
        impostor_accused_conversion_rate=None,
        skip_ballots=1,
        correct_skip_ballots=0,
        missed_skip_ballots=0,
        unclassified_skip_ballots=0,
        citation_coerced_skip_ballots=1,
        missed_skip_impostor_voters=0,
        missed_skip_teammate_coerced=0,
        missed_skip_invalid_target=0,
        threshold_inversions=0,
    )

    assert report.citation_coerced_skip_ballots == 1
    assert report.skip_ballots == 1


def test_conversion_model_rejects_skip_sum_missing_coerced() -> None:
    """A coerced ballot left out of the skip sum fails the extended invariant."""

    with pytest.raises(ValidationError, match="citation_coerced"):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=None,
            skip_ballots=1,
            correct_skip_ballots=0,
            missed_skip_ballots=0,
            unclassified_skip_ballots=0,
            citation_coerced_skip_ballots=0,
            missed_skip_impostor_voters=0,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


def test_conversion_model_rejects_negative_coerced() -> None:
    with pytest.raises(ValidationError, match="non-negative"):
        ConversionReport(
            total_ejections=0,
            impostor_ejections=0,
            ejection_accuracy=None,
            impostor_accused_meetings=0,
            impostor_accused_conversions=0,
            impostor_accused_conversion_rate=None,
            skip_ballots=0,
            correct_skip_ballots=0,
            missed_skip_ballots=0,
            unclassified_skip_ballots=0,
            citation_coerced_skip_ballots=-1,
            missed_skip_impostor_voters=0,
            missed_skip_teammate_coerced=0,
            missed_skip_invalid_target=0,
            threshold_inversions=0,
        )


# ---------------------------------------------------------------------------
# Committed-bytes pins (the 2/99 pin, moved here per the task contract)
# ---------------------------------------------------------------------------


def test_committed_9p2i_recompute_pins_the_coerced_bucket() -> None:
    """The coerced-bucket pin: the baseline-6 re-record carries one coerced SKIP.

    The meeting-layer graduation re-record (four levers unconditional,
    impostor_roll_call OFF) produced a single uncited zero-flag EJECT->SKIP
    coercion prefix, so ``citation_coerced_skip_ballots`` reads 1 and exactly one
    ballot carries the marker head. The STORED conversion block was regenerated at
    baseline 6 with the divert already applied, so recompute agrees with it
    exactly.
    """

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )

    # STORED block: the regenerated baseline-6 partition (divert already applied).
    assert report.conversion.citation_coerced_skip_ballots == 1
    assert report.conversion.missed_skip_ballots == 96  # was 129
    assert report.conversion.threshold_inversions == 46  # was 87
    assert report.conversion.missed_skip_impostor_voters == 48  # was 41

    # RECOMPUTE: the divert populates the coerced bucket, matching the STORED block.
    result = compute_conversion_report(report.report.games)

    assert result.total_ejections == 99  # was 101
    assert result.impostor_ejections == 85  # was 78
    assert result.ejection_accuracy == pytest.approx(85 / 99)  # was 78 / 101
    assert result.impostor_accused_meetings == 122  # was 134
    assert result.impostor_accused_conversions == 85  # was 78
    assert result.impostor_accused_conversion_rate == pytest.approx(85 / 122)  # was 78 / 134
    assert result.skip_ballots == 333  # was 451
    assert result.correct_skip_ballots == 236  # was 321
    assert result.missed_skip_ballots == 96  # was 129
    assert result.unclassified_skip_ballots == 0
    assert result.citation_coerced_skip_ballots == 1
    assert result.missed_skip_impostor_voters == 48  # was 41
    assert result.missed_skip_teammate_coerced == 2  # was 0
    assert result.missed_skip_invalid_target == 2  # was 1
    assert result.threshold_inversions == 46  # was 87

    # Exactly one ballot carries the marker head: the baseline-6 bytes have a
    # single coerced SKIP, so the divert scan yields one entry.
    head = UNCITED_ZERO_FLAG_EJECT_MARKER.partition("{")[0]
    diverted = [
        (game.game_id, ballot.voter, game.roles[ballot.voter])
        for game in report.report.games
        for meeting in game.meetings
        for ballot in meeting.ballots
        if ballot.target == "SKIP" and ballot.rationale_text.startswith(head)
    ]
    assert len(diverted) == 1


def test_committed_4p1i_recompute_has_no_coerced_and_is_unchanged() -> None:
    """The 4p1i bytes carry no coercion marker; every bucket reads as before."""

    report = TournamentEvalReport.model_validate_json(
        _COMMITTED_4P1I_REPORT.read_text(encoding="utf-8")
    )
    result = compute_conversion_report(report.report.games)

    assert result.citation_coerced_skip_ballots == 0
    assert result.skip_ballots == 61  # was 90
    assert result.correct_skip_ballots == 54  # was 88
    assert result.missed_skip_ballots == 7  # was 2
    assert result.unclassified_skip_ballots == 0
    assert result.missed_skip_impostor_voters == 7  # was 1
    assert result.missed_skip_invalid_target == 0
    assert result.threshold_inversions == 0  # was 1
    assert result.total_ejections == 21  # was 12
    assert result.impostor_ejections == 20  # was 10


@pytest.mark.parametrize(
    ("path", "expected_coerced"),
    [(_COMMITTED_9P2I_REPORT, 1), (_COMMITTED_4P1I_REPORT, 0)],
)
def test_extended_invariant_holds_over_every_committed_meeting(
    path: Path, expected_coerced: int
) -> None:
    """A DoD item: the extended partition invariant holds per committed meeting.

    For every committed game and every meeting, a single-meeting slice is fed
    to :func:`compute_conversion_report`; construction itself asserts the
    extended invariant (the model validator raises on any inconsistency). The
    per-meeting coerced counts accumulate to the whole-report total.
    """

    report = TournamentEvalReport.model_validate_json(path.read_text(encoding="utf-8"))
    total_coerced = 0
    for game in report.report.games:
        for meeting in game.meetings:
            slice_game = game.model_copy(update={"meetings": (meeting,)})
            per_meeting = compute_conversion_report([slice_game])
            total_coerced += per_meeting.citation_coerced_skip_ballots

    assert total_coerced == expected_coerced


# ---------------------------------------------------------------------------
# The Task-19.5 by-cause recount (the fixture behind the re-doctrine)
# ---------------------------------------------------------------------------

# The recount tables over the two committed sample sets, measured from the
# committed bytes. The ml_corpus tables are recorded in the PR rather than
# pinned here (this file's committed-bytes pins are the samples sets).
_EXPECTED_RECOUNTS: Mapping[str, ThresholdInversionRecount] = {
    "9p2i": ThresholdInversionRecount(
        threshold_inversions=87,
        marker_free=87,
        rendered_at_threshold=36,
        rendered_below_0_70=81,
        rendered_0_70_to_0_80=5,
        rendered_at_or_above_0_80=1,
        in_skipped_meetings=78,
        in_crew_ejected_meetings=8,
        in_impostor_ejected_meetings=1,
    ),
    "4p1i": ThresholdInversionRecount(
        threshold_inversions=1,
        marker_free=1,
        rendered_at_threshold=0,
        rendered_below_0_70=1,
        rendered_0_70_to_0_80=0,
        rendered_at_or_above_0_80=0,
        in_skipped_meetings=1,
        in_crew_ejected_meetings=0,
        in_impostor_ejected_meetings=0,
    ),
}


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (_COMMITTED_9P2I_REPORT, _EXPECTED_RECOUNTS["9p2i"]),
        (_COMMITTED_4P1I_REPORT, _EXPECTED_RECOUNTS["4p1i"]),
    ],
    ids=["9p2i", "4p1i"],
)
def test_committed_recount_pins_the_by_cause_table(
    path: Path, expected: ThresholdInversionRecount
) -> None:
    """The Task-19.5 by-cause table over committed bytes — the pinned fixture
    behind the ``threshold_inversions`` re-doctrine.

    The triage proposed "unrecognized citation-gated SKIPs" as the mechanism
    behind the committed 87; the recount refutes it over the bytes.
    ``marker_free == threshold_inversions`` on both sets is the load-bearing
    cell: it pins that NO by-design rewrite (invalid target, teammate coercion,
    parse default, ballot redirect, citation gate) leaks into the remainder, so
    what is left is genuinely the voter's own decision. The rendered bands then
    say what kind of decision it was — on samples/9p2i the mass sits AT the
    advisory line (81 of 87 below 0.70, 36 of those exactly at the 0.60
    reference) rather than deep above it, which is a conservatism reading, not
    a disobedience reading. The two ml_corpus tables are recorded in the PR.

    Equality against a whole :class:`ThresholdInversionRecount` literal (not
    field-by-field asserts) makes a new cell a loud failure rather than a
    silently unpinned one.
    """

    report = TournamentEvalReport.model_validate_json(path.read_text(encoding="utf-8"))

    recount = recount_threshold_inversions(report.report.games)

    assert recount == expected
    # Cross-pin: the recount folds the SAME per-ballot classification the
    # published census folds, so its total cannot drift from the stored block.
    assert recount.threshold_inversions == report.conversion.threshold_inversions
