"""Unit tests for scripts/_verify_samples.py + scripts/verify_samples.sh (4.17).

Builds fixtures by copying a committed sample into a tmp dir, optionally
corrupting one recorded state-hash, and asserts the verifier (a) passes clean
samples and (b) fails loud on drift with the divergent tick + hashes. One
end-to-end test drives the bash wrapper.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

import _verify_samples as vs
from api.replay_loader import ReplayLoader

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The flat 4p1i baseline now lives under replays/samples/4p1i/ (Task 12.12).
_REAL_SAMPLES = _REPO_ROOT / "replays" / "samples" / "4p1i"
_VERIFY_SH = _REPO_ROOT / "scripts" / "verify_samples.sh"
_SEED = 0  # smallest committed sample: fast to reconstruct
_MEETING_SEED = 22  # a committed sample that contains a meeting


def _copy_seed(dst_dir: Path, seed: int) -> Path:
    src = _REAL_SAMPLES / f"replay-seed-{seed}.jsonl"
    dst = dst_dir / src.name
    dst.write_bytes(src.read_bytes())
    return dst


def _corrupt_first_tick_hash(path: Path) -> int:
    """Flip one hex char of the first real tick's recorded state_hash.

    Returns the tick whose hash was corrupted. Engine playback reconstructs the
    true hash, which then diverges from this tampered record.
    """

    lines = path.read_text().splitlines()
    corrupted_tick: int | None = None
    out: list[str] = []
    for line in lines:
        obj = json.loads(line)
        if (
            corrupted_tick is None
            and obj.get("kind", "tick") == "tick"
            and obj.get("tick", -1) >= 0
        ):
            digest = obj["state_hash"]
            obj["state_hash"] = ("1" if digest[0] != "1" else "0") + digest[1:]
            corrupted_tick = int(obj["tick"])
            line = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        out.append(line)
    assert corrupted_tick is not None
    path.write_text("\n".join(out) + "\n")
    return corrupted_tick


def test_clean_sample_verifies(tmp_path: Path) -> None:
    _copy_seed(tmp_path, _SEED)
    assert vs.verify_samples(tmp_path) == []


def test_corrupted_hash_detected(tmp_path: Path) -> None:
    path = _copy_seed(tmp_path, _SEED)
    tick = _corrupt_first_tick_hash(path)
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.game_id == f"headless-seed-{_SEED}"
    assert failure.tick == tick
    assert failure.expected != failure.actual
    assert f"diverged at tick {tick}" in failure.render()


def test_main_clean_exit_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _copy_seed(tmp_path, _SEED)
    rc = vs.main([str(tmp_path)])
    assert rc == 0
    assert "verified clean" in capsys.readouterr().out


def test_main_corrupted_exit_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _copy_seed(tmp_path, _SEED)
    tick = _corrupt_first_tick_hash(path)
    rc = vs.main([str(tmp_path)])
    assert rc == 1
    out = capsys.readouterr().out
    assert f"tick {tick}" in out
    assert "FAILED" in out


def test_main_empty_dir_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert vs.main([str(tmp_path)]) == 2


def test_main_missing_dir_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert vs.main([str(tmp_path / "does-not-exist")]) == 2


def test_verify_sh_is_executable() -> None:
    assert _VERIFY_SH.exists()
    assert os.access(_VERIFY_SH, os.X_OK)


@pytest.mark.skipif(
    shutil.which("uv") is None or shutil.which("bash") is None,
    reason="needs uv + bash for the end-to-end shell wrapper",
)
def test_verify_sh_detects_corruption(tmp_path: Path) -> None:
    path = _copy_seed(tmp_path, _SEED)
    tick = _corrupt_first_tick_hash(path)
    proc = subprocess.run(
        ["bash", str(_VERIFY_SH), str(tmp_path)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert f"tick {tick}" in proc.stdout


def _corrupt_meeting_before_hash(path: Path) -> int:
    """Flip one hex char of the first meeting's recorded ``state_hash_before``.

    Returns the meeting tick. ``load_replay`` never checks this field, so the
    verifier's cross-check is the only thing that catches the corruption.
    """

    lines = path.read_text().splitlines()
    corrupted_tick: int | None = None
    out: list[str] = []
    for line in lines:
        obj = json.loads(line)
        if corrupted_tick is None and obj.get("kind") == "meeting":
            digest = obj["state_hash_before"]
            obj["state_hash_before"] = ("1" if digest[0] != "1" else "0") + digest[1:]
            corrupted_tick = int(obj["tick"])
            line = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        out.append(line)
    assert corrupted_tick is not None
    path.write_text("\n".join(out) + "\n")
    return corrupted_tick


def test_meeting_state_hash_before_corruption_detected(tmp_path: Path) -> None:
    path = _copy_seed(tmp_path, _MEETING_SEED)
    tick = _corrupt_meeting_before_hash(path)
    # load_replay alone does NOT inspect state_hash_before, so it still passes —
    # this is the gap the cross-check closes.
    ReplayLoader(tmp_path).load_replay(f"headless-seed-{_MEETING_SEED}")
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.game_id == f"headless-seed-{_MEETING_SEED}"
    assert failure.tick == tick
    assert "state_hash_before" in failure.reason
    assert failure.expected != failure.actual


def test_duplicate_seed_alias_rejected(tmp_path: Path) -> None:
    _copy_seed(tmp_path, _SEED)  # replay-seed-0.jsonl
    # A zero-padded second file maps to the same numeric seed; ReplayLoader would
    # dedup it to one canonical path, so the verifier must reject the ambiguity.
    (tmp_path / "replay-seed-00.jsonl").write_bytes(
        (_REAL_SAMPLES / f"replay-seed-{_SEED}.jsonl").read_bytes()
    )
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    assert failures[0].game_id == f"headless-seed-{_SEED}"
    assert "map to seed 0" in failures[0].reason


def test_missing_canonical_seed_detected(tmp_path: Path) -> None:
    # A manifest declares seeds 0 and 22, but seed 22's replay is absent.
    _copy_seed(tmp_path, _SEED)  # only replay-seed-0.jsonl present
    (tmp_path / "MANIFEST.md").write_text(
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
        "| 0 | m | (none) | d | s | 0.0000 | CREWMATES |\n"
        "| 22 | m | accusation_round.v2 | d | s | 0.2000 | CREWMATES |\n"
    )
    failures = vs.verify_samples(tmp_path)
    assert [f.game_id for f in failures] == ["headless-seed-22"]
    assert "missing" in failures[0].reason


def test_no_manifest_skips_completeness_check(tmp_path: Path) -> None:
    # An ad-hoc directory without a manifest declares no expected set, so a
    # single clean sample passes (completeness is only enforced via a manifest).
    _copy_seed(tmp_path, _SEED)
    assert vs.verify_samples(tmp_path) == []


def _manifest_for_seeds(*seeds: int) -> str:
    header = (
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
    )
    rows = "".join(
        f"| {seed} | m | (none) | d | s | 0.0000 | CREWMATES |\n" for seed in seeds
    )
    return header + rows


def test_unmanifested_sample_rejected(tmp_path: Path) -> None:
    # The manifest lists only seed 0, but seed 22's replay is also on disk. It
    # would be consumed by ReplayLoader (and any Phase 5 directory walk) with no
    # provenance row, so verification must reject the unmanifested extra.
    _copy_seed(tmp_path, _SEED)  # replay-seed-0.jsonl
    _copy_seed(tmp_path, _MEETING_SEED)  # replay-seed-22.jsonl (unmanifested)
    (tmp_path / "MANIFEST.md").write_text(_manifest_for_seeds(_SEED))
    failures = vs.verify_samples(tmp_path)
    assert [f.game_id for f in failures] == [f"headless-seed-{_MEETING_SEED}"]
    assert "not listed in MANIFEST.md" in failures[0].reason


def _corrupt_meeting_tick(path: Path, new_tick: int) -> None:
    """Point the first meeting record at a tick with no recorded tick row."""

    lines = path.read_text().splitlines()
    done = False
    out: list[str] = []
    for line in lines:
        obj = json.loads(line)
        if not done and obj.get("kind") == "meeting":
            obj["tick"] = new_tick
            done = True
            line = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        out.append(line)
    assert done
    path.write_text("\n".join(out) + "\n")


def test_orphaned_meeting_tick_detected(tmp_path: Path) -> None:
    path = _copy_seed(tmp_path, _MEETING_SEED)
    _corrupt_meeting_tick(path, 9999)  # no tick row exists at 9999
    # load_replay only attaches a meeting when a *reconstructed* tick enters
    # MEETING phase, so it silently drops the orphaned meeting and still
    # "succeeds" — this is the gap the tick-presence check closes.
    ReplayLoader(tmp_path).load_replay(f"headless-seed-{_MEETING_SEED}")
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    assert failures[0].game_id == f"headless-seed-{_MEETING_SEED}"
    assert "9999" in failures[0].reason
    assert "orphaned" in failures[0].reason
