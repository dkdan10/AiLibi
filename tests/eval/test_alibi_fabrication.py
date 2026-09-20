"""Unit tests for the alibi-fabrication-rate metric (DESIGN.md §11.3, §5.4).

Fixtures are built by instantiating the report-schema and meeting-schema models
directly -- this metric is a pure analyzer, so no tournament run, orchestrator,
or LLM is involved. The tests pin the chosen **subject-membership** join rule in
both directions (survived vs caught), its accepted cross-author failure mode,
the author-not-subject denominator semantics, per-meeting multiplicity dedup,
and partial-replay robustness.

**The None-iff-undefined rate convention (Task 19.5).** ``survival_rate`` is
``None`` — not ``0.0`` — when no impostor filed an alibi: the rate is
*undefined*, and the pre-19.5 division-safe ``0.0`` is retired because it read
as "impostors filed alibis and NONE survived", the strongest possible detector
result, when it actually meant there was nothing to measure
(audits/audit-phase-19-triage.md §7 item 6). The zero-denominator fixtures
below therefore pin ``None``, and the model's validator enforces the
biconditional fail-loud in both directions.
"""

from __future__ import annotations

import functools
from collections.abc import Mapping
from typing import Final, Literal

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.alibi_fabrication import (
    AlibiFabricationReport,
    compute_alibi_fabrication_rate,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    Claim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
)

# A roster with one impostor and three crewmates; the default for fixtures where
# the specific assignment does not matter. ``imp`` is the impostor.
_ROLES: Mapping[PlayerId, Role] = {
    "imp": "IMPOSTOR",
    "crew-a": "CREWMATE",
    "crew-b": "CREWMATE",
    "crew-c": "CREWMATE",
}

_ZERO_COST = GameCostSummary(
    total_cost_usd=0.0,
    total_input_tokens=0,
    total_output_tokens=0,
    by_model={},
)


# ---------------------------------------------------------------------------
# Fixture builders -- minimal, metric-relevant payloads only
# ---------------------------------------------------------------------------


def _alibi(
    *,
    subject: PlayerId,
    from_tick: int = 10,
    to_tick: int = 20,
    room: str = "STORAGE",
    evidence: tuple[str, ...] = (),
) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        route=(AlibiSegment(room=room, from_tick=from_tick, to_tick=to_tick),),
        evidence=evidence,
    )


def _accusation(*, against: PlayerId) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=0.5, reason="suspicious"
    )


def _report(
    *, author: PlayerId, claims: tuple[Claim, ...] = (), tick: int = 30
) -> MeetingTurn:
    """An ``opening`` chain turn authored by ``author`` (§5.2)."""

    return MeetingTurn(
        turn_id=f"{author}:turn-{tick}",
        turn_index=0,
        speaker=author,
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=claims,
        free_text="",
    )


def _statement(
    *,
    speaker: PlayerId,
    claims: tuple[Claim, ...] = (),
    statement_id: str = "s-1",
    tick: int = 30,
) -> MeetingTurn:
    """A ``reply`` chain turn spoken by ``speaker`` (§5.2)."""

    return MeetingTurn(
        turn_id=statement_id,
        turn_index=1,
        speaker=speaker,
        turn_kind="reply",
        reply_to=None,
        observations=(),
        claims=claims,
        free_text="",
    )


def _contradiction(
    *,
    kind: Literal["alibi_conflict", "alibi_vs_sighting"],
    subjects: tuple[PlayerId, ...],
    contradiction_id: str = "c-1",
    event_a_id: str = "ev-a",
    event_b_id: str = "ev-b",
) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id=contradiction_id,
        kind=kind,
        event_a_id=event_a_id,
        event_b_id=event_b_id,
        subjects=subjects,
        description="",
    )


