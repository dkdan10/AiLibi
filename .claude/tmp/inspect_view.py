import sys
sys.path.insert(0, '/Users/danielkeinan/projects/AiLibi')
from pathlib import Path
from api.replay_loader import ReplayLoader

loader = ReplayLoader(Path('/Users/danielkeinan/projects/AiLibi/replays/samples/9p2i'))
view = loader.load_replay('headless-seed-0')
d = view.model_dump()
print('view keys:', list(d.keys()))
t1 = d['ticks'][1]
print('tick keys:', list(t1.keys()))
import json
print(json.dumps(t1, indent=2, default=str)[:3000])
