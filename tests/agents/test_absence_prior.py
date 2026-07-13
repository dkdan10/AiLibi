"""Tests for the Task 16.8 absence-prior lever (default-OFF).

Pins the Task 16.8 absence prior end to end: a publicly UNPLACED living player
(:func:`meetings.transcript.absent_players` -- the meeting's living roster minus
the players public testimony placed) takes the WEAK
:data:`~agents.memory.beliefs.ABSENCE_SUSPICION_DELTA` (0.08) in the TRANSIENT
``pre_vote`` half of :func:`~agents.memory.beliefs.apply_meeting_evidence_rules`,
behind the default-OFF :func:`~agents.memory.beliefs.absence_prior_enabled` lever.

The delta is the :data:`~agents.memory.beliefs.WEAK_CONTRADICTION_SUSPICION_DELTA`
lone-weak-signal discipline applied to a SECOND weak channel (Task 16.8's sizing
contract): alone it stays sub-gate (0.50 + 0.08 = 0.58 < the §4.6 0.60 gate -- a
quiet crewmate is never ejectable on absence alone), while stacked with a second
independent weak signal it deliberately CAN cross. The documented boundary table
below is pinned BOTH as the raw constant arithmetic AND as the value realized
through the fold, then quantize-then-compared on the vote surface's ``"%.2f"``
grid (the Task 15.6 band lesson), per the Task 15.5 boundary-sum precedent
(:class:`tests.agents.test_beliefs.TestBoundarySumGateCrossings`).

Composition is never bypassed (the constant's docstring): the delta rides the
Task 14.10 :data:`~agents.memory.beliefs.CONTRADICTION_RENDER_CEIL` ceiling, the
Task 15.5 :data:`~agents.memory.beliefs.REPORTER_EXCULPATION_SOFT_LIFT_CAP`, the
§4.7 teammate / self / roster guards, and -- downstream in the manager's
vote-time graph -- :func:`meetings.manager._joint_capped_suspicion`. It is a SOFT
``testimony_spread``-channel movement that mints NO
:class:`~meetings.schemas.ContradictionRef`, so the Task 16.6 citation gate's
zero-flag boundary is structurally out of reach (the flag-independence both tasks
pin -- the 16.8 side mirrors
:class:`tests.meetings.test_citation_gate.TestAbsenceDeltaNonInteraction`).

Layout mirrors the Task-16.4 hard-evidence-gate suite
(:mod:`tests.agents.test_beliefs_hard_evidence_gate`): the resolver's default-OFF
/ truthy-ON contract, the sizing invariants, the documented boundary table, the
transient-only + guard + reporter + ceiling + joint-cap composition pins, the
flag-independence pin, the OFF-path byte-identity pins, and the offline
counterfactual RE-MEASURED on the committed baseline-3 9p2i bytes (the DoD-bullet-4
calibration evidence, cloned from
:class:`tests.agents.test_beliefs_hard_evidence_gate.TestHardEvidenceGateOnCommittedBytes`).
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from orchestrator.replay import MeetingReplayEntry

from agents.memory.beliefs import (
    ABSENCE_SUSPICION_DELTA,
    ACCUSATION_SUSPICION_DELTA,
    CONTRADICTION_RENDER_CEIL,
    ENV_ABSENCE_PRIOR,
    MEETING_CONTRADICTION_LIFT_CAP,
    MEETING_SUSPICION_DECAY_RATE,
    SUSPICION_PROVENANCE_ATOL,
    TESTIMONY_SPREAD_CAP_DELTA,
    TESTIMONY_SPREAD_TWO_VOICE_DELTA,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
    BeliefState,
    PlayerBelief,
    absence_prior_enabled,
    apply_contradiction_rule,
    apply_meeting_evidence_rules,
)
from meetings.manager import (
    MeetingBeliefEvidence,
    SuspicionEntry,
    _suspicion_graph_with_contradictions,  # noqa: PLC2701
    derive_belief_evidence,
    guard_ballot_citation,
)
from meetings.schemas import ContradictionRef, MeetingTranscript, VoteBallot
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_SELF_STATED,
)
from orchestrator.replay import _TOGGLEABLE_LEVER_RESOLVERS  # noqa: PLC2701

_GATE = 0.60  # DESIGN.md §4.6 eject gate (inclusive)
_NEUTRAL = 0.50  # the neutral suspicion prior
_LEVER_ON: dict[str, str] = {ENV_ABSENCE_PRIOR: "1"}
_LEVER_OFF: dict[str, str] = {}


def _snapshot(state: BeliefState) -> dict[str, PlayerBelief]:
    """Every belief row as a frozen snapshot (scalar + provenance) -- for =="""

    return {player_id: state.view(player_id) for player_id in state.known_players()}


def _rendered(value: float) -> str:
    """The vote surface's ``"%.2f"`` render of ``value`` (the 15.6 band grid)."""

    return "%.2f" % value


def _weak_flag(subject: str) -> ContradictionRef:
    """One detector-flagged WEAK ``alibi_conflict`` naming ``subject`` (+0.08).

    Appends the exact self-stated marker
    :func:`meetings.transcript.detect_contradictions` writes, so the weak
    classification path under test is the production one (the precedent shape in
    :func:`tests.agents.test_beliefs._meeting_flag`).
    """

    description = (
        f"Alibi places {subject} in A (ticks 0-9); "
        f"sighting reports {subject} in B at tick 5. "
        f"{WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_SELF_STATED}]"
    )
    return ContradictionRef(
        contradiction_id=f"contra:alibi_conflict:{subject}",
        kind="alibi_conflict",
        event_a_id="a",
        event_b_id="b",
        subjects=(subject,),
        description=description,
    )


def _strong_flag(subject: str) -> ContradictionRef:
    """One STRONG (non-weak) ``alibi_conflict`` naming ``subject`` (+0.30).

    Clones :func:`tests.agents.test_beliefs_hard_evidence_gate._strong_flag`.
    """

    return ContradictionRef(
        contradiction_id=f"c-{subject}",
        kind="alibi_conflict",
        subjects=(subject,),
        description="strong cross-speaker conflict",
        event_a_id="turn:m-1:turn-0:claim:0",
        event_b_id="turn:m-1:turn-1:claim:0",
    )


