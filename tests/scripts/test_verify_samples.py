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

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REAL_SAMPLES = _REPO_ROOT / "replays" / "samples"
_VERIFY_SH = _REPO_ROOT / "scripts" / "verify_samples.sh"
_SEED = 0  # smallest committed sample: fast to reconstruct


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
