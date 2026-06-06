import sys
sys.path.insert(0, '/Users/danielkeinan/projects/AiLibi')
from pathlib import Path
from collections import Counter
from api.replay_loader import ReplayLoader

loader = ReplayLoader(Path('/Users/danielkeinan/projects/AiLibi/replays/samples/9p2i'))
view = loader.load_replay('headless-seed-0')
d = view.model_dump()
# find tick where p-4 dies
for t in d['ticks']:
    for a in t['agent_states']:
        if a['agent_id'] == 'p-4' and not a['is_alive']:
            print('p-4 dead at tick', t['tick'])
            import json
            print('events at that tick:', json.dumps(t['events'], default=str)[:800])
            break
    else:
        continue
    break

# Now count deaths across all 50 games via is_alive transitions (engine-truth)
total_deaths = 0
event_kinds = Counter()
total_meeting_triggered_events = 0
for meta in loader.list_replays():
    gid = meta.game_id
    dd = loader.load_replay(gid).model_dump()
    prev_alive = None
    for t in dd['ticks']:
        alive = {a['agent_id'] for a in t['agent_states'] if a['is_alive']}
        if prev_alive is not None:
            died = prev_alive - alive
            total_deaths += len(died)
        prev_alive = alive
        for ev in t['events']:
            k = ev.get('kind') or ev.get('type') or str(ev)[:40]
            event_kinds[k] += 1
print('total deaths via is_alive transitions:', total_deaths)
print('event kinds across all games:', dict(event_kinds))
