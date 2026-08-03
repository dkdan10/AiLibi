"""Tests for the learned crew scorer + the crew eval twin (Task 15.16).

Pins the definition-of-done contract for :mod:`training.crew.scorer`:

* the scorer satisfies the 15.15 ``BakeoffPolicy`` / 15.10 ``FramePolicy``
  protocols and is byte-deterministic (argmax with lexical intent-key
  tie-break, stdlib math only);
* emergency semantics are preserved: the wrapper drives the inner FSM (so
  the ``EmergencyPacingTracker`` pacing/announce bookkeeping runs exactly
  once per tick / per meeting, untouched by the interposition), and a scorer
  that selects the emergency press emits the FSM's ``reason``-stamped intent
  and passes the mask validation (the 15.16 canonicalization at work);
* the FSM-delegate baseline is production parity (identical state-hash chain
  to an uninterposed rollout, anchor CE exactly 0);
* the CI-budget entrant trains deterministically through the shared 15.14 ES
  core, and the eval twin emits the full 15.15-shaped row (gate / referee /
  fitness / determinism / leak) with the crew metric block + the Q6
  coverage-cue diagnostic, through the candidate's OWN factory — including
  the leak-test factory mode the observable-only DoD names;
* the entrant-side menu module keeps the 15.15 import firewall: no ``eval.*``
  import may appear in :mod:`training.crew.options` (the harness-twin in
  ``scorer.py`` is the one module that computes reported metrics);
* the Task 18.16 conviction seam threads the SAME shared
  :class:`~training.bakeoff.harness.ConvictionFitnessTerm` object into the crew
  inner fitness (one counter, both sides): GO adds the term additively, NO-GO
  leaves it structurally absent (``conviction=None``, never zero-weighted), and
  the eval row stamps the conviction provenance triple.
"""

from __future__ import annotations

