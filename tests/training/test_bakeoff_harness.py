"""Tests for the impostor bake-off harness (Task 15.15).

Pins the harness's three owned things: the fixed eval-seed set (the frozen
corpus test split), the entrant-firewall AST scan (no entrant grows a private
``eval.*`` loop), and the fixed eval protocol — the full metric tuple a
candidate-tier row carries, the experiment-tier demotion a determinism FAIL
triggers (the 15.17 torch seam), the artifact freeze/reload round trip, and the
15.14 Goodhart surrogate re-run obligation. Every game runs at a tiny CI budget
(a handful of 9p2i fake-provider rollouts through :func:`rollout_candidate`), not
the operator-executed full protocol.

Task 18.16 adds the conviction-integration pins: the entrant firewall now also
scans for a private ``training.conviction`` loop; the GO-gated
:class:`ConvictionFitnessTerm` loads under a fixture GO verdict and is
STRUCTURALLY absent (``None``) under NO-GO; the term composes additively into
:func:`inner_episode_fitness` with the conservative
``DEFAULT_CONVICTION_WEIGHT <= DEFAULT_ANCHOR_PENALTY_WEIGHT`` weight; ONE
sha-keyed :class:`ConvictionUseCounter` threads through both the term and
:func:`conviction_prescreen` under the cumulative staleness cap; the additive
anchor-policy seam on :class:`DecisionTrace` is byte-identical to the scripted
FSM when a delegate anchor is supplied and re-anchors the CE (never the
FSM-keyed agreement) under an alternative; and the committed row stamps the
conviction provenance triple ("ships"/weight under GO, "absent"/None under
NO-GO).
"""

from __future__ import annotations

