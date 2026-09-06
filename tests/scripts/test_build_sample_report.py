"""Reconstructed reports preserve all four committed sets, including failures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_sample_report as bsr
from eval.meeting_quality import TournamentEvalReport
from eval.balance_eval import build_tournament_report
from eval.meeting_quality import build_tournament_eval_report
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import (
    CrewTacticalPolicyStamp,
    FailedCallReplayEntry,
    TacticalPolicyStamp,
)
from tests._helpers.committed import report_9p2i

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The flat 4p1i baseline now lives under replays/samples/4p1i/ (Task 12.12).
_FLAT_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"
_COMMITTED_REPORT = _FLAT_4P1I / "tournament-eval-report.json"
_COMMITTED_SETS = (
    "samples/4p1i",
    "samples/9p2i",
    "ml_corpus/4p1i",
    "ml_corpus/9p2i",
)


def _copy_flat_replays(dst: Path) -> None:
    """Copy the committed flat 4p/1i replay JSONL into ``dst`` (no roster.json).

    A directory with no ``roster.json`` is the flat 4p/1i default, so a rebuild in
    ``dst`` re-seeds 4p/1i exactly as the committed set does.
    """

    for jsonl in _FLAT_4P1I.glob("replay-seed-*.jsonl"):
        (dst / jsonl.name).write_bytes(jsonl.read_bytes())


def test_rebuild_matches_committed_flat_4p1i() -> None:
    """A rebuild from the committed 4p/1i replays equals the committed report."""

    rebuilt = bsr.historical_report_payload(bsr.build_report(_FLAT_4P1I))
    committed = json.loads(_COMMITTED_REPORT.read_text(encoding="utf-8"))
    assert rebuilt == committed, (
        "The committed flat 4p/1i tournament-eval-report.json is STALE — it does "
        "not match a rebuild from its own replays. Run `uv run python "
        "scripts/build_sample_report.py --sample-dir replays/samples/4p1i` and commit it."
    )


@pytest.mark.parametrize("relative_dir", _COMMITTED_SETS)
def test_check_reports_consistent_on_committed_sets(relative_dir: str) -> None:
    """``--check`` covers both rosters' canonical and failed-call-bearing sets."""

    assert bsr.check_report(_REPO_ROOT / "replays" / relative_dir) == 0


def test_historical_serialization_preserves_real_attempt_ids() -> None:
    report = report_9p2i()
    original = report.report.games[0]
    legacy_call = FailedCallReplayEntry(
        game_id=original.game_id,
        meeting_id=f"{original.game_id}:meeting-0",
        tick=0,
        model="fake",
        prompt_length=10,
        raw_response="invalid response",
        input_tokens=10,
        output_tokens=2,
        cost_usd=0.0,
        error_type="validation",
        error_message="invalid response",
    )
    identified_call = legacy_call.model_copy(update={"call_id": "attempt-2"})
    game = original.model_copy(update={"failed_calls": (legacy_call, identified_call)})
    candidate = report.model_copy(
        update={"report": report.report.model_copy(update={"games": (game,)})}
    )
    payload = bsr.historical_report_payload(candidate)
    failed = payload["report"]["games"][0]["failed_calls"]
    assert "call_id" not in failed[0]
    assert failed[1]["call_id"] == "attempt-2"
    # An indiscriminate exclude_none would also erase this historical field.
    assert failed[0]["rendered_vote_max"] is None
    assert failed[1]["rendered_vote_max"] is None
    assert json.loads(bsr._serialize(candidate)) == payload
    assert candidate.report.games[0].failed_calls[1].call_id == "attempt-2"


def test_historical_serialization_preserves_existing_cells_and_omits_added_metadata() -> (
    None
):
    report = report_9p2i()
    current = report.model_dump(mode="json")
    historical = bsr.historical_report_payload(report)
    for current_game, historical_game in zip(
        current["report"]["games"], historical["report"]["games"], strict=True
    ):
        assert current_game["outcome_verified"] is True
        assert current_game["completion_status"] == "completed"
        assert "completion_status" not in historical_game
        assert "outcome_verified" not in historical_game
        historical_game["completion_status"] = current_game["completion_status"]
        historical_game["outcome_verified"] = current_game["outcome_verified"]
        for key in (
            "agent_factory_kind",
            "experiment_config",
            "substrate_flags",
            "tactical_policy",
            "crew_tactical_policy",
        ):
            assert key not in historical_game
            historical_game[key] = current_game[key]
        for current_meeting, historical_meeting in zip(
            current_game["meetings"], historical_game["meetings"], strict=True
        ):
            assert current_meeting["skip_confidence_threshold"] is None
            assert "skip_confidence_threshold" not in historical_meeting
            historical_meeting["skip_confidence_threshold"] = None
    assert "provenance_groups" not in historical["report"]
    historical["report"]["provenance_groups"] = current["report"]["provenance_groups"]
    assert historical == current


