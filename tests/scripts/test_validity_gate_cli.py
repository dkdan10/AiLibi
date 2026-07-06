"""Tests for scripts/validity_gate.py (Task 15.1).

Drives ``main`` directly (no subprocess). Confirms the committed 9p2i + 4p1i sets
PASS (exit 0), that ``--json`` emits the machine-readable report, and that every
one of the eight checks has a synthetic violation that flips the exit code to 1
and names the failing check. Byte-editable checks corrupt a copied mini-set; the
two kill checks (which the engine cannot emit by construction) and the railroad
check inject a synthetic reconstruction / report via monkeypatch.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pytest

import validity_gate
from eval import validity
from eval.report_schema import GameReport, MeetingReport
from eval.validity import _GameReconstruction, _KillFact
from eval.win_condition_selfcheck import WinConditionSelfCheck
from meetings.schemas import ContradictionRef
from orchestrator.replay import LLMCallRecord

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def _mini(tmp_path: Path, *, seeds: Sequence[int] = (0, 1, 2)) -> Path:
    shutil.copy(_NINE / "roster.json", tmp_path / "roster.json")
    for seed in seeds:
        shutil.copy(
            _NINE / f"replay-seed-{seed}.jsonl", tmp_path / f"replay-seed-{seed}.jsonl"
        )
    return tmp_path


def _rewrite_lines(
    path: Path, transform: Callable[[dict[str, Any]], dict[str, Any] | None]
) -> None:
    """Rewrite ``path`` line-by-line through ``transform``.

    ``transform`` returns a modified JSON object (rewritten) or ``None`` to drop
    the line.
    """

    lines = path.read_text().splitlines()
    out: list[str] = []
    for line in lines:
        new = transform(json.loads(line))
        if new is None:
            continue
        out.append(json.dumps(new, sort_keys=True, separators=(",", ":")))
    path.write_text("\n".join(out) + "\n")


# --------------------------------------------------------------------------- #
# PASS + JSON + usage                                                          #
# --------------------------------------------------------------------------- #


def test_committed_sets_pass(capsys: pytest.CaptureFixture[str]) -> None:
    assert validity_gate.main([str(_NINE)]) == 0
    assert validity_gate.main([str(_FOUR)]) == 0
    out = capsys.readouterr().out
    assert "Validity gate PASSED" in out


def test_json_output_is_machine_readable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert validity_gate.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert payload["games_total"] == 50
    assert [c["name"] for c in payload["checks"]] == [
        "all_games_reach_game_over",
        "meeting_rate_and_resolution",
        "no_tick_1_kills",
        "no_friendly_fire_kills",
        "no_railroaded_crew_ejections",
        "no_dangling_primary_reason_id",
        "cost_and_provenance_exact",
        "byte_identical_reconstruction",
    ]


def test_missing_dir_is_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert validity_gate.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert validity_gate.main([str(tmp_path)]) == 2


def test_mini_set_passes(tmp_path: Path) -> None:
    assert validity_gate.main([str(_mini(tmp_path))]) == 0


# --------------------------------------------------------------------------- #
# Byte-editable violation fixtures (flip exit code + name the failing check)   #
# --------------------------------------------------------------------------- #


def _fail_and_get_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> dict[str, Any]:
    assert validity_gate.main([str(tmp_path), "--json"]) == 1
    payload: dict[str, Any] = json.loads(capsys.readouterr().out)
    return payload


def _failing_names(payload: dict[str, Any]) -> set[str]:
    return {c["name"] for c in payload["checks"] if not c["passed"]}


def test_fails_when_game_over_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mini = _mini(tmp_path, seeds=(0,))

    def drop_game_over(obj: dict[str, Any]) -> dict[str, Any] | None:
        return None if obj.get("kind") == "game_over" else obj

    _rewrite_lines(mini / "replay-seed-0.jsonl", drop_game_over)
    payload = _fail_and_get_check(mini, capsys)
    assert "all_games_reach_game_over" in _failing_names(payload)


def test_fails_on_unresolved_meeting(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mini = _mini(tmp_path, seeds=(0,))
    path = mini / "replay-seed-0.jsonl"
    lines = path.read_text().splitlines()
    ghost = {
        "kind": "failed_call",
        "game_id": "headless-seed-0",
        "meeting_id": "headless-seed-0:ghost-meeting",
        "tick": 99,
        "model": "m",
        "prompt_length": 0,
        "raw_response": "",
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "error_type": "ValidationError",
        "error_message": "crashed before resolving",
    }
    lines.append(json.dumps(ghost, sort_keys=True, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n")
    payload = _fail_and_get_check(mini, capsys)
    assert "meeting_rate_and_resolution" in _failing_names(payload)


def test_fails_on_dangling_primary_reason_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mini = _mini(tmp_path, seeds=(0,))

    def dangle(obj: dict[str, Any]) -> dict[str, Any]:
        if obj.get("kind") == "meeting" and obj.get("ballots"):
            obj["ballots"][0]["primary_reason_id"] = "ghost-turn-id"
        return obj

    _rewrite_lines(mini / "replay-seed-0.jsonl", dangle)
    payload = _fail_and_get_check(mini, capsys)
    assert "no_dangling_primary_reason_id" in _failing_names(payload)


def test_fails_on_multiple_models(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Drift: seed 0 uses a different model than seeds 1-2 (coherent mixed-tier is
    # allowed; per-game model-set drift across the run is the violation).
    mini = _mini(tmp_path, seeds=(0, 1, 2))

    def swap_model(obj: dict[str, Any]) -> dict[str, Any]:
        if obj.get("kind") == "meeting":
            for call in obj.get("llm_calls", []):
                call["model"] = "A-Totally-Different-Model"
        return obj

    _rewrite_lines(mini / "replay-seed-0.jsonl", swap_model)
    payload = _fail_and_get_check(mini, capsys)
    assert "cost_and_provenance_exact" in _failing_names(payload)


def test_fails_on_corrupted_state_hash(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mini = _mini(tmp_path, seeds=(0,))
    flipped = {"done": False}

    def corrupt(obj: dict[str, Any]) -> dict[str, Any]:
        if (
            not flipped["done"]
            and obj.get("kind", "tick") == "tick"
            and obj.get("tick", -1) >= 1
        ):
            digest = obj["state_hash"]
            obj["state_hash"] = ("1" if digest[0] != "1" else "0") + digest[1:]
            flipped["done"] = True
        return obj

    _rewrite_lines(mini / "replay-seed-0.jsonl", corrupt)
    payload = _fail_and_get_check(mini, capsys)
    assert "byte_identical_reconstruction" in _failing_names(payload)


# --------------------------------------------------------------------------- #
# Synthetic-injection violation fixtures (engine cannot emit these bytes)      #
# --------------------------------------------------------------------------- #


def _synthetic_reconstruction(
    seed: int, *, kill_tick: int, victim_role: str
) -> list[_GameReconstruction]:
    win = WinConditionSelfCheck(
        game_id=f"headless-seed-{seed}",
        seed=seed,
        winner="CREWMATES",
        reason="CREWMATE_EJECT",
        first_zero_impostor_tick=None,
        game_over_tick=7,
    )
    kill = _KillFact(
        seed=seed,
        tick=kill_tick,
        killer="p-1",
        killer_role="IMPOSTOR",
        victim="p-2",
        victim_role=victim_role,  # type: ignore[arg-type]
    )
    return [_GameReconstruction(seed=seed, win_check=win, kills=(kill,))]


def test_fails_on_tick_1_kill(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mini = _mini(tmp_path, seeds=(0,))
    monkeypatch.setattr(
        validity,
        "_reconstruct_set",
        lambda _d: _synthetic_reconstruction(0, kill_tick=1, victim_role="CREWMATE"),
    )
    payload = _fail_and_get_check(mini, capsys)
    assert "no_tick_1_kills" in _failing_names(payload)


def test_fails_on_friendly_fire(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mini = _mini(tmp_path, seeds=(0,))
    monkeypatch.setattr(
        validity,
        "_reconstruct_set",
        lambda _d: _synthetic_reconstruction(0, kill_tick=5, victim_role="IMPOSTOR"),
    )
    payload = _fail_and_get_check(mini, capsys)
    assert "no_friendly_fire_kills" in _failing_names(payload)


def test_fails_on_railroaded_crew_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mini = _mini(tmp_path, seeds=(0, 1, 2))
    real = validity.assemble_tournament_report(mini)

    def _railroad(game: GameReport) -> GameReport:
        crew = next(pid for pid, role in game.roles.items() if role == "CREWMATE")
        meeting: MeetingReport = game.meetings[0]
        call = LLMCallRecord(
            call_kind="meeting",
            model="Qwen/Qwen3-32B",
            prompt=(
                "## Your suspicion of each player\n"
                f"- `{crew}`: suspicion 1.0, trust 0.0\n## Next\n"
            ),
            response_text="{}",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
        )
        flags = tuple(
            ContradictionRef(
                contradiction_id=f"c-{i}",
                kind="alibi_conflict",
                event_a_id="a",
                event_b_id="b",
                subjects=(crew,),
                description="synthetic",
            )
            for i in range(2)
        )
        bad_meeting = meeting.model_copy(
            update={"llm_calls": (call,), "contradictions": flags}
        )
        return game.model_copy(update={"meetings": (bad_meeting, *game.meetings[1:])})

    injected = _railroad(real.games[0])
    bad_report = real.model_copy(update={"games": (injected, *real.games[1:])})
    monkeypatch.setattr(validity, "assemble_tournament_report", lambda _d: bad_report)
    payload = _fail_and_get_check(mini, capsys)
    assert "no_railroaded_crew_ejections" in _failing_names(payload)


def test_json_failure_names_failing_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    mini = _mini(tmp_path, seeds=(0,))
    monkeypatch.setattr(
        validity,
        "_reconstruct_set",
        lambda _d: _synthetic_reconstruction(0, kill_tick=0, victim_role="IMPOSTOR"),
    )
    assert validity_gate.main([str(mini)]) == 1
    text = capsys.readouterr().out
    assert "Validity gate FAILED" in text
    assert "no_tick_1_kills" in text
    assert "no_friendly_fire_kills" in text