import ast
import inspect
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from agents.memory.store import AgentMemory
from agents.tactical.features import (
    ENCODER_VERSION,
    TacticalFeatureEncoder,
    mlp_genome_length,
)
from engine.world import load_canonical_map
from eval.watchability import population_relative_conversion_floor
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
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
from observation.packet import (
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import MeetingRunner, build_default_meeting_runner
from training.bakeoff import policy_es
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import run_goodhart_probe
from training.bakeoff.harness import (
    ANCHOR_CE_CEILING,
    BAKEOFF_BASELINE_ID,
    BakeoffPolicy,
    BakeoffProtocolConfig,
    BakeoffResult,
    ConvictionFitnessTerm,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    DEFAULT_CONVICTION_WEIGHT,
    DecisionTrace,
    PRESCREEN_CONVERSION_PIN,
    PRESCREEN_FLAGS_PER_MEETING_FLOOR,
    TrainedCandidate,
    conviction_prescreen,
    evaluate_candidate,
    inner_episode_fitness,
    intent_key,
    load_candidate_weights,
    load_conviction_fitness_term,
    load_eval_seeds,
    rollout_candidate,
    run_goodhart_surrogate_rerun,
    write_candidate_artifact,
)
from training.conviction.dataset import CONVICTION_FEATURE_NAMES, ConvictionMeetingRow
from training.conviction.fidelity import (
    ConvictionGoVerdict,
    load_conviction_verdict,
    write_conviction_verdict_artifact,
)
from training.conviction.model import (
    ConvictionEconomyModel,
    ConvictionStalenessCap,
    ConvictionStalenessExceededError,
    ConvictionUseCounter,
    load_conviction_model_artifact,
    load_conviction_staleness_cap,
    write_conviction_model_artifact,
)
from training.conviction.serving import ConvictionServingMeetingRunner
from training.determinism import PolicyFrame
from training.rewards import compute_shaped_reward
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
# 1b. The selection-bar pin (Task 18.14): baseline-6 + goodhart default.       #
# --------------------------------------------------------------------------- #


def test_selection_bar_pins_the_baseline_6_floors() -> None:
    """Pin Task 18.14: the bake-off selects on the baseline-6 (adopted Phase-18)
    floors and the goodhart probe default tracks the same literal.

    The flip is coupled: moving ``BAKEOFF_BASELINE_ID`` to ``baseline-6`` requires
    ``run_goodhart_probe``'s default ``baseline_id`` to move with it, so the probe
    keeps measuring against the same floors the bake-off selects on."""

    assert BAKEOFF_BASELINE_ID == "baseline-6"
    signature = inspect.signature(run_goodhart_probe)
    probe_default = signature.parameters["baseline_id"].default
    assert probe_default == BAKEOFF_BASELINE_ID


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


def _forbidden_conviction_imports(path: Path) -> list[tuple[str, int, str]]:
    """Every ``training.conviction`` / ``training.conviction.*`` import in ``path``.

    The 18.16 twin of :func:`_forbidden_eval_imports`: the harness + the crew
    scorer OWN the conviction seam (they load the frozen artifact, meter the one
    shared counter, and compose the GO-gated term), so no ENTRANT may grow a
    private conviction loop against the frozen instrument.
    """

    tree = ast.parse(path.read_text(), filename=str(path))
    offenders: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "training.conviction" or alias.name.startswith(
                    "training.conviction."
                ):
                    offenders.append((str(path), node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module is not None and (
                module == "training.conviction"
                or module.startswith("training.conviction.")
            ):
                offenders.append((str(path), node.lineno, module))
    return offenders


def test_entrant_modules_do_not_import_conviction() -> None:
    offenders: list[tuple[str, int, str]] = []
    for module_path in _ENTRANT_MODULES:
        offenders.extend(_forbidden_conviction_imports(module_path))
    assert offenders == [], (
        "entrant modules must not import training.conviction.* (the harness + "
        "the crew scorer own the GO-gated conviction seam — no entrant grows a "
        f"private conviction loop); offenders: {offenders!r}"
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

    # Task 18.16: the default protocol reads the COMMITTED conviction artifact
    # dir (a GO verdict), so the row stamps the provenance triple — the term
    # ships, the weight is named, and the sha keys to the committed instrument.
    assert result.conviction_fitness_term == "ships"
    assert result.conviction_weight == DEFAULT_CONVICTION_WEIGHT
    assert result.conviction_weights_sha256 == _COMMITTED_CONVICTION_SHA256

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


# --------------------------------------------------------------------------- #
# 9. The committed re-run protocol pins (Task 17.12).                          #
#                                                                              #
# The bake-off re-run under the baseline-5 floors + re-grounded surrogate      #
# regenerated the committed rows (baseline-3 -> baseline-5) while reproducing  #
# the Phase-15 genomes byte-identically. Nothing else in this module reads the #
# committed jsonl/artifacts, so these are pure-file-read pins on the SHIPPED   #
# state: a future re-run that moves the rows or the floor constants must trip  #
# a pin HERE (not only in a downstream champion test). No game rollouts.       #
# --------------------------------------------------------------------------- #

_RESULTS_JSONL: Path = Path("training/reports/results-impostor-bakeoff.jsonl")
_IMPOSTOR_ARTIFACT_ROOT: Path = Path("training/artifacts/impostor")

# The canonical entrant order the committed slate ships in (locked decision 1:
# the full four-method slate), one row each.
_CANONICAL_ENTRANTS: tuple[str, ...] = (
    "bc-dagger",
    "utility-es",
    "policy-es",
    "map-elites",
)

# The baseline-5 supply-gauge floor pins (eval/watchability.py:755-762), carried
# as LITERALS so a pin trips if EITHER the committed rows OR the floor constants
# drift apart. 7/203 and 90/179 round-trip exactly through the row's JSON.
_WITNESSED_EVENT_RATE_FLOOR: float = 7 / 203  # 0.034482758620689655
_FLAGS_PER_MEETING_FLOOR: float = 90 / 179  # 0.5027932960893855

# The four re-run genomes reproduced Phase 15 byte-for-byte; these full digests
# are also depended on downstream (tests/agents/test_learned_policy.py pins the
# utility-es sha), so a weights move must trip THIS pin in the bake-off's own
# test file too.
_COMMITTED_WEIGHTS_SHA256: dict[str, str] = {
    "bc-dagger": "ddb1e706ae1a827e68b359f1bd4d491e77d1761f6d8ccf66571987b06d784d94",
    "utility-es": "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0",
    "policy-es": "561e5ff36478dacf4806782e57f3411fc8a6c38a5a52f22bb85b3abd1e86ca89",
    "map-elites": "b4469dec6f95def6ba53b9ca37b81b4285b02501374047f290c6a579de0f84bb",
}


def _committed_bakeoff_rows() -> list[dict[str, Any]]:
    """The committed re-run rows, one parsed dict per entrant, in file order."""

    rows: list[dict[str, Any]] = [
        json.loads(line)
        for line in _RESULTS_JSONL.read_text().splitlines()
        if line.strip()
    ]
    return rows


def _supply_gauges_by_name(row: Mapping[str, Any]) -> dict[str, Any]:
    """The row's supply gauges keyed by ``name`` (three per candidate row)."""

    return {str(gauge["name"]): gauge for gauge in row["supply_gauges"]}


def test_rerun_rows_are_the_four_canonical_entrants() -> None:
    rows = _committed_bakeoff_rows()
    entrants = tuple(str(row["entrant"]) for row in rows)
    # Exactly the four entrants, in canonical order, one row each.
    assert entrants == _CANONICAL_ENTRANTS
    assert len(set(entrants)) == len(_CANONICAL_ENTRANTS)


def test_rerun_rows_pin_the_baseline_5_protocol() -> None:
    frozen_eval_seeds = load_eval_seeds()
    for row in _committed_bakeoff_rows():
        # The rows moved to the baseline-5 (phase-close) floors; every row is a
        # candidate-tier row (no determinism demotion under the frozen genomes).
        assert row["baseline_id"] == "baseline-5"
        assert row["tier"] == "candidate"
        # The recorded protocol trains on the fake-provider meeting path (no
        # surrogate meetings), and meters the surrogate divergence column only
        # during eval.
        assert row["surrogate_uses_training"] == 0
        assert int(row["surrogate_uses_eval"]) > 0
        # The eval set is the frozen corpus test split: 30 seeds, all seed%5==4.
        eval_seeds = tuple(int(seed) for seed in row["eval_seeds"])
        assert eval_seeds == frozen_eval_seeds
        assert len(eval_seeds) == 30
        assert all(seed % 5 == 4 for seed in eval_seeds)


def test_rerun_rows_carry_the_baseline_5_supply_floors() -> None:
    for row in _committed_bakeoff_rows():
        gauges = _supply_gauges_by_name(row)
        assert set(gauges) == {
            "witnessed_event_rate",
            "flags_per_meeting",
            "testimony_backed_conversion",
        }
        # The two absolute floors are the baseline-5 point estimates, pinned as
        # literals: 7/203 (rare-event witnessed rate) and 90/179 (flags/meeting).
        assert gauges["witnessed_event_rate"]["floor"] == _WITNESSED_EVENT_RATE_FLOOR
        assert gauges["flags_per_meeting"]["floor"] == _FLAGS_PER_MEETING_FLOOR
        # The conversion floor is the 16.11 population-relative DERIVED value:
        #   min(1.0, (64/135) * ((90/179) / measured flags_per_meeting)).
        # On the fake-provider path measured flags_per_meeting is 0.0, so the
        # ratio diverges and the derived floor caps at exactly 1.0.
        assert gauges["flags_per_meeting"]["measured"] == 0.0
        assert gauges["testimony_backed_conversion"]["floor"] == 1.0


def test_rerun_rows_match_the_committed_artifact_digests() -> None:
    for row in _committed_bakeoff_rows():
        entrant = str(row["entrant"])
        entrant_dir = _IMPOSTOR_ARTIFACT_ROOT / entrant
        row_sha = str(row["weights_sha256"])

        # The full 64-hex digest, pinned as a literal (Phase-15 genome byte-
        # identical): a re-run that moves the weights trips here.
        assert len(row_sha) == 64
        assert row_sha == _COMMITTED_WEIGHTS_SHA256[entrant]

        # The digest the loader verifies against on reload (``<64-hex>  <name>``).
        sidecar = (entrant_dir / "weights.json.sha256").read_text()
        assert sidecar.split()[0] == row_sha

        # The loader sha-verifies the artifact bytes on reload and raises on
        # drift; a successful reload proves the row digest == sha256(committed
        # weights bytes), closing row -> sidecar -> bytes.
        weights = load_candidate_weights(entrant_dir)
        assert isinstance(weights, tuple)
        assert len(weights) > 0


# The persisted 15.9 provenance stamp fields, per entrant (the machine-readable
# source Task 17.14's multi-finalist recorder stamps games from — "stamp fields
# come from the candidate's own config, never from the committed champion's
# constants"). ``method`` uses the productized single-line tokens: utility-es
# carries the SAME token as the shipped champion's production stamp
# (`agents/tactical/learned/factory.py::CHAMPION_METHOD`) so one policy never
# wears two stamps.
_STAMP_FILENAME: str = "stamp.json"
_STAMP_FIELDS: frozenset[str] = frozenset(
    {"policy_id", "method", "encoder_version", "weights_sha256", "anchor_policy"}
)
_COMMITTED_STAMP_METHODS: dict[str, str] = {
    "bc-dagger": "bc-dagger",
    "utility-es": "utility-scorer-es",
    "policy-es": "policy-net-es",
    "map-elites": "map-elites",
}


def test_rerun_artifacts_carry_the_15_9_provenance_stamp() -> None:
    from agents.tactical.learned.factory import (
        CHAMPION_ANCHOR_POLICY,
        CHAMPION_METHOD,
        CHAMPION_POLICY_ID,
    )

    for row in _committed_bakeoff_rows():
        entrant = str(row["entrant"])
        stamp_path = _IMPOSTOR_ARTIFACT_ROOT / entrant / _STAMP_FILENAME
        stamp = json.loads(stamp_path.read_text())

        # Exactly the five 15.9 fields (orchestrator.replay.TacticalPolicyStamp's
        # shape), no extras, all plain strings.
        assert set(stamp) == _STAMP_FIELDS
        assert all(isinstance(value, str) for value in stamp.values())

        # The stamp names THIS candidate and closes against the committed bytes:
        # stamp sha == row sha == sidecar sha (test above), so a future harness
        # regeneration that moves the weights without refreshing the stamp trips
        # loudly here.
        assert stamp["policy_id"] == entrant
        assert stamp["method"] == _COMMITTED_STAMP_METHODS[entrant]
        assert stamp["encoder_version"] == row["encoder_version"]
        assert stamp["weights_sha256"] == row["weights_sha256"]
        assert stamp["anchor_policy"] == "fsm-default"

    # The utility-es stamp agrees field-for-field with the shipped champion's
    # production stamp constants — the 17.14 conflation guard: one policy, one
    # stamp, whether recorded through the champion factory or the finalist
    # recorder.
    utility_stamp = json.loads(
        (_IMPOSTOR_ARTIFACT_ROOT / "utility-es" / _STAMP_FILENAME).read_text()
    )
    assert utility_stamp["policy_id"] == CHAMPION_POLICY_ID
    assert utility_stamp["method"] == CHAMPION_METHOD
    assert utility_stamp["anchor_policy"] == CHAMPION_ANCHOR_POLICY


# --------------------------------------------------------------------------- #
# 10. The 18.16 conviction integration + anchor-policy seam.                   #
#                                                                              #
# The GO-gated additive conviction term, the referee pre-screen, and the      #
# additive anchor-policy seam. Fixture-pinned (a synthetic 3-row GO/NO-GO      #
# artifact under tmp_path) except where the DEFAULT protocol reads the         #
# committed artifact dir — those pin the committed GO sha literal below.       #
# --------------------------------------------------------------------------- #

# The committed conviction artifact sha (training/artifacts/conviction/), pinned
# as a literal so a re-ground that moves the weights trips the default-protocol
# row-stamp pins HERE (the committed GO verdict is keyed to exactly this).
_COMMITTED_CONVICTION_SHA256: str = (
    "4841f8e02eb7b587237c5b88bc2d350c12c7a5b5ac5c7ae1481069235c7b2a47"
)


def _fixture_features(values: Sequence[float]) -> dict[str, float]:
    """A per-meeting feature mapping over ``CONVICTION_FEATURE_NAMES`` (order set)."""

    return dict(zip(CONVICTION_FEATURE_NAMES, values, strict=True))


def _write_conviction_fixture(
    artifact_dir: Path, *, go: bool, max_uses: int = 50
) -> str:
    """Commit a synthetic 3-row conviction artifact + GO/NO-GO verdict; return sha.

    Three ``ConvictionMeetingRow`` rows (features keyed in
    ``CONVICTION_FEATURE_NAMES`` order — the validator checks it), fit and frozen
    exactly as the 18.15 corpus path does, then a directly-constructed
    :class:`ConvictionGoVerdict` keyed to the frozen sha — GO ⇒ ``fitness_term``
    "ships" / ``prescreen_role`` "gating"; NO-GO ⇒ "absent" / "advisory". The
    numbers below are synthetic (this fixture pins the INTEGRATION plumbing, not
    the model's held-out fidelity — that is ``training/conviction/``'s own suite).
    """

    rows = [
        ConvictionMeetingRow(
            seed=1,
            game_id="g1",
            meeting_id="m-1",
            meeting_index=1,
            tick=10,
            features=_fixture_features([3, 0, 0.1, 0.2, 0.0, 0, 0, 0, 0, 0, 0, 0]),
            flags_minted=0,
            rederived_flags=0,
            persisted_vent_flags=0,
            conversion_attempted=0,
            conversion_converted=0,
            testimony_backed_conversion=False,
            is_ejection=False,
            ceiling_reachable=False,
        ),
        ConvictionMeetingRow(
            seed=2,
            game_id="g2",
            meeting_id="m-2",
            meeting_index=2,
            tick=20,
            features=_fixture_features([5, 1, 0.8, 0.4, 0.3, 2, 1, 1, 0, 0, 1, 1]),
            flags_minted=2,
            rederived_flags=2,
            persisted_vent_flags=0,
            conversion_attempted=1,
            conversion_converted=1,
            testimony_backed_conversion=True,
            is_ejection=True,
            ceiling_reachable=True,
        ),
        ConvictionMeetingRow(
            seed=3,
            game_id="g3",
            meeting_id="m-3",
            meeting_index=3,
            tick=30,
            features=_fixture_features([7, 2, 0.6, 0.5, 0.1, 3, 0, 0, 2, 1, 0, 0]),
            flags_minted=5,
            rederived_flags=3,
            persisted_vent_flags=2,
            conversion_attempted=2,
            conversion_converted=0,
            testimony_backed_conversion=False,
            is_ejection=True,
            ceiling_reachable=False,
        ),
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


# The two feature mappings the term-in-fitness + pre-screen tests score.
_MEETING_A: dict[str, float] = _fixture_features(
    [4, 1, 0.5, 0.3, 0.2, 1, 0, 0, 1, 1, 0, 0]
)
_MEETING_B: dict[str, float] = _fixture_features(
    [6, 2, 0.7, 0.4, 0.1, 2, 1, 1, 0, 0, 1, 1]
)
_MEETING_C: dict[str, float] = _fixture_features(
    [2, 0, 0.1, 0.1, 0.0, 0, 0, 0, 0, 0, 0, 0]
)


# --------------------------------------------------------------------------- #
# The anchor-policy seam stubs (module-level; each a full BakeoffPolicy).       #
# --------------------------------------------------------------------------- #


class _DelegatingDistributionPolicy:
    """A candidate that DELEGATES to the FSM but reports a non-delta distribution.

    ``evaluate`` returns the FSM's own intent (so the game trajectory is the FSM
    delegate's, byte-identical to ``policy=None``), while ``choice_distribution``
    splits mass ``{fsm_key: 0.25, "wait": 0.75}`` — collapsing to ``{"wait":
    0.75}`` when the FSM's own key IS ``"wait"``. ``wait_tally`` counts the
    scored decisions whose FSM proposal was ``wait`` (the alternative-anchor test
    reads it to prove some FSM decisions were non-wait).
    """

    encoder_version: str = ENCODER_VERSION

    def __init__(self) -> None:
        self.wait_tally = 0

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(0.0,),
            logits=(0.0,),
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
        key = intent_key(fsm_intent)
        if key == "wait":
            self.wait_tally += 1
        return {key: 0.25, "wait": 0.75}


class _FsmDelegateAnchor:
    """An anchor policy that IS the scripted FSM proposal (evaluate → fsm_intent).

    Setting this as ``DecisionTrace.anchor_policy`` must be provably byte-
    identical to the default ``anchor_policy=None`` path (the seam defaults to
    the scripted FSM). Also serves as a deterministic FSM-delegate CANDIDATE.
    """

    encoder_version: str = ENCODER_VERSION

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(),
            logits=(),
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


class _AlwaysWaitAnchor:
    """An alternative anchor that always proposes ``wait`` (re-anchors the CE)."""

    encoder_version: str = ENCODER_VERSION

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(),
            logits=(),
            intent=WaitIntent(actor=packet.agent_id, type="wait"),
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


def _impostor_packet() -> ObservationPacket:
    """A minimal synthetic IMPOSTOR packet for the direct-record fail-loud test."""

    return ObservationPacket(
        tick=5,
        agent_id="p-1",
        self_state=SelfView(
            room="CAFETERIA",
            role="IMPOSTOR",
            pending_task_id=None,
            fellow_impostor_ids=("p-2",),
        ),
        visible_players=(PlayerView(id="p-3", room="CAFETERIA", action=None),),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=14,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=0,
    )


# --------------------------------------------------------------------------- #
# 10.2 GO/NO-GO term loading (fixture-pinned).                                  #
# --------------------------------------------------------------------------- #


def test_conviction_weight_is_conservative() -> None:
    # The task-hint conservatism pin: the conviction term ships at a weight at or
    # below the anchor penalty — the lambda tuning belongs to the campaign, not
    # this integration.
    assert DEFAULT_CONVICTION_WEIGHT <= DEFAULT_ANCHOR_PENALTY_WEIGHT


def test_load_conviction_term_under_go(tmp_path: Path) -> None:
    sha = _write_conviction_fixture(tmp_path, go=True)
    term = load_conviction_fitness_term(tmp_path)
    assert term is not None
    assert term.weight == DEFAULT_CONVICTION_WEIGHT
    assert term.weights_sha256 == sha
    # The counter the term will meter is keyed to the exact frozen artifact.
    assert term.use_counter.cap.weights_sha256 == sha
    assert term.verdict.fitness_term == "ships"


def test_load_conviction_term_under_nogo_is_structurally_absent(
    tmp_path: Path,
) -> None:
    _write_conviction_fixture(tmp_path, go=False)
    # STRUCTURAL absence: the loader returns None (no zero-weighted ghost).
    assert load_conviction_fitness_term(tmp_path) is None


def test_conviction_term_rejects_nogo_verdict(tmp_path: Path) -> None:
    sha = _write_conviction_fixture(tmp_path, go=False)
    model, loaded_sha = load_conviction_model_artifact(tmp_path)
    assert loaded_sha == sha
    verdict = load_conviction_verdict(tmp_path)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(tmp_path))
    # Direct construction with a NO-GO verdict can never build the term.
    with pytest.raises(ValueError, match="GO verdict"):
        ConvictionFitnessTerm(
            model=model,
            weights_sha256=sha,
            verdict=verdict,
            use_counter=counter,
        )


def test_conviction_bundle_drift_fails_loud(tmp_path: Path) -> None:
    _write_conviction_fixture(tmp_path, go=True)
    # Re-key the committed verdict to a DIFFERENT 64-hex sha: the loader's
    # bundle drift-check must fail loud (the verdict and weights drifted).
    drifted = load_conviction_verdict(tmp_path).model_copy(
        update={"weights_sha256": "0" * 64}
    )
    write_conviction_verdict_artifact(drifted, tmp_path)
    with pytest.raises(ValueError, match="drifted"):
        load_conviction_fitness_term(tmp_path)


# --------------------------------------------------------------------------- #
# 10.3 The term composes additively into the inner fitness (fixture-pinned).    #
# --------------------------------------------------------------------------- #


def test_conviction_term_in_inner_fitness(tmp_path: Path) -> None:
    _write_conviction_fixture(tmp_path, go=True)
    rollout_dir = tmp_path / "rollout"
    trace = DecisionTrace()
    rollout = rollout_candidate(None, 1004, output_dir=rollout_dir, trace=trace)
    assert rollout.complete  # the additive-composition identity needs a full game
    base = inner_episode_fitness(rollout, trace)

    term = load_conviction_fitness_term(tmp_path)
    assert term is not None
    uses_before = term.use_counter.uses
    for features in (_MEETING_A, _MEETING_B):
        trace.record_conviction_prediction(term.predict_meeting(features))

    # The counter advanced by exactly one use per predicted meeting.
    assert term.use_counter.uses - uses_before == 2

    # The composition is additive and EXACT: base (anchor-composed, conviction
    # absent) plus the weighted mean predicted supply.
    assert inner_episode_fitness(rollout, trace, conviction=term) == (
        base + term.weight * trace.mean_predicted_supply()
    )

    # The mean predicted supply is the flags head's supply score, recomputed via
    # a SECOND, unmetered model load (predict does not meter — the term does).
    unmetered, _ = load_conviction_model_artifact(tmp_path)
    expected = [
        unmetered.predict(features).expected_flags
        for features in (_MEETING_A, _MEETING_B)
    ]
    assert trace.mean_predicted_supply() == math.fsum(expected) / 2


def test_inner_fitness_has_no_ghost_term_when_conviction_none(tmp_path: Path) -> None:
    # Under NO-GO the ONLY possibility is conviction=None; the fitness is exactly
    # the inline anchor formula with no ghost conviction addend.
    rollout_dir = tmp_path / "rollout"
    policy = _DelegatingDistributionPolicy()
    trace = DecisionTrace()
    rollout = rollout_candidate(policy, 1004, output_dir=rollout_dir, trace=trace)
    assert rollout.complete
    expected = (
        compute_shaped_reward(rollout, "IMPOSTOR").total()
        - DEFAULT_ANCHOR_PENALTY_WEIGHT * trace.mean_anchor_ce()
    )
    assert inner_episode_fitness(rollout, trace) == expected


# --------------------------------------------------------------------------- #
# 10.4 One shared counter threads the cumulative staleness cap.                 #
# --------------------------------------------------------------------------- #


def test_shared_counter_threads_the_cumulative_cap(tmp_path: Path) -> None:
    _write_conviction_fixture(tmp_path, go=True, max_uses=3)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(tmp_path))
    term = load_conviction_fitness_term(tmp_path, use_counter=counter)
    assert term is not None

    # Two predicted meetings through the term, then the third use through the
    # pre-screen — the SAME counter, cumulative against the committed cap.
    term.predict_meeting(_MEETING_A)
    term.predict_meeting(_MEETING_B)
    conviction_prescreen([_MEETING_C], artifact_dir=tmp_path, use_counter=counter)
    assert counter.uses == 3

    # A fourth use — either path — trips the staleness cap.
    with pytest.raises(ConvictionStalenessExceededError):
        term.predict_meeting(_MEETING_A)


def test_shared_counter_rejects_wrong_sha_and_looser_cap(tmp_path: Path) -> None:
    sha = _write_conviction_fixture(tmp_path, go=True, max_uses=3)

    # A counter keyed on a DIFFERENT sha never meters this artifact.
    wrong_sha = ConvictionUseCounter(
        ConvictionStalenessCap(weights_sha256="0" * 64, max_uses=3, unit="meetings")
    )
    with pytest.raises(ValueError, match="never meters two artifacts"):
        load_conviction_fitness_term(tmp_path, use_counter=wrong_sha)

    # A supplied counter may TIGHTEN the committed cap, never LOOSEN it.
    looser = ConvictionUseCounter(
        ConvictionStalenessCap(weights_sha256=sha, max_uses=4, unit="meetings")
    )
    with pytest.raises(ValueError, match="never loosen"):
        load_conviction_fitness_term(tmp_path, use_counter=looser)


# --------------------------------------------------------------------------- #
# 10.5 The additive anchor-policy seam.                                         #
# --------------------------------------------------------------------------- #


def test_anchor_seam_fsm_delegate_is_byte_identical(tmp_path: Path) -> None:
    default_trace = DecisionTrace()
    default_rollout = rollout_candidate(
        _DelegatingDistributionPolicy(),
        1004,
        output_dir=tmp_path / "default",
        trace=default_trace,
    )
    fsm_trace = DecisionTrace(anchor_policy=_FsmDelegateAnchor())
    fsm_rollout = rollout_candidate(
        _DelegatingDistributionPolicy(),
        1004,
        output_dir=tmp_path / "fsm",
        trace=fsm_trace,
    )

    # The seam defaults to the scripted FSM: an explicit FSM-delegate anchor is
    # provably byte-identical (==) to anchor_policy=None on every scored number.
    assert default_trace.anchor_ce_sum == fsm_trace.anchor_ce_sum
    assert default_trace.offmenu_decisions == fsm_trace.offmenu_decisions
    assert default_trace.agreement_hits == fsm_trace.agreement_hits
    assert inner_episode_fitness(default_rollout, default_trace) == (
        inner_episode_fitness(fsm_rollout, fsm_trace)
    )


def test_anchor_seam_alternative_anchor_rekeys_ce_not_agreement(
    tmp_path: Path,
) -> None:
    fsm_trace = DecisionTrace(anchor_policy=_FsmDelegateAnchor())
    rollout_candidate(
        _DelegatingDistributionPolicy(),
        1004,
        output_dir=tmp_path / "fsm",
        trace=fsm_trace,
    )
    wait_candidate = _DelegatingDistributionPolicy()
    wait_trace = DecisionTrace(anchor_policy=_AlwaysWaitAnchor())
    wait_rollout = rollout_candidate(
        wait_candidate,
        1004,
        output_dir=tmp_path / "wait",
        trace=wait_trace,
    )
    assert wait_rollout.complete
    assert wait_trace.scored_decisions > 0

    # Under the always-wait anchor every scored decision keys on the "wait" mass
    # (0.75, merged or not), so the CE is scored_decisions × -log(0.75) EXACTLY
    # (reproduced by summing the identical addend in a loop).
    reproduced = 0.0
    for _ in range(wait_trace.scored_decisions):
        reproduced += -math.log(0.75)
    assert wait_trace.anchor_ce_sum == reproduced
    assert wait_trace.offmenu_decisions == 0

    # Some FSM decisions were non-wait (scored > the wait tally), so the re-keyed
    # CE genuinely DIFFERS from the FSM-anchored run's.
    assert wait_trace.scored_decisions > wait_candidate.wait_tally
    assert wait_trace.anchor_ce_sum != fsm_trace.anchor_ce_sum

    # Agreement stays FSM-keyed regardless of the anchor policy — it must not
    # silently re-anchor onto the alternative.
    assert wait_trace.agreement_hits == fsm_trace.agreement_hits

    # The fitness delta is exactly the anchor-penalty term's re-keyed difference
    # (same rollout ⇒ the shaped reward cancels bit-for-bit).
    assert inner_episode_fitness(wait_rollout, wait_trace) - inner_episode_fitness(
        wait_rollout, fsm_trace
    ) == -DEFAULT_ANCHOR_PENALTY_WEIGHT * (
        wait_trace.mean_anchor_ce() - fsm_trace.mean_anchor_ce()
    )


def test_anchor_seam_requires_public_map_and_memory() -> None:
    # An alternative anchor policy needs the map + memory to evaluate; record()
    # fails loud when they are omitted (never a silent skip of the re-anchor).
    trace = DecisionTrace(anchor_policy=_AlwaysWaitAnchor())
    wait = WaitIntent(actor="p-1", type="wait")
    with pytest.raises(ValueError, match="anchor_policy"):
        trace.record(
            _impostor_packet(),
            fsm_intent=wait,
            chosen=wait,
            distribution=None,
        )


# --------------------------------------------------------------------------- #
# 10.6 The referee pre-screen (fixture-pinned).                                 #
# --------------------------------------------------------------------------- #


def test_conviction_prescreen_under_go(tmp_path: Path) -> None:
    sha = _write_conviction_fixture(tmp_path, go=True)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(tmp_path))
    features = [_MEETING_A, _MEETING_B, _MEETING_C]
    verdict = conviction_prescreen(features, artifact_dir=tmp_path, use_counter=counter)

    assert verdict.weights_sha256 == sha
    assert verdict.meetings_scored == 3
    assert verdict.conviction_uses == 3

    # The predicted flags density is the unmetered recompute's fsum mean (exact).
    unmetered, _ = load_conviction_model_artifact(tmp_path)
    expected_flags = [unmetered.predict(f).expected_flags for f in features]
    assert verdict.predicted_flags_per_meeting == math.fsum(expected_flags) / 3

    # The floors are the committed baseline-6 pins consumed as NUMBERS. The
    # conversion anchor is the PER-MEETING unit (the model's native label unit;
    # the referee's converted/attempted pair gauge is structurally not
    # predictable): the pair pin's numerator (78 converted backed accusations —
    # one ejection per meeting, so 78 converting meetings) over the same
    # committed 165-meeting census the flags floor reads.
    assert verdict.flags_floor == PRESCREEN_FLAGS_PER_MEETING_FLOOR == 180 / 165
    assert verdict.conversion_pin == PRESCREEN_CONVERSION_PIN == 78 / 165

    # The conversion floor derives population-relative from the PREDICTED flags
    # density via the public eval.watchability derivation.
    assert verdict.conversion_floor == population_relative_conversion_floor(
        pinned_conversion=78 / 165,
        pinned_flags_per_meeting=180 / 165,
        measured_flags_per_meeting=verdict.predicted_flags_per_meeting,
    )

    # The expected converting share (mean conversion probability) is REPORTED
    # beside the thresholded channel — the exact unmetered-recompute mean —
    # and is never a pass input (the pass bits below read only the thresholded
    # share): the gated channel stays the pinned-threshold call, the model's
    # only verdict-validated operating point.
    conversion_probs = [unmetered.predict(f).conversion_prob for f in features]
    assert verdict.predicted_mean_conversion_prob == math.fsum(conversion_probs) / 3

    # The pass bits are the literal comparisons and the verdict is their AND.
    assert verdict.predicted_flags_pass == (
        verdict.predicted_flags_per_meeting >= verdict.flags_floor
    )
    assert verdict.predicted_conversion_pass == (
        verdict.predicted_converting_share >= verdict.conversion_floor
    )
    assert verdict.predicted_floors_pass == (
        verdict.predicted_flags_pass and verdict.predicted_conversion_pass
    )

    # Under GO the pre-screen GATES (advisory_only is False).
    assert verdict.model_verdict == "GO"
    assert verdict.prescreen_role == "gating"
    assert verdict.advisory_only is False


def test_conviction_prescreen_under_nogo_is_advisory_only(tmp_path: Path) -> None:
    _write_conviction_fixture(tmp_path, go=False)
    verdict = conviction_prescreen([_MEETING_A], artifact_dir=tmp_path)
    # Advisory-only doctrine: a driver must never gate real-path spend on it.
    assert verdict.model_verdict == "NO-GO"
    assert verdict.prescreen_role == "advisory"
    assert verdict.advisory_only is True


def test_conviction_prescreen_empty_batch_is_the_starvation_fail(
    tmp_path: Path,
) -> None:
    # An empty batch is the evidence-STARVATION verdict, not an exception (the
    # referee's own doctrine: starvation is not a pass —
    # eval/watchability.py::evaluate_supply_floors): the driver gets a
    # machine-readable FAILING verdict it can cheaply reject on.
    sha = _write_conviction_fixture(tmp_path, go=True)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(tmp_path))
    verdict = conviction_prescreen([], artifact_dir=tmp_path, use_counter=counter)

    assert verdict.weights_sha256 == sha
    assert verdict.meetings_scored == 0
    # Nothing was predicted, so nothing was metered.
    assert verdict.conviction_uses == 0
    assert counter.uses == 0
    # Every predicted channel reads 0.0 and the derived conversion demand is
    # the maximal 1.0 (the population_relative_conversion_floor starvation
    # shape); both floors FAIL unconditionally.
    assert verdict.predicted_flags_per_meeting == 0.0
    assert verdict.predicted_converting_share == 0.0
    assert verdict.predicted_mean_conversion_prob == 0.0
    assert verdict.conversion_floor == 1.0
    assert verdict.predicted_flags_pass is False
    assert verdict.predicted_conversion_pass is False
    assert verdict.predicted_floors_pass is False
    # The role fields still ride the committed verdict (GO fixture: gating).
    assert verdict.prescreen_role == "gating"
    assert verdict.advisory_only is False


# --------------------------------------------------------------------------- #
# 10.7 The row stamps the conviction provenance triple.                         #
# --------------------------------------------------------------------------- #


def test_evaluate_candidate_row_says_absent_under_nogo(tmp_path: Path) -> None:
    conviction_dir = tmp_path / "conviction-nogo"
    sha = _write_conviction_fixture(conviction_dir, go=False)
    candidate = TrainedCandidate(
        entrant="nogo-row-probe",
        policy=_FsmDelegateAnchor(),
        weights=(0.0,),
        config={"entrant": "nogo-row-probe"},
    )
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        repeat_n=2,
        surrogate_artifact_dir=None,
        conviction_artifact_dir=conviction_dir,
    )
    result = evaluate_candidate(candidate, protocol, artifact_root=tmp_path)

    # The row says the term is STRUCTURALLY absent: "absent", weight None, and
    # the sha still keys to the (diagnostic-only) instrument the rows describe.
    assert result.conviction_fitness_term == "absent"
    assert result.conviction_weight is None
    assert result.conviction_weights_sha256 == sha