def test_check_flags_a_stale_report(tmp_path: Path) -> None:
    """``--check`` returns 1 when the on-disk report drifts from a rebuild."""

    _copy_flat_replays(tmp_path)
    stale = json.loads(_COMMITTED_REPORT.read_text(encoding="utf-8"))
    stale["meeting_rate"]["meetings_total"] += 7  # tamper: no longer matches replays
    (tmp_path / "tournament-eval-report.json").write_text(json.dumps(stale))
    assert bsr.check_report(tmp_path) == 1


@pytest.mark.parametrize(
    "identity",
    [
        "factory",
        "experiment",
        "substrate",
        "cutoff",
        "tactical_policy",
        "crew_tactical_policy",
    ],
)
def test_current_serialization_cannot_hide_recorded_identity_as_legacy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, identity: str
) -> None:
    game = next(game for game in report_9p2i().report.games if game.meetings)
    if identity == "factory":
        game = game.model_copy(update={"agent_factory_kind": "scripted"})
    elif identity == "experiment":
        game = game.model_copy(
            update={
                "experiment_config": RecordedExperimentConfig(crew_idle_policy="patrol")
            }
        )
    elif identity == "substrate":
        game = game.model_copy(
            update={
                "substrate_flags": {
                    **(game.substrate_flags or {}),
                    "testimony_shapes": True,
                }
            }
        )
    elif identity == "cutoff":
        game = game.model_copy(
            update={
                "meetings": (
                    game.meetings[0].model_copy(
                        update={"skip_confidence_threshold": 0.8}
                    ),
                    *game.meetings[1:],
                )
            }
        )
    else:
        stamp_class = (
            TacticalPolicyStamp
            if identity == "tactical_policy"
            else CrewTacticalPolicyStamp
        )
        game = game.model_copy(
            update={
                identity: stamp_class(
                    policy_id="custom-policy",
                    method="scripted-test",
                    encoder_version="none",
                    weights_sha256="none",
                    anchor_policy="fsm-default",
                )
            }
        )
    candidate = build_tournament_eval_report(
        build_tournament_report(games=(game,), seeds=(game.seed,))
    )
    monkeypatch.setattr(bsr, "build_report", lambda directory: candidate)
    assert bsr.historical_report_payload(candidate) == candidate.model_dump(mode="json")
    bsr.write_report(tmp_path)
    assert bsr.check_report(tmp_path) == 0
    path = tmp_path / "tournament-eval-report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["report"]["provenance_groups"]
    assert "agent_factory_kind" in payload["report"]["games"][0]
    # Plant a historical-shaped output while the actual source remains current.
    del payload["report"]["provenance_groups"]
    for raw_game in payload["report"]["games"]:
        for key in (
            "agent_factory_kind",
            "experiment_config",
            "substrate_flags",
            "tactical_policy",
            "crew_tactical_policy",
            "completion_status",
            "outcome_verified",
        ):
            del raw_game[key]
        for meeting in raw_game["meetings"]:
            del meeting["skip_confidence_threshold"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert bsr.check_report(tmp_path) == 1


def test_write_report_emits_a_loadable_consistent_file(tmp_path: Path) -> None:
    """``write_report`` writes a model-valid report matching the committed one."""

    _copy_flat_replays(tmp_path)
    bsr.write_report(tmp_path)
    written = (tmp_path / "tournament-eval-report.json").read_text(encoding="utf-8")
    # New reports expose unknown historical identity; the compatibility
    # projection still preserves every committed metric and recorded cell.
    restored = TournamentEvalReport.model_validate_json(written)
    assert restored.report.provenance_groups is not None
    assert all(game.agent_factory_kind is None for game in restored.report.games)
    assert bsr.historical_report_payload(restored) == json.loads(
        _COMMITTED_REPORT.read_text(encoding="utf-8")
    )
    assert bsr.check_report(tmp_path) == 0


def test_seeds_on_disk_skips_an_audit_sidecar(tmp_path: Path) -> None:
    """The planted case: a ``<n>.audit`` stem is skipped, not parsed.

    A wrapper writes ``replay-seed-<n>.audit.jsonl`` beside the replay and the
    glob matches it; parsing that stem raised an uncaught ``ValueError``, so this
    guard is the difference between a report and a crash.
    """

    (tmp_path / "replay-seed-4.jsonl").write_text("")
    (tmp_path / "replay-seed-9.jsonl").write_text("")

    assert bsr._seeds_on_disk(tmp_path) == [4, 9]

    (tmp_path / "replay-seed-4.audit.jsonl").write_text("")

    assert bsr._seeds_on_disk(tmp_path) == [4, 9]


def test_seeds_on_disk_still_raises_on_a_mistyped_replay(tmp_path: Path) -> None:
    """The other half: only the recognised sidecar is skipped.

    A mistyped ``replay-seed-4x.jsonl`` must not be silently excluded — building
    a report over the remaining games and calling it the set's is worse than the
    crash the sidecar guard removed.
    """

    (tmp_path / "replay-seed-4.jsonl").write_text("")
    (tmp_path / "replay-seed-4x.jsonl").write_text("")

    with pytest.raises(ValueError, match="replay-seed-4x.jsonl"):
        bsr._seeds_on_disk(tmp_path)
