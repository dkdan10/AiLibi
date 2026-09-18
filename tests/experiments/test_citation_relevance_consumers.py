"""The relevance lever's other consumers, and the counterfactual's cross-check.

Two carry-over repairs from the review of
``tasks/work/relevance-aware-citation-guard.md``, both small and both with a
planted case here (``tasks/work/fresh-deduction-calibration-3.md``):

* ``citation_relevance_version`` is a field of ``RecordedExperimentConfig`` and a
  member of ``meetings.evidence_profile.EXPERIMENT_ENV_NAMES``, so a harness that
  turns a config into an environment has to state it. Two did not, and a lever a
  config carries and the environment drops is a capture that SAYS it ran with the
  relevance rule on and rendered with it off;
* ``experiments/citation_relevance_counterfactual.py`` believes its after-column
  only because its before-column was re-graded and agreed with the archive's own
  checkpoint. A replay the checkpoint has no row for used to skip that check
  silently, which passes a whole directory through unchecked in exactly the case
  where the two have come apart.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from experiments import deduction_scenarios, investigation_evaluation
from experiments.citation_relevance_counterfactual import CounterfactualError
from experiments.citation_relevance_counterfactual import main as counterfactual_main
from meetings.evidence_profile import EXPERIMENT_ENV_NAMES
from orchestrator.experiment_config import RecordedExperimentConfig

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The fifth run's committed archive. Read here as REPLAY ROWS and never
#: printed: what these cases need from it is one file that the counterfactual
#: can walk, and the archive already holds it.
_FIFTH_RUN = _REPO_ROOT / "audits" / "deduction-candidate" / "run-2026-09-16"


class _RunnerReached(Exception):
    """Raised by the stubbed meeting runner once the environment is captured."""


def _capture_environment(
    monkeypatch: pytest.MonkeyPatch, module: Any
) -> dict[str, str]:
    """Stub one harness's meeting-runner builder and keep the env it is handed.

    The environment is assembled before the runner is built, so stopping there
    reads exactly what the harness would have rendered under without running a
    game for it.
    """

    captured: dict[str, str] = {}

    def _stub(*, llm_client: object, env: dict[str, str], public_map: object) -> None:
        captured.update(env)
        raise _RunnerReached

    monkeypatch.setattr(module, "build_default_meeting_runner", _stub)
    return captured


class TestEveryExperimentLeverReachesTheRenderer:
    """PLANTED both ways: a config carrying the lever, in each harness."""

    def test_the_scenario_harness_exports_the_relevance_lever(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """`deduction_scenarios.run_case` states every registry lever.

        Before the repair the env dict named four of the five and dropped
        `AILIBI_CITATION_RELEVANCE`, so this config — which asks for the
        relevance rule explicitly — rendered with the rule off and the capture
        recorded the version anyway.
        """

        captured = _capture_environment(monkeypatch, deduction_scenarios)
        with pytest.raises(_RunnerReached):
            deduction_scenarios.run_case(
                tmp_path,
                case="honest",
                experiment_config=RecordedExperimentConfig(
                    format_version=2,
                    evidence_reasoning_version=2,
                    citation_relevance_version=1,
                ),
            )
        assert captured["AILIBI_CITATION_RELEVANCE"] == "1"
        assert set(EXPERIMENT_ENV_NAMES) <= set(captured)

    def test_the_investigation_harness_exports_the_relevance_lever(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The sibling consumer, held to the same rule for the same reason."""

        captured = _capture_environment(monkeypatch, investigation_evaluation)
        arm = investigation_evaluation.InvestigationArm(
            name="relevance_on",
            experiment_config=RecordedExperimentConfig(
                format_version=2,
                evidence_reasoning_version=2,
                citation_relevance_version=1,
            ),
        )
        with pytest.raises(_RunnerReached):
            investigation_evaluation.run_case(
                tmp_path,
                definition=investigation_evaluation.development_cases()[0],
                arm=arm,
            )
        assert captured["AILIBI_CITATION_RELEVANCE"] == "1"
        assert set(EXPERIMENT_ENV_NAMES) <= set(captured)

    def test_a_config_without_the_lever_still_resolves_it_off(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The export is a no-op where the config carries no version.

        `_enabled` reads an absent key and a `"0"` the same way, so the repair
        adds a stated zero rather than a behaviour change to every capture these
        two harnesses have already made.
        """

        captured = _capture_environment(monkeypatch, deduction_scenarios)
        with pytest.raises(_RunnerReached):
            deduction_scenarios.run_case(
                tmp_path,
                case="honest",
                experiment_config=RecordedExperimentConfig(
                    format_version=2, evidence_reasoning_version=2
                ),
            )
        assert captured["AILIBI_CITATION_RELEVANCE"] == "0"


class TestTheCounterfactualCrossChecksEveryReplay:
    """The before-column is the record's, or the command stops."""

    def _one_replay(self, tmp_path: Path) -> Path:
        replay = sorted(_FIFTH_RUN.glob("combined_accounts-seed-*.jsonl"))[0]
        shutil.copy(replay, tmp_path / replay.name)
        return replay

    def test_a_replay_with_no_checkpoint_row_is_a_stop(self, tmp_path: Path) -> None:
        """PLANTED: a directory whose final checkpoint lists no units.

        Before the repair this skipped the cross-check and reported an
        after-column computed from a before-column nothing had checked. The
        archive and its checkpoint disagreeing about which units exist is the
        one case the check was written for.
        """

        self._one_replay(tmp_path)
        (tmp_path / "checkpoint-final.json").write_text(
            json.dumps({"units": []}), encoding="utf-8"
        )
        with pytest.raises(CounterfactualError, match="no row in its final checkpoint"):
            counterfactual_main(tmp_path)

    def test_the_same_replay_passes_with_its_own_checkpoint_row(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """The positive control: the plant is the missing row, not the copy.

        The committed checkpoint carries this replay's unit, so the same
        directory runs to its aggregates — which is what says the refusal above
        is about the cross-check rather than about a one-file archive.
        """

        self._one_replay(tmp_path)
        shutil.copy(
            _FIFTH_RUN / "checkpoint-final.json", tmp_path / "checkpoint-final.json"
        )
        assert counterfactual_main(tmp_path) == 0
        # Counts only: the command's own contract is that it prints no prompt,
        # no prefix and no transcript, and this is a spot check of it.
        printed = capsys.readouterr().out
        assert "rationale_text" not in printed
        assert "prompt" not in printed