# --------------------------------------------------------------------------- #
# 10.8 Review hardening: delivered-use metering + drift-checked row stamping.  #
# --------------------------------------------------------------------------- #


def test_conviction_uses_charge_only_delivered_predictions(tmp_path: Path) -> None:
    # The cap's pinned unit is a DELIVERED prediction (PR #304 review): a
    # malformed feature mapping fail-louds out of the model without burning
    # quota, on both the term path and the pre-screen path.
    _write_conviction_fixture(tmp_path, go=True)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(tmp_path))
    term = load_conviction_fitness_term(tmp_path, use_counter=counter)
    assert term is not None

    malformed = dict(_MEETING_A)
    del malformed["alive_count"]
    with pytest.raises(ValueError, match="CONVICTION_FEATURE_NAMES"):
        term.predict_meeting(malformed)
    assert counter.uses == 0  # the failed prediction charged nothing

    term.predict_meeting(_MEETING_A)
    assert counter.uses == 1  # the delivered prediction charged exactly one

    # Mid-batch pre-screen failure: the completed prediction stays charged,
    # the malformed one does not, and no verdict is emitted.
    with pytest.raises(ValueError, match="CONVICTION_FEATURE_NAMES"):
        conviction_prescreen(
            [_MEETING_B, malformed], artifact_dir=tmp_path, use_counter=counter
        )
    assert counter.uses == 2


