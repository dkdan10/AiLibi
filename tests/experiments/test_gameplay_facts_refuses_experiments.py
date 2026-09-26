"""The gameplay-facts extractor reads only recordings made without experiment settings.

``audits/workflows/extract_gameplay_facts.py`` re-simulates each recording with
no settings and re-derives its meeting chain, so a recording made with experiment
settings (the one-reply rebuttal, the regroup reset, ...) would fail a later
extraction invariant or, worse, pass one on facts its settings changed. Before
any re-simulation it now refuses such a seed with a plain message naming the
seed and its settings. Its acceptance of a rebuttal recording waits for the
adoption of that setting.

Three cases over fake recordings in a temporary directory: the scripted rebuttal
recording is refused with that message before the first advance, an unstamped
recording still extracts, and the message names every setting the recording
turned on.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

from orchestrator.experiment_config import RecordedExperimentConfig
from tests._helpers.scripted_meeting import (
    ACCUSE_THE_OPENER,
    ScriptedMeetingClient,
    record_game,
)

# Imported dynamically: audits/workflows/ is not a package (see
# tests/experiments/test_gameplay_facts_suspicion_row.py).
_facts: Any = importlib.import_module("audits.workflows.extract_gameplay_facts")


def _refuse_every_advance(monkeypatch: pytest.MonkeyPatch) -> None:
    def _advance(*args: object, **kwargs: object) -> object:
        raise AssertionError("a refused recording advanced")

    monkeypatch.setattr(_facts, "advance_tick", _advance)


def test_the_scripted_rebuttal_recording_is_refused_before_any_resimulation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / "rebuttal" / "9p2i"
    record_game(
        directory,
        seed=3,
        config=RecordedExperimentConfig(bounded_rebuttal_version=1),
        client=ScriptedMeetingClient(script=ACCUSE_THE_OPENER),
    )
    monkeypatch.setattr(_facts, "SAMPLE_DIR", directory)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    _refuse_every_advance(monkeypatch)
    with pytest.raises(SystemExit) as refused:
        _facts.main()
    assert str(refused.value) == (
        "seed 3: the recording was made with experiment settings "
        "(bounded_rebuttal_version = 1); this extractor reads only recordings made "
        "without experiment settings"
    )


def test_the_message_names_every_setting_the_recording_turned_on() -> None:
    with pytest.raises(SystemExit) as refused:
        _facts.refuse_experiment_settings(
            7,
            RecordedExperimentConfig(
                meeting_reset="hub_with_grace",
                vent_exit_policy="observed_risk",
                bounded_rebuttal_version=1,
            ),
        )
    assert str(refused.value) == (
        "seed 7: the recording was made with experiment settings "
        "(meeting_reset = 'hub_with_grace', vent_exit_policy = 'observed_risk', "
        "bounded_rebuttal_version = 1); this extractor reads only recordings made "
        "without experiment settings"
    )
    # The settings format is not a setting: a later-format recording names only
    # the settings it turned on.
    with pytest.raises(SystemExit) as later:
        _facts.refuse_experiment_settings(
            7, RecordedExperimentConfig(format_version=2, bounded_rebuttal_version=1)
        )
    assert "(bounded_rebuttal_version = 1)" in str(later.value)
    _facts.refuse_experiment_settings(7, None)


def test_an_unstamped_fake_recording_still_extracts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    directory = tmp_path / "plain" / "9p2i"
    record_game(directory, seed=3, config=None)
    monkeypatch.setattr(_facts, "SAMPLE_DIR", directory)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    assert _facts.main() == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["games_analyzed"] == 1
    facts = json.loads(Path(summary["facts_path"]).read_text(encoding="utf-8"))
    assert facts["games_analyzed"] == 1