def _meeting(
    *,
    reports: tuple[MeetingTurn, ...] = (),
    statements: tuple[MeetingTurn, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    meeting_id: str = "m-0",
    tick: int = 30,
) -> MeetingReport:
    # One ordered chain (DESIGN.md §5.2): opening ``reports`` turn(s) then any
    # ``statements`` (reply / opt-in) turns. The alibi metric reads each turn's
    # ``speaker`` (author) + alibi claims, so the concatenation is equivalent to
    # the old (reports, statements) split.
    return MeetingReport(
        meeting_id=meeting_id,
        tick=tick,
        triggered_by="crew-a",
        trigger="report",
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=tuple(reports) + tuple(statements)),
        ballots=(),
        contradictions=contradictions,
        llm_calls=(),
    )


def _game(
    *,
    meetings: tuple[MeetingReport, ...],
    roles: Mapping[PlayerId, Role] = _ROLES,
    game_id: str = "game-0",
    seed: int = 0,
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=None,
        reason="",
        final_tick=None,
        roles=roles,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=(),
        prompt_versions={},
        cost=_ZERO_COST,
    )


def _tournament(*games: GameReport) -> TournamentReport:
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=games,
        seeds_used=tuple(g.seed for g in games),
    )


# ---------------------------------------------------------------------------
# Survived vs caught (the core join, both directions)
# ---------------------------------------------------------------------------


def test_impostor_self_alibi_with_no_contradiction_survives() -> None:
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),)
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=1, survived=1, survival_rate=1.0
    )


def test_impostor_alibi_caught_by_alibi_conflict() -> None:
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),),
                    contradictions=(
                        _contradiction(kind="alibi_conflict", subjects=("imp",)),
                    ),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=1, survived=0, survival_rate=0.0
    )


def test_impostor_alibi_caught_by_alibi_vs_sighting() -> None:
    # The second alibi_* kind also catches: both kinds feed the caught-subject set.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),),
                    contradictions=(
                        _contradiction(kind="alibi_vs_sighting", subjects=("imp",)),
                    ),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report).survived == 0


def test_contradiction_about_other_subject_does_not_catch() -> None:
    # The impostor's alibi is about ``imp``; the only contradiction names a
    # different subject, so subject-membership does not match -> survives.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),),
                    contradictions=(
                        _contradiction(kind="alibi_conflict", subjects=("crew-b",)),
                    ),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report).survived == 1


# ---------------------------------------------------------------------------
# Author (not subject) defines an "impostor alibi"
# ---------------------------------------------------------------------------


def test_crewmate_alibi_is_excluded_from_numerator_and_denominator() -> None:
    # A crewmate self-alibi is not counted at all -- even when a contradiction
    # names that crewmate, it stays out of the denominator.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(author="crew-a", claims=(_alibi(subject="crew-a"),)),
                    ),
                    contradictions=(
                        _contradiction(kind="alibi_conflict", subjects=("crew-a",)),
                    ),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=0, survived=0, survival_rate=None
    )


def test_impostor_alibi_about_another_player_counts_but_crewmate_about_impostor_does_not() -> (  # noqa: E501
    None
):
    # "Impostor alibi" is by AUTHOR role, not subject. The impostor's alibi
    # *about* crew-a counts; crew-a's alibi *about* the impostor does not.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(author="imp", claims=(_alibi(subject="crew-a"),)),
                        _report(author="crew-a", claims=(_alibi(subject="imp"),)),
                    ),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=1, survived=1, survival_rate=1.0
    )


# ---------------------------------------------------------------------------
# Cross-author conflict: the accepted subject-membership failure mode
# ---------------------------------------------------------------------------


