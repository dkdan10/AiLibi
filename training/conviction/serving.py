"""The live conviction serving path — run_meeting-time feature assembly (Task 18.30).

The conviction gradient (:mod:`training.conviction.model`) was wired and pinned
at the fitness seam but DORMANT: no live accessor served the four kill/body
features, so every training loop passed ``conviction=None`` and the pre-screen
accepted only caller-built vectors (training/reports/report-conviction-model.md
§10). This module lands the serving path: it reconstructs the exact
:data:`~training.conviction.dataset.CONVICTION_FEATURE_NAMES` vector from the
``MeetingRunner.run_meeting`` inputs ``(meeting_id, state, agents)`` at trigger
time — the same 12 features the offline table
(:func:`training.conviction.dataset.build_conviction_table`) reduces each
recorded meeting to.

**The feature fence, served live.** Every feature draws ONLY from the
run_meeting input universe :data:`training.conviction.dataset.
CONVICTION_FEATURE_PROVENANCE` declares (the committed provenance test asserts
it feature by feature):

* ``alive_count`` / ``meeting_index`` — the living roster off ``state.players``
  and the index parsed off the orchestrator-formatted ``meeting_id`` (the
  ``training/surrogate/runner.py`` precedent).
* ``max_suspicion`` / ``mean_suspicion`` / ``suspicion_margin`` /
  ``cells_at_gate`` — aggregates over the non-self (voter, candidate) belief
  cells, live via each agent's ``suspicion_graph_for_meeting()``.
* ``vent_witness_pairs`` / ``vent_witnessed_candidates`` — the voter-local
  witnessed-vent pins via each agent's ``vent_witness_records_for_meeting()``.
* ``kill_pin_pairs`` / ``kill_pinned_candidates`` and ``body_proximity_pairs``
  / ``body_proximity_candidates`` — the game-long voter-local witnessed-kill and
  §6.3 Rule-1 body-proximity pins, via the 18.30 kill/body ``*_for_meeting``
  accessor pair (:meth:`orchestrator.game.TacticalAgent.
  kill_witness_records_for_meeting` / ``body_proximity_records_for_meeting``).
  The DESIGN.md §4.7 teammate firewall the offline pins inherit (kill =
  crew-witnesses-only; body = teammate-excluded for an impostor observer) lives
  IN those accessors, not here — the assembler reads their already-guarded
  subject sets.

**The J1 raw-recovery decision.** The live ``SuspicionEntry.suspicion`` scalar
is the CLAMPED render (the Task-16.4 hard-evidence gate is unconditional since
its retirement to always-ON, so an entirely-soft conviction-grade row renders
capped at ``HARD_EVIDENCE_GATE_RENDER_CEIL = 0.59``), while the offline table's
``belief_suspicion`` column is the RAW fold scalar. Reading ``entry.suspicion``
would diverge — most sharply on ``cells_at_gate``, a discrete flip at the
0.60 gate the 0.59 clamp sits one notch under. So the assembler RECOVERS the raw
scalar from the eight provenance channels exactly as
:func:`training.surrogate.dataset.measure_belief_render_parity` does
(``0.5 + sum(the eight fields) == the raw suspicion``, the belief store's 16.3
sum invariant), never reading the clamped ``suspicion``. An absent graph row is
production's unseeded neutral prior 0.5 (the ``training/surrogate/runner.py``
precedent) — synthesized for every non-self (voter, candidate) pair a voter's
graph omits, so the live cell grid matches the offline table's full-roster
``row.candidates``.

**Correctness is by measurement, not assertion.** The committed parity pin
(``tests/training/test_conviction_serving.py``) re-drives the corpus TEST split
through real :class:`~orchestrator.game.TacticalAgent` instances and asserts the
live-assembled vector equals the offline table's row feature-for-feature (exact
``==``, every ``CONVICTION_FEATURE_NAMES`` entry, every meeting) — the
live/offline semantics gap closes there.

This module NEVER imports ``eval.*`` (the committed AST firewall test scans every
``training/conviction/*.py``): the labels the model was fit against are the
referee's quantities, mirrored from recorded bytes, and the serving path stays
on the same side of the firewall.

Public surface (stable — the loops import these):
:func:`assemble_live_conviction_features`, :class:`LiveConvictionFeatureError`,
:class:`LiveConvictionAgent`, :class:`ConvictionServingMeetingRunner`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Final, Protocol, runtime_checkable

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import WorldState
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger
from meetings.render_contract import SuspicionEntry
from meetings.schemas import VentWitnessRecord
from orchestrator.game import (
    BodyProximityRecord,
    KillWitnessRecord,
    MeetingArtifacts,
    MeetingRunner,
)
from training.conviction.model import ConvictionPrediction

# The orchestrator's meeting-id format (``orchestrator/game.py`` ``_game_id`` +
# ``_run_and_apply_meeting``): ``"{game_id}:meeting-{meeting_index}"``. Parsed
# for the ``meeting_index`` feature exactly as ``training/surrogate/runner.py``
# does, rather than counting invocations (a runner's lifetime is a wiring
# choice; the id is always orchestrator-stamped per game).
_MEETING_ID_SEPARATOR: Final[str] = ":meeting-"

# The belief store's neutral prior (``agents.memory.beliefs`` ``_DEFAULT_
# SUSPICION``), mirrored by name — this module is downstream of the render
# contract and never imports ``agents.*`` internals for a constant. Two uses:
# the raw-suspicion recovery base and the unseeded absent-cell default.
_NEUTRAL_PRIOR: Final[float] = 0.5


class LiveConvictionFeatureError(RuntimeError):
    """The live feature assembly could not honestly reconstruct the vector.

    Raised by :func:`assemble_live_conviction_features` when a run_meeting input
    is structurally unusable — a ``meeting_id`` that does not carry the
    orchestrator's format, a living voter with no constructed agent, an agent
    that does not expose the four conviction accessors, or a meeting with no
    non-self cell. Deliberately NOT silently recoverable (AGENTS.md "no silent
    fallbacks"): a mis-assembled feature vector fed to the frozen model would
    corrupt the training signal invisibly.
    """


@runtime_checkable
class LiveConvictionAgent(Protocol):
    """The four meeting-open accessors the live assembler reads (Task 18.30).

    The structural contract the assembler requires of every living voter's
    agent — the belief graph plus the three typed first-hand record channels.
    ``runtime_checkable`` so the assembler can gate each agent by ``isinstance``
    (presence-only, per the protocol runtime semantics); the training-side
    ``_CandidateAgent`` / ``_CrewCandidateAgent`` wrappers satisfy it through
    their ``__getattr__`` delegation. Intentionally NARROWER than, and separate
    from, :class:`orchestrator.game.MeetingAwareAgent`: the kill/body accessors
    are a training-side seam and never joined the meeting-layer protocol (whose
    runtime ``isinstance`` gate would break test doubles).
    """

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]: ...

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]: ...

    def kill_witness_records_for_meeting(self) -> tuple[KillWitnessRecord, ...]: ...

    def body_proximity_records_for_meeting(
        self,
    ) -> tuple[BodyProximityRecord, ...]: ...


def _raw_suspicion(entry: SuspicionEntry) -> float:
    """Recover the RAW fold scalar from the entry's provenance decomposition.

    ``_NEUTRAL_PRIOR + sum(the eight channels)`` — the belief store's 16.3 sum
    invariant, the exact recovery
    :func:`training.surrogate.dataset.measure_belief_render_parity` uses to
    sidestep the J1 render clamp on ``entry.suspicion`` (see the module
    docstring). The offline table's ``belief_suspicion`` column is this raw
    scalar, so the live features must recover it rather than read the clamp.
    """

    return _NEUTRAL_PRIOR + (
        entry.flag_lift
        + entry.body_proximity
        + entry.kill_or_vent_pin
        + entry.testimony_spread
        + entry.accusation_carry
        + entry.carried_hard
        + entry.carried_soft
        + entry.unattributed
    )


def _meeting_index_from_id(meeting_id: str) -> int:
    """Read the per-game meeting index off the orchestrator-formatted id."""

    _, separator, suffix = meeting_id.rpartition(_MEETING_ID_SEPARATOR)
    if not separator or not suffix.isdigit():
        raise LiveConvictionFeatureError(
            f"meeting_id {meeting_id!r} does not carry the orchestrator's "
            f"'{{game_id}}{_MEETING_ID_SEPARATOR}{{index}}' format; the live "
            "assembler cannot derive the meeting_index feature from it"
        )
    return int(suffix)


def assemble_live_conviction_features(
    *,
    meeting_id: str,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
) -> dict[str, float]:
    """Assemble the fenced conviction feature vector live at meeting-open.

    Reduces the run_meeting inputs to exactly
    :data:`~training.conviction.dataset.CONVICTION_FEATURE_NAMES` (order
    preserved — the model's layout contract), mirroring the offline
    ``training.conviction.dataset._meeting_features`` reduction feature-for-
    feature (the parity pin proves the equality on the corpus test split). All
    aggregates run over the NON-self (voter, candidate) cells; the belief scalar
    is the RAW recovery (:func:`_raw_suspicion`), and an absent graph row reads
    the neutral 0.5 prior so the cell grid matches the offline full roster.

    Iterates voters and candidates in sorted id order so the float summation for
    ``mean_suspicion`` is deterministic and byte-matches the offline sorted-row
    reduction. Fails loud (:class:`LiveConvictionFeatureError`) on a malformed
    ``meeting_id``, a missing or non-conforming voter agent, or a meeting with no
    non-self cell — never silently emitting a corrupt vector.
    """

    living = sorted(
        player_id for player_id, player in state.players.items() if player.alive
    )
    meeting_index = float(_meeting_index_from_id(meeting_id))

    suspicions: list[float] = []
    per_candidate_max: dict[PlayerId, float] = {}
    cells_at_gate = 0
    vent_pairs = 0
    kill_pairs = 0
    proximity_pairs = 0
    vent_candidates: set[PlayerId] = set()
    kill_candidates: set[PlayerId] = set()
    proximity_candidates: set[PlayerId] = set()

    for voter in living:
        agent = agents.get(voter)
        if agent is None:
            raise LiveConvictionFeatureError(
                f"meeting {meeting_id!r} has no agent for living player "
                f"{voter!r}; every alive voter must have a constructed agent"
            )
        if not isinstance(agent, LiveConvictionAgent):
            raise LiveConvictionFeatureError(
                f"agent for {voter!r} does not expose the conviction serving "
                "accessors (suspicion_graph_for_meeting, "
                "vent_witness_records_for_meeting, kill_witness_records_for_"
                "meeting, body_proximity_records_for_meeting) — the live "
                "assembler reads the same inputs the offline table reduces"
            )
        graph = {
            entry.player_id: entry for entry in agent.suspicion_graph_for_meeting()
        }
        vent_subjects = {
            record.subject for record in agent.vent_witness_records_for_meeting()
        }
        kill_subjects = {
            record.subject for record in agent.kill_witness_records_for_meeting()
        }
        body_subjects = {
            record.subject for record in agent.body_proximity_records_for_meeting()
        }
        for candidate in living:
            if candidate == voter:
                continue
            entry = graph.get(candidate)
            # The RAW fold scalar (not the clamped ``entry.suspicion``); an
            # absent row is production's unseeded neutral prior.
            suspicion = _raw_suspicion(entry) if entry is not None else _NEUTRAL_PRIOR
            suspicions.append(suspicion)
            prior = per_candidate_max.get(candidate)
            if prior is None or suspicion > prior:
                per_candidate_max[candidate] = suspicion
            if suspicion >= DEFAULT_SKIP_CONFIDENCE_THRESHOLD:
                cells_at_gate += 1
            if candidate in vent_subjects:
                vent_pairs += 1
                vent_candidates.add(candidate)
            if candidate in kill_subjects:
                kill_pairs += 1
                kill_candidates.add(candidate)
            if candidate in body_subjects:
                proximity_pairs += 1
                proximity_candidates.add(candidate)

    if not suspicions:
        raise LiveConvictionFeatureError(
            f"meeting {meeting_id!r} has no non-self belief cells; a live "
            "meeting always seats at least two living voters"
        )

    leads = sorted(per_candidate_max.values(), reverse=True)
    margin = leads[0] - leads[1] if len(leads) >= 2 else 0.0
    return {
        "alive_count": float(len(living)),
        "meeting_index": meeting_index,
        "max_suspicion": max(suspicions),
        "mean_suspicion": sum(suspicions) / len(suspicions),
        "suspicion_margin": margin,
        "cells_at_gate": float(cells_at_gate),
        "vent_witness_pairs": float(vent_pairs),
        "vent_witnessed_candidates": float(len(vent_candidates)),
        "kill_pin_pairs": float(kill_pairs),
        "kill_pinned_candidates": float(len(kill_candidates)),
        "body_proximity_pairs": float(proximity_pairs),
        "body_proximity_candidates": float(len(proximity_candidates)),
    }


class ConvictionServingMeetingRunner:
    """A :class:`~orchestrator.game.MeetingRunner` that serves the term live (18.30).

    Wraps an inner runner: on ``run_meeting`` it assembles the pre-meeting
    conviction feature vector (:func:`assemble_live_conviction_features`) from
    the trigger-time inputs, predicts the supply, records the prediction, then
    delegates to the inner runner unchanged and returns its artifacts. The
    assembly + prediction happen BEFORE delegation (the features are
    pre-meeting), and the wrapper never mutates ``state`` (precedent:
    ``training/realpath.py::_TimeoutMeetingRunner``).

    ``predict`` / ``record`` are CALLBACKS, not concrete types, precisely so this
    module never imports ``training.bakeoff.harness`` / ``training.crew.scorer``
    (no cycle): the loops bind ``term.predict_meeting`` and
    ``trace.record_conviction_prediction``. ``on_features``, when supplied,
    receives the assembled mapping (the pre-screen collector's feed). If
    ``predict`` raises — e.g. the staleness cap is spent — the error propagates
    unchanged; the wrapper never swallows it (AGENTS.md "no silent fallbacks").
    """

    def __init__(
        self,
        *,
        inner: MeetingRunner,
        predict: Callable[[Mapping[str, float]], ConvictionPrediction],
        record: Callable[[ConvictionPrediction], None],
        on_features: Callable[[Mapping[str, float]], None] | None = None,
    ) -> None:
        self._inner = inner
        self._predict = predict
        self._record = record
        self._on_features = on_features

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        """Serve the conviction term for one meeting, then delegate unchanged."""

        features = assemble_live_conviction_features(
            meeting_id=meeting_id, state=state, agents=agents
        )
        prediction = self._predict(features)
        self._record(prediction)
        if self._on_features is not None:
            self._on_features(features)
        return await self._inner.run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )


__all__ = [
    "ConvictionServingMeetingRunner",
    "LiveConvictionAgent",
    "LiveConvictionFeatureError",
    "assemble_live_conviction_features",
]
