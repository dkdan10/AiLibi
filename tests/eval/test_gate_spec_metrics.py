"""Tests for the Task 10.6 gp-7 gate-spec metrics (DESIGN.md §11.3).

Audit anchor: audit-2026-06-11-2218-gameplay-data.md gp-7 (C-C-6). Three
layers, mirroring :mod:`tests.eval.test_gate_metrics`:

* **Channel decomposition** (:func:`eval.meeting_quality.decompose_ejection_channels`)
  — synthetic shapes for each §6.3 design channel over the quantized rule
  lattice, including the 1.0-clamp vent shape where carry is
  presence-attributed.
* **Aggregates** — :func:`compute_multi_signal_conversion` /
  :func:`compute_supply_gauges` folds plus their fail-loud validators.
* **Committed pins** — the gauges and the decomposition read the committed
  9p2i bytes.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
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
from eval.report_io import read_report_text, report_path
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
    AlibiSegment,
    ContradictionRef,
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
    is_weak_contradiction,
)
from orchestrator.replay import LLMCallRecord
from tests._helpers.recorded_counts import recorded_counts

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
_COMMITTED_9P2I_REPORT = report_path(_COMMITTED_9P2I_DIR)


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
        type="alibi",
        subject=subject,
        route=(AlibiSegment(room=room, from_tick=from_tick, to_tick=to_tick),),
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
    contradictions: tuple[ContradictionRef, ...] | None = None,
    llm_calls: tuple[LLMCallRecord, ...] = (),
    meeting_id: str = "m-0",
) -> MeetingReport:
    """A resolved meeting whose recorded flags are what the detector emitted.

    The instruments read the RECORDED array, so a fixture that leaves it empty
    while the transcript carries a contradiction records a meeting the game
    never played. Recording the detector's own output keeps every fixture a
    faithful recording of its transcript; pass ``contradictions`` explicitly
    to record something the transcript alone cannot mint (a grounded
    ``vent_sighting``) or to plant a row that disagrees with it.
    """

    ballots = tuple(_ballot(voter=voter) for voter in voters)
    transcript = MeetingTranscript(turns=turns)
    recorded = (
        detect_contradictions(
            transcript, roster=frozenset(ballot.voter for ballot in ballots)
        )
        if contradictions is None
        else contradictions
    )
    return MeetingReport(
        meeting_id=meeting_id,
        tick=40,
        triggered_by="p-0",
        trigger="report",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=transcript,
        ballots=ballots,
        contradictions=recorded,
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

    def test_an_impostor_accusing_itself_is_not_an_accused_impostor_meeting(
        self,
    ) -> None:
        # Planted: the only accusation of an impostor is its own, so no other
        # voter accused it and the meeting is not in the gauge's population.
        meeting = _meeting(
            turns=(
                _turn(
                    speaker=_IMPOSTOR,
                    index=0,
                    kind="opening",
                    claims=(_accusation(against=_IMPOSTOR),),
                ),
            ),
            llm_calls=(_graph_call(agent_id="p-0", rows={_IMPOSTOR: 0.70}),),
        )
        gauges = compute_supply_gauges((_game(meetings=(meeting,)),))

        assert gauges.accused_impostor_meetings == 0
        assert gauges.over_gate_listener_rows == 0
        assert gauges.over_gate_listeners_per_accused_impostor_meeting is None

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
# The folds over the committed 9p2i bytes, cross-checked rather than transcribed
# ---------------------------------------------------------------------------


def _load_committed_9p2i() -> TournamentEvalReport:
    return TournamentEvalReport.model_validate_json(
        read_report_text(_COMMITTED_9P2I_REPORT)
    )


@dataclass(frozen=True)
class _RecordedSupply:
    """The supply gauges' flag and accusation counts, folded off the replay rows."""

    meetings: int
    flags: int
    weak_flags: int
    strong_flags: int
    zero_flag_meetings: int
    crew_subjects: int
    impostor_subjects: int
    accused_impostor_meetings: int


def _recorded_supply(
    set_dir: Path, roles_by_game: Mapping[str, Mapping[PlayerId, Role]]
) -> _RecordedSupply:
    """Fold ``set_dir``'s recorded meeting rows into the supply gauges' counts.

    The second surface beside the committed report the gauges read: the raw
    ``kind == "meeting"`` rows of every replay file, their non-vent flags (the
    band read by the production predicate
    :func:`meetings.transcript.is_weak_contradiction`) and their accusation
    claims, with each game's roles taken from the report by ``game_id``.
    Counts only; no text leaves this function.
    """

    meetings = flags = weak = strong = zero = crew = impostor = accused = 0
    for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                if row.get("kind") != "meeting":
                    continue
                roles = roles_by_game[row["game_id"]]
                meetings += 1
                recorded = [
                    ContradictionRef.model_validate(flag)
                    for flag in row["contradictions"]
                    if flag["kind"] != "vent_sighting"
                ]
                flags += len(recorded)
                zero += int(not recorded)
                for flag in recorded:
                    if is_weak_contradiction(flag):
                        weak += 1
                    else:
                        strong += 1
                    for subject in flag.subjects:
                        if roles[subject] == "IMPOSTOR":
                            impostor += 1
                        else:
                            crew += 1
                accused += int(
                    any(
                        claim["type"] == "accusation"
                        and claim["against"] != turn["speaker"]
                        and roles[claim["against"]] == "IMPOSTOR"
                        for turn in row["transcript"]["turns"]
                        for claim in turn["claims"]
                    )
                )
    return _RecordedSupply(
        meetings=meetings,
        flags=flags,
        weak_flags=weak,
        strong_flags=strong,
        zero_flag_meetings=zero,
        crew_subjects=crew,
        impostor_subjects=impostor,
        accused_impostor_meetings=accused,
    )


