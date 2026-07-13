"""Tests for the Task 16.4 J1 hard-evidence render gate (default-OFF lever).

Covers the J1 render clamp introduced in Task 16.4
(audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J1): a belief row whose
Task-16.3 typed :class:`~agents.memory.beliefs.SuspicionProvenance` decomposition
is ENTIRELY soft renders clamped one display notch below the §4.6 eject gate
(:data:`~agents.memory.beliefs.HARD_EVIDENCE_GATE_RENDER_CEIL` = 0.59), while a row
carrying ANY grounded (hard) component -- or an ``unattributed`` residual of
unknown class -- renders untouched. The clamp is a render-time lever, never a
fold-time cap: the stored :class:`~agents.memory.beliefs.BeliefState` scalar and the
belief-fold arithmetic are never mutated, and with the lever OFF (the default) every
touched read-site is byte-identical to pre-task HEAD.

The clamp sits behind the default-OFF
:func:`~agents.memory.beliefs.hard_evidence_gate_enabled` resolver (the 13.5/14.10
live-toggle pattern, cloned from the Task-15.5 ``reporter_exculpation`` resolver) and
applies at exactly two read-sites: the store's §6.6 belief lines
(:func:`agents.memory.store._build_belief_lines`) and the vote-ballot suspicion-graph
builder (:meth:`orchestrator.game.TacticalAgent.suspicion_graph_for_meeting`). The
pure classification predicate
(:func:`~agents.memory.beliefs.hard_evidence_gated_suspicion`) is lever-agnostic --
gating lives at the call sites (the 15.5 in-line pattern).

Test layout mirrors the Task-15.5
:class:`tests.agents.test_beliefs.TestReporterExculpationOnCommittedBytes` precedent:

* the resolver's default-OFF / truthy-ON contract;
* the pure helper's HARD/SOFT/EXEMPT classification (parametrised);
* the mandatory cross-meeting persistent-hard fixture (a meeting-1 grounded vent
  survives decay + the meeting-boundary roll as ``carried_hard`` and is never
  clamped at meeting 2; the soft twin rolls to ``carried_soft`` and clamps);
* the two production render read-sites (store + game builder), incl. the override
  pass-through and the trust-vs-suspicion selection consequence;
* the pre-vote re-render path and the clamp-before-joint-cap ordering pin;
* the offline counterfactual RE-MEASURED on the committed baseline-4 9p2i bytes (the
  over-damping canary -- zero hard-flag-backed conviction outcomes change).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from eval.funnel import InformationFunnelReport
    from orchestrator.replay import MeetingReplayEntry

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    ENV_HARD_EVIDENCE_GATE,
    HARD_EVIDENCE_GATE_RENDER_CEIL,
    SUSPICION_PROVENANCE_ATOL,
    VENTING_SUSPICION_DELTA,
    BeliefState,
    SuspicionProvenance,
    apply_meeting_evidence_rules,
    apply_observation_rules,
    hard_evidence_gate_enabled,
    hard_evidence_gated_suspicion,
)
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory, render_for_prompt
from agents.tactical.crewmate_policy import CrewmatePolicy
from meetings.manager import (
    SuspicionEntry,
    _suspicion_graph_with_contradictions,  # noqa: PLC2701
    derive_belief_evidence,
)
from meetings.schemas import ContradictionRef, MeetingTranscript
from observation.packet import GlobalView, ObservationPacket, PlayerView, SelfView
from orchestrator.game import TacticalAgent

_GATE = 0.60  # DESIGN.md §4.6 eject gate
_CEIL = HARD_EVIDENCE_GATE_RENDER_CEIL  # 0.59, one "%.2f" notch under the gate
_LEVER_ON: Mapping[str, str] = {ENV_HARD_EVIDENCE_GATE: "1"}
_LEVER_OFF: Mapping[str, str] = {}


# --------------------------------------------------------------------------- #
# A. The resolver (cloned from the 5febf48 reporter-exculpation resolver)      #
# --------------------------------------------------------------------------- #


class TestHardEvidenceGateResolver:
    """The Task-16.4 lever resolver -- DEFAULT-OFF, the live-toggle pattern.

    Clones the Task-15.5 ``reporter_exculpation_enabled`` resolver shape (which
    itself clones the retired 13.5 / 14.10 resolvers): an unset / empty /
    unrecognised value reads ``False`` so the two render read-sites stay
    byte-identical to the committed baseline-4 substrate;
    ``1/true/yes/on`` (case-insensitive, whitespace-trimmed) reads ``True``.
    ``env=None`` falls back to the live process environment.
    """

    def test_default_off_on_an_empty_mapping(self) -> None:
        # The DEFAULT: a bare env cell resolves OFF, so nothing clamps.
        assert hard_evidence_gate_enabled(env={}) is False

    def test_default_off_when_the_key_is_absent(self) -> None:
        # An unrelated export leaves the gate OFF -- only its own key counts.
        assert hard_evidence_gate_enabled(env={"AILIBI_SOMETHING_ELSE": "1"}) is False

    @pytest.mark.parametrize(
        "value",
        ["1", "true", "yes", "on", "TRUE", "Yes", "On", " 1 ", "  true  ", "\tyes\n"],
    )
    def test_on_for_each_truthy_value_and_case_or_whitespace_variant(
        self, value: str
    ) -> None:
        # Every documented truthy token, plus case + surrounding-whitespace
        # variants (the resolver strips then lowercases before the set test).
        assert hard_evidence_gate_enabled(env={ENV_HARD_EVIDENCE_GATE: value}) is True

    @pytest.mark.parametrize(
        "value", ["0", "false", "", "garbage", "2", "no", "off", "yesno", "  "]
    )
    def test_off_for_falsy_or_unrecognised_values(self, value: str) -> None:
        # Explicit falsy tokens, the empty string, and junk all read OFF: the
        # resolver is an allow-list membership test, not a truthiness cast.
        assert hard_evidence_gate_enabled(env={ENV_HARD_EVIDENCE_GATE: value}) is False

    def test_env_none_reads_the_live_process_environment_on(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # ``env=None`` (and the bare call) reads ``os.environ`` LIVE -- an export
        # flips the gate on without a mapping argument.
        monkeypatch.setenv(ENV_HARD_EVIDENCE_GATE, "1")
        assert hard_evidence_gate_enabled() is True
        assert hard_evidence_gate_enabled(env=None) is True

    def test_env_none_reads_the_live_process_environment_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # With the export deleted the live read is OFF -- the default.
        monkeypatch.delenv(ENV_HARD_EVIDENCE_GATE, raising=False)
        assert hard_evidence_gate_enabled() is False
        assert hard_evidence_gate_enabled(env=None) is False


# --------------------------------------------------------------------------- #
# B. The pure helper's HARD / SOFT / EXEMPT classification                     #
# --------------------------------------------------------------------------- #


class TestHardEvidenceGatedSuspicionHelper:
    """The pure J1 classification predicate (Task 16.4; audit §3.4 J1).

    Classifies on the Task-16.3 typed decomposition ONLY (never the scalar,
    never prose). Every row is built so ``0.5 + provenance.total == suspicion``
    (the module sum invariant), so each case is a real belief-row shape. A row is
    ENTIRELY soft -- and only then clamped to :data:`_CEIL` -- when
    ``hard_total`` and ``unattributed`` are both at/under
    :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL` and ``soft_total``
    carries real lift. Any hard component, an ``unattributed`` residual (EXEMPT
    by the Task-16.4 decision -- evidence of unknown class is never suppressed),
    or no soft lift at all returns the scalar verbatim.
    """

    @pytest.mark.parametrize(
        ("provenance", "suspicion", "expected"),
        [
            # -- entirely-soft, over-gate: the clamp binds ------------------- #
            # a single carried-soft accusation prior at 0.70 -> sub-gate 0.59.
            (SuspicionProvenance(carried_soft=0.20), 0.70, _CEIL),
            # fresh testimony-spread + accusation-carry, still all soft.
            (
                SuspicionProvenance(testimony_spread=0.12, accusation_carry=0.08),
                0.70,
                _CEIL,
            ),
            # -- the DoD hard fixture: the SAME 0.70 scalar, hard component --- #
            # carried-hard (a rolled grounded pin) exempts -> untouched.
            (SuspicionProvenance(carried_hard=0.20), 0.70, 0.70),
            # ANY hard component exempts even a mostly-soft row.
            (
                SuspicionProvenance(carried_soft=0.15, body_proximity=0.05),
                0.70,
                0.70,
            ),
            # -- the pure hard channels: never clamped ----------------------- #
            (SuspicionProvenance(kill_or_vent_pin=0.50), 1.00, 1.00),
            (SuspicionProvenance(flag_lift=0.30), 0.80, 0.80),
            (SuspicionProvenance(body_proximity=0.20), 0.70, 0.70),
            # -- the Task-16.4 unattributed-EXEMPT decision ------------------ #
            # an unknown-class residual is neither hard nor soft; the gate never
            # clamps a row carrying it, protecting the over-damping canary.
            (SuspicionProvenance(unattributed=0.20), 0.70, 0.70),
            # a ULP-scale unattributed residual (within the sum-invariant
            # tolerance) still classifies the row soft-only -> clamped.
            (
                SuspicionProvenance(carried_soft=0.20, unattributed=1e-12),
                0.70,
                _CEIL,
            ),
            # -- boundary + no-op cases -------------------------------------- #
            # a sub-gate soft row: the ``min`` is a no-op (already under 0.59).
            (SuspicionProvenance(carried_soft=0.08), 0.58, 0.58),
            # exactly at the gate: clamped one notch under.
            (SuspicionProvenance(carried_soft=0.10), 0.60, _CEIL),
            # all-zero provenance (no soft lift): the neutral prior is exempt.
            (SuspicionProvenance(), 0.50, 0.50),
        ],
    )
    def test_classifies_on_the_typed_split(
        self, provenance: SuspicionProvenance, suspicion: float, expected: float
    ) -> None:
        assert hard_evidence_gated_suspicion(suspicion, provenance) == pytest.approx(
            expected
        )

    def test_the_same_scalar_splits_on_provenance_the_dod_fixture(self) -> None:
        # The DoD's central claim: two rows with the IDENTICAL 0.70 scalar render
        # differently -- the carried-soft one clamps, the carried-hard one holds.
        soft = SuspicionProvenance(carried_soft=0.20)
        hard = SuspicionProvenance(carried_hard=0.20)
        assert hard_evidence_gated_suspicion(0.70, soft) == pytest.approx(_CEIL)
        assert hard_evidence_gated_suspicion(0.70, hard) == pytest.approx(0.70)

    def test_the_helper_never_mutates_its_frozen_input(self) -> None:
        # Purity: the frozen SuspicionProvenance is unchanged by the call.
        provenance = SuspicionProvenance(carried_soft=0.20, unattributed=1e-12)
        hard_evidence_gated_suspicion(0.70, provenance)
        assert provenance == SuspicionProvenance(carried_soft=0.20, unattributed=1e-12)

    def test_the_helper_is_lever_agnostic(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The predicate NEVER reads the env / lever (the gating is the 15.5
        # in-line pattern at the call sites): the result is identical whether the
        # ambient lever is exported ON or deleted.
        provenance = SuspicionProvenance(carried_soft=0.20)
        monkeypatch.setenv(ENV_HARD_EVIDENCE_GATE, "1")
        on = hard_evidence_gated_suspicion(0.70, provenance)
        monkeypatch.delenv(ENV_HARD_EVIDENCE_GATE, raising=False)
        off = hard_evidence_gated_suspicion(0.70, provenance)
        assert on == off == pytest.approx(_CEIL)


# --------------------------------------------------------------------------- #
# C. The mandatory cross-meeting persistent-hard fixture (DoD bullet 2)        #
# --------------------------------------------------------------------------- #


def _packet(*, visible_players: tuple[PlayerView, ...]) -> ObservationPacket:
    """A minimal perception packet for ``observer`` (clones the test_beliefs shape)."""

    return ObservationPacket(
        tick=10,
        agent_id="observer",
        self_state=SelfView(room="R", role="CREWMATE", pending_task_id=None),
        visible_players=visible_players,
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


class TestCrossMeetingPersistentHardCarry:
    """The DoD cross-meeting fixture: a meeting-1 grounded flag survives to
    meeting 2 as HARD and is never clamped; the soft twin rolls to soft and is.

    Drives the REAL write paths (no hand-built provenance): perception's
    :func:`~agents.memory.beliefs.apply_observation_rules` for the vent pin and the
    composed meeting fold
    :func:`~agents.memory.beliefs.apply_meeting_evidence_rules` (``phase=None``, the
    boundary every production absorb reaches) for the decay + the meeting-boundary
    roll. This is the guarantee the over-damping canary rests on: a grounded pin
    stays HARD across the carry, so the J1 gate can never suppress standing hard
    evidence.
    """

    def test_meeting_one_vent_carries_hard_and_is_never_clamped_at_meeting_two(
        self,
    ) -> None:
        # Meeting 1: ``observer`` witnesses ``venter`` vent -- the grounded HARD
        # kill_or_vent_pin channel (0.5 -> suspicion 1.0).
        meeting_one = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                visible_players=(PlayerView(id="venter", room="R", action="vent"),)
            ),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )
        assert meeting_one.view("venter").suspicion == pytest.approx(
            0.5 + VENTING_SUSPICION_DELTA
        )
        assert meeting_one.view("venter").provenance.kill_or_vent_pin == pytest.approx(
            VENTING_SUSPICION_DELTA
        )

        # The meeting boundary: the composed fold with ``venter`` UNREINFORCED, so
        # it both DECAYS (1.0 -> 0.875) and rolls its fresh kill_or_vent_pin into
        # carried_hard (the persistent HARD carry).
        rolled = apply_meeting_evidence_rules(
            meeting_one, own_id="observer", accused=(), phase=None
        )
        view = rolled.view("venter")
        provenance = view.provenance
        # The roll landed in carried_hard with every fresh bucket zeroed.
        assert provenance.carried_hard > 0.0
        assert provenance.carried_hard == pytest.approx(0.375)
        assert provenance.kill_or_vent_pin == 0.0
        assert provenance.flag_lift == 0.0
        assert provenance.body_proximity == 0.0
        assert provenance.hard_total > SUSPICION_PROVENANCE_ATOL

        # Meeting 2 evaluation: the carried-hard exemption survives decay, so the
        # gate returns the decayed scalar UNCHANGED.
        gated = hard_evidence_gated_suspicion(view.suspicion, provenance)
        assert gated == pytest.approx(view.suspicion)
        assert gated == pytest.approx(0.875)

    def test_the_soft_twin_rolls_to_carried_soft_and_clamps(self) -> None:
        # Seed a prior soft accusation-carry (0.5 -> 0.65), then one composed fold
        # accusing the subject (+0.05 -> 0.70). The subject is reinforced, so it
        # does NOT decay; the roll folds accusation_carry into carried_soft.
        beliefs = BeliefState()
        beliefs.adjust_suspicion("subject", delta=0.15, source="accusation_carry")
        rolled = apply_meeting_evidence_rules(
            beliefs, own_id="observer", accused=("subject",), phase=None
        )
        view = rolled.view("subject")
        provenance = view.provenance
        assert view.suspicion == pytest.approx(0.70)
        assert view.suspicion == pytest.approx(0.65 + ACCUSATION_SUSPICION_DELTA)
        # The roll classification: entirely soft, no hard component, no residual.
        assert provenance.carried_soft == pytest.approx(0.20)
        assert provenance.accusation_carry == 0.0
        assert provenance.hard_total <= SUSPICION_PROVENANCE_ATOL
        assert abs(provenance.unattributed) <= SUSPICION_PROVENANCE_ATOL
        # The clamp: an entirely-soft conviction-grade prior renders sub-gate.
        assert hard_evidence_gated_suspicion(
            view.suspicion, provenance
        ) == pytest.approx(_CEIL)


# --------------------------------------------------------------------------- #
# D. The store belief-line render read-site (`_build_belief_lines`)            #
# --------------------------------------------------------------------------- #


def _self_state_event(*, agent_id: str = "p-1") -> EpisodicEvent:
    """A single tick-0 ``self_state`` row (perception has run once)."""

    return EpisodicEvent(
        tick=0,
        type="self_state",
        payload={
            "agent_id": agent_id,
            "room": "CAFETERIA",
            "role": "CREWMATE",
            "pending_task_id": None,
        },
        provenance="observed",
    )


def _saw_player_event(*, player_id: str) -> EpisodicEvent:
    """A tick-0 co-spawn sighting so ``player_id`` is a known roster id."""

    return EpisodicEvent(
        tick=0,
        type="saw_player",
        payload={"player_id": player_id, "room": "CAFETERIA", "action": None},
        provenance="observed",
    )


def _memory_with_beliefs(
    seeds: Mapping[str, tuple[float, float, SuspicionProvenance]],
) -> AgentMemory:
    """An ``AgentMemory`` (perception run once) with the given belief rows seeded.

    ``seeds`` maps ``player_id -> (suspicion, trust, provenance)``; each id is
    recorded as a co-spawn sighting so it survives the §6.6 roster filter, and its
    belief row is seeded via the real
    :meth:`~agents.memory.beliefs.BeliefState.seed_player` write path (which
    reconciles any residual into ``unattributed`` -- so a consistent
    ``(scalar, provenance)`` pair keeps its classification).
    """

    memory = AgentMemory()
    memory.episodic.append(_self_state_event())
    for player_id in sorted(seeds):
        memory.episodic.append(_saw_player_event(player_id=player_id))
        suspicion, trust, provenance = seeds[player_id]
        memory.beliefs.seed_player(
            player_id, suspicion=suspicion, trust=trust, provenance=provenance
        )
    return memory


class TestStoreBeliefLineReadSite:
    """The store's §6.6 belief-line clamp (:func:`_build_belief_lines`)."""

    def test_lever_on_clamps_soft_only_and_holds_hard(self) -> None:
        # ON: a soft-only 0.70 renders "suspicion 0.59"; the carried-hard 0.70
        # renders "suspicion 0.70" untouched -- pinned by the exact substring.
        memory = _memory_with_beliefs(
            {
                "p-2": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20)),
                "p-3": (0.70, 0.5, SuspicionProvenance(carried_hard=0.20)),
            }
        )
        rendered = render_for_prompt(memory, env=_LEVER_ON)
        assert "p-2: suspicion 0.59" in rendered
        assert "p-3: suspicion 0.70" in rendered

    def test_lever_off_is_byte_identical_to_no_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # OFF (an empty mapping) must render EXACTLY the same bytes as passing no
        # env at all under a clean environment -- the byte-identity contract.
        monkeypatch.delenv(ENV_HARD_EVIDENCE_GATE, raising=False)
        memory = _memory_with_beliefs(
            {"p-2": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20))}
        )
        off_render = render_for_prompt(memory, env=_LEVER_OFF)
        no_env_render = render_for_prompt(memory)
        assert off_render == no_env_render
        # The soft-only row renders its RAW stored scalar when the lever is OFF.
        assert "p-2: suspicion 0.70" in off_render

    def test_override_value_passes_through_untouched_lever_on(self) -> None:
        # ON with an override: the override VALUE is the post-fold pipeline truth
        # (the builder already clamped the seed before the manager pre-vote fold),
        # so it passes through UNCLAMPED even though the STORED provenance is
        # soft-only -- re-clamping against the stored provenance would misclassify
        # a row that took fresh HARD lift this meeting. A player ABSENT from the
        # override still renders its clamped stored scalar.
        memory = _memory_with_beliefs(
            {
                "p-2": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20)),
                "p-4": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20)),
            }
        )
        rendered = render_for_prompt(
            memory, suspicion_override={"p-2": 0.66}, env=_LEVER_ON
        )
        assert "p-2: suspicion 0.66" in rendered  # override value, untouched
        assert "p-4: suspicion 0.59" in rendered  # stored scalar, clamped

    def test_trust_line_wins_when_the_clamp_shrinks_the_suspicion_deviation(
        self,
    ) -> None:
        # The clamped value is the row's effective signal: a row whose trust
        # deviation sits between the clamped and raw suspicion deviations flips to
        # the trust line lever-ON. suspicion 0.70 soft-only (dev 0.20), trust 0.35
        # (dev 0.15): OFF the suspicion line wins (0.20 >= 0.15); ON the clamped
        # 0.59 (dev 0.09 < 0.15) yields to the trust line.
        memory = _memory_with_beliefs(
            {"p-5": (0.70, 0.35, SuspicionProvenance(carried_soft=0.20))}
        )
        assert "p-5: suspicion 0.70" in render_for_prompt(memory, env=_LEVER_OFF)
        assert "p-5: trust 0.35" in render_for_prompt(memory, env=_LEVER_ON)


# --------------------------------------------------------------------------- #
# E. The game suspicion-graph builder read-site                               #
# --------------------------------------------------------------------------- #


def _tactical_agent_with_beliefs(
    seeds: Mapping[str, tuple[float, float, SuspicionProvenance]],
) -> TacticalAgent:
    """A real ``TacticalAgent`` whose belief store holds the seeded rows."""

    agent = TacticalAgent(agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"))
    for player_id in sorted(seeds):
        suspicion, trust, provenance = seeds[player_id]
        agent.memory.beliefs.seed_player(
            player_id, suspicion=suspicion, trust=trust, provenance=provenance
        )
    return agent


class TestGameSuspicionGraphBuilderReadSite:
    """The vote-ballot builder clamp (:meth:`TacticalAgent.suspicion_graph_for_meeting`)."""

    def test_lever_on_clamps_the_scalar_but_keeps_raw_provenance(self) -> None:
        agent = _tactical_agent_with_beliefs(
            {
                "p-2": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20)),
                "p-3": (0.70, 0.5, SuspicionProvenance(carried_hard=0.20)),
                "p-4": (0.58, 0.5, SuspicionProvenance(carried_soft=0.08)),
            }
        )
        rows = {
            e.player_id: e for e in agent.suspicion_graph_for_meeting(env=_LEVER_ON)
        }

        # The soft-only over-gate row: the scalar is clamped to 0.59 while the
        # eight provenance kwargs stay the RAW 16.3 decomposition, so the scalar
        # deliberately renders BELOW its decomposition sum. This scalar-vs-
        # decomposition divergence is pinned per the Task-16.4 Decision: the
        # decomposition is the true evidence record; the manager's seed_player
        # reconciles the shortfall as an unattributed residual on reseed.
        soft = rows["p-2"]
        assert soft.suspicion == pytest.approx(_CEIL)
        assert soft.carried_soft == pytest.approx(0.20)  # RAW, not clamped
        decomposition_sum = (
            soft.flag_lift
            + soft.body_proximity
            + soft.kill_or_vent_pin
            + soft.testimony_spread
            + soft.accusation_carry
            + soft.carried_hard
            + soft.carried_soft
            + soft.unattributed
        )
        assert 0.5 + decomposition_sum == pytest.approx(0.70)  # RAW scalar

        # The carried-hard row is untouched; the sub-gate soft row is a min no-op.
        assert rows["p-3"].suspicion == pytest.approx(0.70)
        assert rows["p-4"].suspicion == pytest.approx(0.58)

    def test_lever_off_equals_the_no_env_rows_exactly(self) -> None:
        agent = _tactical_agent_with_beliefs(
            {
                "p-2": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20)),
                "p-3": (0.70, 0.5, SuspicionProvenance(carried_hard=0.20)),
            }
        )
        off_rows = agent.suspicion_graph_for_meeting(env=_LEVER_OFF)
        no_env_rows = agent.suspicion_graph_for_meeting()
        assert off_rows == no_env_rows
        # OFF the soft-only row carries its RAW over-gate scalar.
        off = {e.player_id: e.suspicion for e in off_rows}
        assert off["p-2"] == pytest.approx(0.70)


# --------------------------------------------------------------------------- #
# F. The pre-vote re-render path + the clamp-before-joint-cap ordering pins    #
# --------------------------------------------------------------------------- #


def _clamped_seed(entry: SuspicionEntry) -> SuspicionEntry:
    """Replicate the builder lever-ON: clamp the scalar, keep the provenance RAW.

    Mirrors :meth:`TacticalAgent.suspicion_graph_for_meeting` under the lever --
    the eight provenance kwargs ride through untouched, only ``suspicion`` moves.
    """

    provenance = SuspicionProvenance(
        flag_lift=entry.flag_lift,
        body_proximity=entry.body_proximity,
        kill_or_vent_pin=entry.kill_or_vent_pin,
        testimony_spread=entry.testimony_spread,
        accusation_carry=entry.accusation_carry,
        carried_hard=entry.carried_hard,
        carried_soft=entry.carried_soft,
        unattributed=entry.unattributed,
    )
    clamped = hard_evidence_gated_suspicion(entry.suspicion, provenance)
    return SuspicionEntry(
        player_id=entry.player_id,
        suspicion=clamped,
        trust=entry.trust,
        flag_lift=entry.flag_lift,
        body_proximity=entry.body_proximity,
        kill_or_vent_pin=entry.kill_or_vent_pin,
        testimony_spread=entry.testimony_spread,
        accusation_carry=entry.accusation_carry,
        carried_hard=entry.carried_hard,
        carried_soft=entry.carried_soft,
        unattributed=entry.unattributed,
    )


def _strong_flag(subject: str) -> ContradictionRef:
    """One STRONG (non-weak) ``alibi_conflict`` naming ``subject`` (+0.30)."""

    return ContradictionRef(
        contradiction_id=f"c-{subject}",
        kind="alibi_conflict",
        subjects=(subject,),
        description="strong cross-speaker conflict",
        event_a_id="turn:m-1:turn-0:claim:0",
        event_b_id="turn:m-1:turn-1:claim:0",
    )


class TestPreVoteRerenderAndOrdering:
    """The manager re-render path (Rule 2 + pre-vote fold) composed on clamped seeds.

    Imports :func:`meetings.manager._suspicion_graph_with_contradictions` +
    :class:`SuspicionEntry` exactly as the
    :class:`tests.agents.test_beliefs.TestReporterExculpationOnCommittedBytes`
    precedent does. The builder clamps the seed BEFORE the manager fold, so fresh
    same-meeting lift lands ON TOP of the clamped seed through the untouched fold
    arithmetic (the clamp-before-joint-cap ordering, pinned here).
    """

    def test_soft_only_seed_survives_the_re_emit_of_an_unrelated_flag(self) -> None:
        # The DoD pre-vote re-render pin. Builder-ON rows (a soft-only 0.70 clamped
        # to 0.59, plus an unrelated subject) fed as the suspicion graph, with a
        # STRONG contradiction on the UNRELATED subject forcing the re-emit path:
        # the soft-only subject takes no fresh lift and stays 0.59.
        soft = SuspicionEntry(
            player_id="subject", suspicion=0.70, trust=0.5, carried_soft=0.20
        )
        unrelated = SuspicionEntry(
            player_id="other", suspicion=0.55, trust=0.5, carried_soft=0.05
        )
        graph = (_clamped_seed(soft), _clamped_seed(unrelated))
        emitted = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=graph,
            contradictions=(_strong_flag("other"),),
            transcript=MeetingTranscript(turns=()),
        )
        rows = {e.player_id: e.suspicion for e in emitted}
        assert rows["subject"] == pytest.approx(_CEIL)

        # And the emitted rows re-render through the store as an override: the
        # soft-only subject's belief line reads "suspicion 0.59".
        memory = _memory_with_beliefs(
            {"subject": (0.70, 0.5, SuspicionProvenance(carried_soft=0.20))}
        )
        rendered = render_for_prompt(memory, suspicion_override=rows, env=_LEVER_ON)
        assert "subject: suspicion 0.59" in rendered

    def test_clamp_before_joint_cap_ordering(self) -> None:
        # The Integration-risk pin: a soft-only 0.70 subject WITH a STRONG
        # contradiction on ITSELF. The clamp sits BEFORE the joint cap, so the two
        # legs emit DIFFERENT bytes while both stay convictable.
        soft = SuspicionEntry(
            player_id="subject", suspicion=0.70, trust=0.5, carried_soft=0.20
        )
        flags = (_strong_flag("subject"),)
        transcript = MeetingTranscript(turns=())
        off = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=(soft,),
            contradictions=flags,
            transcript=transcript,
        )
        on = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=(_clamped_seed(soft),),
            contradictions=flags,
            transcript=transcript,
        )
        off_susp = {e.player_id: e.suspicion for e in off}["subject"]
        on_susp = {e.player_id: e.suspicion for e in on}["subject"]
        # OFF (seed raw 0.70): the +0.30 flag ceils at max(prior, 0.97) -> 0.97
        # (0.70 + 0.27), joint-capped at 0.70 + 0.30 = 1.00 (non-binding).
        assert off_susp == pytest.approx(0.97)
        # ON (seed clamped to 0.59): the full +0.30 flag lands (the 0.97 ceiling
        # does not bind), joint-capped at 0.59 + 0.30 = 0.89 -- anchored on the
        # CLAMPED prior, not the raw one.
        assert on_susp == pytest.approx(0.89)
        # Both verdicts stay >= 0.60 (the canary outcome-preservation) while the
        # rendered bytes differ -- the pinned before-the-joint-cap ordering.
        assert off_susp >= _GATE and on_susp >= _GATE

    def test_contradiction_render_ceiling_exempts_a_witnessed_kill(self) -> None:
        # Compose-never-bypass: a witnessed-kill 1.0 prior (kill_or_vent_pin=0.5)
        # is HARD, so the builder clamp is a no-op ON. A strong flag on it lifts by
        # max(prior, 0.97) - prior = 0.0, so ON and OFF both emit 1.0 (the
        # CONTRADICTION_RENDER_CEIL max(prior, CEIL) exemption).
        kill = SuspicionEntry(
            player_id="killer", suspicion=1.0, trust=0.5, kill_or_vent_pin=0.5
        )
        flags = (_strong_flag("killer"),)
        transcript = MeetingTranscript(turns=())
        off = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=(kill,),
            contradictions=flags,
            transcript=transcript,
        )
        on = _suspicion_graph_with_contradictions(
            voter_id="voter",
            suspicion_graph=(_clamped_seed(kill),),
            contradictions=flags,
            transcript=transcript,
        )
        assert {e.player_id: e.suspicion for e in off}["killer"] == pytest.approx(1.0)
        assert {e.player_id: e.suspicion for e in on}["killer"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# G. The offline counterfactual on committed baseline-4 bytes (DoD bullet 3)   #
# --------------------------------------------------------------------------- #

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HARD_BACKED_FLOOR = 40  # the precedent's non-vacuity bar


@dataclass(frozen=True)
class _EjectionRow:
    """One re-derived ejection's OFF/ON verdict data (per meeting)."""

    seed: int
    meeting_id: str
    ejectee: str
    ejectee_role: str
    hard_backed: bool
    off_max: float
    on_max: float


@dataclass(frozen=True)
class _GateCounterfactual:
    """The full 9p2i counterfactual sweep, aggregated once (class-scoped)."""

    total_ejections: int
    kept: dict[str, int]
    already_sub_gate: dict[str, int]
    still_over: dict[str, int]
    soft_only_total: int
    hard_backed: int
    outcome_changes: int
    outcome_change_detail: tuple[str, ...]
    subject_level_flips: tuple[str, ...]
    ejectee_clamp_raises: tuple[str, ...]


def _entry_provenance(entry: SuspicionEntry) -> SuspicionProvenance:
    """Rebuild a SuspicionProvenance from an emitted graph row's eight fields."""

    return SuspicionProvenance(
        flag_lift=entry.flag_lift,
        body_proximity=entry.body_proximity,
        kill_or_vent_pin=entry.kill_or_vent_pin,
        testimony_spread=entry.testimony_spread,
        accusation_carry=entry.accusation_carry,
        carried_hard=entry.carried_hard,
        carried_soft=entry.carried_soft,
        unattributed=entry.unattributed,
    )


class TestHardEvidenceGateOnCommittedBytes:
    """The J1 counterfactual, RE-MEASURED offline on the committed baseline-4 9p2i
    bytes (Task 16.4 DoD bullet 3; the 14.8 analysis-only machinery; re-pinned at the
    Task-16.14 baseline-4 re-record).

    Baseline 4 was recorded with the lever OFF (it did not yet exist), so the
    recorded builder rows are the lever-OFF (raw) suspicion graph. This class walks
    every committed 9p2i meeting ONCE (CPU-only, ~1-2 min, class-scoped), collecting
    each participant's meeting-open suspicion graph, then per EJECTED report meeting
    re-derives the per-voter vote-time fold TWICE:

    * OFF -- :func:`meetings.manager._suspicion_graph_with_contradictions` on the raw
      meeting-open graph (the recorded fold);
    * ON -- the identical call with each seeded row first passed through the builder
      lever-ON clamp (:func:`_clamped_seed`: scalar clamped, provenance kwargs raw).

    An ejectee is HARD-BACKED iff any voter's OFF post-fold row for it carries
    provenance with ``hard_total > SUSPICION_PROVENANCE_ATOL`` (the exact typed split
    Task 16.3 built, superseding the 15.5 value-proxy). The reported numbers re-check
    the planning-doc §3.4 J1 hypothesis (24/31 crew mis-ejects neutralised vs 6/16
    catches risked -- baseline-2-era, quoted only as the prior hypothesis) and PIN
    the over-damping canary: ZERO hard-backed ejections change their §4.6 verdict.
    """

    _SET_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"

    @pytest.fixture(scope="class")
    def walk(
        self,
    ) -> dict[
        tuple[int, str],
        tuple[MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]]],
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
            tuple[MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]]],
        ] = {}
        for path in _seed_paths(self._SET_DIR):
            for meeting in walk_replay_meetings(
                path, game_map=game_map, renderers_for_set=renderers
            ):
                graphs = {p.agent_id: p.suspicion_graph for p in meeting.participants}
                collected[(meeting.seed, meeting.meeting_id)] = (meeting.entry, graphs)
        return collected

    @pytest.fixture(scope="class")
    def funnel(self) -> InformationFunnelReport:
        from eval.funnel import compute_information_funnel

        return compute_information_funnel(self._SET_DIR)

    @pytest.fixture(scope="class")
    def roles_by_seed(self) -> dict[int, dict[str, str]]:
        report = json.loads(
            (self._SET_DIR / "tournament-eval-report.json").read_text(encoding="utf-8")
        )
        return {game["seed"]: game["roles"] for game in report["report"]["games"]}

    def _rows(
        self,
        entry: MeetingReplayEntry,
        graphs: dict[str, tuple[SuspicionEntry, ...]],
        roles: dict[str, str],
        *,
        clamp: bool,
    ) -> tuple[dict[str, dict[str, SuspicionEntry]], list[str]]:
        """Re-derive the per-voter post-fold rows; ``clamp`` replicates lever-ON."""

        voters = sorted({ballot.voter for ballot in entry.ballots})
        impostors = sorted(pid for pid, role in roles.items() if role == "IMPOSTOR")
        evidence = derive_belief_evidence(
            entry.transcript,
            contradictions=entry.contradictions,
            roster=frozenset(voters),
        )
        rows: dict[str, dict[str, SuspicionEntry]] = {}
        for voter in voters:
            graph = graphs.get(voter, ())
            if clamp:
                graph = tuple(_clamped_seed(e) for e in graph)
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
                reporter=entry.triggered_by,
            )
            rows[voter] = {e.player_id: e for e in emitted}
        return rows, voters

    @staticmethod
    def _subject_max(rows: dict[str, dict[str, SuspicionEntry]], subject: str) -> float:
        return max(
            (row[subject].suspicion for row in rows.values() if subject in row),
            default=0.0,
        )

    @pytest.fixture(scope="class")
    def counterfactual(
        self,
        walk: dict[
            tuple[int, str],
            tuple[MeetingReplayEntry, dict[str, tuple[SuspicionEntry, ...]]],
        ],
        funnel: InformationFunnelReport,
        roles_by_seed: dict[int, dict[str, str]],
    ) -> _GateCounterfactual:
        """The whole sweep, computed once for every downstream assertion."""

        ejections = [
            row
            for row in funnel.per_meeting
            if row.outcome == "EJECTED" and row.ejected is not None
        ]
        kept = {"CREWMATE": 0, "IMPOSTOR": 0}
        already = {"CREWMATE": 0, "IMPOSTOR": 0}
        still = {"CREWMATE": 0, "IMPOSTOR": 0}
        hard_backed = 0
        outcome_changes = 0
        outcome_change_detail: list[str] = []
        subject_flips: list[str] = []
        raises: list[str] = []

        for row in ejections:
            ejected = row.ejected
            assert ejected is not None  # narrows for mypy (filtered above)
            roles = roles_by_seed[row.seed]
            entry, graphs = walk[(row.seed, row.meeting_id)]
            off_rows, voters = self._rows(entry, graphs, roles, clamp=False)
            on_rows, _ = self._rows(entry, graphs, roles, clamp=True)

            ejectee_hard = any(
                ejected in off_rows[voter]
                and _entry_provenance(off_rows[voter][ejected]).hard_total
                > SUSPICION_PROVENANCE_ATOL
                for voter in voters
            )
            off_max = self._subject_max(off_rows, ejected)
            on_max = self._subject_max(on_rows, ejected)
            role = roles.get(ejected, "UNKNOWN")

            # The clamp never RAISES the ejectee's rendered suspicion.
            if on_max > off_max + SUSPICION_PROVENANCE_ATOL:
                raises.append(f"{row.seed}:{row.meeting_id} {off_max}->{on_max}")

            if ejectee_hard:
                hard_backed += 1
                if (off_max >= _GATE) != (on_max >= _GATE):
                    outcome_changes += 1
                    outcome_change_detail.append(
                        f"{row.seed}:{row.meeting_id} {ejected}({role}) "
                        f"off={off_max:.4f} on={on_max:.4f}"
                    )
            elif off_max < _GATE:
                already[role] = already.get(role, 0) + 1
            elif on_max < _GATE:
                kept[role] = kept.get(role, 0) + 1  # the clamp neutralised it
            else:
                still[role] = still.get(role, 0) + 1

            # Subject-level canary sweep: ON never flips ANY hard-backed subject
            # row across the 0.60 verdict, for any voter, anywhere in the corpus.
            for voter in voters:
                for subject, off_entry in off_rows[voter].items():
                    if (
                        _entry_provenance(off_entry).hard_total
                        > SUSPICION_PROVENANCE_ATOL
                        and subject in on_rows[voter]
                    ):
                        on_entry = on_rows[voter][subject]
                        if (off_entry.suspicion >= _GATE) != (
                            on_entry.suspicion >= _GATE
                        ):
                            subject_flips.append(
                                f"{row.seed}:{row.meeting_id} v={voter} s={subject}"
                            )

        soft_only_total = (
            sum(kept.values()) + sum(already.values()) + sum(still.values())
        )
        return _GateCounterfactual(
            total_ejections=len(ejections),
            kept=kept,
            already_sub_gate=already,
            still_over=still,
            soft_only_total=soft_only_total,
            hard_backed=hard_backed,
            outcome_changes=outcome_changes,
            outcome_change_detail=tuple(outcome_change_detail),
            subject_level_flips=tuple(subject_flips),
            ejectee_clamp_raises=tuple(raises),
        )

    # -- the census this counterfactual is measured over ---------------------

    def test_report_ejection_census(
        self, funnel: InformationFunnelReport, counterfactual: _GateCounterfactual
    ) -> None:
        # 79 EJECTED report meetings on the committed baseline-4 9p2i set (down
        # from the 95 baseline-3 recorded; the Qwen3.6-27B / qwen3_6_27b.v1
        # re-record thinned the ejection rate further).
        assert funnel.report_ejections == 79
        assert counterfactual.total_ejections == 79

    # -- (i) the soft-only split, by ejectee role ----------------------------

    def test_soft_only_split_by_role(self, counterfactual: _GateCounterfactual) -> None:
        # Over the 15 soft-only (non-hard-backed) ejections the clamp would:
        #   kept        = off >= 0.60 AND on < 0.60 (the deciding soft lift damped);
        #   already     = off < 0.60 at graph level (render-side / LLM-read eject);
        #   still_over  = off >= 0.60 AND on >= 0.60 (fresh same-meeting lift holds).
        # Split by ejectee role -- CREWMATE = mis-ejects the clamp neutralises,
        # IMPOSTOR = genuine catches the clamp risks. On baseline-4 the polarity
        # is favourable: the clamp neutralises 1 soft-decided crew mis-eject and
        # risks ZERO impostor catches (the 14 still-over ejections carry fresh
        # same-meeting hard lift), inverting the baseline-3 0-crew / 2-impostor
        # split -- exactly why the DoD re-measures rather than carrying a prior
        # figure. (The baseline-2-era 24/31-vs-6/16 hypothesis is long superseded.)
        assert counterfactual.kept == {"CREWMATE": 1, "IMPOSTOR": 0}
        assert counterfactual.already_sub_gate == {"CREWMATE": 0, "IMPOSTOR": 0}
        assert counterfactual.still_over == {"CREWMATE": 5, "IMPOSTOR": 9}
        assert counterfactual.soft_only_total == 15

    # -- (ii) the hard-backed count (non-vacuity floor) ----------------------

    def test_hard_backed_count_is_non_vacuous(
        self, counterfactual: _GateCounterfactual
    ) -> None:
        # There ARE hard-flag-backed convictions to guard: 64 of the 79 ejections
        # carry a grounded (hard_total > atol) post-fold row for the ejectee.
        assert counterfactual.hard_backed >= _HARD_BACKED_FLOOR
        assert counterfactual.hard_backed == 64
        assert (
            counterfactual.hard_backed + counterfactual.soft_only_total
            == counterfactual.total_ejections
        )

    # -- (iii) THE CANARY: zero hard-backed outcome changes -------------------

    def test_zero_hard_backed_ejections_change_outcome(
        self, counterfactual: _GateCounterfactual
    ) -> None:
        # The contract's hard line: over every hard-backed ejection the §4.6 gate
        # verdict is IDENTICAL ON and OFF -- the clamp never suppresses standing
        # hard evidence.
        assert counterfactual.outcome_changes == 0, counterfactual.outcome_change_detail

    def test_subject_level_hard_backed_canary_sweep(
        self, counterfactual: _GateCounterfactual
    ) -> None:
        # The broader sweep: NO hard-backed subject row (ejectee or not, any voter)
        # flips across the 0.60 verdict under the clamp, anywhere in the 95 meetings.
        assert counterfactual.subject_level_flips == ()

    def test_the_clamp_never_raises_an_ejectee_row(
        self, counterfactual: _GateCounterfactual
    ) -> None:
        # on_max <= off_max for every ejectee -- the clamp only ever lowers.
        assert counterfactual.ejectee_clamp_raises == ()