def test_evaluate_candidate_rejects_drifted_conviction_bundle(tmp_path: Path) -> None:
    # Row provenance must describe a bundle a trainer could actually LOAD: a
    # partially-updated artifact dir (verdict re-keyed off the weights) fails
    # the eval BEFORE any side effects instead of stamping stale rows.
    conviction_dir = tmp_path / "conviction-drifted"
    _write_conviction_fixture(conviction_dir, go=True)
    drifted = load_conviction_verdict(conviction_dir).model_copy(
        update={"weights_sha256": "0" * 64}
    )
    write_conviction_verdict_artifact(drifted, conviction_dir)
    candidate = TrainedCandidate(
        entrant="drift-row-probe",
        policy=_FsmDelegateAnchor(),
        weights=(0.0,),
        config={"entrant": "drift-row-probe"},
    )
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        surrogate_artifact_dir=None,
        conviction_artifact_dir=conviction_dir,
    )
    with pytest.raises(ValueError, match="drifted"):
        evaluate_candidate(candidate, protocol, artifact_root=tmp_path)


# --------------------------------------------------------------------------- #
# 10.9 The eval loops serve the term LIVE (Task 18.30).                          #
# --------------------------------------------------------------------------- #


def test_evaluate_candidate_go_serves_the_term_live(tmp_path: Path) -> None:
    """Under the committed GO verdict the eval pass serves the term live.

    The default protocol reads the committed conviction dir, so the row stamps a
    non-None predicted-meeting count and a composed mean supply (rows say so),
    and ``inner_fitness_real`` differs from the same candidate's NO-GO run by
    EXACTLY the weighted mean supply — the served rollout observes only, so the
    two trajectories are byte-identical and the conviction addend is the only
    difference (single seed ⇒ set-level fitness == the episode fitness).
    """

    genome = _forced_kill_genome()
    policy = policy_es.build_masked_mlp_policy(genome, hidden=8)
    candidate = TrainedCandidate(
        entrant="live-go-probe",
        policy=policy,
        weights=genome,
        config={
            "entrant": "live-go-probe",
            "hidden": 8,
            "encoder_version": policy.encoder_version,
        },
    )
    # GO: the committed conviction dir is the default — the loop serves it live.
    go_protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        surrogate_artifact_dir=None,
    )
    go_row = evaluate_candidate(candidate, go_protocol, artifact_root=tmp_path / "go")

    # NO-GO: a fixture dir keyed into the protocol — structural absence, no
    # wrapper, no fitness addend.
    nogo_dir = tmp_path / "conviction-nogo"
    _write_conviction_fixture(nogo_dir, go=False)
    nogo_protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        surrogate_artifact_dir=None,
        conviction_artifact_dir=nogo_dir,
    )
    nogo_row = evaluate_candidate(
        candidate, nogo_protocol, artifact_root=tmp_path / "nogo"
    )

    # Rows say so: GO carries the live term, a real predicted-meeting count, and
    # the composed mean supply; NO-GO leaves all three structurally absent.
    assert go_row.conviction_fitness_term == "ships"
    assert go_row.conviction_weight == DEFAULT_CONVICTION_WEIGHT
    assert go_row.conviction_meetings_predicted is not None
    assert go_row.conviction_meetings_predicted > 0
    assert go_row.conviction_mean_predicted_supply is not None

    assert nogo_row.conviction_fitness_term == "absent"
    assert nogo_row.conviction_weight is None
    assert nogo_row.conviction_meetings_predicted is None
    assert nogo_row.conviction_mean_predicted_supply is None

    # The honest composition: the ONLY difference between the GO and NO-GO eval
    # fitness is the weighted mean predicted supply (exact ==, not approx — the
    # wrapper never mutates state, so the trajectories are byte-identical).
    assert go_row.inner_fitness_real == (
        nogo_row.inner_fitness_real
        + DEFAULT_CONVICTION_WEIGHT * go_row.conviction_mean_predicted_supply
    )