class TestCommittedGateSpecFolds:
    """The gp-7 folds over the committed 9p2i bytes agree with the report.

    No count of the shown bytes is transcribed here: ``build_sample_report.py
    --check`` holds the committed report these folds read byte for byte, and the
    synthetic cases above hold each fold. What stays is the cross-check of two
    surfaces over the shown bytes: the per-ejection decomposition, the
    multi-signal fold and the committed report's own impostor-ejection count
    agree, and the supply gauges equal an independent fold of the recorded
    meeting rows and sit inside the committed report's flag taxonomy. The
    committed report carries no supply block, so no byte-identity gate holds
    the gauges themselves. The over-gate listener rows parse each voter's
    rendered graph, which no second surface counts: the synthetic case above
    holds that fold, and its shown count is not asserted.
    """

    def test_the_decomposition_the_fold_and_the_report_agree(self) -> None:
        report = _load_committed_9p2i()
        channels_by_site = {
            f"seed-{game.seed}:m{index}": sorted(channels)
            for game in report.report.games
            for index in range(len(game.meetings))
            if (channels := decompose_ejection_channels(game, index)) is not None
        }
        result = compute_multi_signal_conversion(report.report.games)

        assert result.impostor_ejections > 0
        assert result.impostor_ejections == report.conversion.impostor_ejections
        assert len(channels_by_site) == result.impostor_ejections
        assert result.multi_signal_conversions == sum(
            1 for channels in channels_by_site.values() if len(channels) >= 2
        )
        assert result.single_signal_conversions == sum(
            1 for channels in channels_by_site.values() if len(channels) == 1
        )
        counts = Counter(
            channel for channels in channels_by_site.values() for channel in channels
        )
        assert {
            CHANNEL_CONTRADICTION_FLAG: result.conversions_with_contradiction_flag,
            CHANNEL_BODY_PROXIMITY: result.conversions_with_body_proximity,
            CHANNEL_VENT_WITNESS: result.conversions_with_vent_witness,
            CHANNEL_PRIOR_MEETING_CARRY: result.conversions_with_prior_meeting_carry,
        } == {
            channel: counts[channel]
            for channel in (
                CHANNEL_CONTRADICTION_FLAG,
                CHANNEL_BODY_PROXIMITY,
                CHANNEL_VENT_WITNESS,
                CHANNEL_PRIOR_MEETING_CARRY,
            )
        }

    def test_the_supply_gauges_equal_a_fold_of_the_recorded_rows(self) -> None:
        report = _load_committed_9p2i()
        games = report.report.games
        gauges = compute_supply_gauges(games)
        recorded = _recorded_supply(
            _COMMITTED_9P2I_DIR, {game.game_id: game.roles for game in games}
        )

        assert gauges.meetings_total == recorded.meetings > 0
        assert gauges.total_flags == recorded.flags
        assert (gauges.weak_flags, gauges.strong_flags) == (
            recorded.weak_flags,
            recorded.strong_flags,
        )
        assert gauges.zero_contradiction_meetings == recorded.zero_flag_meetings
        assert (gauges.flag_subjects_crew, gauges.flag_subjects_impostor) == (
            recorded.crew_subjects,
            recorded.impostor_subjects,
        )
        assert gauges.accused_impostor_meetings == recorded.accused_impostor_meetings
        assert gauges.genuine_subject_meetings == sum(
            1
            for game in games
            for meeting in game.meetings
            if genuine_class_subjects(meeting)
        )

        # The committed report's taxonomy is the other surface: it partitions
        # every recorded flag, vent sightings included, and its weak-signal and
        # cross-statement classes are the non-vent weak and strong flags that
        # do not link one artifact to itself.
        taxonomy = report.deduction.evidence_taxonomy
        vent_flags = recorded_counts(_COMMITTED_9P2I_DIR).flag_kinds.get(
            "vent_sighting", 0
        )
        assert taxonomy.flags_total == gauges.total_flags + vent_flags
        assert gauges.weak_flags >= taxonomy.weak_signal_flags
        assert gauges.strong_flags >= taxonomy.cross_statement_flags
