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
from eval.vote_correctness import (
    compute_genuine_class_conversion,
    genuine_class_subjects,
)
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
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_PROXY_INTRA_TURN,
    WEAK_REASON_RETARGETED_PROXY,
    detect_contradictions,
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
# The Wave-1 (10.9) re-record's corrected baseline — now the FROZEN prior-era
# A/B anchor that the Task 10.17 Wave-2 re-record measured against (its headline
# rows are pinned below), alongside the still-frozen corrected_w0_* anchor.
_W1_BASELINE_FIXTURE = (
    _REPO_ROOT / "tests" / "fixtures" / "phase10" / "corrected_w1_baseline.json"
)
# The Wave-2 (10.17) re-record's corrected baseline, the current-era pin produced
# by the same operator command over the committed 9p2i bytes. This W2 file is what
# the committed bytes now re-derive to; corrected_w0_* / corrected_w1_* stay frozen
# as the prior-era A/B anchors.
_W2_BASELINE_FIXTURE = (
    _REPO_ROOT / "tests" / "fixtures" / "phase10" / "corrected_w2_baseline.json"
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
    """A transcript whose re-derived flag on the impostor is WEAK (+0.08).

    Task 13.14 reverses the self-stated down-weight for the
    ``alibi_vs_sighting`` band, so a self-stated INTERIOR sighting is now
    STRONG. This builder therefore lands the sighting on the alibi window's
    ENDPOINT tick (``to_tick=8``), which keeps the genuine endpoint-tick weak
    guard in force -- still a self-stated flag, still weak (+0.08), the same
    single impostor-subject flag the eval instruments key on.
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
            observations=(_sighting(subject=_IMPOSTOR, tick=8),),
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

    def test_flag_stacked_on_a_clamped_vent_row_keeps_the_vent_channel(
        self,
    ) -> None:
        # The Codex-review clamp shape: a vent witness's 1.00 row plus a
        # SAME-meeting weak flag. Subtracting the flag mass from the
        # clamped ceiling would read persistent 0.42, lose the vent
        # channel, and invent body proximity from the residue; the
        # clamp-aware branch keeps vent and never attributes proximity
        # from an un-invertible remainder.
        game = _game(
            meetings=(
                _accused_meeting(meeting_id="m-a"),
                _meeting(
                    meeting_id="m-eject",
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_weak_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 1.00}),),
                ),
            )
        )
        channels = decompose_ejection_channels(game, 1)
        assert channels == frozenset(
            {
                CHANNEL_CONTRADICTION_FLAG,
                CHANNEL_VENT_WITNESS,
                CHANNEL_PRIOR_MEETING_CARRY,
            }
        )
        assert channels is not None and CHANNEL_BODY_PROXIMITY not in channels

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


class TestPostGuardUnattributedImpossible:
    """Task 10.9.2 (PR #147 F2): unattributed ejections are structurally gone.

    The seed-12 m0 shape — an impostor ejected with NO rendered over-gate
    row anywhere and no naming flag — decomposed to zero channels (the gp-7
    decomposition itself flagged it; W0 unattributed was 0). The
    ballot-target graph guard makes that shape impossible on post-guard
    recordings: every eject ballot under a MUST-vote verdict names a target
    whose rendered row meets the 0.60 gate, and a rendered row at or above
    the gate always decomposes to at least one §6.3 channel — the lift over
    the 0.5 prior is either flag mass (flag channel) or persistent mass
    (proximity / vent / carry).
    """

    def test_pre_guard_seed12_shape_decomposes_to_zero_channels(self) -> None:
        # The class the guard removes: ejected impostor, no naming flag,
        # no rendered row for the ejected anywhere — [] channels.
        game = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    llm_calls=(_graph_call(agent_id="p-0", rows={"p-1": 0.80}),),
                ),
            )
        )
        assert decompose_ejection_channels(game, 0) == frozenset()

    def test_over_gate_rendered_row_always_attributes_a_channel(self) -> None:
        # Post-guard, the winning eject target carries a rendered row at or
        # above the gate. At the 0.60 floor with no flags the 0.10 lift
        # over the prior is persistent mass (body proximity); with a flag
        # the flag channel is present; at the 1.0 clamp the vent channel
        # is. No over-gate row can decompose to zero channels.
        no_flag = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.60}),),
                ),
            )
        )
        with_flag = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=_weak_flag_turns(),
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.60}),),
                ),
            )
        )
        clamped = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 1.00}),),
                ),
            )
        )

        assert decompose_ejection_channels(no_flag, 0) == frozenset(
            {CHANNEL_BODY_PROXIMITY}
        )
        flag_channels = decompose_ejection_channels(with_flag, 0)
        assert flag_channels is not None
        assert CHANNEL_CONTRADICTION_FLAG in flag_channels
        assert decompose_ejection_channels(clamped, 0) == frozenset(
            {CHANNEL_VENT_WITNESS}
        )


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
                conversions_with_single_witness_inform=0,
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
                conversions_with_single_witness_inform=0,
                multi_signal_rate=0.0,
            )


class TestComputeSupplyGauges:
    def test_flag_census_shares_and_role_split(self) -> None:
        # Task 13.14: a genuine-class (interior, non-proxy) sighting
        # contradiction is now STRONG, while the surviving WEAK band is the
        # endpoint guard (NOT genuine class). The census therefore separates the
        # two: a strong genuine flag and a weak endpoint flag, both on the
        # impostor.
        games = (
            _game(
                meetings=(
                    # A genuine-class STRONG flag on the impostor.
                    _meeting(meeting_id="m-0", turns=_strong_flag_turns()),
                    # An endpoint-banded WEAK flag on the impostor (not genuine).
                    _meeting(meeting_id="m-1", turns=_weak_flag_turns()),
                    # No claims at all: a zero-contradiction meeting.
                    _meeting(meeting_id="m-2"),
                ),
            ),
        )
        gauges = compute_supply_gauges(games)

        assert gauges.meetings_total == 3
        assert gauges.total_flags == 2
        assert gauges.weak_flags == 1
        assert gauges.strong_flags == 1
        assert gauges.zero_contradiction_meetings == 1
        assert gauges.zero_contradiction_share == pytest.approx(1 / 3)
        assert gauges.genuine_subject_meetings == 1
        assert gauges.genuine_subject_share == pytest.approx(1 / 3)
        assert gauges.flag_subjects_impostor == 2
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
        # helper on the same bytes. Task 13.14: the genuine (interior,
        # non-proxy) class is now STRONG, so use the strong-flag builder.
        meeting = _meeting(turns=_strong_flag_turns())
        assert genuine_class_subjects(meeting) == frozenset({_IMPOSTOR})
        gauges = compute_supply_gauges((_game(meetings=(meeting,)),))
        assert gauges.genuine_subject_meetings == 1


def _retargeted_proxy_turns() -> tuple[MeetingTurn, ...]:
    """A transcript whose ONLY non-endpoint sighting-flag is a re-target.

    The impostor states a proxy alibi about a crewmate (CAFETERIA 2-8); a
    third party sights the crewmate in a disjoint room at an interior tick
    (STORAGE@5) and the crewmate's OWN self-sighting agrees — the Task
    10.6 proxy rule suppresses the flag on the crewmate and re-targets it
    WEAK at the impostor speaker.
    """

    return (
        _turn(
            speaker=_IMPOSTOR,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_CREWMATE),),
        ),
        _turn(
            speaker=_CREWMATE,
            index=1,
            kind="reply",
            observations=(_sighting(subject=_CREWMATE, tick=5),),
        ),
        _turn(
            speaker="p-2",
            index=2,
            kind="reply",
            observations=(_sighting(subject=_CREWMATE, tick=5),),
        ),
    )


class TestRetargetedProxyFlagsAreNotGenuineClass:
    """A re-target names the proxy speaker, not a sighted-and-contradicted
    subject — it must not enter the alibi-lie gauge (Codex review, P1).

    Without the exclusion, an impostor whose false PROXY alibi about
    someone else gets re-targeted would count as genuine-class SUPPLIED
    (the re-target flag is ``alibi_vs_sighting`` with no endpoint band),
    inflating the PRIMARY gate and the genuine-subject gauge with a flag
    class whose evidence is one weak re-target.
    """

    def test_retarget_at_an_impostor_does_not_supply_the_gate(self) -> None:
        meeting = _meeting(turns=_retargeted_proxy_turns())

        # The re-target exists (a non-endpoint alibi_vs_sighting naming
        # the impostor)...
        roster = frozenset(ballot.voter for ballot in meeting.ballots)
        flags = detect_contradictions(meeting.transcript, roster=roster)
        assert any(
            _IMPOSTOR in flag.subjects
            and WEAK_REASON_RETARGETED_PROXY in flag.description
            for flag in flags
        )
        # ...but it is NOT genuine-class supply: no one's own location was
        # contradicted by a sighting here.
        assert genuine_class_subjects(meeting) == frozenset()

        conversion = compute_genuine_class_conversion((_game(meetings=(meeting,)),))
        assert conversion.supplied == 0
        assert conversion.converted == 0

    def test_retarget_meeting_is_not_a_genuine_subject_meeting(self) -> None:
        gauges = compute_supply_gauges(
            (_game(meetings=(_meeting(turns=_retargeted_proxy_turns()),)),)
        )
        assert gauges.genuine_subject_meetings == 0
        # The re-target still shows in the honest flag census (one weak
        # flag naming the impostor speaker) — the exclusion is about the
        # genuine CLASS, never about hiding the flag.
        assert gauges.total_flags >= 1
        assert gauges.flag_subjects_impostor >= 1


def _proxy_intra_turn_turns() -> tuple[MeetingTurn, ...]:
    """A transcript whose only non-endpoint sighting flag is a 10.10 re-target.

    The impostor authors BOTH a proxy alibi about a crewmate (CAFETERIA
    2-8) AND a contradicting sighting of that crewmate (STORAGE@5,
    interior tick) on ONE turn. The Task 10.10 same-speaker guard re-targets
    the flag WEAK at the impostor SPEAKER — whose own location was never
    contradicted — so it must not enter the alibi-lie gauge.
    """

    return (
        _turn(
            speaker=_IMPOSTOR,
            index=0,
            kind="opening",
            claims=(_alibi(subject=_CREWMATE),),
            observations=(_sighting(subject=_CREWMATE, tick=5),),
        ),
    )


class TestProxyIntraTurnRetargetsAreNotGenuineClass:
    """A 10.10 same-speaker re-target names the speaker, not a contradicted
    subject — like the 10.6 cross-speaker re-target, it must stay out of the
    genuine alibi-lie gauge (Codex review on PR #152, P2).
    """

    def test_proxy_intra_turn_retarget_does_not_supply_the_gate(self) -> None:
        meeting = _meeting(turns=_proxy_intra_turn_turns())

        # The re-target exists (a non-endpoint alibi_vs_sighting naming the
        # impostor speaker)...
        roster = frozenset(ballot.voter for ballot in meeting.ballots)
        flags = detect_contradictions(meeting.transcript, roster=roster)
        assert any(
            _IMPOSTOR in flag.subjects
            and flag.kind == "alibi_vs_sighting"
            and WEAK_REASON_PROXY_INTRA_TURN in flag.description
            and WEAK_REASON_ENDPOINT_TICK not in flag.description
            for flag in flags
        )
        # ...but it is NOT genuine-class supply: no one's own location was
        # contradicted by a sighting here.
        assert genuine_class_subjects(meeting) == frozenset()

        conversion = compute_genuine_class_conversion((_game(meetings=(meeting,)),))
        assert conversion.supplied == 0
        assert conversion.converted == 0


# ---------------------------------------------------------------------------
# Committed pins + the corrected Wave-0 baseline fixture (the 10.9 A/B home)
# ---------------------------------------------------------------------------


def _load_committed_9p2i() -> TournamentEvalReport:
    return TournamentEvalReport.model_validate_json(
        _COMMITTED_9P2I_REPORT.read_text(encoding="utf-8")
    )


class TestCommittedW2GateSpecPins:
    """The gp-7 pins over the committed Wave-2 bytes (re-recorded in phase 11).

    These re-derive from the committed 9p2i bytes. W2 first landed in Task 10.17
    (W1 -> W2); the phase-11 Wave-1 re-record (vents/cover-on-reply/kill-memory)
    refreshed the W2 bytes again, moving the sample-derived values (each move
    explained by Wave-1 behavior — the headline being 0 strong flags as vents
    hide the post-kill sighting trail). The frozen prior-era A/B anchors
    (corrected_w0_baseline.json and corrected_w1_baseline.json) are pinned
    separately by the two ``test_w*_baseline_fixture_carries_the_anchor_rows``
    tests below.
    """

    def test_committed_ejections_decompose_as_the_w2_baseline(self) -> None:
        # W2: 34 impostor ejections (the phase-11 Wave-1 re-record; the prior W2
        # read 24, the W1 anchor 11). Sourced from the committed W2 baseline
        # fixture rather than transcribed, so the pin is the rederived-channels
        # == committed-baseline equality the operator command produced. The W1
        # 11-ejection map remains pinned in corrected_w1_baseline.json (anchor
        # test below).
        report = _load_committed_9p2i()
        channels_by_site = {
            f"seed-{game.seed}:m{index}": sorted(channels)
            for game in report.report.games
            for index in range(len(game.meetings))
            if (channels := decompose_ejection_channels(game, index)) is not None
        }
        expected = json.loads(_W2_BASELINE_FIXTURE.read_text(encoding="utf-8"))[
            "impostor_ejection_channels"
        ]
        assert channels_by_site == expected

    def test_multi_signal_conversion_reads_0_of_69(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Re-extracted on the qwen3_32b v3 re-record (Featherless, Qwen/Qwen3-32B,
        # all four Phase-13.5 substrate flags ON — the committed bytes carry the
        # flag stamp, so the census must be re-derived under the flag-ON substrate).
        # The de-imperatived gate now ejects on raw argmax suspicion far more often
        # (69 impostor ejections, up from the W2 14), and on the new substrate those
        # rows carry only the single contradiction_flag channel (or none): 57 of 69
        # single-signal, 12 unattributed, 0 multi-signal — the multi-signal rate
        # falls to 0.0. The channel decomposition per site is pinned below against
        # the committed W2 baseline fixture.
        monkeypatch.setenv("AILIBI_TESTIMONY_AS_CONTENT", "1")
        monkeypatch.setenv("AILIBI_WITNESSED_KILL_EVIDENCE", "1")
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        monkeypatch.setenv("AILIBI_UNFREEZE_MEMORY", "1")
        report = _load_committed_9p2i()
        result = compute_multi_signal_conversion(report.report.games)

        assert result.impostor_ejections == 69
        assert result.multi_signal_conversions == 0
        assert result.single_signal_conversions == 57
        assert result.unattributed_conversions == 12
        assert result.multi_signal_rate == pytest.approx(0.0)

    def test_supply_gauges_read_the_corrected_instrument(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The supply row, re-extracted on the qwen3_32b v3 re-record (Featherless,
        # Qwen/Qwen3-32B, all four Phase-13.5 substrate flags ON — the committed
        # bytes carry the flag stamp, so the flag census must re-derive under the
        # flag-ON substrate). The new substrate lights every inferential channel:
        # 702 flags now split 302w/400s (the 13.5 STRONG rules — testimony-as-content,
        # witnessed-kill-evidence, movement, unfreeze — fire off the recorded bytes),
        # 152 meetings, flag role split 451 CREW / 251 IMP, zero-contradiction 41,
        # genuine-subject supply 63, accused-impostor 127. The over-gate listener
        # gauge reads 0: the flag-ON detector no longer routes suspicion through the
        # recorded §6.6 listener rows the gauge keys on. The expected eval-metric
        # shift, not a regression.
        monkeypatch.setenv("AILIBI_TESTIMONY_AS_CONTENT", "1")
        monkeypatch.setenv("AILIBI_WITNESSED_KILL_EVIDENCE", "1")
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        monkeypatch.setenv("AILIBI_UNFREEZE_MEMORY", "1")
        report = _load_committed_9p2i()
        gauges = compute_supply_gauges(report.report.games)

        assert gauges.meetings_total == 152
        assert gauges.total_flags == 702
        assert gauges.weak_flags == 302
        assert gauges.strong_flags == 400
        assert gauges.zero_contradiction_meetings == 41
        assert gauges.genuine_subject_meetings == 63
        assert gauges.flag_subjects_crew == 451
        assert gauges.flag_subjects_impostor == 251
        assert gauges.accused_impostor_meetings == 127
        assert gauges.over_gate_listener_rows == 0

    def test_corrected_w2_baseline_matches_a_rederivation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # ONE home: corrected_w2_baseline.json IS the current-era baseline,
        # produced by the operator command (with the Task-14.7 substrate flags ON)
        #   AILIBI_TESTIMONY_AS_CONTENT=1 AILIBI_WITNESSED_KILL_EVIDENCE=1 \
        #   AILIBI_MOVEMENT_PERCEPTION=1 AILIBI_UNFREEZE_MEMORY=1 \
        #   scripts/build_sample_report.py --sample-dir replays/samples/9p2i
        #     --baseline-out tests/fixtures/phase10/corrected_w2_baseline.json
        # A byte-identical re-derivation here proves (a) the committed W2 fixture
        # has not drifted from the committed bytes and (b) the whole derivation
        # chain — detector, predicate, metrics — is deterministic end to end. The
        # re-record stamps its game_over records flag-ON, so the re-derivation must
        # run under the same substrate the fixture was built under.
        # corrected_w0/w1_baseline.json are the frozen prior-era A/B anchors,
        # decoupled from the W2 bytes by the re-record (rows pinned below).
        monkeypatch.setenv("AILIBI_TESTIMONY_AS_CONTENT", "1")
        monkeypatch.setenv("AILIBI_WITNESSED_KILL_EVIDENCE", "1")
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        monkeypatch.setenv("AILIBI_UNFREEZE_MEMORY", "1")
        report = build_report(_COMMITTED_9P2I_DIR)
        rederived = serialize_corrected_baseline(
            corrected_baseline_from_report(report, sample_dir=_COMMITTED_9P2I_DIR)
        )
        assert rederived == _W2_BASELINE_FIXTURE.read_text(encoding="utf-8")

    def test_w0_baseline_fixture_carries_the_anchor_rows(self) -> None:
        # The frozen 10.9 A/B anchor: corrected_w0_baseline.json keeps the W0
        # rows the re-record measures against (never re-derived since 10.9).
        # Pinned by content so the anchor cannot silently drift to a later era.
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

    def test_w1_baseline_fixture_carries_the_anchor_rows(self) -> None:
        # The frozen 10.17 A/B anchor: corrected_w1_baseline.json keeps the W1
        # rows the Wave-2 re-record measures against (never re-derived in 10.17).
        # Pinned by content so the anchor cannot silently drift to the W2 era —
        # mirrors the W0 anchor test exactly.
        baseline = json.loads(_W1_BASELINE_FIXTURE.read_text(encoding="utf-8"))
        assert baseline["sample_dir"] == "9p2i"
        assert baseline["genuine_class_conversion"]["supplied"] == 8
        assert baseline["genuine_class_conversion"]["converted"] == 2
        assert baseline["multi_signal_conversion"]["multi_signal_conversions"] == 11
        assert baseline["multi_signal_conversion"]["impostor_ejections"] == 11
        assert baseline["supply_gauges"]["total_flags"] == 85
        assert baseline["supply_gauges"]["weak_flags"] == 84
        assert baseline["supply_gauges"]["strong_flags"] == 1
        assert sorted(baseline["impostor_ejection_channels"]) == [
            "seed-16:m1",
            "seed-16:m2",
            "seed-25:m2",
            "seed-27:m1",
            "seed-29:m1",
            "seed-2:m2",
            "seed-38:m0",
            "seed-39:m2",
            "seed-43:m2",
            "seed-44:m1",
            "seed-45:m1",
        ]