def test_cross_author_conflict_falsely_counts_impostor_alibi_as_caught() -> None:
    # The accepted false positive of subject-membership: crew-a and crew-b file
    # conflicting alibis ABOUT the impostor, producing an alibi_conflict that
    # names ``imp`` -- but the impostor's OWN alibi is not one of the conflicting
    # events. event_a_id/event_b_id point at the crewmates' alibis; the metric
    # reads only ``subjects``, so the impostor's self-alibi is counted as caught.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(
                            author="imp",
                            claims=(_alibi(subject="imp", room="STORAGE"),),
                        ),
                        _report(
                            author="crew-a",
                            claims=(_alibi(subject="imp", room="ELECTRICAL"),),
                        ),
                        _report(
                            author="crew-b",
                            claims=(_alibi(subject="imp", room="MEDBAY"),),
                        ),
                    ),
                    contradictions=(
                        _contradiction(
                            kind="alibi_conflict",
                            subjects=("imp",),
                            event_a_id="report:crew-a@30:claim:0",
                            event_b_id="report:crew-b@30:claim:0",
                        ),
                    ),
                ),
            )
        )
    )

    # Only the impostor-authored alibi is in the denominator (the crewmate
    # alibis are excluded), and subject-membership marks it caught.
    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=1, survived=0, survival_rate=0.0
    )


# ---------------------------------------------------------------------------
# Multiplicity: dedup by value tuple, per meeting
# ---------------------------------------------------------------------------


def test_duplicate_alibi_in_report_and_statement_counts_once() -> None:
    # Same (author, subject, from_tick, to_tick, room) restated in a report and
    # a statement (with different evidence, which is excluded from the key) is a
    # single alibi.
    alibi_report = _alibi(subject="imp", evidence=("scan_task",))
    alibi_statement = _alibi(subject="imp", evidence=("camera_log",))
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(_report(author="imp", claims=(alibi_report,)),),
                    statements=(_statement(speaker="imp", claims=(alibi_statement,)),),
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=1, survived=1, survival_rate=1.0
    )


def test_distinct_alibis_by_same_impostor_count_separately() -> None:
    # Different rooms -> different value tuples -> two alibis, both surviving.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(
                            author="imp",
                            claims=(
                                _alibi(subject="imp", room="STORAGE"),
                                _alibi(subject="imp", room="MEDBAY"),
                            ),
                        ),
                    )
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=2, survived=2, survival_rate=1.0
    )


def test_same_tuple_in_two_meetings_counts_twice() -> None:
    # Dedup is per meeting (the detector runs per transcript), so the identical
    # tuple in two separate meetings is two alibis.
    duplicated = (_report(author="imp", claims=(_alibi(subject="imp"),)),)
    report = _tournament(
        _game(
            meetings=(
                _meeting(reports=duplicated, meeting_id="m-0"),
                _meeting(reports=duplicated, meeting_id="m-1"),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=2, survived=2, survival_rate=1.0
    )


# ---------------------------------------------------------------------------
# Partial-replay robustness
# ---------------------------------------------------------------------------


def test_meeting_with_no_alibis_contributes_nothing() -> None:
    # An impostor participates but files only a (non-alibi) accusation.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(author="imp", claims=(_accusation(against="crew-a"),)),
                    )
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=0, survived=0, survival_rate=None
    )


def test_no_impostor_participants_contributes_nothing() -> None:
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(author="crew-a", claims=(_alibi(subject="crew-a"),)),
                        _report(author="crew-b", claims=(_alibi(subject="crew-c"),)),
                    )
                ),
            )
        )
    )

    assert compute_alibi_fabrication_rate(report).total_impostor_alibis == 0


def test_game_with_no_meetings_contributes_nothing() -> None:
    report = _tournament(_game(meetings=()))

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=0, survived=0, survival_rate=None
    )


def test_empty_tournament_has_undefined_rate() -> None:
    # No games -> no impostor alibis -> the rate is UNDEFINED (``None``), not
    # 0.0: there was nothing to measure, so the metric must not report the
    # strongest possible detector result (Task 19.5).
    report = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=()
    )

    assert compute_alibi_fabrication_rate(report) == AlibiFabricationReport(
        total_impostor_alibis=0, survived=0, survival_rate=None
    )


