"""Normal-policy measurements refuse missing, relabeled or unowned evidence."""

from __future__ import annotations

from pathlib import Path

import pytest

from experiments import investigation_evaluation as evaluation
from experiments.deduction_evaluation import source_hashes

ROOT = Path(__file__).resolve().parents[2]


def test_real_matrix_keeps_component_costs_and_old_follow_control(
    tmp_path: Path,
) -> None:
    result = evaluation.evaluate(tmp_path / "capture", root=ROOT)
    assert len(result.captures) == 35
    assert all(row.outcome_verified for row in result.captures)
    indexed = {(row.arm, row.definition.seed): row for row in result.captures}
    assert indexed[("search", 6)].plans
    assert (
        indexed[("search", 6)].body_report_ticks[0]
        < indexed[("off", 6)].body_report_ticks[0]
    )
    assert indexed[("contextual_self_report", 1)].impostor_report_ticks
    assert indexed[("unconditional_self_report", 0)].impostor_report_ticks
    assert any(row.reference == "old_patrol" for row in result.comparisons)
    assert all(row.wrongful_accusations == 0 for row in result.captures)
    assert result.verdict == "MECHANICS_ONLY"
    # A changed discarded attempt must not masquerade as a changed game.
    contextual_zero = next(
        r
        for r in result.comparisons
        if r.arm == "contextual_self_report" and r.case == "five-player-seed-0"
    )
    assert contextual_zero.changed_submitted_actions
    assert not contextual_zero.changed_trajectory
    reference = indexed[("off", 0)]
    discarded_only = reference.model_copy(
        update={"arm": "perturbed", "submitted_actions_sha256": "changed-attempt"}
    )
    paired = evaluation.compare_pair(reference, discarded_only)
    assert paired.changed_submitted_actions and not paired.changed_trajectory
    saved = (tmp_path / "capture" / "evaluation.json").read_bytes()
    with pytest.raises(FileExistsError):
        evaluation.evaluate(tmp_path / "capture", root=ROOT)
    assert (tmp_path / "capture" / "evaluation.json").read_bytes() == saved
    with pytest.raises(ValueError, match="complete frozen matrix"):
        evaluation.paired_comparisons(
            result.captures[:-1], arms=result.arms, definitions=result.definitions
        )
    changed = result.captures[0].model_copy(
        update={"definition": result.definitions[1]}
    )
    with pytest.raises(ValueError, match="frozen input identity"):
        evaluation.paired_comparisons(
            (changed, *result.captures[1:]),
            arms=result.arms,
            definitions=result.definitions,
        )


def test_source_drift_keeps_partial_bytes_without_a_success_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = source_hashes
    reads = 0

    def changed(root: Path) -> dict[str, str]:
        nonlocal reads
        reads += 1
        result = original(root)
        if reads > 1:
            result["agents/tactical/investigation.py"] = "planted-change"
        return result

    arms, definitions = evaluation.comparison_arms(), evaluation.development_cases()
    monkeypatch.setattr(evaluation, "comparison_arms", lambda: arms[:1])
    monkeypatch.setattr(evaluation, "development_cases", lambda: definitions[:1])
    monkeypatch.setattr(evaluation, "source_hashes", changed)
    with pytest.raises(ValueError, match="sources changed"):
        evaluation.evaluate(tmp_path / "capture", root=ROOT)
    assert not (tmp_path / "capture" / "evaluation.json").exists()
    assert list((tmp_path / "capture").rglob("replay-seed-*.jsonl"))


def test_foreign_and_future_plan_sources_fail_actual_record_check(
    tmp_path: Path,
) -> None:
    arm = next(a for a in evaluation.comparison_arms() if a.name == "search")
    case = next(d for d in evaluation.development_cases() if d.seed == 6)
    capture = evaluation.run_case(tmp_path / "real", definition=case, arm=arm)
    result = evaluation.measure_capture(capture)
    row = result.plans[0]
    evaluation.validate_plan_sources(capture, (row,))
    foreign = row.model_copy(update={"observer_id": "unseen-observer"})
    with pytest.raises(ValueError, match="not owned"):
        evaluation.validate_plan_sources(capture, (foreign,))
    future = row.model_copy(
        update={
            "plan": row.plan.model_copy(
                update={"source_tick": row.plan.decision_tick + 1}
            )
        }
    )
    with pytest.raises(ValueError, match="actual source and bounds"):
        evaluation.validate_plan_sources(capture, (future,))
    wrong_citation = row.model_copy(
        update={
            "plan": row.plan.model_copy(
                update={"source_observation_id": "foreign-private-citation"}
            )
        }
    )
    with pytest.raises(ValueError, match="exact observation of its owner"):
        evaluation.validate_plan_sources(capture, (wrong_citation,))
