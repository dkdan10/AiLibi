#!/usr/bin/env python3
"""Record the Task-18.11 meeting-layer gate probe (FULL + CREW-ONLY), $0 real path.

The operator leg of the 18.11 gate: two 25-seed 9p2i probe sets on the real
Featherless path, one per arm, recorded to working dirs OUTSIDE the tree (the
probe is a working artifact — ``tasks/phase-18.md`` 18.11 Files-NOT-in-scope; only
the MEASUREMENTS are committed, into ``audits/audit-phase-18-meeting-gate.md``).

Two workers, one per arm, with WORK-STEALING: the moment an arm's seeds are all
recorded, that worker steals seeds from the slower arm so both finish together.
Per-seed invocations are load-bearing, not just convenient — every ``AILIBI_*``
lever is read ONCE at runner construction, so a worker cannot switch arms
mid-process; a stolen seed instead runs as a FRESH ``run_tournament.py`` process
under the other arm's env. The child env clears every live substrate lever in
``_ALL_LEVER_VARS`` (the four arm levers AND ``absence_prior``, which is part of
no arm) before applying the arm's own exports, and preflight additionally
REFUSES a parent-shell ``AILIBI_ABSENCE_PRIOR`` export outright (the
``record_ml_corpus.sh`` guard), so a stray export can neither leak into an arm's
recorded substrate stamp nor sit ambient when the validity gate later runs in
the same shell.

Resumable + Ctrl-C-safe: a seed whose ``replay-seed-<seed>.jsonl`` already carries
a ``game_over`` row is skipped, so re-running continues where a previous run (or a
container reclaim) stopped rather than restarting. ``^C`` halts in-flight seeds and
exits cleanly; the ≤ N_workers partial recordings left behind carry no
``game_over`` and are simply re-recorded (``--force``) on the next run.

Usage:
  uv run python scripts/record_meeting_gate_probe.py \
      --probe-root "$HOME/ailibi-probe-18-11" [--start-seed 2000] [--num-seeds 25] \
      [--workers 2] [--max-attempts 8] [--dry-run]

Requires (a real run refuses to start otherwise — no silent off-substrate record):
  FEATHERLESS_API_KEY set, AILIBI_LLM_PROVIDER=featherless,
  AILIBI_PROMPT_SET=qwen3_6_27b.

After it finishes, per the session runbook (arm flags exported so the ambient
snapshot matches the recorded stamp): remove ``*.audit.jsonl`` from each arm dir,
drop ``roster.json`` in, then ``scripts/validity_gate.py`` +
``scripts/verify_samples.sh`` + the four-cell measurement.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import FrameType

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_TOURNAMENT = REPO_ROOT / "scripts" / "run_tournament.py"

# The two probe arms and the ``AILIBI_*`` levers each exports (the merged
# 18.8/18.9/18.10 mechanisms; ``tasks/phase-18.md`` 18.11 implementation hint).
# FULL = the whole package; CREW-ONLY = the round + endpoint exemption only (the
# vent variant travels with the package and is measured on the FULL arm; the
# impostor-answer template arm stays default).
_ARMS: dict[str, dict[str, str]] = {
    "full": {
        "AILIBI_ROLL_CALL_ROUND": "1",
        "AILIBI_WHEREABOUTS_INTERIOR_FLAGS": "1",
        "AILIBI_VENT_PLACEMENT_CONTRADICTIONS": "1",
        "AILIBI_IMPOSTOR_ROLL_CALL": "1",
    },
    "crew-only": {
        "AILIBI_ROLL_CALL_ROUND": "1",
        "AILIBI_WHEREABOUTS_INTERIOR_FLAGS": "1",
    },
}

# Every LIVE substrate lever that is not part of an arm's own exports — cleared
# from the child env before an arm's vars are applied, so a crew-only seed can
# never inherit a stray FULL export and NO probe seed can inherit a stray
# absence-prior export (the recorded substrate stamp must reflect EXACTLY the
# arm under test; ``absence_prior`` is a live stamped toggle that is part of NO
# probe arm — its graduation rides the gate ruling, so a leak here would both
# change gameplay and contaminate bars (a)/(b)). The parent-shell export is
# additionally REFUSED at preflight, mirroring scripts/record_ml_corpus.sh's
# absence-prior guard.
_ALL_LEVER_VARS: tuple[str, ...] = (
    "AILIBI_ROLL_CALL_ROUND",
    "AILIBI_WHEREABOUTS_INTERIOR_FLAGS",
    "AILIBI_VENT_PLACEMENT_CONTRADICTIONS",
    "AILIBI_IMPOSTOR_ROLL_CALL",
    "AILIBI_ABSENCE_PRIOR",
)

_ARM_DIR: dict[str, str] = {"full": "full", "crew-only": "crew-only"}

# env var -> the substrate-flag snapshot key it toggles (orchestrator.replay's
# Task-18.11 registry). Used by the resume path to verify an existing
# recording's stamp actually matches its arm directory before skipping it.
_LEVER_STAMP_KEYS: dict[str, str] = {
    "AILIBI_ROLL_CALL_ROUND": "roll_call_round",
    "AILIBI_WHEREABOUTS_INTERIOR_FLAGS": "whereabouts_interior_flags",
    "AILIBI_VENT_PLACEMENT_CONTRADICTIONS": "vent_placement_contradictions",
    "AILIBI_IMPOSTOR_ROLL_CALL": "impostor_roll_call",
    "AILIBI_ABSENCE_PRIOR": "absence_prior",
}

# The locked eval model (llm.featherless_client.DEFAULT_FEATHERLESS_MODEL, the
# Task-16.2 lock) — duplicated here as a literal so this operator script stays
# stdlib-only (it is invoked from arbitrary CWDs where the repo packages may
# not be importable); the validity gate re-pins the same id from the bytes.
_LOCKED_MODEL: str = "Qwen/Qwen3.6-27B"

# The canonical hosted endpoint (llm.featherless_client
# .DEFAULT_FEATHERLESS_BASE_URL) — the same literal scripts/record_ml_corpus.sh
# pins. build_default_client honors AILIBI_FEATHERLESS_BASE_URL, so a leftover
# mock/staging export would record the whole probe against an alternate
# endpoint while the model/cost census still LOOKS coherent (a mock can echo
# the locked model id at $0) — preflight refuses any non-default value.
_DEFAULT_BASE_URL: str = "https://api.featherless.ai/v1"

# Cooperative-stop signal, shared across the worker threads; the SIGINT handler
# sets it and terminates in-flight children so ^C is responsive.
_STOP = threading.Event()
_ACTIVE_LOCK = threading.Lock()
_ACTIVE: dict[str, "subprocess.Popen[bytes]"] = {}
_PRINT_LOCK = threading.Lock()


def _log(message: str) -> None:
    with _PRINT_LOCK:
        print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def _fmt_duration(seconds: float) -> str:
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"


def _has_game_over(path: Path) -> bool:
    """Whether ``path`` is a COMPLETE recording (carries a ``game_over`` row).

    A partial recording (an interrupted or crashed seed) never reaches the
    ``game_over`` final row, so this is the resume predicate: complete → skip,
    partial/absent → (re-)record.
    """

    if not path.exists():
        return False
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            # A valid-JSON-but-non-object line (a corrupt row) must read as
            # "incomplete", not crash the resume scan.
            if isinstance(row, dict) and row.get("kind") == "game_over":
                return True
    except (OSError, json.JSONDecodeError):
        return False
    return False


def _recorded_stamp_matches_arm(path: Path, arm: str) -> bool:
    """Whether an existing recording's substrate stamp matches ``arm`` exactly.

    The resume guard: a per-seed file left by an OLDER, interrupted, or
    polluted run (a full/ seed stamped crew-only, an absence-prior-ON stamp, a
    file copied between arm dirs) must NOT be skipped as "already recorded" —
    it would contaminate the arm's measurements while the completeness pass
    reads green. Reads the ``game_over`` row's ``substrate_flags`` and requires
    every lever in :data:`_LEVER_STAMP_KEYS` to equal the arm's intent: True
    iff the lever is in ``_ARMS[arm]`` (``absence_prior`` is in no arm, so it
    must stamp False/absent). A missing stamp fails the match (fail-safe:
    re-record). Callers only invoke this on files :func:`_has_game_over`
    accepted, so the parse cannot raise here.
    """

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or row.get("kind") != "game_over":
            continue
        flags = row.get("substrate_flags")
        if not isinstance(flags, dict):
            return False
        return all(
            bool(flags.get(stamp_key)) == (env_var in _ARMS[arm])
            for env_var, stamp_key in _LEVER_STAMP_KEYS.items()
        )
    return False


@dataclass
class _Board:
    """The shared, lock-protected work board for the two arms."""

    remaining: dict[str, list[int]]
    total_units: int
    done: int = 0
    failed: list[tuple[str, int]] = field(default_factory=list)
    durations: list[float] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def claim(self, home_arm: str) -> tuple[str, int] | None:
        """Claim the next seed: the worker's home arm first, else steal.

        Stealing prefers the arm with the most remaining seeds, so two workers
        converge on the slowest arm and both finish together.
        """

        with self.lock:
            if self.remaining.get(home_arm):
                return home_arm, self.remaining[home_arm].pop(0)
            candidates = sorted(
                (arm for arm, seeds in self.remaining.items() if seeds),
                key=lambda arm: len(self.remaining[arm]),
                reverse=True,
            )
            if not candidates:
                return None
            arm = candidates[0]
            return arm, self.remaining[arm].pop(0)

    def record_done(self, duration: float) -> None:
        with self.lock:
            self.done += 1
            self.durations.append(duration)

    def record_failure(self, arm: str, seed: int) -> None:
        with self.lock:
            self.failed.append((arm, seed))

    def snapshot(self) -> tuple[int, int, float]:
        """(done, remaining_units, mean_seed_duration) under the lock."""

        with self.lock:
            remaining = sum(len(seeds) for seeds in self.remaining.values())
            mean = sum(self.durations) / len(self.durations) if self.durations else 0.0
            return self.done, remaining, mean

    def per_arm_left(self) -> dict[str, int]:
        with self.lock:
            return {arm: len(seeds) for arm, seeds in self.remaining.items()}


def _eta(board: _Board, workers: int) -> str:
    _done, remaining, mean = board.snapshot()
    if mean <= 0.0 or remaining == 0:
        return "estimating…" if remaining else "0s"
    # Both workers stay busy (work-stealing) until the tail, so the remaining
    # wall is roughly ceil(remaining / workers) seeds at the mean per-seed cost.
    waves = -(-remaining // max(1, workers))
    return "~" + _fmt_duration(waves * mean)


def _child_env(arm: str) -> dict[str, str]:
    env = dict(os.environ)
    for var in _ALL_LEVER_VARS:
        env.pop(var, None)
    env.update(_ARMS[arm])
    return env


def _record_seed(
    *,
    arm: str,
    seed: int,
    arm_dir: Path,
    reports_dir: Path,
    max_attempts: int,
    worker: str,
) -> tuple[bool, float]:
    """Record ONE seed under ``arm``'s env, with crash-retry + jittered backoff.

    Returns ``(ok, wall_seconds)``. ``ok`` is True only when the child exits 0 AND
    the seed's replay carries a ``game_over`` row (a recorded parse failure is not
    a crash — ``run_tournament`` persists it and still completes the game). Mirrors
    the ``scripts/record_ml_corpus.sh`` per-seed retry loop, since
    ``run_tournament.py`` itself does not read ``AILIBI_SEED_MAX_ATTEMPTS``.
    """

    replay_path = arm_dir / f"replay-seed-{seed}.jsonl"
    report_path = reports_dir / f"{arm}-seed-{seed}.json"
    env = _child_env(arm)
    started = time.monotonic()
    for attempt in range(1, max_attempts + 1):
        if _STOP.is_set():
            return False, time.monotonic() - started
        cmd = [
            sys.executable,
            str(RUN_TOURNAMENT),
            "--roster-preset",
            "9p2i",
            "--start-seed",
            str(seed),
            "--num-games",
            "1",
            "--output-dir",
            str(arm_dir),
            "--report-output",
            str(report_path),
            "--force",
        ]
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        key = f"{worker}:{arm}:{seed}"
        with _ACTIVE_LOCK:
            _ACTIVE[key] = proc
        _, stderr = proc.communicate()
        with _ACTIVE_LOCK:
            _ACTIVE.pop(key, None)
        if _STOP.is_set():
            return False, time.monotonic() - started
        if proc.returncode == 0 and _has_game_over(replay_path):
            # Drop the per-seed audit sidecar: it is not needed for measurement
            # and its ``replay-seed-<seed>.audit.jsonl`` name matches the
            # ``replay-seed-*.jsonl`` glob the validity gate / funnel folds use,
            # so leaving it would break every downstream read. The arm dir is
            # then measurement-ready (only ``roster.json`` still needs dropping in).
            audit_path = arm_dir / f"replay-seed-{seed}.audit.jsonl"
            audit_path.unlink(missing_ok=True)
            return True, time.monotonic() - started
        # Deterministic-enough jittered backoff (2s, 4s, 8s, … capped), varied by
        # seed so two workers retrying at once do not resynchronise on the plan.
        if attempt < max_attempts:
            backoff = min(2**attempt, 30) + (seed % 5)
            tail = (stderr or b"").decode("utf-8", "replace").strip().splitlines()
            reason = tail[-1] if tail else f"exit {proc.returncode}"
            _log(
                f"{worker} [{arm}] seed {seed} attempt {attempt}/{max_attempts} "
                f"failed ({reason}); retrying in {backoff}s"
            )
            for _ in range(backoff):
                if _STOP.is_set():
                    return False, time.monotonic() - started
                time.sleep(1)
    return False, time.monotonic() - started


def _worker(
    *,
    name: str,
    home_arm: str,
    board: _Board,
    probe_root: Path,
    reports_dir: Path,
    max_attempts: int,
    workers: int,
) -> None:
    while not _STOP.is_set():
        claim = board.claim(home_arm)
        if claim is None:
            _log(f"{name} [{home_arm}] no work left — exiting")
            return
        arm, seed = claim
        stolen = "" if arm == home_arm else f" (stolen from {arm})"
        left = board.per_arm_left()
        done, remaining, _mean = board.snapshot()
        _log(
            f"{name} [{arm}] recording seed {seed}{stolen}  "
            f"[full {left.get('full', 0)} left, crew-only "
            f"{left.get('crew-only', 0)} left | {remaining} queued | "
            f"{done}/{board.total_units} done | ETA {_eta(board, workers)}]"
        )
        ok, dur = _record_seed(
            arm=arm,
            seed=seed,
            arm_dir=probe_root / _ARM_DIR[arm],
            reports_dir=reports_dir,
            max_attempts=max_attempts,
            worker=name,
        )
        if _STOP.is_set():
            _log(
                f"{name} [{arm}] seed {seed} interrupted after {_fmt_duration(dur)} "
                "— will re-record on resume"
            )
            return
        if ok:
            board.record_done(dur)
            done, remaining, _mean = board.snapshot()
            _log(
                f"{name} [{arm}] seed {seed} DONE in {_fmt_duration(dur)}  "
                f"[{done}/{board.total_units} done | {remaining} left | "
                f"ETA {_eta(board, workers)}]"
            )
        else:
            board.record_failure(arm, seed)
            _log(
                f"{name} [{arm}] seed {seed} FAILED after {max_attempts} attempts "
                "— left unrecorded (re-run to retry)"
            )


def _build_board(
    *, start_seed: int, num_seeds: int, probe_root: Path
) -> tuple[_Board, int]:
    """Build the work board, skipping seeds already recorded (resume).

    "Already recorded" requires BOTH a ``game_over`` row AND a substrate stamp
    that matches the arm directory (:func:`_recorded_stamp_matches_arm`): a
    complete-looking file whose stamp names a different arm (or a stray
    ``absence_prior`` ON) is queued for re-record with a loud notice, never
    silently counted complete.
    """

    seeds = list(range(start_seed, start_seed + num_seeds))
    remaining: dict[str, list[int]] = {}
    already = 0
    for arm in _ARMS:
        arm_dir = probe_root / _ARM_DIR[arm]
        arm_dir.mkdir(parents=True, exist_ok=True)
        pending: list[int] = []
        for seed in seeds:
            replay_path = arm_dir / f"replay-seed-{seed}.jsonl"
            if _has_game_over(replay_path):
                if _recorded_stamp_matches_arm(replay_path, arm):
                    already += 1
                    continue
                _log(
                    f"[{arm}] seed {seed}: existing recording's substrate stamp "
                    f"does NOT match the {arm} arm — re-recording it"
                )
            pending.append(seed)
        remaining[arm] = pending
    total = num_seeds * len(_ARMS)
    board = _Board(remaining=remaining, total_units=total, done=already)
    return board, already


def _preflight(*, dry_run: bool) -> None:
    """Fail loud on a missing / wrong substrate env (no silent off-substrate)."""

    problems: list[str] = []
    provider = os.environ.get("AILIBI_LLM_PROVIDER", "")
    prompt_set = os.environ.get("AILIBI_PROMPT_SET", "")
    if provider != "featherless":
        problems.append(f"AILIBI_LLM_PROVIDER must be 'featherless' (got {provider!r})")
    if prompt_set != "qwen3_6_27b":
        problems.append(
            "AILIBI_PROMPT_SET must be 'qwen3_6_27b' — the impostor-answer variant "
            f"is authored only for that set (got {prompt_set!r})"
        )
    if not os.environ.get("FEATHERLESS_API_KEY"):
        problems.append("FEATHERLESS_API_KEY must be set for the real-path probe")
    for model_var in ("AILIBI_LLM_MEETING_MODEL", "AILIBI_LLM_TRIGGER_MODEL"):
        # The record_ml_corpus.sh model-override guard, mirrored: an exported
        # override routes llm.provider.build_default_client to a NON-LOCKED
        # model while this preflight's provider/prompt-set checks still pass —
        # the multi-hour probe would then record off-model, caught only later
        # by the validity gate's model census. Unset, or exactly the locked
        # model, are the only acceptable states.
        override = os.environ.get(model_var, "").strip()
        if override and override != _LOCKED_MODEL:
            problems.append(
                f"{model_var}={override!r} would record the probe on a "
                f"non-locked model (the Task-16.2 lock is {_LOCKED_MODEL!r}); "
                "unset it or set it to the locked model"
            )
    base_url_override = os.environ.get("AILIBI_FEATHERLESS_BASE_URL", "").strip()
    if base_url_override and base_url_override != _DEFAULT_BASE_URL:
        # The record_ml_corpus.sh endpoint guard, mirrored: a leftover
        # mock/staging endpoint can echo the locked model id at $0, so the
        # validity gate's census would NOT catch it — refuse before any spend.
        problems.append(
            f"AILIBI_FEATHERLESS_BASE_URL={base_url_override!r} would record "
            f"the probe against a non-canonical endpoint (the hosted default "
            f"is {_DEFAULT_BASE_URL!r}); unset it before recording"
        )
    if os.environ.get("AILIBI_ABSENCE_PRIOR", "").strip():
        # The record_ml_corpus.sh absence-prior guard, mirrored: the lever is a
        # live stamped toggle that is part of NO probe arm (its graduation rides
        # the gate ruling). The child env scrubs it too (_ALL_LEVER_VARS), but a
        # polluted parent shell would ALSO run the later validity gate under the
        # same export — refuse up front rather than record anything from a shell
        # whose ambient substrate disagrees with the probe's intent.
        problems.append(
            "AILIBI_ABSENCE_PRIOR is exported — the absence prior is not part of "
            "any probe arm (its graduation rides the 18.11 ruling); unset it "
            "before recording"
        )
    if problems and not dry_run:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        raise SystemExit(2)
    if problems and dry_run:
        for problem in problems:
            _log(f"[dry-run] would refuse a real run: {problem}")


def _run_metadata_now() -> dict[str, str]:
    """The endpoint/model/substrate lineage of THIS run, as preflight resolved it."""

    return {
        "base_url": os.environ.get("AILIBI_FEATHERLESS_BASE_URL", "").strip()
        or _DEFAULT_BASE_URL,
        "model": _LOCKED_MODEL,
        "provider": os.environ.get("AILIBI_LLM_PROVIDER", ""),
        "prompt_set": os.environ.get("AILIBI_PROMPT_SET", ""),
    }


def _check_run_metadata(probe_root: Path, *, dry_run: bool) -> None:
    """Bind resumed files to a verifiable run lineage (``.probe-meta.json``).

    The replay bytes do not record WHICH endpoint served them, so a resumed
    file that passes the stamp check could still predate the endpoint pin (or
    come from a mock that echoed the locked model at $0) — the preflight only
    protects children this run actually launches. The marker closes that gap:
    a fresh run writes the resolved endpoint/model/provider/prompt-set to
    ``<probe-root>/.probe-meta.json`` BEFORE any seed records; a resume run
    refuses when the marker mismatches the current environment, and refuses
    completed files that predate the marker entirely (an unverifiable lineage
    — delete them or move them out to proceed). Dry-run reports and writes
    nothing.
    """

    marker = probe_root / ".probe-meta.json"
    now = _run_metadata_now()
    have_completed = any(
        _has_game_over(path)
        for arm in _ARMS
        for path in sorted((probe_root / _ARM_DIR[arm]).glob("replay-seed-*.jsonl"))
        if (probe_root / _ARM_DIR[arm]).is_dir()
        and not path.name.endswith(".audit.jsonl")
    )
    if marker.exists():
        recorded = json.loads(marker.read_text(encoding="utf-8"))
        if recorded != now:
            print(
                f"error: {marker} records a different run lineage "
                f"({recorded!r}) than the current environment ({now!r}); "
                "completed files under this root cannot be mixed with a "
                "different endpoint/model/prompt-set — fix the environment or "
                "use a fresh --probe-root",
                file=sys.stderr,
            )
            raise SystemExit(2)
        return
    if have_completed:
        print(
            f"error: {probe_root} holds completed recordings but no "
            f"{marker.name} lineage marker — their recording endpoint is "
            "unverifiable (they may predate the endpoint pin or come from a "
            "mock that echoed the locked model). Delete or move them, or "
            "re-record into a fresh --probe-root",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if dry_run:
        _log(f"[dry-run] would write the run-lineage marker {marker}")
        return
    probe_root.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(now, indent=2, sort_keys=True), encoding="utf-8")
    _log(f"wrote run-lineage marker {marker}")


def _install_sigint() -> None:
    def _handler(_signum: int, _frame: FrameType | None) -> None:
        if _STOP.is_set():
            return
        _STOP.set()
        # No _log here: the handler runs on the main thread, which may already
        # hold the non-reentrant _PRINT_LOCK inside _log — taking it again would
        # deadlock the handler. A bare os.write to stderr is async-signal-safe
        # enough for this one-line notice.
        os.write(
            2,
            b"\n^C - halting in-flight seeds; re-run the same command to resume.\n",
        )
        with _ACTIVE_LOCK:
            for proc in _ACTIVE.values():
                try:
                    proc.terminate()
                except ProcessLookupError:
                    pass

    signal.signal(signal.SIGINT, _handler)


def _print_plan(board: _Board, *, workers: int, max_attempts: int) -> None:
    left = board.per_arm_left()
    _log(
        f"probe plan: {board.total_units} units "
        f"(full {left.get('full', 0)} to record, crew-only "
        f"{left.get('crew-only', 0)} to record; {board.done} already recorded), "
        f"{workers} workers, up to {max_attempts} attempts/seed"
    )


def _dispatch_workers(
    *, board: _Board, probe_root: Path, args: argparse.Namespace
) -> None:
    reports_dir = probe_root / ".reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    home_arms = list(_ARMS)
    threads: list[threading.Thread] = []
    for index in range(args.workers):
        home = home_arms[index % len(home_arms)]
        thread = threading.Thread(
            target=_worker,
            kwargs={
                "name": f"worker-{index + 1}",
                "home_arm": home,
                "board": board,
                "probe_root": probe_root,
                "reports_dir": reports_dir,
                "max_attempts": args.max_attempts,
                "workers": args.workers,
            },
            daemon=True,
        )
        threads.append(thread)
        thread.start()
        # Stagger worker starts (the 16.14 ballot-collision note) so two fresh
        # Featherless requests do not launch in lock-step.
        if index + 1 < args.workers and not _STOP.is_set():
            time.sleep(min(60, 5 + index * 5))
    for thread in threads:
        while thread.is_alive():
            thread.join(timeout=1.0)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--probe-root",
        required=True,
        type=Path,
        help="working dir OUTSIDE the repo; arms record under <root>/full and "
        "<root>/crew-only (nothing here is committed)",
    )
    parser.add_argument("--start-seed", type=int, default=2000)
    parser.add_argument("--num-seeds", type=int, default=25)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=int(os.environ.get("AILIBI_SEED_MAX_ATTEMPTS", "8")),
        help="crash-retry attempts per seed (default: AILIBI_SEED_MAX_ATTEMPTS or 8)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the plan and the per-seed assignment; touch no network",
    )
    args = parser.parse_args(argv)

    if args.num_seeds < 1 or args.workers < 1 or args.max_attempts < 1:
        parser.error("--num-seeds, --workers, and --max-attempts must be >= 1")

    # Probe recordings are working artifacts OUTSIDE the tree (18.11
    # Files-NOT-in-scope) — refuse a root under the repo before creating
    # anything, dry-run included (a relative path from the repo root would
    # otherwise dirty the worktree with out-of-scope replay sets).
    probe_root: Path = args.probe_root.resolve()
    repo = REPO_ROOT.resolve()
    if probe_root == repo or repo in probe_root.parents:
        parser.error(
            f"--probe-root {probe_root} is inside the repository ({repo}); "
            "probe recordings are working artifacts and must live OUTSIDE the "
            "tree — pick a path outside the repo"
        )

    _preflight(dry_run=args.dry_run)
    _check_run_metadata(probe_root, dry_run=args.dry_run)
    board, already = _build_board(
        start_seed=args.start_seed, num_seeds=args.num_seeds, probe_root=probe_root
    )
    _print_plan(board, workers=args.workers, max_attempts=args.max_attempts)
    if already:
        _log(
            f"resuming: {already}/{board.total_units} seeds already recorded — skipped"
        )

    _done, remaining, _mean = board.snapshot()
    if remaining == 0:
        _log("nothing to record — every seed already carries a game_over. Done.")
        return 0

    if args.dry_run:
        for arm, seeds in board.per_arm_left().items():
            _log(f"[dry-run] {arm}: {seeds} seeds to record → {probe_root / arm}")
        _log("[dry-run] no network touched.")
        return 0

    _install_sigint()
    _log(
        f"recording to {probe_root} — seeds "
        f"{args.start_seed}..{args.start_seed + args.num_seeds - 1} per arm"
    )
    wall_started = time.monotonic()
    _dispatch_workers(board=board, probe_root=probe_root, args=args)
    elapsed = time.monotonic() - wall_started

    done, remaining, _mean = board.snapshot()
    if _STOP.is_set():
        _log(
            f"stopped after {_fmt_duration(elapsed)} — {done}/{board.total_units} "
            "recorded. Re-run the SAME command to resume."
        )
        return 130
    if board.failed:
        _log(
            f"finished with {len(board.failed)} unrecorded seed(s): "
            f"{sorted(board.failed)} — re-run to retry them."
        )
        return 1
    # Completeness is re-derived FROM DISK, never from the counters: a worker
    # thread that died on an unexpected exception leaves its claimed seed
    # unrecorded without touching board.failed, and "ALL recorded" on an
    # incomplete probe would silently starve the gate measurement.
    final_board, _ = _build_board(
        start_seed=args.start_seed, num_seeds=args.num_seeds, probe_root=probe_root
    )
    _done, still_missing, _mean = final_board.snapshot()
    if still_missing:
        _log(
            f"finished but {still_missing} seed(s) are NOT on disk with a "
            f"game_over ({dict(final_board.per_arm_left())}) — a worker likely "
            "died; re-run the SAME command to record them."
        )
        return 1
    _log(
        f"ALL {board.total_units} seeds recorded in {_fmt_duration(elapsed)}. "
        "Next: remove *.audit.jsonl, drop roster.json, validity-gate + verify + "
        "measure each arm (arm flags exported)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