def test_author_absent_from_roles_fails_loud() -> None:
    # ``roles`` covers every player by construction; an alibi author missing
    # from it is a malformed report and must raise, not silently count as crew.
    report = _tournament(
        _game(
            meetings=(
                _meeting(
                    reports=(
                        _report(author="ghost", claims=(_alibi(subject="ghost"),)),
                    )
                ),
            ),
            roles={"crew-a": "CREWMATE"},
        )
    )

    with pytest.raises(KeyError, match="ghost"):
        compute_alibi_fabrication_rate(report)


# ---------------------------------------------------------------------------
# Aggregation across games / meetings
# ---------------------------------------------------------------------------


def test_multi_game_aggregation_yields_fractional_rate() -> None:
    # Game A: one survived + one caught. Game B (a different roster/impostor):
    # one survived. Total 3 alibis, 2 survived -> rate 2/3.
    game_a = _game(
        game_id="game-a",
        seed=1,
        meetings=(
            _meeting(
                meeting_id="a-0",
                reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),),
            ),
            _meeting(
                meeting_id="a-1",
                reports=(_report(author="imp", claims=(_alibi(subject="imp"),)),),
                contradictions=(
                    _contradiction(kind="alibi_conflict", subjects=("imp",)),
                ),
            ),
        ),
    )
    game_b = _game(
        game_id="game-b",
        seed=2,
        roles={"q-imp": "IMPOSTOR", "q-crew": "CREWMATE"},
        meetings=(
            _meeting(
                meeting_id="b-0",
                reports=(_report(author="q-imp", claims=(_alibi(subject="q-imp"),)),),
            ),
        ),
    )

    result = compute_alibi_fabrication_rate(_tournament(game_a, game_b))

    assert result.total_impostor_alibis == 3
    assert result.survived == 2
    assert result.survival_rate == pytest.approx(2 / 3)


# ---------------------------------------------------------------------------
# Result model shape
# ---------------------------------------------------------------------------


def test_result_model_is_frozen() -> None:
    result = compute_alibi_fabrication_rate(
        TournamentReport(format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=())
    )

    with pytest.raises(ValidationError):
        result.survived = 5


def test_zero_denominator_with_a_numeric_rate_fails_loud() -> None:
    """The None-iff-undefined biconditional, forward direction (Task 19.5).

    The retired ``0.0`` cannot be smuggled back in by a caller: with no
    impostor alibis the rate is undefined, so any float — including the old
    division-safe 0.0 — is a construction error, not a papered-over value
    (AGENTS.md "no silent fallbacks").
    """

    with pytest.raises(ValidationError, match="undefined, not 0.0"):
        AlibiFabricationReport(total_impostor_alibis=0, survived=0, survival_rate=0.0)


def test_nonzero_denominator_without_a_rate_fails_loud() -> None:
    """The biconditional's other direction: a defined rate may not be ``None``.

    ``None`` means undefined, so it must not double as "not computed" once
    impostor alibis exist.
    """

    with pytest.raises(ValidationError, match="must be set"):
        AlibiFabricationReport(total_impostor_alibis=1, survived=1, survival_rate=None)


def test_out_of_range_rate_fails_loud() -> None:
    with pytest.raises(ValidationError, match=r"must be in \[0.0, 1.0\]"):
        AlibiFabricationReport(total_impostor_alibis=2, survived=1, survival_rate=1.5)


def test_survived_exceeding_the_denominator_fails_loud() -> None:
    with pytest.raises(ValidationError, match="cannot exceed total_impostor_alibis"):
        AlibiFabricationReport(total_impostor_alibis=1, survived=2, survival_rate=1.0)


# ---------------------------------------------------------------------------
# Round 5: the multiplicity dedup keys the ACCOUNT, not the narration
# ---------------------------------------------------------------------------

# Two impostors, so the caught/survived split is visible in the rate: ``imp``
# restates its own account (the dedup under test) and ``imp-2`` is caught.
_TWO_IMPOSTOR_ROLES: Mapping[PlayerId, Role] = {
    "imp": "IMPOSTOR",
    "imp-2": "IMPOSTOR",
    "crew-a": "CREWMATE",
}

