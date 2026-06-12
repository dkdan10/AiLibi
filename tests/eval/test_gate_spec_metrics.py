"""Tests for the Task 10.6 gp-7 gate-spec metrics (DESIGN.md §11.3).

Audit anchor: audit-2026-06-11-2218-gameplay-data.md gp-7 (C-C-6). Three
layers, mirroring :mod:`tests.eval.test_gate_metrics`:

* **Channel decomposition** (:func:`eval.meeting_quality.decompose_ejection_channels`)
  — synthetic shapes for each §6.3 design channel over the quantized rule
  lattice, including the 1.0-clamp vent shape where carry is
  presence-attributed.
* **Aggregates** — :func:`compute_multi_signal_conversion` /
  :func:`compute_supply_gauges` folds plus their fail-loud validators.
* **Committed pins + the corrected Wave-0 baseline fixture** — the DoD
  coordinates: the 5 Wave-0 impostor ejections decompose exactly as the
  audit found (seeds 8/11/26/39 multi-signal, seed 24 flag-only), the
  gauges read the corrected instrument, and
  ``tests/fixtures/phase10/corrected_w0_baseline.json`` — the exact file
  the 10.9 A/B reads — equals a byte-identical re-derivation from the
  committed bytes.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.meeting_quality import (
    CHANNEL_BODY_PROXIMITY,
    CHANNEL_CONTRADICTION_FLAG,
    CHANNEL_PRIOR_MEETING_CARRY,
    CHANNEL_VENT_WITNESS,
    MultiSignalConversionReport,
    SupplyGaugesReport,
    TournamentEvalReport,
    compute_multi_signal_conversion,
    compute_supply_gauges,
    decompose_ejection_channels,
)
from eval.report_schema import (
    GameCostSummary,
    GameReport,
    MeetingReport,
)
from eval.vote_correctness import genuine_class_subjects
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.replay import LLMCallRecord

# The baseline builder is a top-level script module (mypy_path = "scripts";
# no scripts/__init__.py), so put scripts/ on sys.path exactly as
# tests/scripts/conftest.py does — the fixture-equality pin must call the
# ONE assembly the operator command runs, never a test-local replica.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from build_sample_report import (  # noqa: E402
    build_report,
    corrected_baseline_from_report,
    serialize_corrected_baseline,
)

_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_IMPOSTOR: PlayerId = "p-3"
_CREWMATE: PlayerId = "p-1"
_VOTERS: tuple[PlayerId, ...] = ("p-0", "p-1", "p-2", "p-3")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMITTED_9P2I_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"
_COMMITTED_9P2I_REPORT = _COMMITTED_9P2I_DIR / "tournament-eval-report.json"
_BASELINE_FIXTURE = (
    _REPO_ROOT / "tests" / "fixtures" / "phase10" / "corrected_w0_baseline.json"
)


# ---------------------------------------------------------------------------
# Fixture builders (the test_gate_metrics conventions)
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


def _strong_flag_turns() -> tuple[MeetingTurn, ...]:
    """A transcript whose re-derived flag on the impostor is STRONG (+0.30).

    A third-party alibi about the impostor (proxy-shaped) against an
    interior-tick sighting, with the impostor's own claims ECHOING the
    alibi — the seed-24 shape, which the 10.6 proxy rule deliberately does
    NOT suppress.
    """

    return (
        _turn(
            speaker=_CREWMATE,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_IMPOSTOR),),
        ),
        _turn(
            speaker=_IMPOSTOR,
            index=1,
            kind="reply",
            claims=(_alibi(subject=_IMPOSTOR),),
        ),
        _turn(
            speaker="p-2",
            index=2,
            kind="reply",
            observations=(_sighting(subject=_IMPOSTOR, tick=5),),
        ),
    )


def _weak_flag_turns() -> tuple[MeetingTurn, ...]:
    """A transcript whose re-derived flag on the impostor is WEAK (+0.08)."""

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
    llm_calls: tuple[LLMCallRecord, ...] = (),
    meeting_id: str = "m-0",
) -> MeetingReport:
    return MeetingReport(
        meeting_id=meeting_id,
        tick=40,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=MeetingTranscript(turns=turns),
        ballots=tuple(_ballot(voter=voter) for voter in voters),
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


def _accused_meeting(
    *, prior: bool = False, meeting_id: str = "m-prior"
) -> MeetingReport:
    """A SKIPPED meeting in which a crewmate verbally accuses the impostor."""

    del prior
    return _meeting(
        meeting_id=meeting_id,
        turns=(
            _turn(
                speaker=_CREWMATE,
                index=0,
                kind="opening",
                claims=(_accusation(against=_IMPOSTOR),),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Channel decomposition (the quantized rule lattice)
# ---------------------------------------------------------------------------


class TestDecomposeEjectionChannels:
    def test_flag_only_ejection_is_single_signal(self) -> None:
        # The seed-24 shape: strong flag (+0.30) from the 0.5 prior renders
        # 0.80 with zero persistent mass — one channel.
        game = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_strong_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.80}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 0) == frozenset(
            {CHANNEL_CONTRADICTION_FLAG}
        )

    def test_flag_proximity_and_carry_decompose(self) -> None:
        # The seed-11 shape: 0.88 = 0.5 prior + 0.2 proximity + 0.10 carry
        # (accused in two earlier meetings) + 0.08 weak flag.
        game = _game(
            meetings=(
                _accused_meeting(meeting_id="m-a"),
                _accused_meeting(meeting_id="m-b"),
                _meeting(
                    meeting_id="m-eject",
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_weak_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.88}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 2) == frozenset(
            {
                CHANNEL_CONTRADICTION_FLAG,
                CHANNEL_BODY_PROXIMITY,
                CHANNEL_PRIOR_MEETING_CARRY,
            }
        )

    def test_vent_witness_at_the_clamp_keeps_presence_based_carry(self) -> None:
        # The seed-8 shape: a vent witness renders 1.00 (the Rule-4 +0.5
        # from the prior, clamp-saturated) and the carry bumps are
        # arithmetically invisible — carry is attributed by the recorded
        # accusation history, vent by the lattice mass.
        game = _game(
            meetings=(
                _accused_meeting(meeting_id="m-a"),
                _meeting(
                    meeting_id="m-eject",
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 1.00}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 1) == frozenset(
            {CHANNEL_VENT_WITNESS, CHANNEL_PRIOR_MEETING_CARRY}
        )

    def test_carry_needs_a_prior_meeting_not_just_mass(self) -> None:
        # Persistent mass with NO prior accusation history attributes to
        # the perception channels only (decayed carry cannot exist
        # without an accusation on record).
        game = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.70}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 0) == frozenset(
            {CHANNEL_BODY_PROXIMITY}
        )

    def test_self_accusation_is_not_carry(self) -> None:
        # The D-D-2 convention: an impostor naming themselves is not crew
        # pressure, so it earns no carry channel.
        game = _game(
            meetings=(
                _meeting(
                    meeting_id="m-self",
                    turns=(
                        _turn(
                            speaker=_IMPOSTOR,
                            index=0,
                            kind="opening",
                            claims=(_accusation(against=_IMPOSTOR),),
                        ),
                    ),
                ),
                _meeting(
                    meeting_id="m-eject",
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.70}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 1) == frozenset(
            {CHANNEL_BODY_PROXIMITY}
        )

    def test_non_impostor_ejection_and_skip_decompose_to_none(self) -> None:
        crewmate_ejected = _game(
            meetings=(_meeting(outcome="EJECTED", ejected=_CREWMATE),)
        )
        skipped = _game(meetings=(_meeting(outcome="SKIPPED"),))
        assert decompose_ejection_channels(crewmate_ejected, 0) is None
        assert decompose_ejection_channels(skipped, 0) is None

    def test_no_rendered_row_decomposes_to_flag_presence_only(self) -> None:
        game = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_weak_flag_turns(),
                ),
            )
        )
        assert decompose_ejection_channels(game, 0) == frozenset(
            {CHANNEL_CONTRADICTION_FLAG}
        )

    def test_decomposition_is_deterministic(self) -> None:
        game = _game(
            meetings=(
                _accused_meeting(meeting_id="m-a"),
                _meeting(
                    meeting_id="m-eject",
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_weak_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.83}),),
                ),
            )
        )
        first = decompose_ejection_channels(game, 1)
        second = decompose_ejection_channels(game, 1)
        assert first == second


class TestComputeMultiSignalConversion:
    def test_partition_and_channel_counts(self) -> None:
        games = (
            _game(
                game_id="g-flag-only",
                seed=1,
                meetings=(
                    _meeting(
                        outcome="EJECTED",
                        ejected=_IMPOSTOR,
                        turns=_strong_flag_turns(),
                        llm_calls=(
                            _graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.80}),
                        ),
                    ),
                ),
            ),
            _game(
                game_id="g-multi",
                seed=2,
                meetings=(
                    _accused_meeting(meeting_id="m-a"),
                    _meeting(
                        meeting_id="m-eject",
                        outcome="EJECTED",
                        ejected=_IMPOSTOR,
                        turns=_weak_flag_turns(),
                        llm_calls=(
                            _graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.83}),
                        ),
                    ),
                ),
            ),
        )
        result = compute_multi_signal_conversion(games)

        assert result.impostor_ejections == 2
        assert result.multi_signal_conversions == 1
        assert result.single_signal_conversions == 1
        assert result.unattributed_conversions == 0
        assert result.conversions_with_contradiction_flag == 2
        assert result.conversions_with_body_proximity == 1
        assert result.conversions_with_vent_witness == 0
        assert result.conversions_with_prior_meeting_carry == 1
        assert result.multi_signal_rate == pytest.approx(0.5)

    def test_no_impostor_ejections_yields_undefined_rate(self) -> None:
        result = compute_multi_signal_conversion(
            (_game(meetings=(_meeting(outcome="SKIPPED"),)),)
        )
        assert result.impostor_ejections == 0
        assert result.multi_signal_rate is None

    def test_validator_rejects_a_broken_partition(self) -> None:
        with pytest.raises(ValidationError, match="must equal impostor_ejections"):
            MultiSignalConversionReport(
                impostor_ejections=2,
                multi_signal_conversions=1,
                single_signal_conversions=0,
                unattributed_conversions=0,
                conversions_with_contradiction_flag=0,
                conversions_with_body_proximity=0,
                conversions_with_vent_witness=0,
                conversions_with_prior_meeting_carry=0,
                multi_signal_rate=0.5,
            )

    def test_validator_rejects_a_defined_rate_with_no_ejections(self) -> None:
        with pytest.raises(ValidationError, match="undefined, not 0.0"):
            MultiSignalConversionReport(
                impostor_ejections=0,
                multi_signal_conversions=0,
                single_signal_conversions=0,
                unattributed_conversions=0,
                conversions_with_contradiction_flag=0,
                conversions_with_body_proximity=0,
                conversions_with_vent_witness=0,
                conversions_with_prior_meeting_carry=0,
                multi_signal_rate=0.0,
            )


class TestComputeSupplyGauges:
    def test_flag_census_shares_and_role_split(self) -> None:
        games = (
            _game(
                meetings=(
                    # A genuine-class weak flag on the impostor.
                    _meeting(meeting_id="m-0", turns=_weak_flag_turns()),
                    # No claims at all: a zero-contradiction meeting.
                    _meeting(meeting_id="m-1"),
                ),
            ),
        )
        gauges = compute_supply_gauges(games)

        assert gauges.meetings_total == 2
        assert gauges.total_flags == 1
        assert gauges.weak_flags == 1
        assert gauges.strong_flags == 0
        assert gauges.zero_contradiction_meetings == 1
        assert gauges.zero_contradiction_share == pytest.approx(0.5)
        assert gauges.genuine_subject_meetings == 1
        assert gauges.genuine_subject_share == pytest.approx(0.5)
        assert gauges.flag_subjects_impostor == 1
        assert gauges.flag_subjects_crew == 0

    def test_over_gate_listeners_count_other_voters_rows(self) -> None:
        meeting = _meeting(
            turns=(
                _turn(
                    speaker=_CREWMATE,
                    index=0,
                    kind="opening",
                    claims=(_accusation(against=_IMPOSTOR),),
                ),
            ),
            llm_calls=(
                # Two listeners over the gate, one under, plus the
                # impostor's own row (excluded: a listener is another
                # voter).
                _graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.70}),
                _graph_call(agent_id="p-1", rows={_IMPOSTOR: 0.60}),
                _graph_call(agent_id="p-2", rows={_IMPOSTOR: 0.55}),
                _graph_call(agent_id=_IMPOSTOR, rows={"p-0": 0.90}),
            ),
        )
        gauges = compute_supply_gauges((_game(meetings=(meeting,)),))

        assert gauges.accused_impostor_meetings == 1
        assert gauges.over_gate_listener_rows == 2
        assert gauges.over_gate_listeners_per_accused_impostor_meeting == (
            pytest.approx(2.0)
        )

    def test_empty_set_reads_undefined_shares(self) -> None:
        gauges = compute_supply_gauges(())
        assert gauges.meetings_total == 0
        assert gauges.zero_contradiction_share is None
        assert gauges.genuine_subject_share is None
        assert gauges.over_gate_listeners_per_accused_impostor_meeting is None

    def test_validator_rejects_a_broken_weak_strong_split(self) -> None:
        with pytest.raises(ValidationError, match="must equal total_flags"):
            SupplyGaugesReport(
                meetings_total=1,
                total_flags=2,
                weak_flags=0,
                strong_flags=1,
                zero_contradiction_meetings=0,
                zero_contradiction_share=0.0,
                genuine_subject_meetings=0,
                genuine_subject_share=0.0,
                flag_subjects_crew=0,
                flag_subjects_impostor=0,
                accused_impostor_meetings=0,
                over_gate_listener_rows=0,
                over_gate_listeners_per_accused_impostor_meeting=None,
            )

    def test_genuine_share_reads_the_one_home_helper(self) -> None:
        # Drift guard: the gauge's membership rule IS
        # eval.vote_correctness.genuine_class_subjects (an import, never a
        # re-derivation) — the synthetic genuine meeting agrees with the
        # helper on the same bytes.
        meeting = _meeting(turns=_weak_flag_turns())
        assert genuine_class_subjects(meeting) == frozenset({_IMPOSTOR})
        gauges = compute_supply_gauges((_game(meetings=(meeting,)),))
        assert gauges.genuine_subject_meetings == 1


# ---------------------------------------------------------------------------
# Committed pins + the corrected Wave-0 baseline fixture (the 10.9 A/B home)
# ---------------------------------------------------------------------------


def _load_committed_9p2i() -> TournamentEvalReport:
    return TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )


class TestCommittedW0GateSpecPins:
    """The gp-7 DoD pins over the committed Wave-0 bytes (no re-record)."""

    def test_the_five_ejections_decompose_as_the_audit_found(self) -> None:
        report = _load_committed_9p2i()
        channels_by_site = {
            f"seed-{game.seed}:m{index}": channels
            for game in report.report.games
            for index in range(len(game.meetings))
            if (channels := decompose_ejection_channels(game, index)) is not None
        }

        assert channels_by_site == {
            "seed-8:m2": frozenset({CHANNEL_VENT_WITNESS, CHANNEL_PRIOR_MEETING_CARRY}),
            "seed-11:m2": frozenset(
                {
                    CHANNEL_CONTRADICTION_FLAG,
                    CHANNEL_BODY_PROXIMITY,
                    CHANNEL_PRIOR_MEETING_CARRY,
                }
            ),
            "seed-24:m0": frozenset({CHANNEL_CONTRADICTION_FLAG}),
            "seed-26:m1": frozenset(
                {
                    CHANNEL_CONTRADICTION_FLAG,
                    CHANNEL_BODY_PROXIMITY,
                    CHANNEL_PRIOR_MEETING_CARRY,
                }
            ),
            "seed-39:m1": frozenset(
                {
                    CHANNEL_CONTRADICTION_FLAG,
                    CHANNEL_BODY_PROXIMITY,
                    CHANNEL_PRIOR_MEETING_CARRY,
                }
            ),
        }

    def test_multi_signal_conversion_reads_4_of_5(self) -> None:
        report = _load_committed_9p2i()
        result = compute_multi_signal_conversion(report.report.games)

        assert result.impostor_ejections == 5
        assert result.multi_signal_conversions == 4
        assert result.single_signal_conversions == 1  # seed 24, flag-only
        assert result.unattributed_conversions == 0
        assert result.multi_signal_rate == pytest.approx(0.8)

    def test_supply_gauges_read_the_corrected_instrument(self) -> None:
        # The corrected Wave-0 supply row: 65 re-derived flags (64w/1s —
        # the storm and the suppressed proxies gone), zero-contradiction
        # share UP one meeting (seed 13 m1 now reads empty), genuine
        # supply untouched at 10 meetings, and the audited role split net
        # of the storm (36 CREW / 29 IMP — C-C-8's cascade base rate).
        report = _load_committed_9p2i()
        gauges = compute_supply_gauges(report.report.games)

        assert gauges.meetings_total == 78
        assert gauges.total_flags == 65
        assert gauges.weak_flags == 64
        assert gauges.strong_flags == 1
        assert gauges.zero_contradiction_meetings == 49
        assert gauges.genuine_subject_meetings == 10
        assert gauges.flag_subjects_crew == 36
        assert gauges.flag_subjects_impostor == 29
        assert gauges.accused_impostor_meetings == 54
        assert gauges.over_gate_listener_rows == 76

    def test_corrected_baseline_fixture_matches_a_rederivation(self) -> None:
        # ONE home: the fixture IS the 10.9 A/B baseline, produced by the
        # operator command
        #   scripts/build_sample_report.py --sample-dir replays/samples/9p2i
        #     --baseline-out tests/fixtures/phase10/corrected_w0_baseline.json
        # A byte-identical re-derivation here proves (a) the committed
        # fixture has not drifted from the committed bytes and (b) the
        # whole derivation chain — detector, predicate, metrics — is
        # deterministic end to end.
        report = build_report(_COMMITTED_9P2I_DIR)
        rederived = serialize_corrected_baseline(
            corrected_baseline_from_report(report, sample_dir_name="9p2i")
        )
        assert rederived == _BASELINE_FIXTURE.read_text(encoding="utf-8")

    def test_fixture_carries_the_headline_baseline_rows(self) -> None:
        # The 10.9 reader's contract: the corrected table's named rows sit
        # at pinned paths inside the fixture.
        baseline = json.loads(_BASELINE_FIXTURE.read_text(encoding="utf-8"))
        assert baseline["sample_dir"] == "9p2i"
        assert baseline["genuine_class_conversion"]["supplied"] == 7
        assert baseline["genuine_class_conversion"]["converted"] == 1
        assert baseline["multi_signal_conversion"]["multi_signal_conversions"] == 4
        assert baseline["multi_signal_conversion"]["impostor_ejections"] == 5
        assert baseline["supply_gauges"]["total_flags"] == 65
        assert baseline["supply_gauges"]["weak_flags"] == 64
        assert baseline["supply_gauges"]["strong_flags"] == 1
        assert sorted(baseline["impostor_ejection_channels"]) == [
            "seed-11:m2",
            "seed-24:m0",
            "seed-26:m1",
            "seed-39:m1",
            "seed-8:m2",
        ]
