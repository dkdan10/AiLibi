"""Tests for eval/deception_instruments.py (Task 18.1).

Two layers, mirroring tests/eval/test_funnel_pooling.py:

* committed-bytes PIN tests -- ``compute_deception_instruments`` over the
  committed corpus / sample sets, with EVERY field pinned. The corpus 9p2i pins
  are the baseline-6 census (549 / 0 / 74 / 176 / 31 / 248 / 161 / 23 / 463 / 150,
  Task 18.13), the primary anchor;
* scripted-fixture UNIT tests over hand-built ``_VJMeeting`` carriers exercising
  each private fold and the Wilson / advisory helpers in isolation.

The corpus 9p2i walk (150 memory-augmented game walks) is the expensive fixture;
it runs once per worker, through the shared cache in tests/_helpers/committed.py.
The corpus 4p1i walk is cheap (tiny 4-player games) and kept as the one-impostor
degenerate anchor.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import PlayerId, Role
from eval.deception_instruments import (
    DeceptionInstrumentsReport,
    RareEventCell,
    _grounded_split,
    _impostor_accusation_partition,
    _impostor_vouch_census,
    _is_frame_conversion,
    _rare_event_cell,
    _wilson_interval,
    compute_deception_instruments,
)
from eval.funnel import _VJMeeting
from meetings.schemas import (
    AccusationClaim,
    Claim,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    SightingRecord,
)
from meetings.transcript import MeetingTriggerKind
from tests._helpers.committed import deception_instruments_report

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS_NINE = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_CORPUS_FOUR = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


# --------------------------------------------------------------------------- #
# Committed-bytes pin fixtures + a full-field checker                          #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def corpus_nine() -> DeceptionInstrumentsReport:
    return deception_instruments_report(_CORPUS_NINE)


@pytest.fixture(scope="session")
def corpus_four() -> DeceptionInstrumentsReport:
    return deception_instruments_report(_CORPUS_FOUR)


@pytest.fixture(scope="session")
def sample_nine() -> DeceptionInstrumentsReport:
    return deception_instruments_report(_NINE)


@pytest.fixture(scope="session")
def sample_four() -> DeceptionInstrumentsReport:
    return deception_instruments_report(_FOUR)


def _check_cell(
    cell: RareEventCell,
    *,
    numerator: int,
    denominator: int,
    rate: float | None,
    wilson_low: float | None,
    wilson_high: float | None,
    advisory: bool,
) -> None:
    assert cell.numerator == numerator
    assert cell.denominator == denominator
    assert cell.advisory is advisory
    if rate is None:
        assert cell.rate is None
        assert cell.wilson_low is None
        assert cell.wilson_high is None
        return
    assert cell.rate == pytest.approx(rate)
    assert cell.wilson_low == pytest.approx(wilson_low, abs=1e-12)
    assert cell.wilson_high == pytest.approx(wilson_high)


def _check_report(
    report: DeceptionInstrumentsReport, expected: dict[str, object]
) -> None:
    """Pin every scalar / rate field; the two rare-event cells are pinned apart."""

    for name, value in expected.items():
        actual = getattr(report, name)
        if isinstance(value, float):
            assert actual == pytest.approx(value), name
        else:
            assert actual == value, name


# --------------------------------------------------------------------------- #
# Corpus 9p2i -- the audit §3.1 census (primary pin)                           #
# --------------------------------------------------------------------------- #


def test_corpus_nine_is_the_audit_census(
    corpus_nine: DeceptionInstrumentsReport,
) -> None:
    r = corpus_nine
    assert r.replay_set_dir == str(_CORPUS_NINE)
    _check_report(
        r,
        {
            "num_players": 9,
            "num_impostors": 2,
            "tasks_per_crewmate": 2,
            "games_total": 150,
            "meetings_total": 432,
            # accusation census (549 frame, 0 teammate, 0 self)
            "impostor_accusations_total": 517,
            "frame_attempts": 517,
            "impostor_self_accusations": 0,
            "frame_attempt_meetings": 426,
            # eject-outcome context (54 / 248 / 161 == 463)
            "crew_ejected_meetings": 26,
            "impostor_ejected_meetings": 254,
            "no_eject_meetings": 152,
            # false-vouch census. NOTE the two DISTINCT denominators below — the
            # audit-phase-18-baseline-6.md §2 row ("34 (grounded 14 / fabricated 4,
            # grounded-share 0.778)") welds them into one cell and so reads as if 34
            # split into 14+4, leaving 16 unaccounted; it does not. There are two
            # separate partitions, and on this corpus BOTH close exactly:
            #   * OBSERVATIONS: 74 false-vouch saw_player observations, of 602
            #     impostor vouch observations, split by their subject's chokepoint
            #     verdict into 57 grounded + 17 fabricated == 74.
            #   * SUBJECT EVENTS: 63 events, split 47 grounded + 16 fabricated == 63,
            #     and the grounded SHARE (0.7460) is over the 63, never the 74.
            "vouch_observations_impostor": 373,
            "false_vouch_saw_player_observations": 42,
            "false_vouch_saw_player_rate": 0.1126005361930295,
            "corroboration_claims_total": 1050,
            "corroboration_claims_impostor": 155,
            "false_vouch_corroborations": 31,
            "false_vouch_corroboration_rate": 0.2,
            "false_vouches_total": 73,
            # grounded split (production chokepoint, saw_player channel): 47+16 == 63
            "false_vouch_subject_events": 36,
            "false_vouch_grounded": 30,
            "false_vouch_fabricated": 6,
            "false_vouch_grounded_share": 0.8333333333333334,
            # observation-level companion join: partitions the 74 observations
            # by their subject's chokepoint verdict (57 + 17 == 74).
            "false_vouch_grounded_subject_observations": 36,
            "false_vouch_fabricated_subject_observations": 6,
        },
    )
    # teammate-non-accusation index: 0 of 549, advisory, Wilson pinned. The
    # teammate firewall holds at the largest denominator it has ever been read at.
    _check_cell(
        r.teammate_accusations,
        numerator=0,
        denominator=517,
        rate=0.0,
        wilson_low=0.0,
        wilson_high=0.007375754932017718,
        advisory=True,
    )
    # frame conversions: 23 of 437 frame-attempt meetings — the FIRST POWERED read
    # of this cell. The numerator clears the rare-event advisory threshold (>7), so
    # advisory flips True -> False: the cell is now referee-eligible rather than
    # reported-only, and the rate rises 0.0120 -> 0.0526 with a Wilson interval
    # ([0.035, 0.078]) that no longer spans the prior point estimate.
    _check_cell(
        r.frame_conversions,
        numerator=23,
        denominator=426,
        rate=0.0539906103286385,
        wilson_low=0.03624276090547163,
        wilson_high=0.07971065076989901,
        advisory=False,
    )
    # nested adopted analyzers.
    assert r.alibi_fabrication.total_impostor_alibis == 103
    assert r.alibi_fabrication.survived == 88
    assert r.alibi_fabrication.survival_rate == pytest.approx(88 / 103)
    assert r.effective_deflection.accused_impostor_events == 397
    assert r.effective_deflection.accused_impostor_survivals == 143
    assert r.effective_deflection.active_survivals == 133
    assert r.effective_deflection.effective_deflections == 77
    assert r.effective_deflection.named_target_deflections == 36
    assert r.effective_deflection.third_party_deflections == 41
    assert r.effective_deflection.skip_saved_active_survivals == 56


# --------------------------------------------------------------------------- #
# Samples 9p2i -- full-field pins                                              #
# --------------------------------------------------------------------------- #


def test_sample_nine_full_pins(sample_nine: DeceptionInstrumentsReport) -> None:
    r = sample_nine
    assert r.replay_set_dir == str(_NINE)
    _check_report(
        r,
        {
            "num_players": 9,
            "num_impostors": 2,
            "tasks_per_crewmate": 2,
            "games_total": 50,
            "meetings_total": 152,
            "impostor_accusations_total": 191,
            "frame_attempts": 191,
            "impostor_self_accusations": 0,
            "frame_attempt_meetings": 151,
            "crew_ejected_meetings": 14,
            "impostor_ejected_meetings": 85,
            "no_eject_meetings": 53,
            "vouch_observations_impostor": 118,
            "false_vouch_saw_player_observations": 6,
            "false_vouch_saw_player_rate": 0.05084745762711865,
            "corroboration_claims_total": 319,
            "corroboration_claims_impostor": 42,
            "false_vouch_corroborations": 9,
            "false_vouch_corroboration_rate": 0.21428571428571427,
            "false_vouches_total": 15,
            "false_vouch_subject_events": 6,
            "false_vouch_grounded": 6,
            "false_vouch_fabricated": 0,
            "false_vouch_grounded_share": 1.0,
            # companion join partitions the 20 observations (15 + 5 == 20).
            "false_vouch_grounded_subject_observations": 6,
            "false_vouch_fabricated_subject_observations": 0,
        },
    )
    _check_cell(
        r.teammate_accusations,
        numerator=0,
        denominator=191,
        rate=0.0,
        wilson_low=0.0,
        wilson_high=0.019716528708448297,
        advisory=True,
    )
    _check_cell(
        r.frame_conversions,
        numerator=12,
        denominator=151,
        rate=0.07947019867549669,
        wilson_low=0.04604220934704814,
        wilson_high=0.13376476758938236,
        advisory=False,
    )
    assert r.alibi_fabrication.total_impostor_alibis == 44
    assert r.alibi_fabrication.survived == 40
    assert r.alibi_fabrication.survival_rate == pytest.approx(40 / 44)
    assert r.effective_deflection.accused_impostor_events == 137
    assert r.effective_deflection.accused_impostor_survivals == 52
    assert r.effective_deflection.active_survivals == 51
    assert r.effective_deflection.effective_deflections == 32
    assert r.effective_deflection.named_target_deflections == 17
    assert r.effective_deflection.third_party_deflections == 15
    assert r.effective_deflection.skip_saved_active_survivals == 19


# --------------------------------------------------------------------------- #
# Samples 4p1i -- the one-impostor degenerate set                             #
# --------------------------------------------------------------------------- #


def test_sample_four_full_pins(sample_four: DeceptionInstrumentsReport) -> None:
    r = sample_four
    assert r.replay_set_dir == str(_FOUR)
    _check_report(
        r,
        {
            "num_players": 4,
            "num_impostors": 1,
            "tasks_per_crewmate": 1,
            "games_total": 50,
            "meetings_total": 40,
            "impostor_accusations_total": 39,
            "frame_attempts": 39,
            "impostor_self_accusations": 0,
            "frame_attempt_meetings": 39,
            "crew_ejected_meetings": 1,
            "impostor_ejected_meetings": 20,
            "no_eject_meetings": 19,
            # no co-impostor exists: every false-vouch cell is structurally 0.
            "vouch_observations_impostor": 4,
            "false_vouch_saw_player_observations": 0,
            "false_vouch_saw_player_rate": 0.0,
            "corroboration_claims_total": 23,
            "corroboration_claims_impostor": 2,
            "false_vouch_corroborations": 0,
            "false_vouch_corroboration_rate": 0.0,
            "false_vouches_total": 0,
            "false_vouch_subject_events": 0,
            "false_vouch_grounded": 0,
            "false_vouch_fabricated": 0,
            "false_vouch_grounded_share": None,
            "false_vouch_grounded_subject_observations": 0,
            "false_vouch_fabricated_subject_observations": 0,
        },
    )
    _check_cell(
        r.teammate_accusations,
        numerator=0,
        denominator=39,
        rate=0.0,
        wilson_low=0.0,
        wilson_high=0.08966985360023902,
        advisory=True,
    )
    _check_cell(
        r.frame_conversions,
        numerator=1,
        denominator=39,
        rate=0.02564102564102564,
        wilson_low=0.00454058606523737,
        wilson_high=0.13181286478627147,
        advisory=True,
    )
    assert r.alibi_fabrication.total_impostor_alibis == 1
    assert r.alibi_fabrication.survived == 1
    assert r.alibi_fabrication.survival_rate == pytest.approx(1 / 1)
    assert r.effective_deflection.accused_impostor_events == 35
    assert r.effective_deflection.accused_impostor_survivals == 15
    assert r.effective_deflection.active_survivals == 15
    assert r.effective_deflection.effective_deflections == 4
    assert r.effective_deflection.skip_saved_active_survivals == 11


# --------------------------------------------------------------------------- #
# Corpus 4p1i -- one-impostor degenerate set (cheap walk)                      #
# --------------------------------------------------------------------------- #


def test_corpus_four_full_pins(corpus_four: DeceptionInstrumentsReport) -> None:
    r = corpus_four
    assert r.replay_set_dir == str(_CORPUS_FOUR)
    _check_report(
        r,
        {
            "num_players": 4,
            "num_impostors": 1,
            "tasks_per_crewmate": 1,
            "games_total": 50,
            "meetings_total": 44,
            "impostor_accusations_total": 44,
            "frame_attempts": 44,
            "impostor_self_accusations": 0,
            "frame_attempt_meetings": 44,
            "crew_ejected_meetings": 1,
            "impostor_ejected_meetings": 28,
            "no_eject_meetings": 15,
            # The baseline-6 roll-call round elicits impostor saw_player vouches
            # and an impostor corroboration on this set for the first time (both
            # denominators were 0 at baseline 5, so both rates read the None
            # sentinel). Both are now POPULATED denominators with a 0 numerator:
            # the impostor vouches, but never falsely — so the rates are honest
            # 0.0 FLOATS, not the None sentinel. Only the grounded-share rate,
            # whose denominator (false_vouch_subject_events) is still 0, stays None.
            "vouch_observations_impostor": 1,
            "false_vouch_saw_player_observations": 0,
            "false_vouch_saw_player_rate": 0.0,
            "corroboration_claims_total": 24,
            "corroboration_claims_impostor": 0,
            "false_vouch_corroborations": 0,
            "false_vouch_corroboration_rate": None,
            "false_vouches_total": 0,
            "false_vouch_subject_events": 0,
            "false_vouch_grounded": 0,
            "false_vouch_fabricated": 0,
            "false_vouch_grounded_share": None,
            "false_vouch_grounded_subject_observations": 0,
            "false_vouch_fabricated_subject_observations": 0,
        },
    )
    _check_cell(
        r.teammate_accusations,
        numerator=0,
        denominator=44,
        rate=0.0,
        wilson_low=6.938893903907228e-18,
        wilson_high=0.08029831778201396,
        advisory=True,
    )
    _check_cell(
        r.frame_conversions,
        numerator=1,
        denominator=44,
        rate=0.022727272727272728,
        wilson_low=0.004023148385637013,
        wilson_high=0.11807979131537633,
        advisory=True,
    )
    # No impostor alibi at all on this set, so the survival rate is undefined --
    # the None sentinel, never 0.0.
    assert r.alibi_fabrication.total_impostor_alibis == 0
    assert r.alibi_fabrication.survived == 0
    assert r.alibi_fabrication.survival_rate is None
    assert r.effective_deflection.accused_impostor_events == 43
    assert r.effective_deflection.skip_saved_active_survivals == 10


# --------------------------------------------------------------------------- #
# Determinism + JSON round-trip                                               #
# --------------------------------------------------------------------------- #


def test_determinism_and_json_round_trip(
    sample_four: DeceptionInstrumentsReport,
) -> None:
    again = compute_deception_instruments(_FOUR)
    assert again == sample_four
    assert again.model_dump() == sample_four.model_dump()
    restored = DeceptionInstrumentsReport.model_validate_json(
        sample_four.model_dump_json()
    )
    assert restored == sample_four


# --------------------------------------------------------------------------- #
# Synthetic fixtures (unit-level, no disk)                                     #
# --------------------------------------------------------------------------- #

_ROOM_A = "MEDBAY"
_ROOM_B = "ENGINEERING"

# p-1 / p-2 impostors (co-impostors), p-3 / p-4 crew.
_ROLES: dict[PlayerId, Role] = {
    "p-1": "IMPOSTOR",
    "p-2": "IMPOSTOR",
    "p-3": "CREWMATE",
    "p-4": "CREWMATE",
}
_LIVING: frozenset[PlayerId] = frozenset({"p-1", "p-2", "p-3", "p-4"})


def _turn(
    speaker: PlayerId,
    index: int,
    *,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-0:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "opt_in",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text="...",
    )


def _meeting(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    living: frozenset[PlayerId] = _LIVING,
    outcome: str = "SKIPPED",
    ejected: PlayerId | None = None,
    sighting_records: dict[PlayerId, tuple[SightingRecord, ...]] | None = None,
    trigger_kind: MeetingTriggerKind = "emergency",
) -> _VJMeeting:
    return _VJMeeting(
        seed=0,
        meeting_id="m-0",
        tick=20,
        trigger_kind=trigger_kind,
        triggered_by="p-1",
        outcome=outcome,
        ejected=ejected,
        living=living,
        transcript=MeetingTranscript(turns=turns),
        ballots=(),
        contradictions=(),
        llm_calls=(),
        suspicion_graph_by_voter={},
        sighting_records_by_speaker=sighting_records or {},
        observation_ids_by_voter={},
        fellow_impostor_ids_by_voter={},
    )


def _accusation(against: PlayerId) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=0.5, reason="..."
    )


def _saw(
    subject: PlayerId, *, tick: int = 10, room: str = _ROOM_A
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room
    )


# -- accusation partition ---------------------------------------------------- #


def test_accusation_partition_splits_frame_teammate_self() -> None:
    meeting = _meeting(
        turns=(
            # impostor p-1 frames crew p-3, accuses co-impostor p-2, self-accuses.
            _turn(
                "p-1",
                0,
                claims=(_accusation("p-3"), _accusation("p-2"), _accusation("p-1")),
            ),
            # crew p-3's accusation never enters the impostor census.
            _turn("p-3", 1, claims=(_accusation("p-1"),)),
        ),
    )
    total, frame, teammate, self_acc = _impostor_accusation_partition(meeting, _ROLES)
    assert (total, frame, teammate, self_acc) == (3, 1, 1, 1)


def test_accusation_partition_is_empty_without_impostor_speech() -> None:
    meeting = _meeting(turns=(_turn("p-3", 0, claims=(_accusation("p-4"),)),))
    assert _impostor_accusation_partition(meeting, _ROLES) == (0, 0, 0, 0)


# -- frame conversion -------------------------------------------------------- #


def test_frame_conversion_detected_when_accused_crew_ejected() -> None:
    meeting = _meeting(
        turns=(_turn("p-1", 0, claims=(_accusation("p-3"),)),),
        outcome="EJECTED",
        ejected="p-3",
    )
    assert _is_frame_conversion(meeting, _ROLES) is True


def test_frame_conversion_false_when_impostor_ejected() -> None:
    meeting = _meeting(
        turns=(_turn("p-1", 0, claims=(_accusation("p-3"),)),),
        outcome="EJECTED",
        ejected="p-2",
    )
    assert _is_frame_conversion(meeting, _ROLES) is False


def test_frame_conversion_false_when_no_eject() -> None:
    meeting = _meeting(
        turns=(_turn("p-1", 0, claims=(_accusation("p-3"),)),),
        outcome="SKIPPED",
        ejected=None,
    )
    assert _is_frame_conversion(meeting, _ROLES) is False


def test_frame_conversion_false_when_ejected_crew_not_accused() -> None:
    # p-1 accused p-3, but p-4 (a different crewmate) was ejected.
    meeting = _meeting(
        turns=(_turn("p-1", 0, claims=(_accusation("p-3"),)),),
        outcome="EJECTED",
        ejected="p-4",
    )
    assert _is_frame_conversion(meeting, _ROLES) is False


# -- impostor vouch census (saw_player) -------------------------------------- #


def test_vouch_census_counts_false_vouch_only_for_co_impostor() -> None:
    meeting = _meeting(
        turns=(
            # impostor p-1: places co-impostor p-2 (false vouch), places crew p-3
            # (an observation but NOT false), self-places p-1 (excluded),
            # places dead p-5 (excluded -- not living).
            _turn(
                "p-1",
                0,
                observations=(_saw("p-2"), _saw("p-3"), _saw("p-1"), _saw("p-5")),
            ),
            # crew speaker p-3 places impostor p-2: excluded by the speaker filter.
            _turn("p-3", 1, observations=(_saw("p-2"),)),
        ),
    )
    observations, false_vouches = _impostor_vouch_census(meeting, _ROLES)
    assert (observations, false_vouches) == (2, 1)


def test_vouch_census_excludes_dead_impostor_speaker() -> None:
    living = frozenset({"p-2", "p-3", "p-4"})
    meeting = _meeting(
        turns=(_turn("p-1", 0, observations=(_saw("p-2"),)),),
        living=living,
    )
    assert _impostor_vouch_census(meeting, _ROLES) == (0, 0)


# -- grounded split ---------------------------------------------------------- #


def test_grounded_split_grounded_when_impostor_holds_matching_record() -> None:
    meeting = _meeting(
        turns=(
            _turn(
                "p-1",
                0,
                observations=(_saw("p-2", tick=10, room=_ROOM_A),),
            ),
        ),
        sighting_records={
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
        },
    )
    assert _grounded_split(meeting, _ROLES) == (1, 1, 0, 1, 0)


def test_grounded_split_fabricated_without_matching_record() -> None:
    meeting = _meeting(
        turns=(
            _turn(
                "p-1",
                0,
                observations=(_saw("p-2", tick=10, room=_ROOM_A),),
            ),
        ),
        sighting_records={
            # wrong room: the vouch cannot ground.
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_B, tick=10),)
        },
    )
    assert _grounded_split(meeting, _ROLES) == (1, 0, 1, 0, 1)


def test_grounded_split_restriction_ignores_crew_speaker_records() -> None:
    # The impostor p-1 false-vouches for co-impostor p-2, but only CREW p-3 holds
    # a matching record. The impostor-restricted mapping drops p-3, so the vouch
    # is FABRICATED -- the whole point of the restriction.
    meeting = _meeting(
        turns=(
            _turn(
                "p-1",
                0,
                observations=(_saw("p-2", tick=10, room=_ROOM_A),),
            ),
            _turn(
                "p-3",
                1,
                observations=(_saw("p-2", tick=10, room=_ROOM_A),),
            ),
        ),
        sighting_records={
            "p-3": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
        },
    )
    assert _grounded_split(meeting, _ROLES) == (1, 0, 1, 0, 1)


def test_grounded_split_empty_without_false_vouch() -> None:
    meeting = _meeting(turns=(_turn("p-1", 0, observations=(_saw("p-3"),)),))
    assert _grounded_split(meeting, _ROLES) == (0, 0, 0, 0, 0)


def test_grounded_split_duplicate_vouches_collapse_to_one_subject_event() -> None:
    # Two placements of the same co-impostor in one meeting: ONE subject event
    # (the chokepoint's granularity), TWO observations in the companion join,
    # both inheriting the subject's verdict.
    meeting = _meeting(
        turns=(
            _turn(
                "p-1",
                0,
                observations=(
                    _saw("p-2", tick=10, room=_ROOM_A),
                    _saw("p-2", tick=12, room=_ROOM_A),
                ),
            ),
        ),
        sighting_records={
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
        },
    )
    assert _grounded_split(meeting, _ROLES) == (1, 1, 0, 2, 0)


def test_grounded_split_mixed_subjects_partition_observations() -> None:
    # p-1's duplicate vouch of p-2 grounds (2 observations); p-2's single vouch
    # of p-1 has no matching record: 2 subject events split 1/1, and the
    # 3 observations split 2/1 -- the companion join partitions the
    # observation numerator exactly.
    meeting = _meeting(
        turns=(
            _turn(
                "p-1",
                0,
                observations=(
                    _saw("p-2", tick=10, room=_ROOM_A),
                    _saw("p-2", tick=12, room=_ROOM_A),
                ),
            ),
            _turn("p-2", 1, observations=(_saw("p-1", tick=10, room=_ROOM_A),)),
        ),
        sighting_records={
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
        },
    )
    assert _grounded_split(meeting, _ROLES) == (2, 1, 1, 2, 1)


# -- Wilson helper ----------------------------------------------------------- #


def test_wilson_interval_known_values() -> None:
    rate, low, high = _wilson_interval(5, 100)
    assert rate == pytest.approx(0.05)
    assert low == pytest.approx(0.02154336145631356)
    assert high == pytest.approx(0.11175196527208817)


def test_wilson_interval_zero_numerator_low_is_zero() -> None:
    rate, low, high = _wilson_interval(0, 10)
    assert rate == pytest.approx(0.0)
    assert low == pytest.approx(0.0, abs=1e-12)
    assert high == pytest.approx(0.2775401687666166)


def test_wilson_interval_zero_denominator_is_none() -> None:
    assert _wilson_interval(0, 0) == (None, None, None)


# -- advisory boundary ------------------------------------------------------- #


def test_advisory_boundary_at_seven() -> None:
    assert _rare_event_cell(7, 50).advisory is True
    assert _rare_event_cell(8, 50).advisory is False


def test_rare_event_cell_zero_denominator_has_none_rate() -> None:
    cell = _rare_event_cell(0, 0)
    assert cell.rate is None
    assert cell.wilson_low is None
    assert cell.wilson_high is None
    assert cell.advisory is True


# -- RareEventCell validator rejections -------------------------------------- #


def test_rare_event_cell_rejects_numerator_over_denominator() -> None:
    with pytest.raises(ValidationError):
        RareEventCell(
            numerator=6,
            denominator=5,
            rate=1.2,
            wilson_low=0.0,
            wilson_high=1.0,
            advisory=True,
        )


def test_rare_event_cell_rejects_wrong_advisory_flag() -> None:
    # Correct Wilson values, ONLY the advisory flag flipped -- isolates the
    # advisory check from the value check.
    rate, low, high = _wilson_interval(3, 10)
    with pytest.raises(ValidationError):
        RareEventCell(
            numerator=3,
            denominator=10,
            rate=rate,
            wilson_low=low,
            wilson_high=high,
            advisory=False,
        )


def test_rare_event_cell_rejects_rate_contradicting_counts() -> None:
    base = _rare_event_cell(5, 415).model_dump()
    base["rate"] = 0.5
    with pytest.raises(ValidationError):
        RareEventCell.model_validate(base)


def test_rare_event_cell_rejects_wilson_bounds_contradicting_counts() -> None:
    base = _rare_event_cell(5, 415).model_dump()
    base["wilson_low"] = base["wilson_low"] + 1e-6
    with pytest.raises(ValidationError):
        RareEventCell.model_validate(base)


def test_rare_event_cell_round_trips_through_json_exactly() -> None:
    # The value check is exact equality; JSON round-trip must preserve the
    # identical doubles or this raises.
    cell = _rare_event_cell(5, 415)
    assert RareEventCell.model_validate_json(cell.model_dump_json()) == cell


def test_rare_event_cell_rejects_none_rate_with_positive_denominator() -> None:
    with pytest.raises(ValidationError):
        RareEventCell(
            numerator=1,
            denominator=10,
            rate=None,
            wilson_low=None,
            wilson_high=None,
            advisory=True,
        )


# -- report validator rejections --------------------------------------------- #


def test_report_rejects_broken_grounded_split(
    sample_four: DeceptionInstrumentsReport,
) -> None:
    base = sample_four.model_dump()
    base["false_vouch_grounded"] = base["false_vouch_grounded"] + 1
    with pytest.raises(ValidationError):
        DeceptionInstrumentsReport.model_validate(base)


def test_report_rejects_broken_accusation_partition(
    sample_four: DeceptionInstrumentsReport,
) -> None:
    base = sample_four.model_dump()
    base["frame_attempts"] = base["frame_attempts"] + 1
    with pytest.raises(ValidationError):
        DeceptionInstrumentsReport.model_validate(base)


def test_report_rejects_broken_observation_companion_join(
    sample_nine: DeceptionInstrumentsReport,
) -> None:
    base = sample_nine.model_dump()
    base["false_vouch_grounded_subject_observations"] = (
        base["false_vouch_grounded_subject_observations"] + 1
    )
    with pytest.raises(ValidationError):
        DeceptionInstrumentsReport.model_validate(base)