_ENVELOPE: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="STORAGE", from_tick=2, to_tick=14),
)
_ONE_STAY: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="STORAGE", from_tick=2, to_tick=8),
)
_TWO_STAYS: Final[tuple[AlibiSegment, ...]] = (
    AlibiSegment(room="STORAGE", from_tick=2, to_tick=6),
    AlibiSegment(room="CAFETERIA", from_tick=7, to_tick=11),
)


def _cuts_of_one_stay(stay: AlibiSegment) -> tuple[tuple[AlibiSegment, ...], ...]:
    """Every narration of ONE continuous stay -- all ``2 ** (n - 1)`` of them.

    The enumeration ``tests/meetings/test_contradictions.py`` runs against the
    detectors, restated here for the metric: a published rate must be as blind
    to the cut as a flag is.
    """

    boundaries = stay.to_tick - stay.from_tick
    shapes: list[tuple[AlibiSegment, ...]] = []
    for mask in range(1 << boundaries):
        legs: list[AlibiSegment] = []
        start = stay.from_tick
        for offset in range(boundaries):
            if mask >> offset & 1:
                legs.append(
                    AlibiSegment(
                        room=stay.room, from_tick=start, to_tick=stay.from_tick + offset
                    )
                )
                start = stay.from_tick + offset + 1
        legs.append(AlibiSegment(room=stay.room, from_tick=start, to_tick=stay.to_tick))
        shapes.append(tuple(legs))
    return tuple(shapes)


def _recuts_of(route: tuple[AlibiSegment, ...]) -> tuple[tuple[AlibiSegment, ...], ...]:
    """Every re-cut of ``route``: the cross product of each stay's own cuts."""

    shapes: tuple[tuple[AlibiSegment, ...], ...] = ((),)
    for stay in route:
        shapes = tuple(
            (*prefix, *legs) for prefix in shapes for legs in _cuts_of_one_stay(stay)
        )
    return shapes


def _route_alibi(*, subject: PlayerId, route: tuple[AlibiSegment, ...]) -> AlibiClaim:
    return AlibiClaim(type="alibi", subject=subject, route=route)


def _restated(
    account: tuple[AlibiSegment, ...], restatement: tuple[AlibiSegment, ...]
) -> AlibiFabricationReport:
    """``imp`` states ``account`` and restates it as ``restatement``.

    A second impostor files an alibi the meeting's contradiction catches, so a
    change in ``imp``'s dedup shows up in ``survival_rate`` and not only in the
    denominator.
    """

    meeting = _meeting(
        reports=(
            _report(author="imp", claims=(_route_alibi(subject="imp", route=account),)),
        ),
        statements=(
            _statement(
                speaker="imp",
                claims=(_route_alibi(subject="imp", route=restatement),),
                statement_id="s-1",
            ),
            _statement(
                speaker="imp-2",
                claims=(
                    _route_alibi(
                        subject="imp-2",
                        route=(AlibiSegment(room="LABS", from_tick=3, to_tick=5),),
                    ),
                ),
                statement_id="s-2",
            ),
        ),
        contradictions=(_contradiction(kind="alibi_vs_sighting", subjects=("imp-2",)),),
    )
    return compute_alibi_fabrication_rate(
        _tournament(_game(meetings=(meeting,), roles=_TWO_IMPOSTOR_ROLES))
    )