# --------------------------------------------------------------------------- #
# A. The resolver (cloned from the 16.4 hard-evidence-gate resolver)           #
# --------------------------------------------------------------------------- #


class TestAbsencePriorResolver:
    """The Task-16.8 lever resolver -- DEFAULT-OFF, the 16.4 live-toggle pattern.

    Clones :func:`agents.memory.beliefs.hard_evidence_gate_enabled` (itself the
    retired 13.5 / 14.10 / 15.5 pattern): an unset / empty / unrecognised value
    reads ``False`` so the pre-vote fold stays byte-identical to the committed
    baseline-3 substrate; ``1/true/yes/on`` (case-insensitive, whitespace-trimmed)
    reads ``True``. ``env=None`` falls back to the live process environment.
    """

    def test_default_off_on_an_empty_mapping(self) -> None:
        # The DEFAULT: a bare env cell resolves OFF, so no absent subject lifts.
        assert absence_prior_enabled(env={}) is False

    def test_default_off_when_the_key_is_absent(self) -> None:
        # An unrelated export leaves the lever OFF -- only its own key counts.
        assert absence_prior_enabled(env={"AILIBI_SOMETHING_ELSE": "1"}) is False

    @pytest.mark.parametrize(
        "value",
        ["1", "true", "yes", "on", "TRUE", "Yes", "On", " on ", " 1 ", "\tyes\n"],
    )
    def test_on_for_each_truthy_value_and_case_or_whitespace_variant(
        self, value: str
    ) -> None:
        # Every documented truthy token, plus case + surrounding-whitespace
        # variants (the resolver strips then lowercases before the set test).
        assert absence_prior_enabled(env={ENV_ABSENCE_PRIOR: value}) is True

    @pytest.mark.parametrize(
        "value", ["0", "", "garbage", "2", "no", "off", "false", "yesno", "  "]
    )
    def test_off_for_falsy_or_unrecognised_values(self, value: str) -> None:
        # Explicit falsy tokens, the empty string, and junk all read OFF: the
        # resolver is an allow-list membership test, not a truthiness cast.
        assert absence_prior_enabled(env={ENV_ABSENCE_PRIOR: value}) is False

    def test_env_none_reads_the_live_process_environment_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # ``env=None`` (and the bare call) reads ``os.environ`` LIVE.
        monkeypatch.setenv(ENV_ABSENCE_PRIOR, "1")
        assert absence_prior_enabled() is True
        assert absence_prior_enabled(env=None) is True

    def test_env_none_reads_the_live_process_environment_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # With the export deleted the live read is OFF -- the default.
        monkeypatch.delenv(ENV_ABSENCE_PRIOR, raising=False)
        assert absence_prior_enabled() is False
        assert absence_prior_enabled(env=None) is False

    def test_env_argument_is_not_mutated_and_reads_deterministically(self) -> None:
        # The resolver never writes its env argument (pure read), so two calls on
        # the same mapping agree and the mapping is unchanged.
        env = {ENV_ABSENCE_PRIOR: "on", "AILIBI_OTHER": "x"}
        before = dict(env)
        assert absence_prior_enabled(env=env) is True
        assert absence_prior_enabled(env=env) is True
        assert env == before

    def test_resolver_is_the_registered_toggleable_lever(self) -> None:
        # The FOURTH live entry in the replay registry (16.4 -> 16.5 -> 16.6 ->
        # 16.8 chain order); the registry suite owns the ordering pin, this is a
        # light identity check that the resolver object is the one registered.
        registered = dict(_TOGGLEABLE_LEVER_RESOLVERS)
        assert registered["absence_prior"] is absence_prior_enabled


# --------------------------------------------------------------------------- #
# B. Sizing invariants (the WEAK lone-signal discipline)                       #
# --------------------------------------------------------------------------- #


class TestAbsenceSizingInvariants:
    """The Task-16.8 sizing contract: a weak, informs-but-cannot-eject delta.

    Mirrors :class:`tests.agents.test_beliefs.TestBoundarySumGateCrossings`'s
    gate-distance invariant on the second weak channel.
    """

    def test_absence_delta_is_exactly_the_documented_value(self) -> None:
        assert ABSENCE_SUSPICION_DELTA == 0.08

    def test_absence_delta_respects_the_contract_ceiling(self) -> None:
        # The contract's upper bound on the magnitude (a single tuning point).
        assert ABSENCE_SUSPICION_DELTA <= 0.08

    def test_absence_alone_cannot_eject_a_baseline_listener(self) -> None:
        # THE structural informs-but-cannot-eject pin: the delta is strictly less
        # than the 0.10 gate-distance from the 0.50 baseline, so absence on a
        # neutral prior lands at 0.58 -- never over the §4.6 gate alone.
        assert ABSENCE_SUSPICION_DELTA < _GATE - _NEUTRAL
        assert _NEUTRAL + ABSENCE_SUSPICION_DELTA < _GATE


# --------------------------------------------------------------------------- #
# C. The documented boundary table (raw + realized + rendered)                 #
# --------------------------------------------------------------------------- #


def _fold_pre_vote(beliefs: BeliefState, **kwargs: object) -> BeliefState:
    """A ``pre_vote`` absence fold with the lever ON (the realized-value path)."""

    return apply_meeting_evidence_rules(
        beliefs,
        own_id="observer",
        phase="pre_vote",
        env=_LEVER_ON,
        **kwargs,  # type: ignore[arg-type]
    )


