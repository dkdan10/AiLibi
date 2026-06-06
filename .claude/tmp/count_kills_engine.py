import sys
sys.path.insert(0, '/Users/danielkeinan/projects/AiLibi')
from pathlib import Path
from collections import Counter
from api.replay_loader import ReplayLoader

loader = ReplayLoader(Path('/Users/danielkeinan/projects/AiLibi/replays/samples/9p2i'))
metas = loader.list_replays()
print('replays listed:', len(metas))

total_kills = 0
reported_bodies = 0
rejected = Counter()
winners = Counter()
mt_triggers = Counter()
for meta in metas:
    gid = meta.game_id if hasattr(meta, 'game_id') else meta['game_id']
    view = loader.load_replay(gid)
    # inspect view structure on first iteration
    if total_kills == 0 and reported_bodies == 0:
        print('view attrs:', [a for a in dir(view) if not a.startswith('_')][:30])
    for t in view.ticks:
        for ev in t.events:
            et = getattr(ev, 'type', None) or type(ev).__name__
            if 'Killed' in str(et):
                total_kills += 1
            if 'Rejected' in str(et):
                rejected[getattr(ev, 'reason', '?')] += 1
            if 'MeetingTriggered' in str(et):
                reported_bodies += 1
print('engine-replayed kills (KilledEvent):', total_kills)
print('meeting triggers (MeetingTriggeredEvent):', reported_bodies)
print('rejected actions by reason:', dict(rejected))
