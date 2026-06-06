"""Verify audit finding B-B-5 by engine re-simulation of replays/samples/9p2i."""
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean, median

REPO = Path("/Users/danielkeinan/projects/AiLibi")
sys.path.insert(0, str(REPO))

from api.replay_loader import (  # noqa: E402
    _deserialize_actions,
    _load_roster_config,
    _meeting_result_from_entry,
    _meeting_trigger_from_events,
)
from engine.tick import advance_tick  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from orchestrator.game import apply_meeting_result  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state  # noqa: E402

FACTS = json.load(
    open("/var/folders/45/z6kbb3x1103dgy43qkw1s3vw0000gn/T/ailibi-gameplay-facts-9p2i.json")
)
roles_by_seed = {g["seed"]: g["roles"] for g in FACTS["games"]}
facts_by_seed = {g["seed"]: g for g in FACTS["games"]}

game_map = load_canonical_map()
sample_dir = REPO / "replays" / "samples" / "9p2i"
roster = _load_roster_config(sample_dir)
assert roster is not None

all_kills = []  # one record per kill
first_meeting = {}  # seed -> dict(tick, crew_dead)
meetings_per_seed = Counter()
game_over_tick = {}
winner_by_seed = {}
hash_ok = 0

for seed in range(50):
    path = sample_dir / f"replay-seed-{seed}.jsonl"
    entries = read_all_entries(path)
    replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
    meeting_by_tick = {e.tick: e for e in entries if isinstance(e, MeetingReplayEntry)}
    end_entries = [e for e in entries if isinstance(e, GameEndReplayEntry)]
    roles = roles_by_seed[seed]

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=roster.num_players,
        num_impostors=roster.num_impostors,
        tasks_per_crewmate=roster.tasks_per_crewmate,
    )
    kills_this = {}  # body_id -> record
    dead_count = 0

    for entry in replay_entries:
        actions = _deserialize_actions(entry.actions)
        state, events = advance_tick(state, actions, game_map=game_map)
        if _state_hash(state) != entry.state_hash:
            raise SystemExit(f"HASH MISMATCH seed {seed} tick {entry.tick}")
        hash_ok += 1

        for ev in events:
            if getattr(ev, "type", None) == "Killed":
                # find the body id the engine created for this victim
                body_id = None
                for bid, b in state.bodies.items():
                    if b.player_id == ev.target and bid not in kills_this:
                        body_id = bid
                rec = dict(
                    seed=seed,
                    tick=entry.tick,
                    victim=ev.target,
                    victim_role=roles[ev.target],
                    killer=ev.actor,
                    room=ev.room,
                    witnesses=list(ev.witnesses),
                    crew_witnesses=[w for w in ev.witnesses if roles[w] == "CREWMATE"],
                    body_id=body_id,
                    reported_tick=None,
                    reporter=None,
                )
                kills_this[body_id] = rec
                all_kills.append(rec)
                dead_count += 1

        if state.phase == "MEETING":
            m_entry = meeting_by_tick.get(entry.tick)
            trigger_kind, body_id = _meeting_trigger_from_events(events)
            reporter = next(
                ev.actor for ev in events if getattr(ev, "type", None) == "MeetingTriggered"
            )
            meetings_per_seed[seed] += 1
            if seed not in first_meeting:
                first_meeting[seed] = dict(tick=entry.tick, crew_dead=dead_count)
            if body_id is not None and body_id in kills_this:
                kills_this[body_id]["reported_tick"] = entry.tick
                kills_this[body_id]["reporter"] = reporter
            else:
                print(f"WARN seed {seed}: reported body {body_id} not matched to a kill")
            if m_entry is None:
                print(f"WARN seed {seed}: meeting at tick {entry.tick} has no meeting entry")
                break
            result = _meeting_result_from_entry(m_entry)
            state, post_events = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            if _state_hash(state) != m_entry.state_hash_after:
                raise SystemExit(f"POST-MEETING HASH MISMATCH seed {seed} tick {entry.tick}")
            if state.phase == "GAME_OVER":
                break
        elif state.phase == "GAME_OVER":
            break

    if end_entries:
        game_over_tick[seed] = end_entries[0].tick
        winner_by_seed[seed] = end_entries[0].winner
    # cross-check vs facts
    f = facts_by_seed[seed]
    assert game_over_tick[seed] == f["game_over_tick"], (seed, game_over_tick[seed], f["game_over_tick"])
    assert winner_by_seed[seed] == f["winner"], seed