# The documented boundary rows whose value is exact constant arithmetic (the
# decay-drift and transient-repeat rows need iteration / multiple meetings and
# are pinned in their own tests below). Each: (description, raw, rendered, crosses).
_CLEAN_BOUNDARY_ROWS: tuple[tuple[str, float, str, bool], ...] = (
    (
        "absence alone on the neutral prior",
        _NEUTRAL + ABSENCE_SUSPICION_DELTA,
        "0.58",
        False,
    ),
    (
        "absence + single-voice inform (+0.05)",
        _NEUTRAL + ACCUSATION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA,
        "0.63",
        True,
    ),
    (
        "absence + two-voice graduated spread (+0.12)",
        _NEUTRAL + TESTIMONY_SPREAD_TWO_VOICE_DELTA + ABSENCE_SUSPICION_DELTA,
        "0.70",
        True,
    ),
    (
        "absence + capped 3+-voice spread (+0.15)",
        _NEUTRAL + TESTIMONY_SPREAD_CAP_DELTA + ABSENCE_SUSPICION_DELTA,
        "0.73",
        True,
    ),
    (
        "absence + fresh accusation-carry prior (0.55)",
        _NEUTRAL + ACCUSATION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA,
        "0.63",
        True,
    ),
    (
        "absence + a lone weak contradiction flag (+0.08)",
        _NEUTRAL + WEAK_CONTRADICTION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA,
        "0.66",
        True,
    ),
)


