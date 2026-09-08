"""The live-vs-reconstructed memory guard is bound to the meeting it checks.

Both harnesses used to ask only whether a reconstructed memory's rendered text
appeared in *some* prompt its agent received anywhere in the game. In a
multi-meeting game that is satisfied by any meeting's prompt, so a mis-indexed
reconstruction that served meeting 0's memory for meeting 1 passed silently and
the published ``memory_projection_sha256`` described memories the model never
saw. Both harnesses' existing adverse tests stayed green under exactly that
mutation.

The planted case here is that mis-indexed reconstruction, applied at the real
integration point (``ReplayLoader.get_meeting_memory``) rather than by editing
the harness, and it is paired with a control in the same shape so a failure
cannot come from the scenario being unable to reconstruct at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import experiments.deduction_evaluation as deduction
import experiments.investigation_evaluation as investigation
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView
from experiments.deduction_scenarios import run_case as run_scenario

_GUARD_MESSAGE = "reconstructed opening memory differs from supplied live input"


def _serve_the_first_meeting_for_every_meeting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Plant an off-by-one reconstruction: every meeting gets meeting 0's memory."""

    original = ReplayLoader.get_meeting_memory
    first_seen: dict[str, str] = {}

    def mis_indexed(
        self: ReplayLoader, game_id: str, meeting_id: str, agent_id: str
    ) -> AgentMemoryView:
        return original(
            self, game_id, first_seen.setdefault(game_id, meeting_id), agent_id
        )

    monkeypatch.setattr(ReplayLoader, "get_meeting_memory", mis_indexed)


def _investigation_measurement(
    directory: Path,
) -> investigation.InvestigationMeasurement:
    """Measure the OFF arm of a development case that holds two meetings."""

    definition = next(
        case for case in investigation.development_cases() if case.seed == 0
    )
    arm = next(arm for arm in investigation.comparison_arms() if arm.name == "off")
    capture = investigation.run_case(directory, definition=definition, arm=arm)
    return investigation.measure_capture(capture)


def _deduction_measurement(directory: Path) -> deduction.CaseMeasurement:
    """Measure the one scenario case that opens a second meeting."""

    arm = next(
        arm for arm in deduction.comparison_arms() if arm.name == "repaired_clock"
    )
    capture = run_scenario(
        directory,
        case="already_known_dead",
        experiment_config=arm.experiment_config,
        temporal_version=arm.temporal_version,
    )
    return deduction.measure_capture(capture, arm=arm, output_dir=directory)


def test_investigation_control_reconstructs_two_meetings(tmp_path: Path) -> None:
    """The control: the planted case below has somewhere to put the substitution."""

    measurement = _investigation_measurement(tmp_path / "control")
    assert measurement.meetings >= 2


def test_investigation_guard_refuses_a_cross_meeting_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _serve_the_first_meeting_for_every_meeting(monkeypatch)
    with pytest.raises(ValueError, match=_GUARD_MESSAGE):
        _investigation_measurement(tmp_path / "planted")


def test_deduction_control_reconstructs_two_meetings(tmp_path: Path) -> None:
    """The control, for the same reason as the investigation one above."""

    measurement = _deduction_measurement(tmp_path / "control")
    assert measurement.meetings >= 2


def test_deduction_guard_refuses_a_cross_meeting_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _serve_the_first_meeting_for_every_meeting(monkeypatch)
    with pytest.raises(ValueError, match=_GUARD_MESSAGE):
        _deduction_measurement(tmp_path / "planted")


def test_guard_refuses_a_recording_that_does_not_mirror_the_live_prompts(
    tmp_path: Path,
) -> None:
    """The meeting partition may not stand in for the live inputs it labels.

    The partition is read from the recorded per-meeting calls, so a recording
    whose calls are not the live provider's inputs would let the reader's own
    bytes be compared against themselves. Dropping one live prompt is enough.
    """

    definition = next(
        case for case in investigation.development_cases() if case.seed == 0
    )
    arm = next(arm for arm in investigation.comparison_arms() if arm.name == "off")
    capture = investigation.run_case(tmp_path / "off", definition=definition, arm=arm)
    assert capture.provider.prompts
    del capture.provider.prompts[0]
    with pytest.raises(ValueError, match="not one of the live provider inputs"):
        investigation.measure_capture(capture)
