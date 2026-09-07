"""Real finite controls plus deliberate source, identity and channel failures."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path
from typing import Literal

import pytest

import experiments.deduction_evaluation as evaluation
from experiments.deduction_scenarios import (
    ScenarioCase,
    ScenarioCapture,
    run_case,
    scenario_definition,
)
from orchestrator.experiment_config import RecordedExperimentConfig


ROOT = Path(__file__).resolve().parents[2]


def test_real_matrix_records_mechanics_without_a_quality_claim(tmp_path: Path) -> None:
    destination = tmp_path / "matrix"
    result = evaluation.evaluate(destination, root=ROOT)
    assert result.verdict == "MECHANICS_ONLY"
    assert len(result.captures) == 42
    assert len(result.comparisons) == 5
    assert all(row.provenance.agent_factory_kind == "custom" for row in result.captures)
    assert all(row.outcome_verified for row in result.captures)
    assert all(row.ballots == row.voluntary_skips for row in result.captures)
    assert all(
        row.correct_ejections == row.wrongful_ejections == 0 for row in result.captures
    )
    assert all(
        row.changed_trajectories == 0 and row.paired_cases == 7
        for row in result.comparisons
    )
    reply = result.comparisons[-1]
    assert (reply.additional_reply_turns, reply.additional_calls) == (1, 1)
    indexed = {(row.arm, row.case): row for row in result.captures}
    assert indexed[("repaired_clock", "witnessed_vent")].role_proof_flags > 0
    assert indexed[("attributed_testimony", "witnessed_vent")].role_proof_flags == 0
    assert indexed[("combined_accounts", "impossible_account")].own_evidence_context
    assert all(
        len(row.reader_projection_sha256) == len(row.memory_projection_sha256) == 64
        for row in result.captures
    )
    for name, digest in result.artifact_hashes.items():
        assert hashlib.sha256((destination / name).read_bytes()).hexdigest() == digest
    saved = evaluation.DeductionEvaluation.model_validate_json(
        (destination / "evaluation.json").read_text()
    )
    assert saved == result
    with pytest.raises(FileExistsError):
        evaluation.evaluate(destination, root=ROOT)
    assert (
        evaluation.DeductionEvaluation.model_validate_json(
            (destination / "evaluation.json").read_text()
        )
        == result
    )
    with pytest.raises(ValueError, match="complete frozen"):
        evaluation.paired_comparisons(
            result.captures[:-1], arms=result.arms, definitions=result.definitions
        )
    changed = result.captures[0].model_copy(
        update={"definition_sha256": "different-inputs"}
    )
    with pytest.raises(ValueError, match="paired scenario inputs"):
        evaluation.paired_comparisons(
            (changed, *result.captures[1:]),
            arms=result.arms,
            definitions=result.definitions,
        )


def test_source_drift_keeps_partial_evidence_without_publishing_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = evaluation.source_hashes
    reads = 0

    def changing(root: Path) -> dict[str, str]:
        nonlocal reads
        reads += 1
        hashes = original(root)
        if reads > 1:
            hashes["observation/temporal.py"] = "planted-change"
        return hashes

    arms = evaluation.comparison_arms()
    monkeypatch.setattr(evaluation, "comparison_arms", lambda: arms[:1])
    monkeypatch.setattr(evaluation, "scenario_cases", lambda: ("honest",))
    monkeypatch.setattr(evaluation, "source_hashes", changing)
    destination = tmp_path / "changed"
    with pytest.raises(ValueError, match="sources changed"):
        evaluation.evaluate(destination, root=ROOT)
    assert list(destination.rglob("replay-seed-1.jsonl"))
    assert not (destination / "evaluation.json").exists()


@pytest.mark.parametrize("channel", ["kill", "vent"])
def test_planted_firsthand_evidence_refuses_a_deduction_label(channel: str) -> None:
    evaluation.validate_channels("honest", kills=0, vents=0)
    with pytest.raises(ValueError, match="deduction case contains"):
        evaluation.validate_channels(
            "honest", kills=int(channel == "kill"), vents=int(channel == "vent")
        )


def test_missing_direct_control_is_not_a_passing_empty_gate() -> None:
    evaluation.validate_channels("witnessed_vent", kills=0, vents=1)
    with pytest.raises(ValueError, match="expected evidence channel"):
        evaluation.validate_channels("witnessed_vent", kills=0, vents=0)


def test_wrong_arm_cannot_relabel_an_actual_recording(tmp_path: Path) -> None:
    actual = evaluation.comparison_arms()[1]
    wrong = evaluation.comparison_arms()[2]
    capture = run_case(
        tmp_path,
        case="honest",
        experiment_config=actual.experiment_config,
        temporal_version=actual.temporal_version,
    )
    with pytest.raises(ValueError, match="identity disagrees"):
        evaluation.measure_capture(capture, arm=wrong, output_dir=tmp_path)


def test_empty_matrix_cannot_publish_passing_empty_comparisons() -> None:
    with pytest.raises(ValueError, match="complete frozen"):
        evaluation.paired_comparisons(
            (),
            arms=evaluation.comparison_arms(),
            definitions=tuple(
                scenario_definition(case) for case in evaluation.scenario_cases()
            ),
        )


def test_existing_roster_is_not_overwritten_by_measurement(tmp_path: Path) -> None:
    arm = evaluation.comparison_arms()[1]
    capture = run_case(tmp_path, case="honest", experiment_config=arm.experiment_config)
    path = tmp_path / "roster.json"
    original = b'{"num_players":99,"num_impostors":1,"tasks_per_crewmate":1}\n'
    path.write_bytes(original)
    with pytest.raises(ValueError, match="existing scenario roster"):
        evaluation.measure_capture(capture, arm=arm, output_dir=tmp_path)
    assert path.read_bytes() == original


def test_changed_scenario_definition_cannot_publish_a_frozen_input_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = run_case

    def changed(
        output_dir: Path,
        *,
        case: ScenarioCase,
        experiment_config: RecordedExperimentConfig,
        temporal_version: Literal[1, 2] | None = 2,
    ) -> ScenarioCapture:
        capture = original(
            output_dir,
            case=case,
            experiment_config=experiment_config,
            temporal_version=temporal_version,
        )
        return replace(
            capture,
            definition=capture.definition.model_copy(
                update={"information_limit": "planted unregistered input change"}
            ),
        )

    monkeypatch.setattr(evaluation, "run_case", changed)
    destination = tmp_path / "changed-input"
    with pytest.raises(ValueError, match="scenario inputs changed"):
        evaluation.evaluate(destination, root=ROOT)
    assert list(destination.rglob("replay-seed-1.jsonl"))
    assert not (destination / "evaluation.json").exists()
