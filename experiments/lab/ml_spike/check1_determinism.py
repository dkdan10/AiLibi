"""Check 1 — DETERMINISM (the cornerstone).

Does a float MLP in the recorded-action loop preserve byte-identical replay +
per-tick state hashes? Run the same seed twice with the same frozen genome and
diff. Also confirm the genome is LOAD-BEARING (genome-run != FSM-run), so a pass
is not the trivial "the MLP changed nothing".
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "check1"
SEEDS = list(range(8))


def main() -> int:
    genome = core.random_genome(7)
    a = TMP / "runA"
    b = TMP / "runB"
    fsm = TMP / "fsm"
    core.run_games(SEEDS, a, genome=genome)
    core.run_games(SEEDS, b, genome=genome)
    core.run_games(SEEDS, fsm, genome=None)

    byte_ok = hash_ok = load_bearing = 0
    for s in SEEDS:
        fa = a / f"replay-seed-{s}.jsonl"
        fb = b / f"replay-seed-{s}.jsonl"
        ff = fsm / f"replay-seed-{s}.jsonl"
        byte_ok += fa.read_bytes() == fb.read_bytes()
        hash_ok += core.state_hashes(fa) == core.state_hashes(fb)
        # genome run differs from FSM run on at least the action stream
        load_bearing += fa.read_bytes() != ff.read_bytes()

    n = len(SEEDS)
    print(f"=== Check 1 — determinism ({n} seeds, frozen genome, two runs each) ===")
    print(f"byte-identical replay (runA == runB):   {byte_ok}/{n}")
    print(f"identical state-hash chain (runA==runB): {hash_ok}/{n}")
    print(f"genome is load-bearing (genome != FSM):  {load_bearing}/{n}")
    verdict = "PASS" if byte_ok == n and hash_ok == n and load_bearing == n else "FAIL"
    print(f"VERDICT: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