class TestAbsenceBoundaryTable:
    """The documented boundary table (the constant's docstring; Task 16.8).

    The core of this task, the Task-15.5 boundary-sum precedent applied to the
    absence channel. Each row is pinned three ways: the raw constant arithmetic
    on the exact floats, the value REALIZED through
    :func:`~agents.memory.beliefs.apply_meeting_evidence_rules` (lever ON,
    ``phase="pre_vote"``), and the quantize-then-compare rendered verdict
    (``float("%.2f" % value)`` vs the 0.60 gate -- the Task 15.6 band lesson,
    IEEE-luck excluded). The table IS the design intent.
    """

    @pytest.mark.parametrize(
        ("description", "raw", "rendered", "crosses"),
        _CLEAN_BOUNDARY_ROWS,
        ids=[row[0] for row in _CLEAN_BOUNDARY_ROWS],
    )
    def test_boundary_row_renders_on_the_correct_side_of_the_gate(
        self, description: str, raw: float, rendered: str, crosses: bool
    ) -> None:
        # The pure "table IS the design intent" pin: the raw arithmetic renders on
        # the ``"%.2f"`` grid exactly as documented, and quantize-then-compare puts
        # it on the intended side of the inclusive 0.60 gate.
        assert _rendered(raw) == rendered
        assert (float(_rendered(raw)) >= _GATE) is crosses

    def test_absence_alone_is_sub_gate_raw_and_realized(self) -> None:
        # UNDER: absence alone on the neutral prior -> 0.58.
        realized = (
            _fold_pre_vote(BeliefState(), accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + ABSENCE_SUSPICION_DELTA
        assert raw == 0.58  # noqa: PLR2004 -- the exact documented boundary
        assert realized == raw
        assert realized < _GATE
        assert _rendered(realized) == "0.58"

    def test_absence_plus_single_voice_inform_crosses(self) -> None:
        # CROSSES: absence + the single-voice inform (+0.05, one voice) -> 0.63.
        realized = (
            _fold_pre_vote(
                BeliefState(),
                accused=("p-2",),
                pre_vote_informed=frozenset({"p-2"}),
                pre_vote_voice_counts={"p-2": 1},
                absent=frozenset({"p-2"}),
            )
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + ACCUSATION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA
        assert realized == raw
        assert realized >= _GATE
        assert _rendered(realized) == "0.63"

    def test_absence_plus_two_voice_spread_crosses(self) -> None:
        # CROSSES: absence + the two-voice graduated spread (+0.12) -> 0.70.
        realized = (
            _fold_pre_vote(
                BeliefState(),
                accused=("p-2",),
                pre_vote_folded=frozenset({"p-2"}),
                pre_vote_voice_counts={"p-2": 2},
                absent=frozenset({"p-2"}),
            )
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + TESTIMONY_SPREAD_TWO_VOICE_DELTA + ABSENCE_SUSPICION_DELTA
        assert realized == raw
        assert realized >= _GATE
        assert _rendered(realized) == "0.70"

    def test_absence_plus_capped_spread_crosses(self) -> None:
        # CROSSES: absence + the capped 3+-voice spread (+0.15) -> 0.73.
        realized = (
            _fold_pre_vote(
                BeliefState(),
                accused=("p-2",),
                pre_vote_folded=frozenset({"p-2"}),
                pre_vote_voice_counts={"p-2": 3},
                absent=frozenset({"p-2"}),
            )
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + TESTIMONY_SPREAD_CAP_DELTA + ABSENCE_SUSPICION_DELTA
        assert realized == raw
        assert realized >= _GATE
        assert _rendered(realized) == "0.73"

    def test_absence_plus_fresh_accusation_carry_crosses(self) -> None:
        # CROSSES: absence + a FRESH accusation-carry prior (0.55, accused last
        # meeting, undecayed) -> 0.63. Accused-then-unaccounted IS the two-signal
        # shape. The carry rides in as the seeded prior; only absence lifts here.
        seed = BeliefState()
        seed.adjust_suspicion(
            "p-2", delta=ACCUSATION_SUSPICION_DELTA, source="accusation_carry"
        )
        assert seed.view("p-2").suspicion == _NEUTRAL + ACCUSATION_SUSPICION_DELTA
        realized = (
            _fold_pre_vote(seed, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + ACCUSATION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA
        assert realized == raw
        assert realized >= _GATE
        assert _rendered(realized) == "0.63"

    def test_absence_plus_lone_weak_flag_crosses(self) -> None:
        # CROSSES: absence + a lone WEAK contradiction flag (+0.08) -> 0.66.
        # Composed the way test_beliefs realizes weak-flag lifts: the contradiction
        # rule lands the 0.08 weak delta, then the pre-vote absence fold lands its
        # 0.08 on top (0.50 -> 0.58 -> 0.66).
        after_flag = apply_contradiction_rule(BeliefState(), [_weak_flag("p-2")])
        assert after_flag.view("p-2").suspicion == pytest.approx(
            _NEUTRAL + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        realized = (
            _fold_pre_vote(after_flag, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        raw = _NEUTRAL + WEAK_CONTRADICTION_SUSPICION_DELTA + ABSENCE_SUSPICION_DELTA
        assert realized == pytest.approx(raw)
        assert realized >= _GATE
        assert _rendered(realized) == "0.66"

    def test_absence_repeated_across_meetings_never_accumulates(self) -> None:
        # UNDER (the transient discipline): absence is applied in the ``pre_vote``
        # half ONLY. Production absorbs the meeting through the PERSISTENT half
        # (``phase=None`` -- it never passes ``absent``), so a perpetually
        # unplaced quiet crewmate renders 0.58 every meeting and NEVER accumulates
        # toward the gate. Simulate three quiet meetings: each persistent absorb
        # carries no absence residue, so the next meeting's pre-vote absence still
        # renders exactly 0.58 from the persisted (neutral) state.
        persisted = BeliefState()
        for _ in range(3):
            # The vote-time (transient) graph: absence lifts to 0.58 this meeting.
            vote_graph = _fold_pre_vote(
                persisted, accused=(), absent=frozenset({"p-2"})
            )
            assert vote_graph.view("p-2").suspicion == 0.58  # noqa: PLR2004
            assert _rendered(vote_graph.view("p-2").suspicion) == "0.58"
            # The persistent absorb (what production runs) never sees ``absent``:
            # the quiet crewmate is unreinforced, so nothing accumulates.
            persisted = apply_meeting_evidence_rules(
                persisted, own_id="observer", accused=(), phase=None
            )
            assert persisted.view("p-2").suspicion == _NEUTRAL

    def test_absence_on_deep_decay_drifted_prior_stays_sub_gate(self) -> None:
        # UNDER: absence + a DECAY-DRIFTED stale prior. A lone accusation bump
        # (0.55) left unreinforced decays into the neutral band across FIVE quiet
        # meetings (0.50 + 0.05 * 0.75**5 ~= 0.5119), and absence on top renders
        # 0.59 < 0.60 -- the delta never resurrects suspicion the Rule-5 decay
        # already discounted.
        seed = BeliefState()
        seed.adjust_suspicion(
            "p-2", delta=ACCUSATION_SUSPICION_DELTA, source="accusation_carry"
        )
        for _ in range(5):
            seed.decay_suspicion("p-2", rate=MEETING_SUSPICION_DECAY_RATE)
        drifted = seed.view("p-2").suspicion
        realized = (
            _fold_pre_vote(seed, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        assert realized == pytest.approx(drifted + ABSENCE_SUSPICION_DELTA)
        assert realized == pytest.approx(0.591865234375)
        assert realized < _GATE  # raw under the gate
        assert _rendered(realized) == "0.59"  # and renders sub-gate too
        assert float(_rendered(realized)) < _GATE

    def test_absence_on_shallow_decay_drifted_prior_lands_at_the_render_band(
        self,
    ) -> None:
        # The DOCUMENTED BOUNDARY of the non-crossing claim (the Task 15.6 band
        # behaviour, deliberate). After only FOUR decays (~0.5158) absence lands
        # at ~0.5958 -- RAW still under the gate, but it RENDERS "0.60" and so sits
        # AT the gate on the ``"%.2f"`` grid the ballot reads. Pinned honestly as
        # the edge of the "absence never accumulates over the gate" claim.
        seed = BeliefState()
        seed.adjust_suspicion(
            "p-2", delta=ACCUSATION_SUSPICION_DELTA, source="accusation_carry"
        )
        for _ in range(4):
            seed.decay_suspicion("p-2", rate=MEETING_SUSPICION_DECAY_RATE)
        realized = (
            _fold_pre_vote(seed, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        assert realized == pytest.approx(0.5958203125)
        assert realized < _GATE  # raw is UNDER the gate ...
        assert _rendered(realized) == "0.60"  # ... but renders AT it (band edge)
        assert float(_rendered(realized)) >= _GATE


# --------------------------------------------------------------------------- #
# D. Transient-only discipline                                                 #
# --------------------------------------------------------------------------- #


class TestAbsenceTransientOnly:
    """Absence applies in the ``pre_vote`` half ONLY -- never persistently.

    The persistent halves (``post_vote`` / composed ``None`` -- the boundary every
    production absorb reaches) ignore ``absent`` entirely, so absence can never
    accumulate across meetings and leaves no residue in the stored state.
    """

    @pytest.mark.parametrize("phase", ["post_vote", None])
    def test_persistent_halves_apply_no_absence_delta(self, phase: str | None) -> None:
        # phase=post_vote and phase=None with ``absent`` non-empty and the lever ON
        # produce the SAME state as absent=frozenset() -- the delta is not applied.
        with_absent = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=(),
            phase=phase,  # type: ignore[arg-type]
            absent=frozenset({"p-2", "p-3"}),
            env=_LEVER_ON,
        )
        without_absent = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=(),
            phase=phase,  # type: ignore[arg-type]
            absent=frozenset(),
            env=_LEVER_ON,
        )
        assert _snapshot(with_absent) == _snapshot(without_absent)
        # No absence row materialised on the persistent path.
        assert "p-2" not in with_absent.known_players()
        assert "p-3" not in with_absent.known_players()

    def test_a_full_meeting_cycle_carries_no_absence_residue(self) -> None:
        # After a full meeting -- transient pre-vote absence lift then the
        # persistent composed absorb -- the persisted state holds no absence
        # residue: the unreinforced absent subject is back at (or absent from) the
        # neutral prior, exactly as if the lever had never fired.
        transient = _fold_pre_vote(BeliefState(), accused=(), absent=frozenset({"p-2"}))
        assert transient.view("p-2").suspicion == 0.58  # noqa: PLR2004
        persisted = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=(),
            phase=None,
            absent=frozenset({"p-2"}),
            env=_LEVER_ON,
        )
        assert persisted.known_players() == ()
        assert persisted.view("p-2").suspicion == _NEUTRAL


# --------------------------------------------------------------------------- #
# E. Guards (self / teammate / roster)                                         #
# --------------------------------------------------------------------------- #


class TestAbsenceGuards:
    """The §4.7 self / teammate firewall and the Task-10.2 roster filter.

    Absence rides the same guards as the accusation bump loop: no self row, no
    teammate lift, and no non-roster row when a roster is supplied.
    """

    def test_own_id_in_absent_mints_no_self_row(self) -> None:
        result = _fold_pre_vote(
            BeliefState(), accused=(), absent=frozenset({"observer", "p-2"})
        )
        assert "observer" not in result.known_players()
        assert result.view("p-2").suspicion == 0.58  # noqa: PLR2004

    def test_fellow_impostor_absent_subject_takes_no_lift(self) -> None:
        # The §4.7 team-internal firewall: an impostor listener never accrues the
        # absence lift against a fellow impostor -- no row even materialises.
        result = _fold_pre_vote(
            BeliefState(),
            accused=(),
            fellow_impostor_ids=("p-2",),
            absent=frozenset({"p-2", "p-3"}),
        )
        assert "p-2" not in result.known_players()
        assert result.view("p-2").suspicion == _NEUTRAL
        assert result.view("p-3").suspicion == 0.58  # noqa: PLR2004

    def test_non_roster_absent_id_is_filtered(self) -> None:
        # A non-roster absent id is dropped input-side (like the accusation
        # channel), so no row materialises; the roster subject alongside lifts.
        result = _fold_pre_vote(
            BeliefState(),
            accused=(),
            roster=frozenset({"observer", "p-3"}),
            absent=frozenset({"p-9", "p-3"}),
        )
        assert "p-9" not in result.known_players()
        assert result.view("p-3").suspicion == 0.58  # noqa: PLR2004


# --------------------------------------------------------------------------- #
# F. Reporter composition (Task 15.5)                                          #
# --------------------------------------------------------------------------- #


class TestAbsenceReporterComposition:
    """The Task-15.5 reporter cap composes with the absence lift.

    The body-report meeting's own reporter takes NO soft pre-vote lift -- absence
    included -- so the lever cannot re-open the H5 innocent-reporter railroad
    (:data:`~agents.memory.beliefs.REPORTER_EXCULPATION_SOFT_LIFT_CAP` = 0.0, an
    unconditional lever since Task 15.7).
    """

    def test_reporter_takes_no_absence_lift_while_others_do(self) -> None:
        result = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=(),
            phase="pre_vote",
            reporter="p-2",
            absent=frozenset({"p-2", "p-3"}),
            env=_LEVER_ON,
        )
        # The reporter's absence delta is capped to 0.0 -- stays exactly neutral.
        assert result.view("p-2").suspicion == _NEUTRAL
        # A non-reporter absent subject lifts to 0.58 in the same fold.
        assert result.view("p-3").suspicion == 0.58  # noqa: PLR2004


# --------------------------------------------------------------------------- #
# G. Ceiling composition (Task 14.10)                                          #
# --------------------------------------------------------------------------- #


class TestAbsenceCeilingComposition:
    """The Task-14.10 :data:`~agents.memory.beliefs.CONTRADICTION_RENDER_CEIL`.

    Absence rides the certain-guilt exclusion: a subject's absence lift can never
    reach the 1.0 clamp, and a prior already at/above the ceiling takes NO lift
    (the ceiling bounds the LIFT, never the prior).
    """

    def test_high_prior_plus_absence_lands_on_the_render_ceiling(self) -> None:
        # Seeded prior 0.95 + absence: the ceiling caps the lift at 0.97 - 0.95 =
        # 0.02, so the row lands EXACTLY on CONTRADICTION_RENDER_CEIL (0.97) --
        # never the naive 0.95 + 0.08 = 1.03 clamped to 1.0.
        seed = BeliefState()
        seed.seed_player("p-2", suspicion=0.95, trust=0.5)
        realized = (
            _fold_pre_vote(seed, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        assert 0.95 + ABSENCE_SUSPICION_DELTA > 1.0  # the naive sum overflows ...
        assert realized == CONTRADICTION_RENDER_CEIL  # ... the ceiling caps it
        assert realized < 1.0

    def test_prior_above_the_ceiling_takes_no_absence_lift(self) -> None:
        # A prior already ABOVE the ceiling (0.98) is exempt -- the ceiling bounds
        # the lift (to 0.0 here), never the prior, so the row is unchanged.
        seed = BeliefState()
        seed.seed_player("p-2", suspicion=0.98, trust=0.5)
        realized = (
            _fold_pre_vote(seed, accused=(), absent=frozenset({"p-2"}))
            .view("p-2")
            .suspicion
        )
        assert realized == 0.98  # noqa: PLR2004


# --------------------------------------------------------------------------- #
# H. Joint-cap composition at the manager level (Task 13.14 DoD)               #
# --------------------------------------------------------------------------- #


class TestAbsenceJointCapComposition:
    """The manager's :func:`meetings.manager._joint_capped_suspicion` composition.

    Absence + a STRONG flag on the same subject caps at ``prior + 0.30`` like every
    other transient stack: 0.80 from the neutral prior, NOT 0.88 -- and the emitted
    row's eight-field provenance sums to the capped scalar within
    :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`.
    """

    def test_absence_plus_strong_flag_caps_at_prior_plus_030(self) -> None:
        graph = (SuspicionEntry(player_id="X", suspicion=_NEUTRAL, trust=0.5),)
        evidence = MeetingBeliefEvidence(
            accused=(), corroborated=(), contradicted=(), absent=("X",)
        )
        rows = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=graph,
            contradictions=(_strong_flag("X"),),
            evidence=evidence,
            # A contradiction fold fails loud without the transcript (14.10 seam).
            transcript=MeetingTranscript(turns=()),
            env=_LEVER_ON,
        )
        row = {entry.player_id: entry for entry in rows}["X"]
        # The strong flag (+0.30) plus absence (+0.08) would reach 0.88; the joint
        # cap anchors at prior 0.50 + MEETING_CONTRADICTION_LIFT_CAP = 0.80.
        assert row.suspicion == pytest.approx(_NEUTRAL + MEETING_CONTRADICTION_LIFT_CAP)
        assert row.suspicion == pytest.approx(0.80)
        assert row.suspicion != pytest.approx(0.88)
        # The provenance sum invariant holds on the emitted (capped) row.
        decomposition = (
            row.flag_lift
            + row.body_proximity
            + row.kill_or_vent_pin
            + row.testimony_spread
            + row.accusation_carry
            + row.carried_hard
            + row.carried_soft
            + row.unattributed
        )
        assert _NEUTRAL + decomposition == pytest.approx(
            row.suspicion, abs=SUSPICION_PROVENANCE_ATOL
        )


# --------------------------------------------------------------------------- #
# I. Flag-independence (the 16.8 side of the 16.6 pin)                         #
# --------------------------------------------------------------------------- #


def _uncited_eject(target: str) -> VoteBallot:
    """An EJECT ballot with BOTH citation channels null (the 16.6 gated shape)."""

    return VoteBallot(
        voter="p-1",
        target=target,
        confidence=0.8,
        primary_reason_id=None,
        primary_reason_observation_id=None,
        considered_alternatives=(),
        rationale_text="a bare gut read.",
    )


class TestAbsenceFlagIndependence:
    """Absence moves SUSPICION only and mints no :class:`ContradictionRef`.

    The 16.8 side of the Task-16.6 non-interaction pin
    (:class:`tests.meetings.test_citation_gate.TestAbsenceDeltaNonInteraction`):
    structurally the absence fold records no inconsistency, and behaviourally an
    absence-lifted zero-flag target still coerces under the citation gate --
    suspicion is not evidence, and a flag is the only escape channel.
    """

    def test_absence_fold_records_no_inconsistency(self) -> None:
        # The lifted row carries an EMPTY inconsistency list -- absence mints no
        # flag (unlike apply_contradiction_rule, which records one).
        result = _fold_pre_vote(BeliefState(), accused=(), absent=frozenset({"p-2"}))
        assert result.view("p-2").suspicion == 0.58  # noqa: PLR2004
        assert result.view("p-2").inconsistencies == ()

    def test_absence_lift_over_the_gate_still_coerces_an_uncited_eject(self) -> None:
        # Behavioural mirror of TestAbsenceDeltaNonInteraction from the absence
        # side: even when the absence prior lifts a zero-flag target over the gate,
        # the citation gate coerces an uncited EJECT to SKIP -- the gate reads only
        # this meeting's flags, never suspicion.
        ballot = _uncited_eject("p-2")
        assert guard_ballot_citation(ballot=ballot, contradictions=()).target == "SKIP"
        # The ONLY escape channel is a flag -- which absence never mints.
        assert (
            guard_ballot_citation(ballot=ballot, contradictions=(_strong_flag("p-2"),))
            is ballot
        )


# --------------------------------------------------------------------------- #
# J. OFF-path byte-identity                                                    #
# --------------------------------------------------------------------------- #


class TestAbsenceOffPathByteIdentity:
    """Lever OFF (or an empty absent set) is byte-identical to the pre-16.8 fold.

    The lever is the ONLY switch: OFF the fold path is not even entered for an
    absence-only meeting, and the emitted graph is the input graph by identity; ON
    the rows change (0.58 rows appear).
    """

    def test_off_fold_with_absent_equals_the_no_absent_fold(self) -> None:
        # (i) fold level: lever OFF with ``absent`` non-empty produces a state
        # equal (rows + suspicion + provenance) to the no-absent fold. A seeded
        # decaying prior + an informed bump make the comparison non-vacuous.
        base = BeliefState()
        base.seed_player("p-7", suspicion=0.7, trust=0.5)
        with_absent = apply_meeting_evidence_rules(
            base,
            own_id="observer",
            accused=("p-5",),
            phase="pre_vote",
            pre_vote_informed=frozenset({"p-5"}),
            absent=frozenset({"p-3"}),
            env=_LEVER_OFF,
        )
        without_absent = apply_meeting_evidence_rules(
            base,
            own_id="observer",
            accused=("p-5",),
            phase="pre_vote",
            pre_vote_informed=frozenset({"p-5"}),
            absent=frozenset(),
            env=_LEVER_OFF,
        )
        assert _snapshot(with_absent) == _snapshot(without_absent)
        # No absence row OFF; the informed bump landed exactly.
        assert "p-3" not in with_absent.known_players()
        assert (
            with_absent.view("p-5").suspicion == _NEUTRAL + ACCUSATION_SUSPICION_DELTA
        )

    def test_graph_level_off_returns_the_input_tuple_by_identity(self) -> None:
        # (ii) graph level: an absence-ONLY meeting (no flags / folds /
        # corroborations) with the lever OFF never enters the fold path -- the
        # early return hands back the INPUT graph tuple, by identity.
        graph = (SuspicionEntry(player_id="p-3", suspicion=_NEUTRAL, trust=0.5),)
        evidence = MeetingBeliefEvidence(
            accused=(), corroborated=(), contradicted=(), absent=("p-3",)
        )
        emitted = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=graph,
            contradictions=(),
            evidence=evidence,
            transcript=None,
            env=_LEVER_OFF,
        )
        assert emitted is graph

    def test_graph_level_on_materialises_the_absence_rows(self) -> None:
        # (iii) the same absence-only meeting with the lever ON DOES change the
        # rows: the absent subject's row appears at 0.58 -- proving the lever is
        # the only switch between (ii) and here.
        graph = (SuspicionEntry(player_id="p-3", suspicion=_NEUTRAL, trust=0.5),)
        evidence = MeetingBeliefEvidence(
            accused=(), corroborated=(), contradicted=(), absent=("p-3",)
        )
        emitted = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=graph,
            contradictions=(),
            evidence=evidence,
            transcript=None,
            env=_LEVER_ON,
        )
        assert emitted is not graph
        assert {entry.player_id: entry.suspicion for entry in emitted} == {"p-3": 0.58}


# --------------------------------------------------------------------------- #
# K. The offline counterfactual on committed baseline-3 9p2i bytes (DoD 4)     #
# --------------------------------------------------------------------------- #

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class _AbsenceCounterfactual:
    """The full 9p2i absence-prior sweep, aggregated once (class-scoped)."""

    total_meetings: int
    nonempty_absent: int
    absent_histogram: tuple[tuple[int, int], ...]
    absent_min: int
    absent_max: int
    absent_median: float
    subset_ok: bool
    determinism_ok: bool
    new_over_gate_meetings: int
    top_candidate_change_meetings: int
    emergency_meetings: int


class TestAbsencePriorOnCommittedBytes:
    """The absence-prior counterfactual, MEASURED offline on the committed
    baseline-3 9p2i bytes (Task 16.8 DoD bullet 4; the 14.8 analysis-only
    machinery, cloned from
    :class:`tests.agents.test_beliefs_hard_evidence_gate.TestHardEvidenceGateOnCommittedBytes`).

    Baseline 3 was recorded with the lever OFF (it did not yet exist), so the
    recorded builder rows are the lever-OFF suspicion graph. This class walks every
    committed 9p2i meeting ONCE (CPU-only, ~10s, class-scoped), and per meeting
    derives ``evidence = derive_belief_evidence(...)`` to measure the absent set,
    then re-derives the per-voter vote-time fold TWICE via
    :func:`meetings.manager._suspicion_graph_with_contradictions` -- OFF (``env={}``)
    and ON (``env={AILIBI_ABSENCE_PRIOR: "1"}``), threading each voter's real
    ``fellow_impostor_ids`` (from the recorded roles) and the manager's exact
    reporter predicate so the measurement is production-faithful:
    ``_collect_one_ballot`` passes ``reporter=None`` for an EMERGENCY meeting
    (``_trigger_is_emergency``), and since ``reporter_exculpation_enabled`` is
    unconditional, getting this wrong is NOT inert -- a spuriously-threaded
    emergency reporter would have its soft lift zeroed on both sides of the
    re-derivation (the committed set has 15 emergency meetings; the recorded
    ``MeetingReplayEntry`` carries no trigger description, so the kind rides
    the walk's reconstructed trigger via ``ReconstructedMeeting.trigger_kind``).

    Absence only LIFTS (it never lowers), so a recorded conviction is never lost
    under the lever -- the counterfactual measures only the NEW-must-vote channel
    (a candidate ON pushes to/over the rendered gate that OFF left under it) and
    the argmax TOP-candidate churn. The measured aggregates are PINNED exactly:
    committed bytes are frozen, so these numbers are the calibration evidence the
    16.17 graduation decision re-checks on the adopting baseline.
    """

    _SET_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"

    @pytest.fixture(scope="class")
    def walk(
        self,
    ) -> dict[
        tuple[int, str],
        tuple[MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]], str | None],
    ]:
        from engine.world import load_canonical_map
        from tests.meetings.test_prompt_byte_golden import (
            _canonical_renderers,  # noqa: PLC2701
            _seed_paths,  # noqa: PLC2701
            walk_replay_meetings,
        )

        game_map = load_canonical_map()
        renderers = _canonical_renderers()
        collected: dict[
            tuple[int, str],
            tuple[
                MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]], str | None
            ],
        ] = {}
        for path in _seed_paths(self._SET_DIR):
            for meeting in walk_replay_meetings(
                path, game_map=game_map, renderers_for_set=renderers
            ):
                graphs = {p.agent_id: p.suspicion_graph for p in meeting.participants}
                collected[(meeting.seed, meeting.meeting_id)] = (
                    meeting.entry,
                    graphs,
                    meeting.trigger_kind,
                )
        return collected

    @pytest.fixture(scope="class")
    def roles_by_seed(self) -> dict[int, dict[str, str]]:
        report = json.loads(
            (self._SET_DIR / "tournament-eval-report.json").read_text(encoding="utf-8")
        )
        return {game["seed"]: game["roles"] for game in report["report"]["games"]}

    @staticmethod
    def _rendered_max_candidate(rows: dict[str, SuspicionEntry]) -> str | None:
        """The voter's §4.6 TOP candidate: argmax by RENDERED suspicion, ties by
        sorted player id (mirrors how the ballot template surfaces its max)."""

        if not rows:
            return None
        return min(
            rows.values(),
            key=lambda entry: (-float(_rendered(entry.suspicion)), entry.player_id),
        ).player_id

    def _voter_rows(
        self,
        entry: MeetingReplayEntry,
        graphs: dict[str, tuple[SuspicionEntry, ...]],
        roles: dict[str, str],
        evidence: MeetingBeliefEvidence,
        voters: list[str],
        *,
        reporter: str | None,
        env: dict[str, str],
    ) -> dict[str, dict[str, SuspicionEntry]]:
        """Re-derive each voter's post-fold rows under ``env`` (OFF or ON).

        ``reporter`` is the manager's exact predicate, computed by the caller:
        ``entry.triggered_by`` for a body report, ``None`` for an emergency
        meeting (``_collect_one_ballot``'s ``_trigger_is_emergency`` branch) --
        the unconditional 15.5 exculpation makes a spurious reporter non-inert.
        """

        impostors = sorted(pid for pid, role in roles.items() if role == "IMPOSTOR")
        rows: dict[str, dict[str, SuspicionEntry]] = {}
        for voter in voters:
            graph = graphs.get(voter, ())
            fellow = (
                tuple(pid for pid in impostors if pid != voter)
                if roles.get(voter) == "IMPOSTOR"
                else ()
            )
            emitted = _suspicion_graph_with_contradictions(
                voter_id=voter,
                suspicion_graph=graph,
                contradictions=entry.contradictions,
                fellow_impostor_ids=fellow,
                evidence=evidence,
                transcript=entry.transcript,
                reporter=reporter,
                env=env,
            )
            rows[voter] = {e.player_id: e for e in emitted}
        return rows

    @pytest.fixture(scope="class")
    def counterfactual(
        self,
        walk: dict[
            tuple[int, str],
            tuple[
                MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]], str | None
            ],
        ],
        roles_by_seed: dict[int, dict[str, str]],
    ) -> _AbsenceCounterfactual:
        """The whole sweep, computed once for every downstream assertion."""

        absent_sizes: list[int] = []
        histogram: Counter[int] = Counter()
        nonempty_absent = 0
        subset_ok = True
        determinism_ok = True
        new_over_gate = 0
        top_changes = 0
        emergency_meetings = 0

        for (seed, _meeting_id), (entry, graphs, trigger_kind) in walk.items():
            voters = sorted({ballot.voter for ballot in entry.ballots})
            roster = frozenset(voters)
            roles = roles_by_seed[seed]
            # The manager's exact reporter predicate (_collect_one_ballot): an
            # emergency meeting has no body-reporter, so the 15.5 exculpation
            # never applies there -- reporter=None on that branch.
            is_emergency = trigger_kind == "emergency"
            if is_emergency:
                emergency_meetings += 1
            reporter = None if is_emergency else entry.triggered_by
            evidence = derive_belief_evidence(
                entry.transcript, contradictions=entry.contradictions, roster=roster
            )
            # Determinism: re-deriving the evidence yields the identical absent set.
            evidence_again = derive_belief_evidence(
                entry.transcript, contradictions=entry.contradictions, roster=roster
            )
            if evidence.absent != evidence_again.absent:
                determinism_ok = False

            size = len(evidence.absent)
            absent_sizes.append(size)
            histogram[size] += 1
            if size:
                nonempty_absent += 1
            if not set(evidence.absent) <= roster:
                subset_ok = False

            off_rows = self._voter_rows(
                entry,
                graphs,
                roles,
                evidence,
                voters,
                reporter=reporter,
                env=_LEVER_OFF,
            )
            off_rows_again = self._voter_rows(
                entry,
                graphs,
                roles,
                evidence,
                voters,
                reporter=reporter,
                env=_LEVER_OFF,
            )
            on_rows = self._voter_rows(
                entry, graphs, roles, evidence, voters, reporter=reporter, env=_LEVER_ON
            )
            # Determinism: two OFF derivations agree row-for-row.
            for voter in voters:
                if {k: e.suspicion for k, e in off_rows[voter].items()} != {
                    k: e.suspicion for k, e in off_rows_again[voter].items()
                }:
                    determinism_ok = False

            meeting_new_over = False
            meeting_top_change = False
            for voter in voters:
                off_v = off_rows[voter]
                on_v = on_rows[voter]
                for subject, on_entry in on_v.items():
                    off_entry = off_v.get(subject)
                    off_rendered = (
                        float(_rendered(off_entry.suspicion))
                        if off_entry is not None
                        else 0.0
                    )
                    if float(_rendered(on_entry.suspicion)) >= _GATE > off_rendered:
                        meeting_new_over = True
                if self._rendered_max_candidate(off_v) != self._rendered_max_candidate(
                    on_v
                ):
                    meeting_top_change = True
            if meeting_new_over:
                new_over_gate += 1
            if meeting_top_change:
                top_changes += 1

        return _AbsenceCounterfactual(
            total_meetings=len(walk),
            nonempty_absent=nonempty_absent,
            absent_histogram=tuple(sorted(histogram.items())),
            absent_min=min(absent_sizes),
            absent_max=max(absent_sizes),
            absent_median=float(median(absent_sizes)),
            subset_ok=subset_ok,
            determinism_ok=determinism_ok,
            new_over_gate_meetings=new_over_gate,
            top_candidate_change_meetings=top_changes,
            emergency_meetings=emergency_meetings,
        )

    # -- the census this counterfactual is measured over ---------------------

    def test_meeting_census(self, counterfactual: _AbsenceCounterfactual) -> None:
        # 139 reconstructed meetings on the committed baseline-3 9p2i set.
        assert counterfactual.total_meetings == 139

    # -- (1) how many meetings carry a non-empty absent set ------------------

    def test_nonempty_absent_meeting_count(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # 115 of the 139 meetings have at least one publicly-unplaced living
        # player -- the absent set is often LARGE (the 16.15 roll-call elicitation
        # does not exist yet), exactly why the lever stays OFF until 16.17.
        assert counterfactual.nonempty_absent == 115

    def test_every_absent_set_is_a_subset_of_the_living_roster(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # Structural: absence is the complement of the stated-paths keys OVER the
        # living roster, so it can never name a non-roster / dead id.
        assert counterfactual.subset_ok is True

    # -- (2) the absent-set size distribution --------------------------------

    def test_absent_set_size_distribution(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # The full histogram of |absent| across the 139 meetings, and its min /
        # max / median. Sizes span 0..8 (a 9-player set minus the reporter and any
        # placed players); the median meeting leaves 2 players unplaced.
        assert counterfactual.absent_histogram == (
            (0, 24),
            (1, 25),
            (2, 23),
            (3, 18),
            (4, 24),
            (5, 12),
            (6, 8),
            (7, 3),
            (8, 2),
        )
        assert counterfactual.absent_min == 0
        assert counterfactual.absent_max == 8
        assert counterfactual.absent_median == 2.0

    # -- (3) how many meetings the delta WOULD flip --------------------------

    def test_new_over_gate_meeting_count(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # The new-must-vote channel: in 29 meetings the lever ON creates at least
        # one NEW at-or-over-the-rendered-gate candidate (for some voter) that OFF
        # had under it. Absence only lifts, so no recorded conviction is ever lost
        # -- this is a pure ADDITION of vote-worthy candidates.
        assert counterfactual.new_over_gate_meetings == 29

    def test_top_candidate_change_meeting_count(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # In 74 meetings some voter's §4.6 TOP candidate (argmax by rendered
        # suspicion, ties by sorted id) CHANGES identity under the lever -- high
        # because a near-neutral graph is tie-broken by id, so a fresh 0.58 absence
        # row readily becomes (or displaces) the rendered argmax. The count is
        # sensitive to the reporter predicate: threading a reporter into the 15
        # emergency meetings (where production passes None) would zero the
        # opener's soft lift on both sides and mis-count seed-26 meeting-1 as a
        # 75th change -- the production-faithful figure is 74.
        assert counterfactual.top_candidate_change_meetings == 74

    def test_emergency_meeting_census(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # 15 of the 139 committed meetings are EMERGENCY meetings (the walk's
        # reconstructed trigger kind) -- the meetings whose re-derivation must
        # pass reporter=None to mirror _collect_one_ballot.
        assert counterfactual.emergency_meetings == 15

    # -- determinism ---------------------------------------------------------

    def test_derivation_is_deterministic(
        self, counterfactual: _AbsenceCounterfactual
    ) -> None:
        # Two evidence derivations (and two OFF re-derivations) agree everywhere --
        # the counterfactual is replay-stable, a precondition for pinning it.
        assert counterfactual.determinism_ok is True
