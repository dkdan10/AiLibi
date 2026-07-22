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
import inspect
import json
from collections.abc import Mapping
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
from training.bakeoff.goodhart import run_goodhart_probe
from training.bakeoff.harness import (
    ANCHOR_CE_CEILING,
    BAKEOFF_BASELINE_ID,
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