print(f"ticks hash-verified: {hash_ok}")
print(f"total kills: {len(all_kills)}  (facts: {FACTS['aggregates']['total_kills']})")

reported = [k for k in all_kills if k["reported_tick"] is not None]
unreported = [k for k in all_kills if k["reported_tick"] is None]
print(f"reported bodies: {len(reported)}/{len(all_kills)} = {len(reported)/len(all_kills):.3f}")

# latency
lat = [k["reported_tick"] - k["tick"] for k in reported]
hist = Counter(lat)
print("latency histogram:", dict(sorted(hist.items())))
print(f"latency mean: {mean(lat):.2f}  median: {median(lat)}")
zero_lat = [k for k in reported if k["reported_tick"] == k["tick"]]
print(f"latency-0 reports: {len(zero_lat)}")

# witnessed kills (crew witness present at kill)
witnessed = [k for k in all_kills if k["crew_witnesses"]]
print(f"\ncrew-witnessed kills: {len(witnessed)}/{len(all_kills)} = {len(witnessed)/len(all_kills):.3f}")
for k in witnessed:
    nxt = "no-next-tick" if k["tick"] >= game_over_tick[k["seed"]] else "next-tick-ok"
    latv = None if k["reported_tick"] is None else k["reported_tick"] - k["tick"]
    rep_by_wit = k["reporter"] in k["crew_witnesses"] if k["reporter"] else None
    print(
        f"  seed {k['seed']:>2} kill t{k['tick']:>2} room {k['room']:<12} victim {k['victim']} "
        f"crew_wit {k['crew_witnesses']} end_t {game_over_tick[k['seed']]} [{nxt}] "
        f"latency {latv} reporter {k['reporter']} (witness? {rep_by_wit})"
    )

with_next = [k for k in witnessed if k["tick"] < game_over_tick[k["seed"]]]
conv1 = [k for k in with_next if k["reported_tick"] is not None and k["reported_tick"] - k["tick"] == 1]
print(f"witnessed with next tick: {len(with_next)}; converted at latency exactly 1: {len(conv1)}")
final_tick_witnessed = [k for k in witnessed if k["tick"] >= game_over_tick[k["seed"]]]
print(f"witnessed on final tick (no next tick): "
      f"{[(k['seed'], k['tick'], k['crew_witnesses']) for k in final_tick_witnessed]}")

# unreported bodies with >=3 ticks left to game end
stale = [k for k in unreported if game_over_tick[k["seed"]] - k["tick"] >= 3]
stale_rooms = Counter(k["room"] for k in stale)
print(f"\nunreported bodies with >=3 ticks to game end: {len(stale)}")
print("by room:", dict(stale_rooms.most_common()))

# first meeting stats
fm_ticks = [v["tick"] for v in first_meeting.values()]
fm_dead = [v["crew_dead"] for v in first_meeting.values()]
print(f"\ngames with >=1 meeting: {len(first_meeting)}/50; total meetings {sum(meetings_per_seed.values())}; "
      f"per game {sum(meetings_per_seed.values())/50:.2f}")
print(f"first-meeting tick mean {mean(fm_ticks):.2f} median {median(fm_ticks)}")
print("crew dead at first meeting hist:", dict(sorted(Counter(fm_dead).items())),
      f"mean {mean(fm_dead):.3f}; >=3 dead in {sum(1 for d in fm_dead if d >= 3)}/{len(fm_dead)}")

zero_meeting = [s for s in range(50) if meetings_per_seed[s] == 0]
print(f"zero-meeting seeds: {zero_meeting}")
for s in zero_meeting:
    nk = sum(1 for k in all_kills if k["seed"] == s)
    print(f"  seed {s}: winner {winner_by_seed[s]} end tick {game_over_tick[s]} kills {nk}")

# game length context
print(f"\ngame_over_tick mean {mean(game_over_tick.values()):.2f} "
      f"median {median(game_over_tick.values())} max {max(game_over_tick.values())}")
print(f"mean latency / mean game length = {mean(lat)/mean(game_over_tick.values()):.2f}")
