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
from orchestrator.replay_integrity import ReplayIntegrityError

_REPO_ROOT = Path(__file__).resolve().parents[2]
# The flat 4p1i baseline now lives under replays/samples/4p1i/ (Task 12.12).
_REAL_SAMPLES = _REPO_ROOT / "replays" / "samples" / "4p1i"
_REAL_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"
_VERIFY_SH = _REPO_ROOT / "scripts" / "verify_samples.sh"
_SEED = 0  # smallest committed sample: fast to reconstruct
_MEETING_SEED = 22  # a committed sample that contains a meeting

# The canonical samples were re-recorded on the Featherless / Qwen/Qwen3-32B
# substrate (prompt set qwen3_32b v4, Task 14.12 baseline 2) with ALL FIVE
# levers unconditionally ON: the four Phase-13.5 levers (the default since Task
# 14.9) plus the Task-14.10 evidence_quality_lift lever (stamped into game_over),
# whose env gate was retired at the Task-14.12 close. Because every lever is now
# env-independent, reconstruction matches the stamp under a BARE environment —
# no AILIBI_* export — so these reconstruction tests need no lever fixture (that
# is the whole point of the retirement; PR #218 Codex review). The wrapper test
# below drives scripts/verify_samples.sh under the ambient (bare) env, pinning
# that the MANIFEST-documented `bash scripts/verify_samples.sh` works clean.


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


def test_clean_sample_verifies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _copy_seed(tmp_path, _SEED)
    assert vs.verify_samples(tmp_path) == []


def test_corrupted_hash_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _copy_seed(tmp_path, _SEED)
    rc = vs.main([str(tmp_path)])
    assert rc == 0
    assert "verified clean" in capsys.readouterr().out


def test_main_corrupted_exit_one(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
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
    # An explicit SAMPLE_DIR arg verifies just that set. Every lever is
    # unconditional (Task-14.12 close), so reconstruction matches the recorded
    # substrate under the bare subprocess env — no lever export needed.
    proc = subprocess.run(
        ["bash", str(_VERIFY_SH), str(tmp_path)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )
    assert proc.returncode == 1
    assert f"tick {tick}" in proc.stdout


@pytest.mark.skipif(
    shutil.which("uv") is None or shutil.which("bash") is None,
    reason="needs uv + bash for the end-to-end shell wrapper",
)
def test_verify_sh_no_arg_walks_every_committed_set(tmp_path: Path) -> None:
    # The documented bare gate `bash scripts/verify_samples.sh` (no argument) must
    # verify EVERY committed set, not just the old 4p1i default — else a stale or
    # corrupted 9p2i replay slips through (PR #218 Codex review). Point
    # AILIBI_SAMPLES_ROOT at a tmp root holding one copied seed (+ its roster
    # sidecar) from each committed set and assert both are walked and pass clean.
    root = tmp_path / "samples"
    for name, src in (("4p1i", _REAL_SAMPLES), ("9p2i", _REAL_9P2I)):
        dst = root / name
        dst.mkdir(parents=True)
        (dst / f"replay-seed-{_SEED}.jsonl").write_bytes(
            (src / f"replay-seed-{_SEED}.jsonl").read_bytes()
        )
        # 9p2i reconstruction reads the roster sidecar; copy it so the seed
        # reconstructs (its absence is a divergence, not a wrapper concern).
        (dst / "roster.json").write_bytes((src / "roster.json").read_bytes())

    proc = subprocess.run(
        ["bash", str(_VERIFY_SH)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "AILIBI_SAMPLES_ROOT": str(root)},
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    # Both sets are walked (a header each) and both verify clean.
    assert "4p1i" in proc.stdout
    assert "9p2i" in proc.stdout
    assert proc.stdout.count("samples verified clean") == 2


def test_verify_sh_no_arg_fails_when_a_set_drifts(tmp_path: Path) -> None:
    # The aggregate exit status must be non-zero if ANY committed set drifts, so
    # the no-arg gate cannot pass while one set is corrupt.
    if shutil.which("uv") is None or shutil.which("bash") is None:
        pytest.skip("needs uv + bash for the end-to-end shell wrapper")
    root = tmp_path / "samples"
    # Set A: clean. Set B: one corrupted hash.
    clean = root / "4p1i"
    clean.mkdir(parents=True)
    (clean / f"replay-seed-{_SEED}.jsonl").write_bytes(
        (_REAL_SAMPLES / f"replay-seed-{_SEED}.jsonl").read_bytes()
    )
    (clean / "roster.json").write_bytes((_REAL_SAMPLES / "roster.json").read_bytes())
    drift = root / "9p2i"
    drift.mkdir(parents=True)
    drift_path = drift / f"replay-seed-{_SEED}.jsonl"
    drift_path.write_bytes((_REAL_9P2I / f"replay-seed-{_SEED}.jsonl").read_bytes())
    (drift / "roster.json").write_bytes((_REAL_9P2I / "roster.json").read_bytes())
    _corrupt_first_tick_hash(drift_path)

    proc = subprocess.run(
        ["bash", str(_VERIFY_SH)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "AILIBI_SAMPLES_ROOT": str(root)},
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr


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


def test_meeting_state_hash_before_corruption_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _copy_seed(tmp_path, _MEETING_SEED)
    tick = _corrupt_meeting_before_hash(path)
    with pytest.raises(ReplayIntegrityError, match="meeting_pre_hash_mismatch"):
        ReplayLoader(tmp_path).load_replay(f"headless-seed-{_MEETING_SEED}")
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.game_id == f"headless-seed-{_MEETING_SEED}"
    assert failure.tick == tick
    assert "meeting_pre_hash_mismatch" in failure.reason


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


def test_missing_canonical_seed_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A manifest declares seeds 0 and 22, but seed 22's replay is absent.
    _copy_seed(tmp_path, _SEED)  # only replay-seed-0.jsonl present
    (tmp_path / "MANIFEST.md").write_text(
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
        "| 0 | m | (none) | d | s | 0.0000 | CREWMATES |\n"
        "| 22 | m | accusation_round.qwen3_32b.v3 | d | s | 0.2000 | CREWMATES |\n"
    )
    failures = vs.verify_samples(tmp_path)
    assert [f.game_id for f in failures] == ["headless-seed-22"]
    assert "missing" in failures[0].reason


def test_no_manifest_skips_completeness_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_unmanifested_sample_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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


def test_orphaned_meeting_tick_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _copy_seed(tmp_path, _MEETING_SEED)
    _corrupt_meeting_tick(path, 9999)  # no tick row exists at 9999
    with pytest.raises(ReplayIntegrityError, match="row_order"):
        ReplayLoader(tmp_path).load_replay(f"headless-seed-{_MEETING_SEED}")
    failures = vs.verify_samples(tmp_path)
    assert len(failures) == 1
    assert failures[0].game_id == f"headless-seed-{_MEETING_SEED}"
    assert "9999" in failures[0].reason
    assert "row_order" in failures[0].reason