def test_evaluate_candidate_nogo_is_structural_absence(tmp_path: Path) -> None:
    """Under a NO-GO fixture the eval fitness is the pre-threading anchor value.

    The term is None everywhere: the row says absent, both liveness columns stay
    None (no zero-weighted ghost), and ``inner_fitness_real`` equals the
    anchor-composed value recomputed from an independent unwrapped rollout of the
    same seed.
    """

    genome = _forced_kill_genome()
    policy = policy_es.build_masked_mlp_policy(genome, hidden=8)
    candidate = TrainedCandidate(
        entrant="live-nogo-probe",
        policy=policy,
        weights=genome,
        config={
            "entrant": "live-nogo-probe",
            "hidden": 8,
            "encoder_version": policy.encoder_version,
        },
    )
    nogo_dir = tmp_path / "conviction-nogo"
    _write_conviction_fixture(nogo_dir, go=False)
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        surrogate_artifact_dir=None,
        conviction_artifact_dir=nogo_dir,
    )
    row = evaluate_candidate(candidate, protocol, artifact_root=tmp_path / "eval")

    assert row.conviction_fitness_term == "absent"
    assert row.conviction_weight is None
    assert row.conviction_meetings_predicted is None
    assert row.conviction_mean_predicted_supply is None

    # The NO-GO eval fitness is exactly the pre-threading anchor-composed value:
    # recompute it from an independent, unwrapped rollout of the same seed/roster.
    trace = DecisionTrace()
    rollout = rollout_candidate(
        policy, 1004, output_dir=tmp_path / "recompute", trace=trace
    )
    assert row.inner_fitness_real == inner_episode_fitness(rollout, trace)


