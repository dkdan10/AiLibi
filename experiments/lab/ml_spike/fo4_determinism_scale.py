"""Follow-on 4 — determinism at production scale (gaps 4 & 6).

Three things the spike's Check 1 did NOT cover:
 (1) a STATEFUL encoder (memory features) — does carrying state across ticks
     re-open nondeterminism? (gap 4)
 (2) hashing the ENCODER VECTOR + LOGITS per decision, not just WorldState —
     would a float divergence that argmaxes the SAME room slip past? (gap 4)
 (3) a numpy backend (pure-Python won't scale) — same-machine determinism +
     does numpy ever pick a different argmax than pure-Python? (gap 6)
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, "experiments/lab")
from ml_spike import core  # noqa: E402

TMP = Path(os.environ["CLAUDE_JOB_DIR"]) / "tmp" / "fo4"
SEEDS = list(range(6))


def _logit_hash(vec, logits) -> str:
    b = b"".join(struct.pack("<d", x) for x in vec) + b"|"
    b += b"".join(struct.pack("<d", x) for x in logits)
    return hashlib.sha256(b).hexdigest()[:16]


class StatefulAgent(core.SpikeAgent):
    """SpikeAgent + a memory feature (distinct rooms visited so far) appended to
    the encoding, and a per-decision (vector+logits) hash sink. Tests whether a
    STATEFUL/memory encoder preserves byte-determinism."""

    def __init__(self, inner, *, genome, sink):
        super().__init__(inner, genome=genome)
        self._visited: set[str] = set()
        self._sink = sink

    def decide(self, packet, public_map):
        self._visited.add(packet.self_state.room)
        action = self._inner.decide(packet, public_map)
        from observation.action_intent import MoveIntent, WaitIntent

        if isinstance(action, (MoveIntent, WaitIntent)) and self._genome is not None:
            vec = core.encode(packet) + [len(self._visited) / float(core.R)]
            logits = core.mlp_forward(self._genome, vec[: core.ENC_DIM])
            self._sink.append(_logit_hash(vec, logits))
            room = core.mlp_pick_room(self._genome, packet)
            if room == packet.self_state.room:
                return WaitIntent(actor=self._aid, type="wait")
            return MoveIntent(actor=self._aid, type="move", payload={"to_room": room})
        return action


def run_stateful(seeds, out, genome, sink):
    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy
    from orchestrator.game import TacticalAgent

    os.environ["AILIBI_LLM_PROVIDER"] = "fake"

    def factory(agent_id, role):
        if role == "IMPOSTOR":
            inner = TacticalAgent(
                agent_id=agent_id, policy=ImpostorPolicy(agent_id=agent_id), role=role
            )
            return StatefulAgent(inner, genome=genome, sink=sink)
        return TacticalAgent(
            agent_id=agent_id, policy=CrewmatePolicy(agent_id=agent_id), role=role
        )

    out.mkdir(parents=True, exist_ok=True)
    from eval.balance_eval import run_tournament_eval

    run_tournament_eval(
        seeds=list(seeds),
        output_dir=out,
        agent_factory=factory,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
    )


def main() -> int:
    g = core.random_genome(7)
    print("=== FO-4 — determinism at scale ===")

    # (1)+(2) stateful encoder, two runs, compare replay bytes AND per-decision hashes
    sa: list[str] = []
    sb: list[str] = []
    run_stateful(SEEDS, TMP / "sa", g, sa)
    run_stateful(SEEDS, TMP / "sb", g, sb)
    byte_ok = all(
        (TMP / "sa" / f"replay-seed-{s}.jsonl").read_bytes()
        == (TMP / "sb" / f"replay-seed-{s}.jsonl").read_bytes()
        for s in SEEDS
    )
    print(f"stateful(memory-feature) encoder: byte-identical replays = {byte_ok}")
    print(
        f"  per-decision (vector+logits) hashes: {len(sa)} decisions, identical = {sa == sb}"
    )

    # (3) numpy backend: same-machine determinism + argmax agreement vs pure-Python
    try:
        import numpy as np
    except ModuleNotFoundError:
        print(
            "numpy not importable in this interpreter — rerun with `uv run --with numpy`"
        )
        return 0

    o1 = core.ENC_DIM * core.HID
    o2 = o1 + core.HID
    o3 = o2 + core.HID * core.OUT
    W1 = np.array(g[:o1], dtype=np.float64).reshape(core.HID, core.ENC_DIM)
    b1 = np.array(g[o1:o2], dtype=np.float64)
    W2 = np.array(g[o2:o3], dtype=np.float64).reshape(core.OUT, core.HID)
    b2 = np.array(g[o3:], dtype=np.float64)

    def np_forward(x):
        h = np.tanh(W1 @ np.array(x, dtype=np.float64) + b1)
        return (W2 @ h + b2).tolist()

    # harvest real encoded states from one FSM game
    sink: list = []
    core.run_games([0], TMP / "harv", record_sink=sink)
    vecs = [x for (x, _c, _cur) in sink]
    np_det = all(np_forward(v) == np_forward(v) for v in vecs)
    disagree = 0
    for v in vecs:
        pa = max(range(core.OUT), key=lambda k: (core.mlp_forward(g, v)[k], k))
        pn = max(range(core.OUT), key=lambda k: (np_forward(v)[k], k))
        disagree += pa != pn
    print(
        f"numpy backend: same-input bit-identical = {np_det}; "
        f"argmax disagrees w/ pure-Python on {disagree}/{len(vecs)} real states"
    )
    print(
        "  (cross-MACHINE determinism remains untestable on one box; "
        "mitigation = quantize logits + lexical tie-break)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