class TestReCuttingARestatementDoesNotMoveTheRate:
    """A restatement that re-cuts one stay is the SAME alibi, so it counts once.

    The per-meeting multiplicity dedup used to key the legs AS STATED, which is
    a narration rather than an account: an impostor who restated its own alibi
    verbatim was deduped, and the same impostor restating it with one extra
    full stop was counted twice. ``total_impostor_alibis`` and
    ``survival_rate`` are published -- they reach the process scorecard, the
    prompt-regression metrics, the served eval routes and the tournament
    dashboard -- so that was a figure the ACCUSED was choosing.

    Exhaustive over every ``2 ** (n - 1)`` narration of each stay, with the
    account stated once as a single continuous stay and once as a route with a
    GENUINE room change.
    """

    @pytest.mark.parametrize(
        ("name", "account"), (("one_stay", _ONE_STAY), ("two_stays", _TWO_STAYS))
    )
    def test_every_recut_restatement_reads_identically(
        self, name: str, account: tuple[AlibiSegment, ...]
    ) -> None:
        baseline = _restated(account, account)
        # Not a vacuous baseline: the verbatim restatement is deduped, the
        # second impostor is caught, and the rate is defined.
        assert (baseline.total_impostor_alibis, baseline.survived) == (2, 1)

        recuts = _recuts_of(account)
        assert len(recuts) == functools.reduce(
            lambda total, stay: total * (1 << (stay.to_tick - stay.from_tick)),
            account,
            1,
        )
        assert account in recuts

        for recut in recuts:
            assert _restated(account, recut) == baseline, (
                name,
                [(leg.room, leg.from_tick, leg.to_tick) for leg in recut],
            )

    def test_a_recut_that_moves_the_surviving_spelling_is_still_one_alibi(
        self,
    ) -> None:
        # Why the key canonicalises the room as well as coalescing the stays.
        # A merged stay keeps the FIRST leg's room TEXT, so where the speaker
        # cuts decides which spelling survives: "cafeteria 2-4" + "CAFETERIA
        # 5-8" coalesces to "cafeteria 2-8" and the mirror cut to "CAFETERIA
        # 2-8". On the raw text those are two keys and the restatement counts
        # again -- the same dial, reached through the spelling instead of the
        # geometry. ``meetings.transcript._claim_route_key`` canonicalises for
        # exactly this reason and the metric reads the same normalisation.
        account = (AlibiSegment(room="CAFETERIA", from_tick=2, to_tick=8),)
        lower_first = (
            AlibiSegment(room="cafeteria", from_tick=2, to_tick=4),
            AlibiSegment(room="CAFETERIA", from_tick=5, to_tick=8),
        )
        upper_first = (
            AlibiSegment(room="CAFETERIA", from_tick=2, to_tick=4),
            AlibiSegment(room="cafeteria", from_tick=5, to_tick=8),
        )
        baseline = _restated(account, account)
        assert _restated(account, lower_first) == baseline
        assert _restated(account, upper_first) == baseline

    def test_a_genuinely_different_account_still_counts_twice(self) -> None:
        # The control the property needs: coalescing merges a CUT, never two
        # different claims. A restatement naming another room is a second alibi.
        other = (AlibiSegment(room="MEDBAY", from_tick=2, to_tick=8),)
        differing = _restated(_ONE_STAY, other)
        assert differing.total_impostor_alibis == 3
        assert differing.survived == 2


def test_the_round_five_restatement_exhibit() -> None:
    """The verifier's repro, as stated: ``STORAGE 2-14`` restated three ways.

    Keyed on the legs as stated, the verbatim restatement read ``total=2
    survived=1 rate=0.5`` while the identical account restated as ``2-7`` plus
    ``8-14``, or as thirteen one-tick legs, read ``total=3 survived=2
    rate=0.667`` -- all three with ``meetings.transcript._claim_route_key``
    already agreeing that they are one account.
    """

    split = (
        AlibiSegment(room="STORAGE", from_tick=2, to_tick=7),
        AlibiSegment(room="STORAGE", from_tick=8, to_tick=14),
    )
    one_tick_legs = tuple(
        AlibiSegment(room="STORAGE", from_tick=tick, to_tick=tick)
        for tick in range(2, 15)
    )

    for restatement in (_ENVELOPE, split, one_tick_legs):
        result = _restated(_ENVELOPE, restatement)
        assert (result.total_impostor_alibis, result.survived) == (2, 1)
        assert result.survival_rate == 0.5