import ast
import json
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import (
    KILL_WITNESS_REASON,
    CrewmatePolicy,
)
from engine.entities import Role
from engine.world import load_canonical_map
from observation.action_intent import (
    EmergencyMeetingIntent,
    ReportBodyIntent,
    WaitIntent,
)
from observation.packet import (
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView, RoomId
from orchestrator.game import TacticalAgent
from training.bakeoff.harness import (
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    DEFAULT_CONVICTION_WEIGHT,
    TRUNCATED_EPISODE_FITNESS,
    BakeoffPolicy,
    TrainedCandidate,
    intent_key,
    load_candidate_weights,
    load_conviction_fitness_term,
    load_train_seeds,
    write_candidate_artifact,
)
from training.conviction.dataset import (
    CONVICTION_FEATURE_NAMES,
    ConvictionMeetingRow,
)
from training.conviction.fidelity import (
    ConvictionGoVerdict,
    load_conviction_verdict,
    write_conviction_verdict_artifact,
)
from training.conviction.model import (
    ConvictionEconomyModel,
    write_conviction_model_artifact,
)
from training.crew.options import (
    CREW_OPTION_KINDS,
    crew_genome_length,
)
from training.crew.scorer import (
    CREW_ENTRANT_NAME,
    CREW_FSM_BASELINE_NAME,
    CoverageCueDiagnostic,
    CrewDecisionTrace,
    CrewEsEntrant,
    CrewOptionScorer,
    CrewProtocolConfig,
    FsmCrewBaseline,
    _CrewCandidateAgent,
    crew_es_budget,
    crew_inner_episode_fitness,
    evaluate_crew_candidate,
    fsm_baseline_candidate,
    rollout_crew_candidate,
    write_crew_results_jsonl,
)
from training.determinism import FramePolicy
from training.env import TacticalRolloutEnv
from training.rewards import compute_shaped_reward

_STAR_MAP = PublicMapView(
    map_id="test_map",
    room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
    room_neighbors={
        "ADMIN": ("CAFETERIA",),
        "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
        "ELECTRICAL": ("CAFETERIA",),
        "MEDBAY": ("CAFETERIA",),
    },
    vent_graph={},
    vent_rooms={},
    task_locations={"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"},
    spawn_room="CAFETERIA",
    meeting_room="CAFETERIA",
    emergency_button_room="CAFETERIA",
)


def _weights_favoring(kind: str, *, weight: float = 100.0) -> tuple[float, ...]:
    """A genome whose linear head loads ONLY the given kind's one-hot."""

    weights = [0.0] * crew_genome_length()
    weights[CREW_OPTION_KINDS.index(kind)] = weight
    return tuple(weights)


def _packet(
    *,
    tick: int,
    room: RoomId,
    agent_id: str = "p-1",
    role: str = "CREWMATE",
    pending_task_id: str | None = None,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=14,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


def _memory(*events: EpisodicEvent) -> AgentMemory:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return AgentMemory(episodic=store)


def _self_state_event(
    *, tick: int, room: RoomId, pending_task_id: str | None = None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SELF_STATE,
        payload={"room": room, "pending_task_id": pending_task_id},
        provenance=PROVENANCE_OBSERVED,
    )


# The Task 18.16 fixture-row feature vectors (12 columns, in
# CONVICTION_FEATURE_NAMES order — the row validator checks key ORDER). Varied
# across rows so both fitted heads see non-degenerate columns.
_CONVICTION_FIXTURE_FEATURE_VALUES: tuple[tuple[float, ...], ...] = (
    (7.0, 0.0, 0.30, 0.20, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    (6.0, 1.0, 0.60, 0.40, 0.15, 2.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0),
    (5.0, 2.0, 0.90, 0.55, 0.25, 3.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0),
)
# One in-vocabulary feature mapping to score at predict time.
_CONVICTION_PREDICT_FEATURES: dict[str, float] = dict(
    zip(
        CONVICTION_FEATURE_NAMES,
        (6.0, 1.0, 0.5, 0.35, 0.1, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0),
        strict=True,
    )
)


def _write_conviction_fixture(
    artifact_dir: Path, *, go: bool, max_uses: int = 50
) -> str:
    """Write a committed conviction bundle (weights + cap + verdict) — GO or NO-GO.

    Three synthetic :class:`ConvictionMeetingRow` rows fit a real
    :class:`ConvictionEconomyModel`, sha-keyed to a directly-constructed
    :class:`ConvictionGoVerdict` whose consequence triple follows ``go``. Returns
    the committed weights sha256 so the caller can pin the row's provenance.
    """

    rows: list[ConvictionMeetingRow] = [
        ConvictionMeetingRow(
            seed=9000 + index,
            game_id=f"synthetic-{index}",
            meeting_id=f"seed9000-meeting-{index}",
            meeting_index=index,
            tick=10 + index,
            features=dict(zip(CONVICTION_FEATURE_NAMES, values, strict=True)),
            flags_minted=rederived + persisted_vent,
            rederived_flags=rederived,
            persisted_vent_flags=persisted_vent,
            conversion_attempted=attempted,
            conversion_converted=converted,
            testimony_backed_conversion=converted > 0,
            is_ejection=is_ejection,
            ceiling_reachable=ceiling_reachable,
        )
        for index, (
            values,
            rederived,
            persisted_vent,
            attempted,
            converted,
            is_ejection,
            ceiling_reachable,
        ) in enumerate(
            zip(
                _CONVICTION_FIXTURE_FEATURE_VALUES,
                (0, 2, 3),  # rederived_flags
                (0, 0, 2),  # persisted_vent_flags
                (0, 1, 2),  # conversion_attempted
                (0, 1, 0),  # conversion_converted
                (False, True, True),  # is_ejection
                (False, True, False),  # ceiling_reachable
                strict=True,
            )
        )
    ]
    model = ConvictionEconomyModel()
    model.fit(rows)
    sha = write_conviction_model_artifact(model, artifact_dir, max_uses=max_uses)
    verdict = ConvictionGoVerdict(
        replay_set_dir="tests/synthetic",
        weights_sha256=sha,
        test_meetings=3,
        test_ejections=2,
        conversions_test=1,
        flag_spearman=0.9 if go else 0.1,
        spearman_bar=0.5,
        meets_spearman_bar=go,
        conversion_recall=0.9 if go else 0.1,
        voice_driven_share=0.2,
        conversion_ceiling=0.8,
        conversion_ceiling_ratio=0.75,
        conversion_bar=0.6,
        meets_conversion_bar=go,
        verdict="GO" if go else "NO-GO",
        fitness_term="ships" if go else "absent",
        prescreen_role="gating" if go else "advisory",
        model_role="training-signal" if go else "diagnostic-only",
    )
    write_conviction_verdict_artifact(verdict, artifact_dir)
    return sha


# --------------------------------------------------------------------------- #
# 1. The entrant-side import firewall (the 15.15 AST-scan pattern).             #
# --------------------------------------------------------------------------- #


def test_options_module_does_not_import_eval() -> None:
    source = Path("training/crew/options.py").read_text()
    tree = ast.parse(source)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            offenders.extend(
                alias.name for alias in node.names if alias.name.startswith("eval")
            )
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None and node.module.startswith("eval"):
                offenders.append(node.module)
    assert not offenders, f"training/crew/options.py imports eval modules: {offenders}"


# --------------------------------------------------------------------------- #
# 2. The scorer satisfies the shared policy protocols and is deterministic.     #
# --------------------------------------------------------------------------- #


def test_scorer_and_baseline_satisfy_policy_protocols() -> None:
    scorer = CrewOptionScorer(weights=_weights_favoring("hold"))
    baseline = FsmCrewBaseline()
    assert isinstance(scorer, BakeoffPolicy)
    assert isinstance(scorer, FramePolicy)
    assert isinstance(baseline, BakeoffPolicy)
    assert isinstance(baseline, FramePolicy)
    assert scorer.encoder_version == "crew-option-features-v1"
    assert baseline.encoder_version == "crew-fsm-delegate-v1"


def test_scorer_rejects_wrong_genome_length() -> None:
    with pytest.raises(ValueError, match="weights length"):
        CrewOptionScorer(weights=(0.0,) * (crew_genome_length() - 1))


def test_scorer_argmax_follows_the_loaded_kind() -> None:
    memory = _memory(
        _self_state_event(tick=3, room="MEDBAY", pending_task_id="swipe_card")
    )
    packet = _packet(tick=3, room="MEDBAY", pending_task_id="swipe_card")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, _STAR_MAP)

    hold_scorer = CrewOptionScorer(weights=_weights_favoring("hold"))
    frame = hold_scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert isinstance(frame.intent, WaitIntent)

    task_scorer = CrewOptionScorer(weights=_weights_favoring("continue_task"))
    frame_task = task_scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert frame_task.intent == fsm_intent  # the FSM's own task walk
    assert len(frame_task.logits) >= 2
    assert frame_task.features  # concatenated per-option features


def test_scorer_delegates_impostor_decisions() -> None:
    scorer = CrewOptionScorer(weights=_weights_favoring("hold"))
    packet = _packet(tick=3, room="MEDBAY", role="IMPOSTOR")
    memory = _memory(_self_state_event(tick=3, room="MEDBAY"))
    fsm_intent = WaitIntent(actor="p-1", type="wait")
    frame = scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert frame.intent == fsm_intent
    assert frame.features == ()
    assert frame.logits == ()
    assert scorer.choice_distribution(
        packet, _STAR_MAP, memory, fsm_intent=fsm_intent
    ) == {intent_key(fsm_intent): 1.0}


def test_choice_distribution_sums_to_one_and_merges_duplicate_intents() -> None:
    # At the hub with a trusted co-located player, buddy-in-place and hold both
    # realize the SAME WaitIntent — the distribution merges them by intent key.
    memory = _memory(
        EpisodicEvent(
            tick=4,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-2", "room": "CAFETERIA", "action": None},
            provenance=PROVENANCE_OBSERVED,
        ),
        _self_state_event(tick=4, room="CAFETERIA"),
    )
    packet = _packet(
        tick=4,
        room="CAFETERIA",
        visible_players=(PlayerView(id="p-2", room="CAFETERIA", action=None),),
    )
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, _STAR_MAP)
    scorer = CrewOptionScorer(weights=_weights_favoring("buddy"))
    distribution = scorer.choice_distribution(
        packet, _STAR_MAP, memory, fsm_intent=fsm_intent
    )
    assert sum(distribution.values()) == pytest.approx(1.0)
    assert "wait" in distribution
    frame = scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert isinstance(frame.intent, WaitIntent)


# --------------------------------------------------------------------------- #
# 3. Trace + diagnostic accounting.                                             #
# --------------------------------------------------------------------------- #


def test_trace_anchor_ce_offmenu_clamp_and_agreement() -> None:
    trace = CrewDecisionTrace()
    wait = WaitIntent(actor="p-1", type="wait")
    press = EmergencyMeetingIntent.model_validate(
        {"type": "emergency", "actor": "p-1", "payload": {"reason": "kill_witnessed"}}
    )
    # On-menu anchor with probability 0.5.
    trace.record(fsm_intent=wait, chosen=wait, distribution={"wait": 0.5})
    # The anchor key is off the distribution: clamped + tallied, not silent.
    trace.record(fsm_intent=press, chosen=wait, distribution={"wait": 1.0})
    assert trace.crew_decisions == 2
    assert trace.scored_decisions == 2
    assert trace.offmenu_decisions == 1
    assert trace.agreement_hits == 1  # wait == wait; emergency != wait
    assert trace.mean_anchor_ce() > 0.0
    # Emergency intent keys are payload-free, so a reason-stamped press agrees
    # with the mask/menu key "emergency".
    trace2 = CrewDecisionTrace()
    trace2.record(fsm_intent=press, chosen=press, distribution={"emergency": 1.0})
    assert trace2.agreement_hits == 1
    assert trace2.mean_anchor_ce() == 0.0

    folded = CrewDecisionTrace()
    folded.fold(trace)
    folded.fold(trace2)
    assert folded.crew_decisions == 3
    assert folded.offmenu_decisions == 1


def test_coverage_cue_diagnostic_accounting() -> None:
    diagnostic = CoverageCueDiagnostic()
    roles: dict[str, Role] = {"p-2": "IMPOSTOR", "p-3": "CREWMATE"}
    memory = _memory(_self_state_event(tick=5, room="MEDBAY"))
    memory.beliefs.seed_player("p-2", suspicion=0.7, trust=0.3)
    packet = _packet(
        tick=5,
        room="MEDBAY",
        visible_players=(
            PlayerView(id="p-2", room="MEDBAY", action=None),
            PlayerView(id="p-3", room="MEDBAY", action=None),
        ),
    )
    diagnostic.record(packet, memory, roles)  # credited + cued (0.7 > 0.5, >= 0.6)
    away_packet = _packet(
        tick=6,
        room="MEDBAY",
        visible_players=(PlayerView(id="p-2", room="ADMIN", action=None),),
    )
    diagnostic.record(away_packet, memory, roles)  # no co-location: not credited
    row = diagnostic.to_row()
    assert row.crew_decisions == 2
    assert row.credited_decisions == 1
    assert row.credited_rate == pytest.approx(0.5)
    assert row.mean_suspicion_toward_shadowed == pytest.approx(0.7)
    assert row.cued_rate == 1.0
    assert row.strongly_cued_rate == 1.0
    assert row.mean_suspicion_toward_colocated_innocents == pytest.approx(0.5)
    assert row.cue_separation == pytest.approx(0.2)


# --------------------------------------------------------------------------- #
# 4. Emergency semantics through the wrapper: tracker bookkeeping untouched,   #
#    and the reason-stamped press passes the mask validation.                   #
# --------------------------------------------------------------------------- #


def _button_room_kill_packet(agent_id: str = "p-1") -> ObservationPacket:
    """Button room, a body AND a witnessed kill: the FSM reports (rung 1), so
    an emergency-loaded scorer OVERRIDES with the reason-stamped press — the
    exact delegated-emergency shape the 15.8 mask gap used to raise on."""

    return _packet(
        tick=6,
        room="CAFETERIA",
        agent_id=agent_id,
        visible_players=(PlayerView(id="p-3", room="CAFETERIA", action="kill"),),
        visible_bodies=(BodyView(id="b-1", room="CAFETERIA", victim_id="p-4"),),
    )


def test_wrapper_emits_reason_stamped_press_through_mask_validation() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    tracker = inner._emergency_tracker
    assert tracker is not None
    observe_calls = 0
    original_observe = tracker.observe_tick

    def counting_observe(**kwargs: object) -> object:
        nonlocal observe_calls
        observe_calls += 1
        return original_observe(**kwargs)  # type: ignore[arg-type]

    tracker.observe_tick = counting_observe  # type: ignore[method-assign, assignment]
    scorer = CrewOptionScorer(weights=_weights_favoring("emergency"))
    agent = _CrewCandidateAgent(
        inner,
        policy=scorer,
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    chosen = agent.decide(_button_room_kill_packet(), _STAR_MAP)
    # The FSM proposed the report (rung 1); the scorer overrode with the
    # kill-witness press, which carries the FSM's reason payload and MUST pass
    # the mask validation (the 15.16 canonicalization).
    assert isinstance(chosen, EmergencyMeetingIntent)
    assert chosen.payload.reason == KILL_WITNESS_REASON
    # The tracker sampled exactly once — by the inner FSM's own decide path —
    # so the interposition adds NO pacing bookkeeping of its own.
    assert observe_calls == 1


def test_wrapper_note_meeting_concluded_keeps_tracker_and_uses_in_lockstep() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    # The tracker's announce/pacing bookkeeping needs memory to re-sample the
    # over-gate baseline at meeting end.
    inner.memory.episodic.append(_self_state_event(tick=8, room="CAFETERIA"))
    tracker = inner._emergency_tracker
    assert tracker is not None
    agent = _CrewCandidateAgent(
        inner,
        policy=CrewOptionScorer(weights=_weights_favoring("hold")),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    agent.note_meeting_concluded(
        end_tick=9, dead_ids=("p-9",), emergency_caller_id="p-1"
    )
    # The wrapper's mask tracker decremented AND the inner tracker's announce
    # bookkeeping ran exactly as production (forwarded verbatim).
    assert agent._emergency_uses_remaining == 0
    assert tracker._own_calls_used == 1
    assert "p-9" in tracker._announced_dead
    assert tracker._last_meeting_end_tick == 9


def test_wrapper_skips_spent_press_and_picks_next_best_option() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    scorer = CrewOptionScorer(weights=_weights_favoring("emergency"))
    agent = _CrewCandidateAgent(
        inner,
        policy=scorer,
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    agent.note_meeting_concluded(
        end_tick=5, dead_ids=(), emergency_caller_id="p-1"
    )  # the one use is spent
    chosen = agent.decide(_button_room_kill_packet(), _STAR_MAP)
    # The press left the menu (uses exhausted — the mask mirror), so the
    # emergency-loaded scorer falls through to another legal option instead of
    # raising or emitting an engine-rejected press.
    assert not isinstance(chosen, EmergencyMeetingIntent)


def test_wrapper_delegates_impostor_and_records_trace() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    trace = CrewDecisionTrace()
    diagnostic = CoverageCueDiagnostic()
    agent = _CrewCandidateAgent(
        inner,
        policy=FsmCrewBaseline(),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=trace,
        diagnostic=diagnostic,
        roles={"p-3": "IMPOSTOR"},
    )
    chosen = agent.decide(_button_room_kill_packet(), _STAR_MAP)
    assert isinstance(chosen, ReportBodyIntent)  # the FSM's rung-1 choice
    assert trace.crew_decisions == 1
    assert trace.agreement_hits == 1
    assert trace.mean_anchor_ce() == 0.0
    assert diagnostic.credited_decisions == 1  # p-3 co-located, engine-truth role


# --------------------------------------------------------------------------- #
# 5. The FSM baseline is production parity; fitness refuses truncation.         #
# --------------------------------------------------------------------------- #


def test_fsm_baseline_rollout_is_production_parity(tmp_path: Path) -> None:
    seed = 1000
    trace = CrewDecisionTrace()
    baseline_rollout = rollout_crew_candidate(
        FsmCrewBaseline(), seed, output_dir=tmp_path / "baseline", trace=trace
    )
    production = TacticalRolloutEnv(
        num_players=9, num_impostors=2, tasks_per_crewmate=2
    ).rollout(seed)
    assert baseline_rollout.state_hashes == production.state_hashes
    assert trace.crew_decisions > 0
    assert trace.agreement_hits == trace.crew_decisions
    assert trace.mean_anchor_ce() == 0.0
    assert trace.offmenu_decisions == 0


def test_crew_inner_fitness_scores_the_truncated_sentinel(tmp_path: Path) -> None:
    trace = CrewDecisionTrace()
    rollout = rollout_crew_candidate(
        FsmCrewBaseline(), 1000, output_dir=tmp_path, max_ticks=3, trace=trace
    )
    assert not rollout.complete
    assert crew_inner_episode_fitness(rollout, trace) == TRUNCATED_EPISODE_FITNESS


# --------------------------------------------------------------------------- #
# 6. The CI-budget entrant + the eval twin's full row.                          #
# --------------------------------------------------------------------------- #


def test_crew_es_entrant_ci_budget_is_deterministic() -> None:
    first = CrewEsEntrant(config=crew_es_budget("ci")).train()
    second = CrewEsEntrant(config=crew_es_budget("ci")).train()
    assert first.entrant == CREW_ENTRANT_NAME
    assert len(first.weights) == crew_genome_length()
    assert first.weights == second.weights
    assert first.train_metadata["es_digest"] == second.train_metadata["es_digest"]
    assert first.config["genome_length"] == crew_genome_length()
    assert isinstance(first.policy, CrewOptionScorer)


def test_crew_es_budget_rejects_unknown_budget() -> None:
    with pytest.raises(ValueError, match="unknown budget"):
        crew_es_budget("overnight")


def test_baseline_artifact_round_trips_empty_genome(tmp_path: Path) -> None:
    candidate = fsm_baseline_candidate()
    entrant_dir, digest = write_candidate_artifact(candidate, tmp_path)
    assert entrant_dir == tmp_path / CREW_FSM_BASELINE_NAME
    assert load_candidate_weights(entrant_dir) == ()
    assert len(digest) == 64


def test_evaluate_crew_candidate_full_row(tmp_path: Path) -> None:
    """The eval twin's full 15.15-shaped row at a tiny CI protocol.

    One eval seed, one determinism seed, the two leak seeds (the factory-mode
    coverage bar needs games that reach bodies). This is the committed pin
    that the crew wrapper passes the leak-test factory mode (the
    observable-only DoD) and that every protocol column populates.
    """

    game_map = load_canonical_map()
    protocol = CrewProtocolConfig(
        eval_seeds=(1000,),
        determinism_seeds=(1004,),
        leak_seeds=(0, 1),
        repeat_n=2,
    )
    # The CI budget is generations=1 / population=2, so the "candidate" is
    # essentially ONE random draw — and most draws are the marathon
    # survive-and-grind shape `CrewEsConfig` documents: training scores them the
    # TRUNCATED sentinel (-10.0) and their games never terminate or reach a body,
    # which starves the leak scan's coverage bar ("the games must reach at least
    # one body"). Task 19.3 replaced the ES core's libm-backed `rng.gauss` with a
    # portable inverse-CDF sampler, which re-rolled that draw, so the ES seed moves
    # 0 -> 7 to keep the fixture on a terminating candidate (champion_fitness
    # 14.59, 232 bodies across the leak seeds). The fragility is pre-existing, not
    # new: measured over es.seed 0..9, the old libm sampler landed a terminating
    # candidate on 4 seeds and the portable one on 1 — the majority marathon under
    # BOTH. Every assertion below is unchanged.
    ci_budget = crew_es_budget("ci")
    budget = replace(ci_budget, es=ci_budget.es.model_copy(update={"seed": 7}))
    entrant = CrewEsEntrant(config=budget, game_map=game_map)
    candidate = entrant.train()
    result = evaluate_crew_candidate(
        candidate, protocol, artifact_root=tmp_path, game_map=game_map
    )

    assert result.entrant == CREW_ENTRANT_NAME
    assert result.tier == "candidate"
    assert result.determinism.deterministic
    assert result.repeat_spread is None
    assert result.genome_length == crew_genome_length()
    assert result.eval_seeds == (1000,)

    # The leak-test factory mode ran through the candidate's OWN crew factory.
    assert result.leak_test_passed
    assert result.leak_packets_scanned is not None
    assert result.leak_packets_scanned > 0
    assert result.leak_failure is None

    # Gate/referee columns populate (selection filters, never fitness terms).
    assert isinstance(result.validity_passed, bool)
    assert isinstance(result.referee_passed, bool)
    assert len(result.referee_scores) == 1

    # The surrogate columns are shape-parity Nones (this track does not meter
    # the 15.13 staleness cap).
    assert result.inner_fitness_surrogate is None
    assert result.truncated_episodes_surrogate is None
    assert result.surrogate_real_divergence is None
    assert result.surrogate_uses_eval == 0

    # The crew metric block + the Q6 diagnostic populate.
    assert 0.0 <= result.crew_win_rate <= 1.0
    assert 0.0 <= result.crew_survival_rate <= 1.0
    assert result.coverage_cue.crew_decisions > 0
    assert result.anchor_cross_entropy >= 0.0
    assert result.fsm_intent_agreement is not None

    # The artifact froze and its sidecar digest matches the row.
    reloaded = load_candidate_weights(tmp_path / CREW_ENTRANT_NAME)
    assert reloaded == candidate.weights
    assert len(result.weights_sha256) == 64

    # Task 18.16: the committed GO verdict stamps the conviction provenance
    # triple — the term ships, the named weight, and the committed sha.
    assert result.conviction_fitness_term == "ships"
    assert result.conviction_weight == DEFAULT_CONVICTION_WEIGHT
    assert (
        result.conviction_weights_sha256
        == "4841f8e02eb7b587237c5b88bc2d350c12c7a5b5ac5c7ae1481069235c7b2a47"
    )

    # The row serializes to one jsonl line and round-trips.
    line = result.to_json_line()
    parsed = json.loads(line)
    assert parsed["entrant"] == CREW_ENTRANT_NAME

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "rows.jsonl"
        write_crew_results_jsonl([result], out)
        assert out.read_text().count("\n") == 1


def test_evaluate_crew_candidate_rejects_foreign_policy(tmp_path: Path) -> None:
    class _NotACrewPolicy:
        encoder_version = "nope"

    candidate = TrainedCandidate(
        entrant="nope",
        policy=_NotACrewPolicy(),  # type: ignore[arg-type]
        weights=(),
        config={},
    )
    protocol = CrewProtocolConfig(eval_seeds=(1000,))
    with pytest.raises(ValueError, match="crew-track policy"):
        evaluate_crew_candidate(candidate, protocol, artifact_root=tmp_path)


# --------------------------------------------------------------------------- #
# 7. The Task 18.16 GO-gated conviction term on the crew inner fitness.         #
# --------------------------------------------------------------------------- #


def test_crew_conviction_term_threads_the_shared_object(tmp_path: Path) -> None:
    """A GO term adds ``weight × mean predicted supply`` to the crew fitness.

    The SAME shared :class:`ConvictionFitnessTerm` type both fitness sides take:
    metering ``predict_meeting`` advances the one counter, and composing the
    crew fitness with ``conviction=term`` adds exactly the recorded mean supply.
    """

    fixture_dir = tmp_path / "conviction"
    _write_conviction_fixture(fixture_dir, go=True)

    trace = CrewDecisionTrace()
    rollout = rollout_crew_candidate(
        None, load_train_seeds()[0], output_dir=tmp_path / "roll", trace=trace
    )
    assert rollout.complete
    base = crew_inner_episode_fitness(rollout, trace)

    term = load_conviction_fitness_term(fixture_dir)
    assert term is not None
    start_uses = term.use_counter.uses
    for _ in range(2):
        trace.record_conviction_prediction(
            term.predict_meeting(_CONVICTION_PREDICT_FEATURES)
        )
    # The one shared counter advanced by exactly the two metered meetings.
    assert term.use_counter.uses == start_uses + 2
    assert trace.conviction_meetings == 2

    combined = crew_inner_episode_fitness(rollout, trace, conviction=term)
    assert combined == base + term.weight * trace.mean_predicted_supply()


def test_crew_conviction_term_absent_under_no_go(tmp_path: Path) -> None:
    """NO-GO: the loader returns None and the fitness is the inline anchor form.

    Structural absence, not a zero-weighted ghost — ``conviction=None`` is
    byte-identical to the bare two-term formula.
    """

    fixture_dir = tmp_path / "conviction"
    _write_conviction_fixture(fixture_dir, go=False)
    assert load_conviction_fitness_term(fixture_dir) is None

    trace = CrewDecisionTrace()
    rollout = rollout_crew_candidate(
        None, load_train_seeds()[0], output_dir=tmp_path / "roll", trace=trace
    )
    assert rollout.complete
    expected = (
        compute_shaped_reward(rollout, "CREWMATE").total()
        - DEFAULT_ANCHOR_PENALTY_WEIGHT * trace.mean_anchor_ce()
    )
    assert crew_inner_episode_fitness(rollout, trace, conviction=None) == expected
    assert crew_inner_episode_fitness(rollout, trace) == expected


def test_crew_trace_fold_includes_conviction_accumulators(tmp_path: Path) -> None:
    """``CrewDecisionTrace.fold`` sums the conviction supply + meeting counters."""

    fixture_dir = tmp_path / "conviction"
    _write_conviction_fixture(fixture_dir, go=True)
    term = load_conviction_fitness_term(fixture_dir)
    assert term is not None

    trace_a = CrewDecisionTrace()
    trace_a.record_conviction_prediction(
        term.predict_meeting(_CONVICTION_PREDICT_FEATURES)
    )
    trace_b = CrewDecisionTrace()
    for _ in range(2):
        trace_b.record_conviction_prediction(
            term.predict_meeting(_CONVICTION_PREDICT_FEATURES)
        )

    folded = CrewDecisionTrace()
    folded.fold(trace_a)
    folded.fold(trace_b)
    assert folded.conviction_meetings == 3
    assert (
        folded.conviction_supply_sum
        == trace_a.conviction_supply_sum + trace_b.conviction_supply_sum
    )


def test_evaluate_crew_candidate_no_go_row(tmp_path: Path) -> None:
    """A NO-GO fixture stamps ``absent`` / None weight / the fixture sha.

    The cheap mirror of :func:`test_evaluate_crew_candidate_full_row`'s
    conviction pins: the FSM baseline over the smallest viable protocol, keyed
    to a tmp_path NO-GO bundle.
    """

    game_map = load_canonical_map()
    fixture_dir = tmp_path / "conviction"
    sha = _write_conviction_fixture(fixture_dir, go=False)
    protocol = CrewProtocolConfig(
        eval_seeds=(1000,),
        determinism_seeds=(1000,),
        repeat_n=2,
        conviction_artifact_dir=fixture_dir,
    )
    result = evaluate_crew_candidate(
        fsm_baseline_candidate(),
        protocol,
        artifact_root=tmp_path / "artifacts",
        game_map=game_map,
    )
    assert result.conviction_fitness_term == "absent"
    assert result.conviction_weight is None
    assert result.conviction_weights_sha256 == sha


def test_evaluate_crew_candidate_rejects_drifted_conviction_bundle(
    tmp_path: Path,
) -> None:
    # The crew twin of the impostor row's drift refusal (PR #304 review): a
    # partially-updated conviction dir (verdict re-keyed off the weights)
    # fails the crew eval BEFORE any side effects instead of stamping stale
    # row provenance.
    conviction_dir = tmp_path / "conviction-drifted"
    _write_conviction_fixture(conviction_dir, go=True)
    drifted = load_conviction_verdict(conviction_dir).model_copy(
        update={"weights_sha256": "0" * 64}
    )
    write_conviction_verdict_artifact(drifted, conviction_dir)
    protocol = CrewProtocolConfig(
        eval_seeds=(1000,),
        determinism_seeds=(1000,),
        repeat_n=2,
        conviction_artifact_dir=conviction_dir,
    )
    with pytest.raises(ValueError, match="drifted"):
        evaluate_crew_candidate(
            fsm_baseline_candidate(), protocol, artifact_root=tmp_path / "artifacts"
        )


def test_body_saw_event_constant_is_pinned() -> None:
    # The diagnostic + menu rely on perception's event vocabulary; pin the two
    # names this package reads so a perception rename fails here, not silently.
    assert EVENT_SAW_BODY == "saw_body"
    assert EVENT_SAW_PLAYER == "saw_player"
