"""Unit tests for eval/vj_instruments.py (Task 16.10).

Three layers:

* scripted-fixture unit tests over hand-built inputs, exercising the typed
  split, the rendered-value proxy, citation compliance, and the
  deterministic voice tier in isolation — every judgment/voice fold proves
  it can MOVE on a synthetic fixture;
* the baseline-5 REPRODUCTION PINS — ``compute_vj_instruments`` over the
  committed 9p2i / 4p1i bytes (Task 16.17 re-record: model Qwen/Qwen3.6-27B,
  prompt set qwen3_6_27b v3, levers hard_evidence_gate / citation_gate /
  observation_id_rendering unconditional-ON, absence_prior OFF). The
  ballot-ECE cell equals the committed ``eval.accusation_calibration`` fold's
  ``vote_ballot_ece`` exactly (one sample stream, two instruments) — on
  baseline 5 that is 0.0565 at n=405. The zero-flag conviction channel and the
  citation-compliance cells are pinned on baseline 5. Vent flags dominate the
  zero-flag channel, so both 9p2i zero-flag convictions land soft_only and the
  unattributed / no-row / sub-gate / no-render classes are an honest zero. The
  soft/hard split's rendered-value axis still pins clean (0 rendered-value
  mismatches), and the typed and proxy splits AGREE on every zero-flag
  conviction (2/2 on the hard axis). The provenance axis reads 0 sum breaches:
  the gauge learned the J1 clamp-exemption (Task 17.1), so the eight by-design
  J1-clamped seed-12 rows — the ballot-graph scalar clamped to 0.59 while the
  raw typed provenance sums to 0.60 — are exempt by the production predicate,
  not integrity failures (their identities pinned per-row in
  ``test_9p2i_j1_clamp_exempt_rows_pinned``);
* the CLI surface — ``measure_baseline.py --vj [--json]`` emits the report
  and round-trips, plus the DoD determinism double-run (two computes of the
  same set are identical).
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

import pytest

# The project resolves script modules as top-level names (mypy_path =
# "scripts"; scripts/ has no __init__.py) — the tests/scripts/conftest.py
# pattern, inlined here because this eval-side test also pins the --vj CLI
# region this task owns.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import measure_baseline  # noqa: E402

from agents.memory.beliefs import (  # noqa: E402
    HARD_EVIDENCE_GATE_RENDER_CEIL,
    SUSPICION_PROVENANCE_ATOL,
)
from eval.accusation_calibration import (  # noqa: E402
    DEFAULT_N_BINS,
    _bin_samples,
    _vote_ballot_samples,
    compute_accusation_calibration,
)
from eval.funnel import _VJGameWalk, _VJMeeting, _walk_set_vj  # noqa: E402
from eval.validity import assemble_tournament_report  # noqa: E402
from eval.vj_instruments import (  # noqa: E402
    VJInstrumentReport,
    VJMeetingRow,
    _citation_counts,
    _cross_check_graphs,
    _distinct_n,
    _flagged_subjects,
    _is_near_dup,
    _meeting_echo,
    _normalize_voice,
    _pre_vote_graphs,
    _proxy_split,
    _room_pattern,
    _row_expected_scalars,
    _row_is_j1_clamp_exempt,
    _row_sum_breaches,
    _strip_leading_markers,
    _typed_split,
    compute_vj_instruments,
)
from meetings.render_contract import SuspicionEntry  # noqa: E402
from meetings.schemas import (  # noqa: E402
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    VoteBallot,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


# --------------------------------------------------------------------------- #
# Scripted fixtures — the typed split                                          #
# --------------------------------------------------------------------------- #


def _entry(player_id: str, suspicion: float, **channels: float) -> SuspicionEntry:
    return SuspicionEntry(
        player_id=player_id, suspicion=suspicion, trust=0.5, **channels
    )


def test_typed_split_hard_backed_wins() -> None:
    graphs = {
        "p-1": (_entry("p-3", 0.8, flag_lift=0.3),),
        "p-2": (_entry("p-3", 0.55, accusation_carry=0.05),),
    }
    assert _typed_split("p-3", ["p-1", "p-2"], graphs) == "hard_backed"


def test_typed_split_soft_only() -> None:
    graphs = {
        "p-1": (_entry("p-3", 0.55, accusation_carry=0.05),),
        "p-2": (_entry("p-3", 0.62, testimony_spread=0.12),),
    }
    assert _typed_split("p-3", ["p-1", "p-2"], graphs) == "soft_only"


def test_typed_split_carried_hard_stays_hard() -> None:
    # A meeting-1 grounded pin rolled into carried_hard is HARD forever —
    # collapsing the carry to soft is exactly what the 16.3 split forbids.
    graphs = {"p-1": (_entry("p-3", 0.8, carried_hard=0.3),)}
    assert _typed_split("p-3", ["p-1"], graphs) == "hard_backed"


def test_typed_split_unattributed_is_neither_hard_nor_soft() -> None:
    graphs = {"p-1": (_entry("p-3", 0.7, unattributed=0.2),)}
    assert _typed_split("p-3", ["p-1"], graphs) == "unattributed_only"


def test_typed_split_no_row_when_absent_from_every_graph() -> None:
    graphs = {"p-1": (_entry("p-4", 0.7, flag_lift=0.2),)}
    assert _typed_split("p-3", ["p-1"], graphs) == "no_row"


# --------------------------------------------------------------------------- #
# Scripted fixtures — the rendered-value proxy                                 #
# --------------------------------------------------------------------------- #


def _vote_prompt(*rows: tuple[str, float]) -> str:
    lines = "\n".join(
        f"- `{player_id}`: suspicion {value:.2f}, trust 0.50"
        for player_id, value in rows
    )
    return f"## Your suspicion of each player\n\n{lines}\n"


def test_proxy_split_buckets_by_max_rendered_value() -> None:
    prompts = {"p-1": _vote_prompt(("p-3", 0.72)), "p-2": _vote_prompt(("p-3", 0.61))}
    assert _proxy_split("p-3", ["p-1", "p-2"], prompts) == "hard_backed"
    assert _proxy_split("p-3", ["p-2"], prompts) == "soft_only"
    assert (
        _proxy_split("p-3", ["p-1"], {"p-1": _vote_prompt(("p-3", 0.55))}) == "sub_gate"
    )
    assert _proxy_split("p-3", ["p-1"], {"p-1": _vote_prompt(("p-4", 0.9))}) == (
        "no_render"
    )
    assert _proxy_split("p-3", ["p-1"], {}) == "no_render"


def test_flagged_subjects_is_the_zero_flag_complement() -> None:
    flag = ContradictionRef(
        contradiction_id="c-0",
        kind="alibi_vs_sighting",
        event_a_id="a",
        event_b_id="b",
        subjects=("p-3",),
        description="…",
    )
    meeting = _judgment_meeting(contradictions=(flag,))
    assert _flagged_subjects(meeting) == frozenset({"p-3"})
    assert _flagged_subjects(_judgment_meeting()) == frozenset()


# --------------------------------------------------------------------------- #
# Scripted fixtures — citation compliance                                      #
# --------------------------------------------------------------------------- #


def _ballot(
    voter: str,
    target: str,
    *,
    reason: str | None = None,
    observation: str | None = None,
    rationale: str = "because",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.7,
        primary_reason_id=reason,
        primary_reason_observation_id=observation,
        rationale_text=rationale,
    )


def _judgment_meeting(
    *,
    ballots: tuple[VoteBallot, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    observation_ids: dict[str, frozenset[str]] | None = None,
) -> _VJMeeting:
    turn = MeetingTurn(
        turn_id="m-0:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=(),
        free_text="opening",
    )
    return _VJMeeting(
        seed=0,
        meeting_id="m-0",
        tick=20,
        trigger_kind="emergency",
        triggered_by="p-1",
        outcome="SKIPPED",
        ejected=None,
        living=frozenset({"p-1", "p-2", "p-3"}),
        transcript=MeetingTranscript(turns=(turn,)),
        ballots=ballots,
        contradictions=contradictions,
        llm_calls=(),
        suspicion_graph_by_voter={},
        sighting_records_by_speaker={},
        observation_ids_by_voter=observation_ids or {},
        fellow_impostor_ids_by_voter={},
    )


def test_citation_counts_split_valid_from_dangling() -> None:
    meeting = _judgment_meeting(
        ballots=(
            _ballot("p-1", "p-3", reason="m-0:turn-0"),  # valid turn citation
            _ballot("p-2", "p-3", reason="m-0:turn-9"),  # dangling turn citation
            _ballot("p-3", "p-1", observation="p-3:5:0"),  # valid observation
            _ballot("p-1", "SKIP"),  # SKIP, uncited
            _ballot("p-2", "p-1", observation="p-2:9:9"),  # dangling observation
        ),
        observation_ids={"p-3": frozenset({"p-3:5:0"})},
    )
    (
        skip,
        turn_valid,
        turn_dangling,
        obs_valid,
        obs_dangling,
        cited_ejects,
        ejects,
    ) = _citation_counts(meeting)
    assert skip == 1
    assert turn_valid == 1
    assert turn_dangling == 1
    assert obs_valid == 1
    assert obs_dangling == 1
    assert cited_ejects == 2  # the two VALID citations; dangling never counts
    assert ejects == 4


def test_observation_citation_valid_only_from_the_voters_own_set() -> None:
    # Another voter's id set never validates this voter's citation.
    meeting = _judgment_meeting(
        ballots=(_ballot("p-1", "p-3", observation="p-3:5:0"),),
        observation_ids={"p-3": frozenset({"p-3:5:0"})},
    )
    counts = _citation_counts(meeting)
    assert counts[3] == 0  # obs_valid
    assert counts[4] == 1  # obs_dangling


# --------------------------------------------------------------------------- #
# Scripted fixtures — the deterministic voice tier                             #
# --------------------------------------------------------------------------- #

_ROOM_RE = _room_pattern(("MEDBAY", "ENGINEERING"))


def test_normalize_voice_collapses_ids_rooms_and_digits() -> None:
    assert (
        _normalize_voice("I saw p-3 in MEDBAY at tick 12.", _ROOM_RE)
        == "i saw player in room at tick n."
    )


def test_strip_leading_markers_drops_system_text_only() -> None:
    text = "[invalid primary_reason_id 'x' nulled] [note] I vote p-3."
    assert _strip_leading_markers(text) == "I vote p-3."
    assert _strip_leading_markers("plain [not leading]") == "plain [not leading]"


def test_near_dup_trigram_jaccard() -> None:
    a = tuple("player vented in room so i vote player".split())
    b = tuple("player vented in room so i vote player now".split())
    assert _is_near_dup(a, b)
    c = tuple("completely different rationale about tasks and alibis here".split())
    assert not _is_near_dup(a, c)
    # Sub-trigram texts compare by exact equality.
    assert _is_near_dup(("hi",), ("hi",))
    assert not _is_near_dup(("hi",), ("ho",))


def test_meeting_echo_moves_on_identical_ballots() -> None:
    echoed, distinct = _meeting_echo(
        [
            "player vented in room so i vote player",
            "player vented in room so i vote player",
            "an unrelated rationale that echoes nothing at all here",
        ]
    )
    assert echoed == 2
    assert distinct == 2
    assert _meeting_echo(["one text", "two text completely different words"])[0] == 0


def test_distinct_n_ratios() -> None:
    tokens = [("a", "b", "a"), ("a", "b")]
    assert _distinct_n(tokens, 1) == pytest.approx(2 / 5)
    assert _distinct_n(tokens, 2) == pytest.approx(2 / 3)
    assert _distinct_n([], 1) is None


# --------------------------------------------------------------------------- #
# Baseline-4 reproduction pins (committed bytes, Task 16.14 re-record)         #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def nine() -> VJInstrumentReport:
    return compute_vj_instruments(_NINE)


@pytest.fixture(scope="module")
def four() -> VJInstrumentReport:
    return compute_vj_instruments(_FOUR)


@pytest.fixture(scope="module")
def nine_walk() -> list[_VJGameWalk]:
    # The raw memory-augmented walk of the committed 9p2i set — the same walk
    # ``compute_vj_instruments`` folds internally, exposed so the J1-clamp-exempt
    # rows can be reconstructed and pinned per-row (their pre-vote graphs).
    walks, *_ = _walk_set_vj(_NINE)
    return walks


def test_9p2i_zero_flag_channel_pins(nine: VJInstrumentReport) -> None:
    # The residual zero-flag conviction channel (close audit §11 bullet 3) on the
    # baseline-7 bytes — convictions_total == the vote-correctness ejection
    # census (99 on 9p2i). Baseline 6 read 165 meetings, 101 convictions and 11
    # zero-flag convictions split 3 crew / 8 impostor, typed 3 hard-backed /
    # 8 soft-only, proxy 7 / 4 / 0 / 0. The channel GREW: the graduated slate
    # closed the STRONG sighting class, so more convictions carry no flag at all.
    assert nine.games_total == 50
    assert nine.meetings_total == 152
    assert nine.convictions_total == 99
    assert nine.zero_flag_convictions == 27
    assert nine.zero_flag_conviction_rate == pytest.approx(27 / 99)
    assert nine.zero_flag_crew_convictions == 11
    assert nine.zero_flag_impostor_convictions == 16
    # The 16.3 TYPED split of the 27 zero-flag convictions.
    assert nine.zero_flag_hard_backed == 7
    assert nine.zero_flag_soft_only == 19
    assert nine.zero_flag_unattributed_only == 1
    assert nine.zero_flag_no_row == 0
    # The planning-doc rendered-value proxy, beside it.
    assert nine.zero_flag_proxy_hard_backed == 14
    assert nine.zero_flag_proxy_soft_only == 8
    assert nine.zero_flag_proxy_sub_gate == 5
    assert nine.zero_flag_proxy_no_render == 0


def test_9p2i_soft_hard_split_cross_checks(nine: VJInstrumentReport) -> None:
    # DoD: the split cross-checks against 16.3's provenance sums (every
    # reconstructed pre-vote row satisfies 0.5 + Σ(eight channels) ==
    # suspicion) and is consistent with the rendered-value proxy within the
    # documented tolerance. On committed baseline-5 bytes the reconstruction
    # reproduces every rendered per-player value exactly (0 rendered-value
    # mismatches), and the typed/proxy splits agree on seven of the eleven
    # zero-flag convictions (7 agreements, 4 disagreements).
    assert nine.provenance_rows_checked == 3948  # was 4550
    # 0 sum breaches: the gauge now mirrors the graduated J1 clamp (Task 17.1;
    # audits/audit-phase-16-close.md §8 routed contract (a)). The three rows that
    # would read as phantom breaches under the naive raw-only invariant — seed 18,
    # meeting headless-seed-18:meeting-3, subject p-7, whose ballot-graph
    # scalar is clamped to 0.59 while the raw typed provenance sums to 0.60, across
    # the four living voters' graphs — are J1-clamp-exempt by the production
    # predicate (the clamp keeps the raw provenance BY DESIGN,
    # tests/agents/test_beliefs_hard_evidence_gate.py::test_clamps_the_scalar_but_
    # keeps_raw_provenance). Their identities are pinned per-row in
    # test_9p2i_j1_clamp_exempt_rows_pinned below.
    assert nine.provenance_sum_breaches == 0
    assert nine.rendered_rows_compared == 3948  # was 4550
    assert nine.rendered_row_mismatches == 0
    assert nine.zero_flag_split_agreements == 20  # was 7
    assert nine.zero_flag_split_disagreements == 7  # was 4


_CLAMP_EXEMPT_SEED = 12
_CLAMP_EXEMPT_MEETING = "headless-seed-12:meeting-4"


def _clamp_exempt_meeting(walks: list[_VJGameWalk]) -> _VJMeeting:
    for walk in walks:
        if walk.seed != _CLAMP_EXEMPT_SEED:
            continue
        for meeting in walk.meetings:
            if meeting.meeting_id == _CLAMP_EXEMPT_MEETING:
                return meeting
    raise AssertionError(
        f"seed-{_CLAMP_EXEMPT_SEED} {_CLAMP_EXEMPT_MEETING} "
        "not in the committed 9p2i walk"
    )


def test_9p2i_j1_clamp_exempt_rows_pinned(nine_walk: list[_VJGameWalk]) -> None:
    # DoD: the previously-phantom provenance-sum breaches (the Phase-16 close §2
    # signature, routed to this task by §8 contract (a)) are asserted INDIVIDUALLY
    # as J1-clamp-exempt, identities pinned. The baseline-7 record moved the
    # anchor: the whole 9p2i set now carries TWO such rows, both over p-2, in
    # seed 12 meeting 4 (baseline 6 read three rows over p-7 in seed 18 meeting
    # 3). Each clamped row is an entirely-soft conviction-grade row (raw
    # 0.5 + Σ = 0.60, all carried_soft) clamped to the J1 render ceiling 0.59
    # while the raw typed provenance is kept. Each is exempt by the PRODUCTION
    # predicate (agents.memory.beliefs.hard_evidence_gated_suspicion), so none is
    # a breach.
    meeting = _clamp_exempt_meeting(nine_walk)
    graphs = _pre_vote_graphs(meeting)
    exempt_rows: list[tuple[str, str]] = []
    for voter in sorted(meeting.living):
        for entry in graphs[voter]:
            if not _row_is_j1_clamp_exempt(entry):
                # every non-exempt row is sound under the J1-aware invariant
                assert not _row_sum_breaches(entry)
                continue
            # identity pinned in the exact-list assertion below; each clamped
            # subject renders at the J1 ceiling
            exempt_rows.append((voter, entry.player_id))
            assert entry.suspicion == pytest.approx(HARD_EVIDENCE_GATE_RENDER_CEIL)
            raw, clamped = _row_expected_scalars(entry)
            # the raw 16.3 invariant WOULD flag it (raw 0.65 != rendered 0.59) ...
            assert raw == pytest.approx(0.65)
            assert abs(raw - entry.suspicion) > SUSPICION_PROVENANCE_ATOL
            # ... but the clamp arithmetic reproduces the rendered scalar exactly,
            # so the gauge does NOT count it as a breach.
            assert clamped == pytest.approx(entry.suspicion)
            assert not _row_sum_breaches(entry)
    # exactly these two (voter, clamped-subject) rows, in graph order
    assert exempt_rows == [
        ("p-3", "p-2"),
        ("p-4", "p-2"),
    ]


def test_cross_check_exempts_the_j1_clamp_but_catches_real_breaches() -> None:
    # DoD: a synthetic genuinely-broken clamped row still counts as a breach, and
    # the gauge does NOT introduce phantom breaches on the two legitimate render
    # shapes (a clamped soft-only row, and a soft-only row emitted RAW by the fold
    # path — the 4p1i case that a naive "always clamp" gauge would mis-flag).
    meeting = _judgment_meeting()  # living {p-1, p-2, p-3}
    by_design = _entry(
        "p-9", 0.59, carried_soft=0.10
    )  # raw 0.60 clamped to 0.59 → sound
    raw_soft = _entry("p-8", 0.60, carried_soft=0.10)  # soft-only emitted RAW → sound
    broken_clamped = _entry(
        "p-7", 0.72, carried_soft=0.10
    )  # neither 0.60 nor 0.59 → breach
    hard_broken = _entry(
        "p-6", 0.90, flag_lift=0.10
    )  # hard row (no clamp), raw 0.60 → breach
    graphs = {
        "p-1": (by_design, raw_soft),
        "p-2": (broken_clamped,),
        "p-3": (hard_broken,),
    }
    checked, breaches, compared, mismatches = _cross_check_graphs(meeting, graphs, {})
    assert checked == 4
    assert compared == 0  # no vote prompts passed
    assert mismatches == 0
    assert breaches == 2  # only the two genuinely-broken rows


def test_row_predicates_classify_raw_clamp_and_breach() -> None:
    # The exemption predicate is the 16.4 soft-only classification: only an
    # entirely-soft row over the ceiling, rendered at the clamp value, is exempt.
    clamped = _entry("p-2", 0.59, carried_soft=0.10)  # raw 0.60 → clamped 0.59
    raw_soft = _entry("p-2", 0.60, carried_soft=0.10)  # soft-only, emitted raw
    sub_ceiling = _entry("p-2", 0.55, testimony_spread=0.05)  # soft, below the ceiling
    hard_raw = _entry("p-2", 0.60, flag_lift=0.10)  # hard channel present → no clamp
    broken = _entry("p-2", 0.72, carried_soft=0.10)  # matches neither raw nor clamp
    hard_broken = _entry(
        "p-2", 0.59, flag_lift=0.10
    )  # hard row rendered 0.59 (raw 0.60)

    # only the clamped soft-only row is J1-clamp-exempt
    assert _row_is_j1_clamp_exempt(clamped)
    for entry in (raw_soft, sub_ceiling, hard_raw, broken, hard_broken):
        assert not _row_is_j1_clamp_exempt(entry)

    # the raw invariant accepts a scalar matching EITHER the raw sum or the clamp;
    # a hard row gets no clamp exemption, so 0.59 against a raw 0.60 is a breach
    for entry in (clamped, raw_soft, sub_ceiling, hard_raw):
        assert not _row_sum_breaches(entry)
    for entry in (broken, hard_broken):
        assert _row_sum_breaches(entry)


def test_9p2i_citation_compliance_pins(nine: VJInstrumentReport) -> None:
    # Every eject ballot cites a valid turn or observation (compliance 1.0) and
    # no citation dangles. The reason-id gate nulled 2 rendered ids and one
    # zero-flag rationale was coerced; the observation-id gate did not fire.
    #
    # These four lines are PARSED by scripts/check_doc_facts.py to re-derive
    # README's citation-compliance row, so they must stay in the bare
    # ``assert nine.<field> == <int>`` shape -- no trailing comment. Baseline 6
    # read 971 / 451 / 520 / 478 / 478 / 0 / 156 / 156 / 0 / 520.
    assert nine.ballots_total == 871
    assert nine.skip_ballots == 333
    assert nine.eject_ballots == 538
    assert nine.turn_citations == 478
    assert nine.turn_citations_valid == 478
    assert nine.turn_citations_dangling == 0
    assert nine.observation_citations == 167
    assert nine.observation_citations_valid == 167
    assert nine.observation_citations_dangling == 0
    assert nine.cited_eject_ballots == 538
    assert nine.citation_compliance_rate == pytest.approx(538 / 538)
    assert nine.nulled_reason_id_markers == 2
    assert nine.nulled_observation_id_markers == 8  # was 0
    assert nine.coerced_zero_flag_markers == 1


def test_9p2i_ballot_calibration_pins_the_baseline_5_cell(
    nine: VJInstrumentReport,
) -> None:
    # Baseline-6 vote-ballot calibration (Task 18.12 re-record): ECE 0.1686 at
    # n=520, equal to the committed accusation-calibration fold's
    # vote_ballot_ece and to measure_baseline --json's vote_ballot_ece /
    # vote_ballot_total (one sample stream). n=520 populates >=5 decile bins,
    # so the calibration is no longer flagged low-power.
    assert nine.ballot_calibration_total == 538  # was 520
    assert nine.ballot_confidence_ece == pytest.approx(
        0.14983271375464421
    )  # was 0.16863461538461605
    assert nine.ballot_confidence_brier == pytest.approx(
        0.1844589219330855
    )  # was 0.20346480769230768
    # LOW POWER on these bytes: the ballots concentrate in fewer decile bins
    # than the >=5 the gauge asks for (baseline 6 populated enough at n=520).
    assert nine.ballot_calibration_low_power is True


def test_9p2i_voice_tier_pins(nine: VJInstrumentReport) -> None:
    assert nine.voice_ballots_total == 871  # was 971
    assert nine.echo_ballots == 0
    assert nine.within_meeting_echo_rate == pytest.approx(0.0)
    assert nine.response_skeleton_share == pytest.approx(
        0.01722158438576349
    )  # was 0.026776519052523172
    assert nine.distinct_skeletons == 850  # was 929
    assert nine.distinct_skeleton_ratio == pytest.approx(
        0.9758897818599311
    )  # was 0.956745623069001
    assert nine.distinct_1 == pytest.approx(0.10613751730503)  # was 0.09441071802386435
    assert nine.distinct_2 == pytest.approx(
        0.3636308439587128
    )  # was 0.33246953740971497


def test_9p2i_pooling_rides_the_same_report(nine: VJInstrumentReport) -> None:
    # DoD: 16.17 reads voice ALONGSIDE zero-flag — pooling + judgment +
    # voice are one machine-readable object per set.
    assert nine.pooling.meetings_total == nine.meetings_total
    assert nine.pooling.whereabouts_claims_total == 763  # was 843
    assert nine.pooling.vouch_observations_total == 819  # was 1389
    assert len(nine.per_meeting) == 152  # was 165


def test_4p1i_reproduces_baseline_5_exactly(four: VJInstrumentReport) -> None:
    assert four.games_total == 50
    assert four.meetings_total == 40  # was 39
    assert four.convictions_total == 21  # was 12
    assert four.zero_flag_convictions == 2  # was 0
    assert four.zero_flag_crew_convictions == 1  # was 0
    assert four.zero_flag_impostor_convictions == 1  # was 0
    assert four.zero_flag_hard_backed == 1  # was 0
    assert four.zero_flag_unattributed_only == 0
    assert four.zero_flag_no_row == 0
    assert four.zero_flag_split_agreements == 2  # was 0
    assert four.zero_flag_split_disagreements == 0
    assert four.provenance_sum_breaches == 0
    assert four.rendered_rows_compared == 131  # was 133
    assert four.rendered_row_mismatches == 0
    assert four.ballots_total == 120  # was 117
    assert four.turn_citations_valid == 47  # was 22
    assert four.turn_citations_dangling == 0
    assert four.cited_eject_ballots == 59  # was 27
    assert four.ballot_confidence_ece == pytest.approx(
        0.1483050847457627
    )  # was 0.0877777777777777
    assert four.ballot_confidence_brier == pytest.approx(
        0.14504237288135594
    )  # was 0.09643333333333333
    assert four.echo_ballots == 0
    assert four.distinct_skeletons == 117  # was 106


def test_ballot_calibration_matches_the_committed_fold(
    four: VJInstrumentReport,
) -> None:
    # One recorded ballot stream, two instruments, and ONE deliberate
    # difference. This instrument reports the stream as recorded;
    # eval/accusation_calibration excludes a ballot whose rationale opens with a
    # guard audit marker, because the meeting layer rewrote its target while
    # preserving the voter's confidence in the target they authored, so the
    # recorded pair is not one agent's act (audit A-3). Both folds are rebuilt
    # here from the same bytes, so the divergence is pinned as a quantity rather
    # than absorbed as an approximation.
    report = assemble_tournament_report(_FOUR)
    calibration = compute_accusation_calibration(report)

    as_recorded = [
        (ballot.confidence, walk_roles[ballot.target] == "IMPOSTOR")
        for game in report.games
        for walk_roles in (game.roles,)
        for meeting in game.meetings
        for ballot in meeting.ballots
        if ballot.target != "SKIP"
    ]
    assert four.ballot_calibration_total == len(as_recorded)
    expected_brier = statistics.fmean(
        (confidence - (1.0 if impostor else 0.0)) ** 2
        for confidence, impostor in as_recorded
    )
    assert four.ballot_confidence_brier == pytest.approx(expected_brier, abs=1e-12)
    _bins, _total, as_recorded_ece = _bin_samples(as_recorded, DEFAULT_N_BINS)
    assert four.ballot_confidence_ece == pytest.approx(as_recorded_ece, abs=1e-12)

    # The calibration fold is the same stream MINUS the guard-authored ballots,
    # and its own binnable set reproduces its published ECE exactly.
    binnable = _vote_ballot_samples(report)
    assert len(binnable) == calibration.vote_ballot_total < len(as_recorded)
    _bins, _total, binnable_ece = _bin_samples(binnable, DEFAULT_N_BINS)
    assert calibration.vote_ballot_ece == pytest.approx(binnable_ece, abs=1e-12)
    assert calibration.vote_ballot_guard_authored_excluded > 0


def test_per_meeting_rows_pair_voice_with_judgment(nine: VJInstrumentReport) -> None:
    row = nine.per_meeting[0]
    assert isinstance(row, VJMeetingRow)
    # Judgment and voice fields ride ONE row (the NO-GO pairing's read).
    assert row.ballots > 0
    assert row.echo_rate is not None
    ejected_rows = [r for r in nine.per_meeting if r.outcome == "EJECTED"]
    assert len(ejected_rows) == 99  # was 101
    assert all(r.typed_split is not None for r in ejected_rows)
    skipped_rows = [r for r in nine.per_meeting if r.outcome == "SKIPPED"]
    assert all(r.typed_split is None for r in skipped_rows)
    assert all(r.zero_flag_conviction is None for r in skipped_rows)


def test_double_run_is_identical(four: VJInstrumentReport) -> None:
    # DoD: the voice tier (and the whole report) is deterministic — a second
    # walk of the same bytes returns an identical value object.
    again = compute_vj_instruments(_FOUR)
    assert again == four
    assert again.model_dump() == four.model_dump()


def test_report_json_round_trips(four: VJInstrumentReport) -> None:
    text = four.model_dump_json()
    assert VJInstrumentReport.model_validate_json(text) == four


# --------------------------------------------------------------------------- #
# The measure_baseline --vj CLI surface                                        #
# --------------------------------------------------------------------------- #


def test_cli_vj_json_emits_the_machine_readable_report(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([str(_FOUR), "--vj", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 1
    report = VJInstrumentReport.model_validate(payload[0])
    assert report.replay_set_dir.endswith("4p1i")
    assert report.convictions_total == 21  # was 12
    assert report.zero_flag_convictions == 2  # was 0
    assert report.pooling.whereabouts_claims_total == 85  # was 86


def test_cli_vj_human_render_names_the_gauges(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([str(_FOUR), "--vj"]) == 0
    out = capsys.readouterr().out
    assert "V&J instruments" in out
    assert "zero-flag convictions: 2/21" in out
    assert "voice:" in out
    assert "pooling:" in out
