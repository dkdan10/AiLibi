"""Tests for the impostor bake-off harness (Task 15.15).

Pins the harness's three owned things: the fixed eval-seed set (the frozen
corpus test split), the entrant-firewall AST scan (no entrant grows a private
``eval.*`` loop), and the fixed eval protocol — the full metric tuple a
candidate-tier row carries, the experiment-tier demotion a determinism FAIL
triggers (the 15.17 torch seam), the artifact freeze/reload round trip, and the
15.14 Goodhart surrogate re-run obligation. Every game runs at a tiny CI budget
(a handful of 9p2i fake-provider rollouts through :func:`rollout_candidate`), not
the operator-executed full protocol.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from agents.memory.store import AgentMemory
from agents.tactical.features import (
    ENCODER_VERSION,
    TacticalFeatureEncoder,
    mlp_genome_length,
)
from engine.world import load_canonical_map
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    KillIntent,
    MoveIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff import policy_es
from training.bakeoff.es import ESConfig
from training.bakeoff.harness import (
    ANCHOR_CE_CEILING,
    BakeoffPolicy,
    BakeoffProtocolConfig,
    BakeoffResult,
    DecisionTrace,
    TrainedCandidate,
    evaluate_candidate,
    intent_key,
    load_candidate_weights,
    load_eval_seeds,
    rollout_candidate,
    run_goodhart_surrogate_rerun,
    write_candidate_artifact,
)
from training.determinism import PolicyFrame
from training.rollout import DESCRIPTOR_VECTOR_FIELDS, EpisodeRollout

# The four entrant modules the firewall test AST-scans (the committed forbidden
# import is any ``eval`` / ``eval.*`` module — the harness is the ONLY bake-off
# module allowed to reach the eval gates).
_ENTRANT_MODULES: tuple[Path, ...] = (
    Path("training/bakeoff/bc.py"),
    Path("training/bakeoff/utility_es.py"),
    Path("training/bakeoff/policy_es.py"),
    Path("training/bakeoff/map_elites.py"),
)
_SPLITS_PATH: Path = Path("replays/ml_corpus/9p2i/splits.json")


# --------------------------------------------------------------------------- #
# 1. The eval-seed-set assertion (definition of done).                         #
# --------------------------------------------------------------------------- #


def test_eval_seeds_are_the_frozen_corpus_test_split() -> None:
    raw = json.loads(_SPLITS_PATH.read_text())
    eval_seeds = load_eval_seeds()
    assert eval_seeds == tuple(raw["test"])
    assert len(eval_seeds) == 30
    assert all(seed % 5 == 4 for seed in eval_seeds)


# --------------------------------------------------------------------------- #
# 2. The entrant firewall (the committed AST scan).                            #
# --------------------------------------------------------------------------- #


def _forbidden_eval_imports(path: Path) -> list[tuple[str, int, str]]:
    """Every ``eval`` / ``eval.*`` import in ``path`` as (file, line, module)."""

    tree = ast.parse(path.read_text(), filename=str(path))
    offenders: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "eval" or alias.name.startswith("eval."):
                    offenders.append((str(path), node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module is not None and (module == "eval" or module.startswith("eval.")):
                offenders.append((str(path), node.lineno, module))
    return offenders


def test_entrant_modules_do_not_import_eval() -> None:
    offenders: list[tuple[str, int, str]] = []
    for module_path in _ENTRANT_MODULES:
        offenders.extend(_forbidden_eval_imports(module_path))
    assert offenders == [], (
        "entrant modules must not import eval.* (the harness computes every "
        f"reported metric); offenders: {offenders!r}"
    )


# --------------------------------------------------------------------------- #
# 3. The canonical intent key — the shared metric alphabet.                    #
# --------------------------------------------------------------------------- #


def test_intent_key_canonicalization() -> None:
    move = MoveIntent.model_validate(
        {"type": "move", "actor": "imp", "payload": {"to_room": "STORAGE"}}
    )
    kill = KillIntent.model_validate(
        {"type": "kill", "actor": "imp", "payload": {"target": "p-3"}}
    )
    vent = VentIntent.model_validate(
        {"type": "vent", "actor": "imp", "payload": {"vent_id": "v-1"}}
    )
    do_task = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "imp", "payload": {"task_id": "t-5"}}
    )
    report = ReportBodyIntent.model_validate(
        {"type": "report", "actor": "imp", "payload": {"body_id": "b-1"}}
    )
    sabotage = SabotageIntent.model_validate(
        {"type": "sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
    )
    repair = RepairSabotageIntent.model_validate(
        {"type": "repair_sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
    )
    wait = WaitIntent(actor="imp", type="wait")
    emergency = EmergencyMeetingIntent(actor="imp", type="emergency")

    assert intent_key(move) == "move:STORAGE"
    assert intent_key(kill) == "kill:p-3"
    assert intent_key(vent) == "vent:v-1"
    assert intent_key(do_task) == "do_task:t-5"
    assert intent_key(report) == "report:b-1"
    assert intent_key(sabotage) == "sabotage:reactor"
    assert intent_key(repair) == "repair:reactor"
    assert intent_key(wait) == "wait"
    assert intent_key(emergency) == "emergency"


# --------------------------------------------------------------------------- #
# 4. rollout_candidate with policy=None (the FSM delegate mode).               #
# --------------------------------------------------------------------------- #


def test_rollout_candidate_fsm_delegate(tmp_path: Path) -> None:
    trace = DecisionTrace()
    rollout = rollout_candidate(None, 1004, output_dir=tmp_path, trace=trace)
    assert isinstance(rollout, EpisodeRollout)
    # The game either terminates (a real winner) or the tick budget capped it —
    # never a silent third state.
    assert rollout.complete or rollout.truncated
    assert (tmp_path / "replay-seed-1004.jsonl").exists()
    # The FSM delegate mode still feeds the trace: impostor decisions were seen.
    assert trace.impostor_decisions > 0
    # Take-rate accounting is internally consistent: a take is a clean-opportunity
    # kill, so kills_taken can never exceed the clean opportunities.
    assert trace.kills_taken <= trace.opportunities
    assert trace.opportunities >= 0


# --------------------------------------------------------------------------- #
# 5. evaluate_candidate end-to-end — the full candidate-tier metric tuple.     #
# --------------------------------------------------------------------------- #


def _forced_kill_genome() -> tuple[float, ...]:
    """A MaskedMlpPolicy genome that ranks the KILL head slot first everywhere.

    Mirrors :func:`training.bakeoff.goodhart._forced_genome`: a zero genome with
    one large output-bias gene on the kill slot, so whenever a kill is
    submission-legal the argmax realizes it (bodies land, meetings trigger, the
    referee + surrogate paths have data). The kill slot is the first KIND slot
    after the ``R`` sorted-room move slots, and the trailing ``output`` genes are
    the output biases (``b2``) — so the gene index is
    ``genome_length - output + kill_slot``.
    """

    public_map = public_map_from_engine_map(load_canonical_map())
    encoder = TacticalFeatureEncoder()
    input_dim = encoder.feature_dimension(public_map)
    rooms = sorted(public_map.room_ids)
    output = len(rooms) + len(policy_es.KIND_SLOTS)
    genome_length = mlp_genome_length(input_dim=input_dim, hidden=8, output=output)
    kill_slot = len(rooms) + policy_es.KIND_SLOTS.index("kill")
    genome = [0.0] * genome_length
    genome[genome_length - output + kill_slot] = 50.0
    return tuple(genome)


def test_evaluate_candidate_full_row(tmp_path: Path) -> None:
    genome = _forced_kill_genome()
    policy = policy_es.build_masked_mlp_policy(genome, hidden=8)
    candidate = TrainedCandidate(
        entrant="forced-kill-probe",
        policy=policy,
        weights=genome,
        config={
            "entrant": "forced-kill-probe",
            "hidden": 8,
            "encoder_version": policy.encoder_version,
        },
    )
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004, 1009),
        determinism_seeds=(1004,),
        leak_seeds=(0, 1),
        repeat_n=2,
        surrogate_artifact_dir=Path("training/artifacts/surrogate"),
    )
    result = evaluate_candidate(candidate, protocol, artifact_root=tmp_path)

    # A deterministic frozen policy lands on the candidate tier with no repeat
    # spread (the experiment-tier seam is exercised separately).
    assert result.tier == "candidate"
    assert result.determinism.deterministic is True
    assert result.repeat_spread is None
    assert result.encoder_version == ENCODER_VERSION

    # The referee scored exactly the two eval seeds.
    assert len(result.referee_scores) == 2
    assert 0.0 <= result.floor_trip_rate <= 1.0
    assert {gauge.name for gauge in result.supply_gauges} == {
        "witnessed_event_rate",
        "flags_per_meeting",
        "testimony_backed_conversion",
    }

    # The validity gate verdict is present (a bool + an explicit failing-check
    # tuple), never elided.
    assert isinstance(result.validity_passed, bool)
    assert isinstance(result.validity_failing_checks, tuple)

    # Both meeting paths were scored — the divergence column is real data.
    assert isinstance(result.inner_fitness_real, float)
    assert isinstance(result.inner_fitness_surrogate, float)
    assert result.surrogate_real_divergence is not None

    # The anchor cross-entropy is a proper log-loss (>= 0) and the ceiling flag is
    # exactly the ceiling comparison — flagged, never dropped.
    assert result.anchor_cross_entropy >= 0.0
    assert result.anchor_ce_ceiling == ANCHOR_CE_CEILING
    assert result.anchor_ce_flagged == (
        result.anchor_cross_entropy > result.anchor_ce_ceiling
    )

    # Take-rate accounting + the surrogate-use meter are populated.
    assert result.take_opportunities >= 0
    assert result.surrogate_uses_eval > 0

    # The frozen artifact's sha256 matches the on-disk sidecar (reload safety).
    sidecar = (tmp_path / "forced-kill-probe" / "weights.json.sha256").read_text()
    assert sidecar.split()[0] == result.weights_sha256

    # The descriptor footprint carries every named 15.8 descriptor axis.
    assert set(result.descriptor_footprint.keys()) == set(DESCRIPTOR_VECTOR_FIELDS)

    # The row round-trips through its own jsonl serialization.
    restored = BakeoffResult.model_validate(json.loads(result.to_json_line()))
    assert restored.entrant == result.entrant
    assert restored.tier == result.tier
    assert restored.weights_sha256 == result.weights_sha256
    assert restored.genome_length == result.genome_length
    assert restored.referee_scores == result.referee_scores


# --------------------------------------------------------------------------- #
# 6. The experiment-tier path — a determinism FAIL demotes, never drops.       #
# --------------------------------------------------------------------------- #


class _DriftingBakeoffPolicy:
    """A deliberately non-deterministic BakeoffPolicy (a call counter in logits).

    Mirrors ``tests/training/test_determinism.py::_DriftingPolicy``: the counter
    accumulates across the determinism harness's two runs (the instance is
    reused), so the frame stream drifts while the intent — pure FSM delegation —
    keeps the game trajectory identical. The result: determinism FAILs on the
    frame digest, so the harness demotes the row to the experiment tier and
    attaches the N-repeat spread rather than dropping it (the 15.17 seam).
    """

    encoder_version: str = ENCODER_VERSION

    def __init__(self) -> None:
        self._counter = 0.0

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        self._counter += 1.0
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(0.0,),
            logits=(self._counter,),
            intent=fsm_intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> Mapping[str, float]:
        return {intent_key(fsm_intent): 1.0}


def test_evaluate_candidate_experiment_tier(tmp_path: Path) -> None:
    policy = _DriftingBakeoffPolicy()
    candidate = TrainedCandidate(
        entrant="drift-probe",
        policy=policy,
        weights=(0.0,),
        config={"entrant": "drift-probe"},
    )
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        repeat_n=2,
        surrogate_artifact_dir=None,
    )
    result = evaluate_candidate(candidate, protocol, artifact_root=tmp_path)

    assert result.tier == "experiment"
    assert result.determinism.deterministic is False
    # The full determinism report rides the row: both digests are hex SHA-256.
    assert len(result.determinism.frame_stream_sha256) == 64
    assert len(result.determinism.state_hash_sha256) == 64
    # The N-repeat metric spread is attached (the seam the torch entrant reports
    # through), with min <= mean <= max on each metric.
    spread = result.repeat_spread
    assert spread is not None
    assert spread.repeats == 2
    for metric in (
        spread.inner_fitness_real,
        spread.impostor_win_rate,
        spread.anchor_cross_entropy,
    ):
        assert metric.min <= metric.mean <= metric.max
    # The surrogate column stays None when the surrogate is disabled.
    assert result.inner_fitness_surrogate is None


# --------------------------------------------------------------------------- #
# 7. Artifact freeze/reload — float-hex JSON + sha256 sidecar.                  #
# --------------------------------------------------------------------------- #


def test_artifact_round_trip(tmp_path: Path) -> None:
    genome = _forced_kill_genome()
    policy = policy_es.build_masked_mlp_policy(genome, hidden=8)
    candidate = TrainedCandidate(
        entrant="round-trip-probe",
        policy=policy,
        weights=genome,
        config={"entrant": "round-trip-probe", "hidden": 8},
    )
    entrant_dir, digest = write_candidate_artifact(candidate, tmp_path)

    # The reload recovers the exact genome, sha256-verified.
    assert load_candidate_weights(entrant_dir) == genome
    # The sidecar carries the standard ``<64-hex>  <basename>`` line.
    sidecar = (entrant_dir / "weights.json.sha256").read_text()
    assert sidecar == f"{digest}  weights.json\n"
    assert len(digest) == 64

    # Corrupting the weights file makes the sha256-verified reload fail loud.
    (entrant_dir / "weights.json").write_text("corrupted")
    with pytest.raises(ValueError):
        load_candidate_weights(entrant_dir)


# --------------------------------------------------------------------------- #
# 8. The 15.14 obligation — the Goodhart probe under the surrogate path.        #
# --------------------------------------------------------------------------- #


def test_goodhart_surrogate_rerun_ci_budget() -> None:
    config = ESConfig(
        generations=1,
        population=1,
        sigma=0.5,
        seed=0,
        fitness_seeds=(1004,),
    )
    rerun = run_goodhart_surrogate_rerun(config=config)

    assert rerun.probe.verdict in ("HELD", "EXPLOITS_FOUND")
    # The forced single-tactic reachability sweep ran every non-FSM lever.
    assert {lever.tactic for lever in rerun.probe.lever_sweep} == {
        "emergency",
        "report",
        "wait",
        "kill",
        "sabotage",
    }

    stats = rerun.meeting_stats
    assert stats.surrogate_meetings >= 0
    for rate in (
        stats.surrogate_ejection_rate,
        stats.surrogate_skip_rate,
        stats.real_ejection_rate,
    ):
        assert rate is None or 0.0 <= rate <= 1.0

    # The surrogate meeting path was actually exercised (metered against the cap).
    assert rerun.surrogate_uses > 0

    # The delta verdict names BOTH the committed 15.14 fake-provider verdict and
    # the surrogate-path verdict.
    assert str(rerun.committed_baseline["verdict"]) in rerun.delta_verdict
    assert rerun.probe.verdict in rerun.delta_verdict


# --------------------------------------------------------------------------- #
# The frozen-candidate protocol is the runtime-checkable BakeoffPolicy.         #
# --------------------------------------------------------------------------- #


def test_masked_mlp_policy_is_bakeoff_policy() -> None:
    policy = policy_es.build_masked_mlp_policy(_forced_kill_genome(), hidden=8)
    assert isinstance(policy, BakeoffPolicy)


# --------------------------------------------------------------------------- #
# A filtered single-entrant rerun keeps the BC warm start (PR #242 review).     #
# --------------------------------------------------------------------------- #


def test_filtered_rerun_keeps_bc_warm_start() -> None:
    # The CLI's `--entrant policy-es` path never runs the BC entrant's own
    # train(); the warm-start closure must train the (deterministic) clone on
    # demand instead of silently degrading to a random init (Codex review on
    # PR #242).
    from training.bakeoff.harness import _build_entrants

    protocol = BakeoffProtocolConfig(eval_seeds=(1004,), surrogate_artifact_dir=None)
    entrants = [
        entrant
        for entrant in _build_entrants("ci", protocol)
        if entrant.name == "policy-es"
    ]
    assert len(entrants) == 1
    candidate = entrants[0].train()
    assert candidate.train_metadata["warm_start_used"] is True