def test_prescreen_accepts_live_assembled_vectors_end_to_end(tmp_path: Path) -> None:
    """The pre-screen consumes live-assembled vectors end-to-end (the DoD).

    One fake-path rollout is wrapped in a
    :class:`ConvictionServingMeetingRunner` that both meters the term and
    collects each assembled feature mapping; the pre-screen then scores those
    live vectors, metering the SAME cumulative counter — one delivered use per
    meeting.
    """

    go_dir = tmp_path / "conviction-go"
    sha = _write_conviction_fixture(go_dir, go=True, max_uses=500)
    counter = ConvictionUseCounter(load_conviction_staleness_cap(go_dir))
    term = load_conviction_fitness_term(go_dir, use_counter=counter)
    assert term is not None

    collected: list[Mapping[str, float]] = []
    trace = DecisionTrace()

    def factory() -> MeetingRunner:
        inner = build_default_meeting_runner(
            llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
        )
        return ConvictionServingMeetingRunner(
            inner=inner,
            predict=term.predict_meeting,
            record=trace.record_conviction_prediction,
            on_features=collected.append,
        )

    policy = policy_es.build_masked_mlp_policy(_forced_kill_genome(), hidden=8)
    rollout_candidate(
        policy,
        1004,
        output_dir=tmp_path / "rollout",
        meeting_runner_factory=factory,
        trace=trace,
    )

    # The serving wrapper assembled one live vector per meeting and metered one
    # use each; every vector carries exactly the fenced feature set.
    assert len(collected) > 0
    assert trace.conviction_meetings == len(collected)
    assert counter.uses == len(collected)
    for features in collected:
        assert set(features) == set(CONVICTION_FEATURE_NAMES)

    # The pre-screen consumes the live-assembled vectors end-to-end, metering the
    # SAME cumulative counter (one delivered use per meeting scored).
    uses_before = counter.uses
    verdict = conviction_prescreen(collected, artifact_dir=go_dir, use_counter=counter)
    assert verdict.meetings_scored == len(collected)
    assert verdict.conviction_uses == len(collected)
    assert counter.uses == uses_before + len(collected)
    assert verdict.weights_sha256 == sha
    assert verdict.model_verdict == "GO"
    assert verdict.prescreen_role == "gating"
    assert verdict.predicted_flags_per_meeting >= 0.0


def test_harness_surrogate_loads_always_wire_the_corpus_fingerprint_fence() -> None:
    """Every harness-side surrogate load passes ``corpus_dir`` (the 18.14 fence).

    The fit-corpus fingerprint check in
    :func:`training.surrogate.runner.load_surrogate_runner_factory` is opt-in
    by keyword; the held PR #303 review thread routed the once-per-run wiring
    to the harness. This AST pin keeps it wired: a future call site that drops
    the keyword re-opens the fence's weaker half silently, so it fails here
    loudly instead.
    """

    import training.bakeoff.harness as harness_module

    source = Path(harness_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    call_sites = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (
            (
                isinstance(node.func, ast.Name)
                and node.func.id == "load_surrogate_runner_factory"
            )
            or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "load_surrogate_runner_factory"
            )
        )
    ]
    assert call_sites, "expected at least one harness surrogate load call site"
    for node in call_sites:
        keywords = {keyword.arg for keyword in node.keywords}
        assert "corpus_dir" in keywords, (
            f"harness.py:{node.lineno} calls load_surrogate_runner_factory "
            "without the corpus_dir fingerprint fence"
        )
