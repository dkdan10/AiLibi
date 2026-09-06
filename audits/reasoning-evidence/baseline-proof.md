# Isolated baseline proof

The probe isolates source from `ee7cbe7a`, immediately before this implementation
batch. It reproduced marker injection and loss of movement origin/source; the
clean strong control stayed strong. The current legacy path produced exactly
the same serialized JSON as the isolated source, including testimony-shapes ON.
The candidate kept both controls strong and retained reported origin/source.
`baseline-before.json`, `baseline-candidate.json` and `baseline-inputs.json`
contain the measured values. They are mechanism fixtures, not model outcomes.

Reproduce without changing refs or historical records:

```bash
AILIBI_REVIEW_OLD=$(mktemp -d)
git archive ee7cbe7a agents meetings engine observation llm orchestrator eval api training scripts pyproject.toml | tar -x -C "$AILIBI_REVIEW_OLD"
.venv/bin/python - "$PWD" "$AILIBI_REVIEW_OLD" <<'PY'
import json, subprocess, sys
from pathlib import Path
current, old = map(Path, sys.argv[1:])
inputs = current / 'audits/reasoning-evidence/baseline-inputs.json'
probe = r'''
import inspect,json,os,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from meetings.schemas import MeetingTranscript,MeetingResult
from meetings.transcript import detect_contradictions,is_weak_contradiction
from meetings.manager import derive_reported_testimony
inputs=json.loads(Path(sys.argv[3]).read_text())
kwargs={'evidence_reasoning_version':1} if sys.argv[2]=='candidate' else {}
out={}
for key in ('clean','injected'):
    flags=detect_contradictions(MeetingTranscript.model_validate(inputs[key]),**kwargs)
    out[key]={'weak':[is_weak_contradiction(f) for f in flags],
              'flags':[f.model_dump() for f in flags]}
os.environ['AILIBI_TESTIMONY_SHAPES']='1'
reducer_kwargs=dict(kwargs)
if 'testimony_shapes' in inspect.signature(derive_reported_testimony).parameters:
    reducer_kwargs['testimony_shapes']=True
rows=derive_reported_testimony(MeetingResult.model_validate(inputs['testimony']),**reducer_kwargs)
out['reported']=[r.model_dump() for r in rows]
print(json.dumps(out,sort_keys=True))
'''
def run(source, mode):
    return subprocess.check_output(
        [sys.executable,'-c',probe,str(source),mode,str(inputs)],text=True)
before=run(old,'legacy')
assert before == run(current,'legacy')
after=json.loads(run(current,'candidate'))
assert json.loads(before)['clean']['weak'] == [False]
assert json.loads(before)['injected']['weak'] == [True]
assert after['clean']['weak'] == after['injected']['weak'] == [False]
assert after['reported'][0]['from_room'] == 'A'
assert after['reported'][0]['source_event_id'] == 'turn:m:turn-0:obs:0'
assert 'from_room' not in json.loads(before)['reported'][0]
print('Baseline defects reproduced; legacy bytes equal; candidate controls pass.')
PY
```

The B36 regression separately demonstrates the old false departure/entry on
the still-callable legacy profile and a genuine later departure on both paths.
No claim is made that the newly added profile was callable at the baseline.
