"""Tests for the Task 5.8 prompt regression suite (DESIGN.md §11.3).

This task IS the Phase 5 close gate, so these tests do two things:

* **Exact-match the frozen baseline.** Recorded fixtures + pure analyzers +
  deterministically-derived roles give byte-stable metric scalars, so the
  computed summary must equal the committed ``baseline.json`` exactly. A
  mismatch is a real metric / loader / schema regression. (The ``> X%``
  tolerance is the *manual* real-provider re-record policy, exercised by
  :func:`test_delta_exceeds_manual_real_provider_tolerance`, not CI's gate.)

* **Demonstrate the prompt-change -> metric-diff loop.** Two fixture sets —
  ``v_a`` (recorded 9p/2i canonical-set replays, seeds 2/6/26) and a variant
  ``v_b`` whose ``impostor_report`` template is bumped one step (``v3 -> v4``)
  and whose recorded meeting gains an ``alibi_conflict`` naming the impostor —
  produce a measurable, attributable delta in the alibi-fabrication survival
  rate. The suite detects the delta and attributes it to the one changed
  template via the per-version provenance.

The fixtures are 9p/2i games (DESIGN.md §3.5), so every role derivation runs
at the canonical roster via :func:`_run_fixture` — the Task 8.12 roster thread
through :func:`run_prompt_regression`.

No network, no live or fake model: every number comes from the recorded
fixtures, so ``AILIBI_LLM_PROVIDER`` is irrelevant
(:func:`test_no_provider_invoked_regardless_of_env`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval.prompt_regression import (
    REAL_PROVIDER_REGRESSION_TOLERANCE,
    PromptRegressionSummary,
    run_prompt_regression,
)
from llm.provider import ENV_PROVIDER

_FIXTURE_ROOT = Path("tests/fixtures/prompt_regression")
_BASELINE_PATH = _FIXTURE_ROOT / "baseline.json"

# The committed fixtures are copies of canonical-set replays recorded at the
# 9p/2i roster (Task 8.12), so role derivation must run at that roster.


def _run_fixture(fixture: str) -> PromptRegressionSummary:
    """Run the suite over one committed fixture at the canonical 9p/2i roster."""

    return run_prompt_regression(
        _FIXTURE_ROOT / fixture,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )


def _load_baseline() -> dict[str, PromptRegressionSummary]:
    """Parse the committed baseline into expected summaries, keyed by fixture."""

    raw = json.loads(_BASELINE_PATH.read_text())
    return {
        name: PromptRegressionSummary.model_validate(payload)
        for name, payload in raw.items()
    }


@pytest.mark.parametrize("fixture", ["v_a", "v_b"])
def test_summary_matches_committed_baseline_exactly(fixture: str) -> None:
    """The computed summary equals the frozen baseline EXACTLY (CI gate).

    Pydantic value equality compares every scalar exactly (floats included);
    because the fixtures are recorded and the analyzers are pure, any drift here
    is a real regression in a metric, the loader, or the report schema.
    """

    expected = _load_baseline()[fixture]
    actual = _run_fixture(fixture)
    assert actual == expected


def test_close_gate_prompt_change_moves_metric_and_attributes_to_template() -> None:
    """A prompt-template change produces a measurable, attributable metric delta.

    The Phase 5 acceptance loop, run deterministically without a model:

    * the alibi-fabrication survival rate genuinely MOVES (``v_a`` 2/7 ->
      ``v_b`` 1/7) over a real, non-vacuous denominator of impostor alibis;
    * the delta is ISOLATED to that metric — vote-correctness, calibration ECE,
      and total cost are unchanged — so it is not an artifact of comparing
      unrelated fields;
    * it is ATTRIBUTABLE to exactly one changed prompt template
      (``impostor_report`` v3 -> v4) via the per-version provenance.
    """

    summary_a = _run_fixture("v_a")
    summary_b = _run_fixture("v_b")

    # The metric moved, over a real (non-vacuous) impostor-alibi denominator:
    # 7 impostor alibis across the three fixture games; 5 are already caught
    # by the live detector in v_a, and v_b's hand-authored contradiction
    # catches one more (2/7 surviving -> 1/7).
    assert summary_a.metrics.total_impostor_alibis == 7
    assert summary_b.metrics.total_impostor_alibis == 7
    assert summary_a.metrics.alibi_survival_rate == 2 / 7
    assert summary_b.metrics.alibi_survival_rate == 1 / 7
    assert (
        summary_a.metrics.alibi_survival_rate != summary_b.metrics.alibi_survival_rate
    )

    # The delta is isolated to the alibi metric: nothing else moved.
    assert (
        summary_a.metrics.vote_correctness_rate
        == summary_b.metrics.vote_correctness_rate
    )
    assert (
        summary_a.metrics.accusation_claim_ece == summary_b.metrics.accusation_claim_ece
    )
    assert summary_a.metrics.vote_ballot_ece == summary_b.metrics.vote_ballot_ece
    assert summary_a.metrics.total_cost_usd == summary_b.metrics.total_cost_usd

    # The W0.3 meeting-rate scalars are orthogonal to the prompt-version change
    # (v_b only flips one alibi contradiction; it touches neither the meeting
    # count nor the trigger classification), so they are identical across both
    # fixtures. All three fixture games (seeds 2/6/26) reach at least one
    # body-report meeting — 8 resolved meetings in total — so the rate is 1.0
    # and emergency is 0 (no emergency meetings observed in the canonical set).
    assert summary_a.metrics.meeting_rate == summary_b.metrics.meeting_rate == 1.0
    assert summary_a.metrics.meetings_total == summary_b.metrics.meetings_total == 8
    assert (
        summary_a.metrics.body_report_meetings
        == summary_b.metrics.body_report_meetings
        == 8
    )
    assert (
        summary_a.metrics.emergency_meetings
        == summary_b.metrics.emergency_meetings
        == 0
    )

    # Attribution: the ONLY (template, version) pair that changed is
    # impostor_report v3 -> v4 — the template responsible for impostor alibis.
    versions_a = {pv.template_name: pv.version for pv in summary_a.prompt_versions}
    versions_b = {pv.template_name: pv.version for pv in summary_b.prompt_versions}
    assert versions_a.keys() == versions_b.keys()
    changed = {
        template
        for template in versions_a
        if versions_a[template] != versions_b[template]
    }
    assert changed == {"impostor_report"}
    assert versions_a["impostor_report"] == "impostor_report_v3"
    assert versions_b["impostor_report"] == "impostor_report_v4"


def test_delta_exceeds_manual_real_provider_tolerance() -> None:
    """The demonstrated alibi-rate delta would trip the manual ``> X%`` policy.

    CI matches the baseline exactly; the ``> X%`` tolerance governs the manual
    real-provider re-record comparison. The demonstrated drop (2/7 -> 1/7 =
    1/7 ≈ 0.143) exceeds the documented ``REAL_PROVIDER_REGRESSION_TOLERANCE``,
    i.e. a re-record showing this much movement would be flagged as a
    regression.
    """

    summary_a = _run_fixture("v_a")
    summary_b = _run_fixture("v_b")

    delta = abs(
        summary_a.metrics.alibi_survival_rate - summary_b.metrics.alibi_survival_rate
    )
    assert delta == pytest.approx(1 / 7)
    assert delta > REAL_PROVIDER_REGRESSION_TOLERANCE


def test_no_provider_invoked_regardless_of_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The suite consults no provider, so ``AILIBI_LLM_PROVIDER`` is irrelevant.

    Pinning the env to an unbuildable provider must not change (or break) the
    result: the regression signal comes entirely from recorded fixtures, with no
    network and no live/fake model call to generate outputs.
    """

    monkeypatch.setenv(ENV_PROVIDER, "nonexistent-provider-xyz")
    actual = _run_fixture("v_a")
    assert actual == _load_baseline()["v_a"]


def test_run_prompt_regression_fails_loud_on_empty_fixture_dir(
    tmp_path: Path,
) -> None:
    """An empty / wrong fixture directory is fail-loud, not a vacuous pass.

    A regression suite that silently produced zero-metric results over a
    misconfigured path would never catch a regression, so a directory with no
    ``replay-seed-*.jsonl`` raises.
    """

    with pytest.raises(ValueError, match="no replay-seed"):
        run_prompt_regression(tmp_path)


def test_summary_round_trips_through_json() -> None:
    """The summary round-trips ``model_dump(mode="json")`` -> ``model_validate``.

    This is the contract ``baseline.json`` relies on: dumping a summary to JSON
    and reloading it reproduces an equal summary (exact float round-trip).
    """

    summary = _run_fixture("v_b")
    reloaded = PromptRegressionSummary.model_validate(
        json.loads(json.dumps(summary.model_dump(mode="json")))
    )
    assert reloaded == summary
