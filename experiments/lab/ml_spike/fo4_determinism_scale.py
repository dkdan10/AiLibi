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
import math
import os
import struct
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)  # experiments/lab (Comment 4)
from ml_spike import core  # noqa: E402

TMP = core.tmp("fo4")
SEEDS = list(range(6))

# Augmented MLP: ENC_DIM + 1 inputs so the memory feature actually drives the
# action (Comment 5), not just the logged hash.
AUG_ENC = core.ENC_DIM + 1
AUG_LEN = AUG_ENC * core.HID + core.HID + core.HID * core.OUT + core.OUT


def _logit_hash(vec, logits) -> str:
    b = b"".join(struct.pack("<d", x) for x in vec) + b"|"
    b += b"".join(struct.pack("<d", x) for x in logits)
    return hashlib.sha256(b).hexdigest()[:16]


def _aug_forward(genome, x):
    """tanh-hidden MLP over AUG_ENC inputs (mirrors core.mlp_forward, +1 input)."""
    o1 = AUG_ENC * core.HID
    o2 = o1 + core.HID
    o3 = o2 + core.HID * core.OUT
    hidden = [0.0] * core.HID
    for j in range(core.HID):
        s = genome[o1 + j]
        base = j * AUG_ENC
        for i in range(AUG_ENC):
            s += genome[base + i] * x[i]
        hidden[j] = math.tanh(s)
    out = [0.0] * core.OUT
    for k in range(core.OUT):
        s = genome[o3 + k]
        base = o2 + k * core.HID
        for j in range(core.HID):
            s += genome[base + j] * hidden[j]
        out[k] = s
    return out


def _aug_vec(packet, visited_frac):
    return core.encode(packet) + [visited_frac]


def _aug_pick(genome, packet, visited_frac):
    room = packet.self_state.room
    cands = core._legal_rooms(room)
    if len(cands) == 1:
        return room
    out = _aug_forward(genome, _aug_vec(packet, visited_frac))
    best, best_key = room, None
    for c in sorted(cands):
        key = (out[core._ROOM_IX[c]], c)
        if best_key is None or key > best_key:
            best_key, best = key, c
    return best


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
            visited_frac = len(self._visited) / float(core.R)
            vec = _aug_vec(packet, visited_frac)
            logits = _aug_forward(self._genome, vec)
            self._sink.append(_logit_hash(vec, logits))
            # the memory feature drives the ACTION, not just the hash (Comment 5)
            room = _aug_pick(self._genome, packet, visited_frac)
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
    import random

    # augmented genome (memory feature in the action loop) for the stateful test.
    # ONE RNG instance, not a fresh Random(7) per weight (round-2 Comment 2: a fresh
    # seed per weight made every parameter identical -> all logits tie -> the pick fell
    # to the lexical tie-break and the memory feature never affected the action).
    _rng = random.Random(7)
    g_aug = [_rng.gauss(0.0, 0.5) for _ in range(AUG_LEN)]
    g = core.random_genome(7)  # core (memoryless) genome for the numpy backend leg
    print("=== FO-4 — determinism at scale ===")

    # (1)+(2) stateful encoder, two runs, compare replay bytes AND per-decision hashes
    sa: list[str] = []
    sb: list[str] = []
    run_stateful(SEEDS, TMP / "sa", g_aug, sa)
    run_stateful(SEEDS, TMP / "sb", g_aug, sb)
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
        # SKIP is not a PASS (Comment 6): exit non-zero so a numpy-less rerun cannot
        # look green while omitting the numpy determinism leg the report cites.
        print(
            "SKIPPED numpy backend leg — numpy not installed. Rerun with "
            "`uv run --with numpy python experiments/lab/ml_spike/fo4_determinism_scale.py`"
        )
        return 2

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

    # harvest real encoded states (+ current room) from one FSM game
    sink: list = []
    core.run_games([0], TMP / "harv", record_sink=sink)
    samples = [(x, cur) for (x, _c, cur) in sink]
    np_det = all(np_forward(x) == np_forward(x) for x, _cur in samples)

    def masked_pick(out: list[float], cur: str) -> str:
        # the recorded action masks to {current} ∪ adjacent rooms (round-2 Comment 4):
        # compare the LEGAL-masked pick, not the full-vector argmax, else an agreed
        # illegal global winner hides a real divergence in the legal candidates.
        best, best_key = cur, None
        for c in sorted(core._legal_rooms(cur)):
            key = (out[core._ROOM_IX[c]], c)
            if best_key is None or key > best_key:
                best_key, best = key, c
        return best

    disagree = 0
    for x, cur in samples:
        if masked_pick(core.mlp_forward(g, x), cur) != masked_pick(np_forward(x), cur):
            disagree += 1
    print(
        f"numpy backend: same-input bit-identical = {np_det}; "
        f"MASKED-legal pick disagrees w/ pure-Python on {disagree}/{len(samples)} real states"
    )
    print(
        "  (cross-MACHINE determinism remains untestable on one box; "
        "mitigation = quantize logits + lexical tie-break)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
