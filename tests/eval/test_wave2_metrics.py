"""Tests for the Task 10.16 Wave-2 metrics + gate spec (DESIGN.md §9, §11).

Audit anchor: audit-2026-06-13-1816-gameplay-data.md (B-B-2 pacing inversion,
C-C-1 conversion, D-D-1 toolkit fingerprint, D-D-2 active-deflection);
experiments/lab/report-deception-battery*.md. Four layers:

* **Conversion per meeting** — the pacing-inversion-proof KPI
  (:func:`eval.meeting_quality.compute_conversion_per_meeting`).
* **Effective deflection** — the active-deflection subcount split from
  SKIP-saved survival (:func:`compute_effective_deflection`).
* **Indistinguishability** — the "never-tasks" fingerprint over the per-tick
  action-by-role ingest (:func:`eval.action_ingest.tally_actions_by_role` +
  :func:`compute_indistinguishability`).
* **The inform channel** — the 10.15 single-witness lever as a fifth
  decompose channel: 1 on the committed W2 bytes (the inform parser's header
  anchor survives the qwen3_6_27b restyle, but the collapsed transcript
  substrate leaves only one single-witness inform conversion), byte-unchanged
  existing channels, and a synthetic fresh inform credited.

The committed-byte pins reproduce the baseline-4 Qwen/Qwen3.6-27B
(qwen3_6_27b.v1, all four templates, the 6-lever Wave-0 substrate all
unconditionally ON) re-record exactly (123/46/40, effective 16 = 7 named +
9 third; conversion 77/160; do_task 388/3666).
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.action_ingest import tally_actions_by_role
from eval.meeting_quality import (
    CHANNEL_BODY_PROXIMITY,
    CHANNEL_SINGLE_WITNESS_INFORM,
    WAVE2_GATE_SPEC,
    ActionRoleTally,
    ConversionPerMeetingReport,
    EffectiveDeflectionReport,
    IndistinguishabilityReport,
    compute_conversion_per_meeting,
    compute_effective_deflection,
    compute_indistinguishability,
    compute_multi_signal_conversion,
    decompose_ejection_channels,
)
from eval.report_schema import GameCostSummary, GameReport, MeetingReport
from meetings.schemas import (
    AccusationClaim,
    MeetingOutcome,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)
from orchestrator.replay import LLMCallRecord

# scripts/ is a top-level module dir (no __init__.py), like tests/scripts and
# tests/eval/test_gate_spec_metrics: the committed-byte pins call the ONE
# operator assembly, never a test-local replica.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from build_sample_report import build_report  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMITTED_9P2I_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"

_ROLES: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}
_IMPOSTOR: PlayerId = "p-3"
_CREW: PlayerId = "p-1"
_VOTERS: tuple[PlayerId, ...] = ("p-0", "p-1", "p-2", "p-3")


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _turn(
    *,
    speaker: PlayerId,
    index: int = 0,
    kind: str = "opening",
    observations: tuple[SawPlayerObservation, ...] = (),
    claims: tuple[AccusationClaim, ...] = (),
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


def _accusation(*, against: PlayerId) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=against, confidence=0.9, reason="looked guilty"
    )


def _sighting(*, subject: PlayerId, tick: int = 5) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", subject=subject, tick=tick, room="STORAGE"
    )


def _ballot(*, voter: PlayerId, target: str = "SKIP") -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.5,
        primary_reason_id=None,
        rationale_text="",
    )


def _graph_call(*, agent_id: PlayerId, suspicion: float) -> LLMCallRecord:
    return LLMCallRecord(
        call_kind="meeting",
        model="fixture-model",
        prompt=(
            "## Your suspicion graph\n"
            f"- `{_IMPOSTOR}`: suspicion {suspicion:.2f}, trust 0.50\n"
            "\n## Decision rules\n"
        ),
        response_text="{}",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.0,
        agent_id=agent_id,
    )


def _meeting(
    *,
    outcome: MeetingOutcome = "SKIPPED",
    ejected: PlayerId | None = None,
    turns: tuple[MeetingTurn, ...] = (),
    ballots: tuple[VoteBallot, ...] | None = None,
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
        ballots=ballots
        if ballots is not None
        else tuple(_ballot(voter=v) for v in _VOTERS),
        contradictions=(),
        llm_calls=llm_calls,
    )


def _game(
    *,
    meetings: tuple[MeetingReport, ...],
    roles: Mapping[PlayerId, Role] = _ROLES,
    seed: int = 1,
) -> GameReport:
    return GameReport(
        game_id=f"g-{seed}",
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


# ---------------------------------------------------------------------------
# Conversion per meeting
# ---------------------------------------------------------------------------


class TestConversionPerMeeting:
    def test_rate_is_ejections_over_resolved_meetings(self) -> None:
        games = (
            _game(
                meetings=(
                    _meeting(outcome="EJECTED", ejected=_IMPOSTOR, meeting_id="m-0"),
                    _meeting(outcome="SKIPPED", meeting_id="m-1"),
                ),
            ),
        )
        result = compute_conversion_per_meeting(games)
        assert result.impostor_ejections == 1
        assert result.resolved_meetings == 2
        assert result.conversion_per_meeting == pytest.approx(0.5)

    def test_no_meetings_yields_undefined_rate(self) -> None:
        result = compute_conversion_per_meeting((_game(meetings=()),))
        assert result.resolved_meetings == 0
        assert result.conversion_per_meeting is None

    def test_independent_of_meeting_count(self) -> None:
        # Padding a game with extra SKIP meetings (the pacing inversion's
        # confound) LOWERS the per-meeting rate — it never rewards length.
        base = _game(meetings=(_meeting(outcome="EJECTED", ejected=_IMPOSTOR),))
        padded = _game(
            meetings=(
                _meeting(outcome="EJECTED", ejected=_IMPOSTOR, meeting_id="m-0"),
                _meeting(outcome="SKIPPED", meeting_id="m-1"),
                _meeting(outcome="SKIPPED", meeting_id="m-2"),
            )
        )
        assert compute_conversion_per_meeting((base,)).conversion_per_meeting == 1.0
        assert compute_conversion_per_meeting(
            (padded,)
        ).conversion_per_meeting == pytest.approx(1 / 3)

    def test_validator_rejects_more_ejections_than_meetings(self) -> None:
        with pytest.raises(ValidationError, match="cannot exceed resolved_meetings"):
            ConversionPerMeetingReport(
                impostor_ejections=3,
                resolved_meetings=2,
                conversion_per_meeting=1.5,
            )

    def test_committed_w2_reads_64_of_179(self) -> None:
        # baseline-5 Qwen/Qwen3.6-27B (qwen3_6_27b.v3, all four templates) re-record
        # with the Wave-0 substrate all unconditionally ON: the gate ejects
        # 80 impostors across 156 resolved meetings — the per-meeting conversion KPI
        # over the new bytes.
        report = build_report(_COMMITTED_9P2I_DIR)
        result = compute_conversion_per_meeting(report.report.games)
        assert result.impostor_ejections == 80
        assert result.resolved_meetings == 156
        assert result.conversion_per_meeting == pytest.approx(80 / 156)


# ---------------------------------------------------------------------------
# Effective deflection
# ---------------------------------------------------------------------------


def _accused_then_counter(
    *,
    counter_target: PlayerId | None,
    outcome: MeetingOutcome,
    ejected: PlayerId | None,
    ballots: tuple[VoteBallot, ...],
    meeting_id: str,
) -> MeetingReport:
    """A meeting where crew accuses the impostor, who optionally counter-accuses."""

    turns = [_turn(speaker="p-0", index=0, claims=(_accusation(against=_IMPOSTOR),))]
    if counter_target is not None:
        turns.append(
            _turn(
                speaker=_IMPOSTOR,
                index=1,
                kind="reply",
                claims=(_accusation(against=counter_target),),
            )
        )
    return _meeting(
        outcome=outcome,
        ejected=ejected,
        turns=tuple(turns),
        ballots=ballots,
        meeting_id=meeting_id,
    )


class TestEffectiveDeflection:
    def test_partition_over_synthetic_cases(self) -> None:
        game = _game(
            meetings=(
                # NAMED: impostor counter-accuses p-1, plurality ejects p-1.
                _accused_then_counter(
                    counter_target=_CREW,
                    outcome="EJECTED",
                    ejected=_CREW,
                    ballots=(
                        _ballot(voter="p-0", target=_CREW),
                        _ballot(voter="p-2", target=_CREW),
                        _ballot(voter=_CREW, target="SKIP"),
                        _ballot(voter=_IMPOSTOR, target="SKIP"),
                    ),
                    meeting_id="m-named",
                ),
                # THIRD: plurality lands on p-2, not the named p-1.
                _accused_then_counter(
                    counter_target=_CREW,
                    outcome="SKIPPED",
                    ejected=None,
                    ballots=(
                        _ballot(voter="p-0", target="p-2"),
                        _ballot(voter=_CREW, target="p-2"),
                        _ballot(voter="p-2", target="SKIP"),
                        _ballot(voter=_IMPOSTOR, target="SKIP"),
                    ),
                    meeting_id="m-third",
                ),
                # STILL: eject-plurality still on the impostor (SKIP-saved).
                _accused_then_counter(
                    counter_target=_CREW,
                    outcome="SKIPPED",
                    ejected=None,
                    ballots=(
                        _ballot(voter="p-0", target=_IMPOSTOR),
                        _ballot(voter=_CREW, target="SKIP"),
                        _ballot(voter="p-2", target="SKIP"),
                        _ballot(voter=_IMPOSTOR, target="SKIP"),
                    ),
                    meeting_id="m-still",
                ),
                # PASSIVE: no counter-accusation — a survival, never active.
                _accused_then_counter(
                    counter_target=None,
                    outcome="SKIPPED",
                    ejected=None,
                    ballots=tuple(_ballot(voter=v) for v in _VOTERS),
                    meeting_id="m-passive",
                ),
                # NO-UNIQUE-PLURALITY: tie eject votes (SKIP-saved).
                _accused_then_counter(
                    counter_target=_CREW,
                    outcome="SKIPPED",
                    ejected=None,
                    ballots=(
                        _ballot(voter="p-0", target=_CREW),
                        _ballot(voter=_CREW, target="p-2"),
                        _ballot(voter="p-2", target="SKIP"),
                        _ballot(voter=_IMPOSTOR, target="SKIP"),
                    ),
                    meeting_id="m-tie",
                ),
                # EJECTED: the impostor went down — an event, not a survival.
                _accused_then_counter(
                    counter_target=_CREW,
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    ballots=tuple(_ballot(voter=v, target=_IMPOSTOR) for v in _VOTERS),
                    meeting_id="m-eject",
                ),
            )
        )
        result = compute_effective_deflection((game,))
        assert result.accused_impostor_events == 6
        assert result.accused_impostor_survivals == 5
        assert result.active_survivals == 4
        assert result.named_target_deflections == 1
        assert result.third_party_deflections == 1
        assert result.effective_deflections == 2
        assert result.skip_saved_active_survivals == 2

    def test_validator_rejects_broken_active_partition(self) -> None:
        with pytest.raises(ValidationError, match="effective \\+ skip-saved"):
            EffectiveDeflectionReport(
                accused_impostor_events=10,
                accused_impostor_survivals=9,
                active_survivals=5,
                effective_deflections=2,
                named_target_deflections=1,
                third_party_deflections=1,
                skip_saved_active_survivals=2,  # 2 + 2 != 5
            )

    def test_committed_w2_reproduces_the_audit_subcount(self) -> None:
        # baseline-5 Qwen/Qwen3.6-27B (qwen3_6_27b.v3, all four templates) re-record,
        # the Wave-0 substrate all unconditionally ON:
        # 139 accused / 60 survived / 56 active; effective 23 = 6 named + 17 third
        # (the gate subcount), NOT the raw 56. On the baseline-5 substrate the active
        # split leans SKIP-saved (33) OVER active-deflection (23) — with the
        # transcript contradiction channel collapsed, fewer of the impostor's
        # survivals come from landing plurality on a named or third-party target.
        report = build_report(_COMMITTED_9P2I_DIR)
        result = compute_effective_deflection(report.report.games)
        assert result.accused_impostor_events == 139
        assert result.accused_impostor_survivals == 60
        assert result.active_survivals == 56
        assert result.named_target_deflections == 6
        assert result.third_party_deflections == 17
        assert result.effective_deflections == 23
        assert result.skip_saved_active_survivals == 33


# ---------------------------------------------------------------------------
# Indistinguishability + the action-by-role ingest
# ---------------------------------------------------------------------------


class TestIndistinguishability:
    def test_shares_and_top_idler(self) -> None:
        tally = ActionRoleTally(
            crewmate_action_counts={"do_task": 10, "wait": 2, "move": 8},
            impostor_action_counts={"wait": 5, "move": 5},
            per_game_player_wait_counts=((3, 1), (4,)),
        )
        result = compute_indistinguishability(tally)
        assert result.crewmate_do_task == 10
        assert result.impostor_do_task == 0
        assert result.crewmate_wait == 2
        assert result.impostor_wait == 5
        assert result.crewmate_actions_total == 20
        assert result.impostor_actions_total == 10
        assert result.crewmate_wait_share == pytest.approx(0.1)
        assert result.impostor_wait_share == pytest.approx(0.5)
        # game1 waits (3,1): 3/4 = 0.75; game2 (4,): 4/4 = 1.0; mean 0.875.
        assert result.top_idler_wait_share == pytest.approx(0.875)

    def test_idle_role_reads_undefined_share(self) -> None:
        tally = ActionRoleTally(
            crewmate_action_counts={"wait": 1},
            impostor_action_counts={},
            per_game_player_wait_counts=(),
        )
        result = compute_indistinguishability(tally)
        assert result.impostor_actions_total == 0
        assert result.impostor_wait_share is None
        assert result.top_idler_wait_share is None  # no waits recorded

    def test_validator_rejects_part_exceeding_total(self) -> None:
        with pytest.raises(
            ValidationError, match="cannot exceed its role action total"
        ):
            IndistinguishabilityReport(
                crewmate_do_task=0,
                impostor_do_task=0,
                crewmate_wait=5,
                impostor_wait=0,
                crewmate_actions_total=3,  # wait 5 > total 3
                impostor_actions_total=0,
                crewmate_wait_share=1.0,
                impostor_wait_share=None,
                top_idler_wait_share=None,
            )

    def test_committed_w2_tasks_fingerprint_closed(self) -> None:
        # baseline-5 Qwen/Qwen3.6-27B (qwen3_6_27b.v3, all four templates) re-record,
        # the Wave-0 substrate all unconditionally ON:
        # the toolkit keeps the D-D-1 fingerprint closed. Impostor do_task 368 vs
        # crew 3511, and the impostor wait-share ~0.069 sits BELOW crew's ~0.144 —
        # the crew carry the dead-crewmate task burden yet idle MORE between
        # consoles, so impostors no longer idle their way to a fingerprint (the
        # closed property holds even more strongly than W1).
        report = build_report(_COMMITTED_9P2I_DIR)
        tally = tally_actions_by_role(_COMMITTED_9P2I_DIR, report.report.games)
        result = compute_indistinguishability(tally)
        assert result.impostor_do_task == 368
        assert result.crewmate_do_task == 3511
        assert result.impostor_wait_share is not None
        assert result.crewmate_wait_share is not None
        assert result.impostor_wait_share == pytest.approx(0.0685, abs=1e-3)
        assert result.crewmate_wait_share == pytest.approx(0.1436, abs=1e-3)
        # The fingerprint is gone: impostor wait-share no longer dwarfs crew's —
        # impostors now idle LESS than the task-burdened crew.
        assert result.impostor_wait_share < 2 * result.crewmate_wait_share

    def test_ingest_is_deterministic(self) -> None:
        report = build_report(_COMMITTED_9P2I_DIR)
        games = report.report.games
        first = tally_actions_by_role(_COMMITTED_9P2I_DIR, games)
        second = tally_actions_by_role(_COMMITTED_9P2I_DIR, games)
        assert first == second

    def test_ingest_fails_loud_on_unseeded_actor(self) -> None:
        # roles-from-seeder: an actor absent from the game's seeded roles
        # cannot be classified, so the ingest fails loud (no silent drop).
        broken = _game(
            meetings=(), roles={"p-0": "CREWMATE"}, seed=0
        )  # replay-seed-0 has p-0..p-8
        with pytest.raises(ValueError, match="absent from game"):
            tally_actions_by_role(_COMMITTED_9P2I_DIR, (broken,))


# ---------------------------------------------------------------------------
# The single-witness inform channel
# ---------------------------------------------------------------------------


def _inform_voice_turns() -> tuple[MeetingTurn, ...]:
    """One observation-backed accuser of the impostor at an interior tick.

    Exactly one independent voice (below the two-witness fold bar), so the
    impostor re-derives into the single-witness inform band.
    """

    return (
        _turn(
            speaker=_CREW,
            index=0,
            kind="opening",
            observations=(_sighting(subject="p-2", tick=5),),
            claims=(_accusation(against=_IMPOSTOR),),
        ),
    )


def _inform_game(*, suspicion: float, turns: tuple[MeetingTurn, ...]) -> GameReport:
    return _game(
        meetings=(
            _meeting(
                outcome="EJECTED",
                ejected=_IMPOSTOR,
                turns=turns,
                llm_calls=(_graph_call(agent_id="p-0", suspicion=suspicion),),
            ),
        )
    )


class TestSingleWitnessInformChannel:
    def test_bare_inform_decomposes_to_inform_alone(self) -> None:
        # R = 0.55 -> persistent 0.05 = one inform quantum, no body.
        game = _inform_game(suspicion=0.55, turns=_inform_voice_turns())
        assert decompose_ejection_channels(game, 0) == frozenset(
            {CHANNEL_SINGLE_WITNESS_INFORM}
        )

    def test_inform_stacks_with_body_proximity(self) -> None:
        # R = 0.75 -> persistent 0.25 = body 0.20 + inform 0.05.
        game = _inform_game(suspicion=0.75, turns=_inform_voice_turns())
        assert decompose_ejection_channels(game, 0) == frozenset(
            {CHANNEL_BODY_PROXIMITY, CHANNEL_SINGLE_WITNESS_INFORM}
        )

    def test_no_voice_same_mass_is_body_not_inform(self) -> None:
        # Same R = 0.55 but a BARE accusation (no observation backing) is no
        # inform voice, so the +0.05-aligned mass stays body proximity — the
        # band gate, not the magnitude, is what credits the channel.
        no_voice = _game(
            meetings=(
                _meeting(
                    outcome="EJECTED",
                    ejected=_IMPOSTOR,
                    turns=(
                        _turn(
                            speaker=_CREW,
                            index=0,
                            claims=(_accusation(against=_IMPOSTOR),),
                        ),
                    ),
                    llm_calls=(_graph_call(agent_id="p-0", suspicion=0.55),),
                ),
            )
        )
        assert decompose_ejection_channels(no_voice, 0) == frozenset(
            {CHANNEL_BODY_PROXIMITY}
        )

    def test_committed_w2_credits_single_witness_inform(self) -> None:
        # The inform fold is recording-time (Task 10.15); the committed W2 bytes
        # carry it LIVE. Re-extracted on the baseline-4 Qwen/Qwen3.6-27B
        # (qwen3_6_27b.v1, all four templates, the 6-lever Wave-0 substrate all
        # unconditionally ON) re-record the channel credits 0 conversions to the
        # single-witness inform band. (This reads the vote-prompt suspicion graph;
        # the parser's header anchor survives the qwen3_6_27b restyle — but on the
        # baseline-4 substrate, with transcript contradiction flags collapsed, no
        # ejection re-derives into the single-witness inform band.)
        report = build_report(_COMMITTED_9P2I_DIR)
        result = compute_multi_signal_conversion(report.report.games)
        assert result.conversions_with_single_witness_inform == 0


def test_gate_spec_states_the_three_tiers_separately() -> None:
    spec = WAVE2_GATE_SPEC
    assert "HARD" in spec
    assert "DIRECTIONAL" in spec
    assert "GUARDRAIL" in spec
    # the guardrail (win split) is explicitly NOT a hard gate
    assert "NOT a hard gate" in spec
    # the directional gates name the Wave-2 levers
    assert "do_task" in spec
    assert "effective_deflection" in spec
    assert "conversion_per_meeting" in spec
    assert "inform" in spec
