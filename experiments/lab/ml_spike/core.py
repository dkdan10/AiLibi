"""ML feasibility spike — core harness (throwaway, design-thread, $0).

Charter: experiments/lab/ml-spike-charter.md. Proves three things on the EXISTING
substrate with ZERO engine edits and NO new dependencies (pure-Python MLP =
airtight byte-determinism, no BLAS):

* the learnable decision = the impostor MOVE choice (frequent, always-legal, puts
  a float MLP argmax in the recorded-action loop);
* injection = a proxy AgentInterface that calls the real FSM TacticalAgent, then
  overrides ONLY a Move/Wait intent with the MLP's pick among legal rooms, and
  delegates everything else (kills, vents, cover, do_task, and the whole meeting
  protocol) to the inner agent unchanged;
* fitness = total impostor kills over K seeds (non-degenerate: random moves wreck
  the FSM's stalk, so the gap to climb is real and BC-from-FSM should recover it).
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import tempfile
from pathlib import Path

# Make `engine`/`eval`/... importable even when a check is run as a bare script from
# any CWD, without requiring PYTHONPATH=. or the Claude env (Comment 4).
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def tmp(name: str) -> Path:
    """Per-probe scratch dir. Uses CLAUDE_JOB_DIR when set, else the system temp dir
    so the committed experiments run from a normal checkout (Comment 4)."""
    base = os.environ.get("CLAUDE_JOB_DIR") or tempfile.gettempdir()
    return Path(base) / "ailibi_ml_spike" / name


from agents.tactical.crewmate_policy import CrewmatePolicy  # noqa: E402
from agents.tactical.impostor_policy import ImpostorPolicy  # noqa: E402
from eval.balance_eval import run_tournament_eval  # noqa: E402
from observation.action_intent import MoveIntent, WaitIntent  # noqa: E402
from orchestrator.game import TacticalAgent  # noqa: E402

# --- fixed topology (canonical_1): sorted for a stable id->index encoding -------
from engine.world import load_canonical_map  # noqa: E402

_MAP = load_canonical_map()
ROOMS: tuple[str, ...] = tuple(sorted(_MAP.rooms.keys()))
R = len(ROOMS)
_ROOM_IX = {r: i for i, r in enumerate(ROOMS)}

ENC_DIM = 3 * R + 4  # room onehot + players/room + bodies/room + 4 scalars
HID = 16
OUT = R
GENOME_LEN = ENC_DIM * HID + HID + HID * OUT + OUT


# --- encoder: ObservationPacket -> fixed float vector (deterministic) ----------
def encode(packet) -> list[float]:
    v = [0.0] * ENC_DIM
    room = packet.self_state.room
    if room in _ROOM_IX:
        v[_ROOM_IX[room]] = 1.0
    for p in packet.visible_players:
        if p.room in _ROOM_IX:
            v[R + _ROOM_IX[p.room]] += 1.0 / 8.0
    for b in packet.visible_bodies:
        if b.room in _ROOM_IX:
            v[2 * R + _ROOM_IX[b.room]] += 1.0
    cd = packet.cooldown
    v[3 * R + 0] = 0.0 if cd is None else min(float(cd) / 5.0, 2.0)
    v[3 * R + 1] = 1.0 if packet.self_state.in_vent else 0.0
    v[3 * R + 2] = float(packet.global_state.task_completion_percent)
    v[3 * R + 3] = 1.0 if packet.global_state.sabotage_active else 0.0
    return v


# --- pure-Python MLP: genome (flat floats) -> per-room scores -------------------
def mlp_forward(genome: list[float], x: list[float]) -> list[float]:
    o1 = ENC_DIM * HID
    o2 = o1 + HID
    o3 = o2 + HID * OUT
    hidden = [0.0] * HID
    for j in range(HID):
        s = genome[o1 + j]
        base = j * ENC_DIM
        for i in range(ENC_DIM):
            s += genome[base + i] * x[i]
        hidden[j] = math.tanh(s)
    out = [0.0] * OUT
    for k in range(OUT):
        s = genome[o3 + k]
        base = o2 + k * HID
        for j in range(HID):
            s += genome[base + j] * hidden[j]
        out[k] = s
    return out


def random_genome(seed: int, scale: float = 0.5) -> list[float]:
    rng = random.Random(seed)
    return [rng.gauss(0.0, scale) for _ in range(GENOME_LEN)]


def mutate(genome: list[float], seed: int, sigma: float = 0.15) -> list[float]:
    rng = random.Random(seed)
    return [w + rng.gauss(0.0, sigma) for w in genome]


def _legal_rooms(room: str) -> list[str]:
    """Candidate move targets = stay (current) + adjacent rooms. All legal."""
    nbrs = _MAP.room_neighbors(room) if room in _ROOM_IX else ()
    cands = [room] + [n for n in nbrs if n in _ROOM_IX]
    # stable, de-duped
    seen: dict[str, None] = {}
    for c in cands:
        seen.setdefault(c, None)
    return list(seen.keys())


def mlp_pick_room(genome: list[float], packet) -> str:
    room = packet.self_state.room
    cands = _legal_rooms(room)
    if len(cands) == 1:
        return room
    out = mlp_forward(genome, encode(packet))
    # argmax over candidates, lexical room-id tie-break (deterministic)
    best = None
    best_key: tuple[float, str] | None = None
    for c in sorted(cands):
        score = out[_ROOM_IX[c]]
        key = (score, c)
        if best_key is None or key > best_key:
            best_key = key
            best = c
    return best  # type: ignore[return-value]


# --- the proxy agent: override only Move/Wait, delegate the rest ----------------
class SpikeAgent:
    """AgentInterface proxy around a real TacticalAgent.

    record_sink mode: log (encode(packet), chosen_room) for every Move/Wait the
    FSM makes (BC data), return the FSM action unchanged.
    play mode (genome set): replace a Move/Wait with the MLP's room pick.
    Everything else (kills/vents/cover/do_task + the meeting protocol + role/
    agent_id/memory) delegates to the inner agent via __getattr__.
    """

    def __init__(self, inner, *, genome=None, record_sink=None) -> None:
        self._inner = inner
        self._genome = genome
        self._record_sink = record_sink
        self._aid = inner.agent_id

    def decide(self, packet, public_map):
        action = self._inner.decide(packet, public_map)
        if isinstance(action, (MoveIntent, WaitIntent)):
            if self._record_sink is not None:
                cur = packet.self_state.room
                chosen = (
                    action.payload.to_room if isinstance(action, MoveIntent) else cur
                )
                self._record_sink.append((encode(packet), chosen, cur))
                return action
            if self._genome is not None:
                room = mlp_pick_room(self._genome, packet)
                if room == packet.self_state.room:
                    return WaitIntent(actor=self._aid, type="wait")
                return MoveIntent(
                    actor=self._aid, type="move", payload={"to_room": room}
                )
        return action

    def __getattr__(self, name):  # delegate meeting protocol + properties
        return getattr(self._inner, name)


def make_factory(*, genome=None, record_sink=None):
    """AgentFactory: SpikeAgent-wrapped impostors, default crew."""

    def factory(agent_id, role):
        if role == "IMPOSTOR":
            inner = TacticalAgent(
                agent_id=agent_id, policy=ImpostorPolicy(agent_id=agent_id), role=role
            )
            return SpikeAgent(inner, genome=genome, record_sink=record_sink)
        return TacticalAgent(
            agent_id=agent_id, policy=CrewmatePolicy(agent_id=agent_id), role=role
        )

    return factory


# --- running games + reading replays -------------------------------------------
def run_games(seeds, out_dir: Path, *, genome=None, record_sink=None):
    os.environ["AILIBI_LLM_PROVIDER"] = "fake"
    out_dir.mkdir(parents=True, exist_ok=True)
    return run_tournament_eval(
        seeds=list(seeds),
        output_dir=out_dir,
        agent_factory=make_factory(genome=genome, record_sink=record_sink),
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        force=True,
    )


def replay_rows(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def count_kills(path: Path) -> int:
    """RESOLVED kills only (Comment 3). Replay tick rows record SUBMITTED kill
    intents even when ``advance_tick`` rejects them (e.g. the target moved earlier
    the same tick), so scanning raw ``kill`` actions overcounts and rewards failed
    attempts. A resolved kill removes its victim, who then never acts again — count
    distinct kill-targets whose last recorded action is at/before the kill tick."""
    rows = replay_rows(path)
    last_act: dict[str, int] = {}
    for row in rows:
        if row.get("kind") == "tick":
            for a in row.get("actions", []):
                last_act[a["actor"]] = row["tick"]
    killed: set[str] = set()
    for row in rows:
        if row.get("kind") == "tick":
            for a in row.get("actions", []):
                if a.get("type") == "kill":
                    tgt = a["payload"]["target"]
                    if last_act.get(tgt, -1) <= row["tick"]:
                        killed.add(tgt)
    return len(killed)


def state_hashes(path: Path) -> list[str]:
    return [r["state_hash"] for r in replay_rows(path) if "state_hash" in r]


def kills_over(seeds, out_dir: Path, *, genome=None) -> int:
    run_games(seeds, out_dir, genome=genome)
    return sum(count_kills(out_dir / f"replay-seed-{s}.jsonl") for s in seeds)
