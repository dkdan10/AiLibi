# Independent investigation implementation review

**Date:** 2026-09-06. This bounded code-first review was frozen before reading
the normal-policy gameplay review. It covers the new intention state, its owned
observation reducer, the pure planner and the version-3 replay-walk integration.
It is not an adoption decision or evidence of improved model deduction.

## Source and state boundaries

`agents/memory/investigation.py` reduces the agent's own typed sightings and
movements by actual source tick, snapshot/event phase and observer-local order.
Movement uses the observed destination. It never parses citation IDs for time,
reads the render-dependent working last-seen cache, or promotes reported claims
and public regrouping to first-hand sightings. Own observed body victims and
public meeting deaths/ejections form the known-dead set; the reducer accepts no
hidden living-status or position argument. Search sources remain historical
placements, not evidence that the subject stayed there or did anything wrong.

The meeting worker independently perturbed rendered-cache placements, reported
observations, public regrouping and foreign-owner memory. The owned reducer
remained unchanged for non-evidence inputs and refused the foreign owner and
malformed/future clocks. Its own tests retain a later snapshot at the actual
later tick, never backdating it into an earlier alibi.

Two narrow state guards were strengthened during review. Conflicting placements
at the same subject/source clock are refused even when a later observation has
already superseded both; retaining only the current maximum had concealed that
malformed input. A consumed source cannot change its citation identity at the
same source tick on a later decision. Both changes have planted regressions.

Working memory owns one immutable state. Consumption is indexed once per known
subject, survives cancellation, cannot regress in time, and cannot exceed the
known roster. A decision cache contains tick, complete packet digest and selected
intent together. Ordinary writes reject conflicting same-tick transitions.
The narrow public-meeting cancellation method clears only the active intention,
retaining the original cache and consumed sources; it cannot renew expiry.

## Planner review

The pure transition in `agents/tactical/investigation.py` separates ordinary
policy intent from the selected search step. Sources become eligible after four
ticks and expire for new selection after twelve. A search lasts at most six
elapsed ticks and inspects at most three rooms. It visits the last-known room
first, then adjacent rooms using deterministic shortest-distance/room ordering.
Visited rooms come from actual current observations, not a previous requested
move. A rejected move therefore does not fabricate inspection.

The review checked reacquisition, observed/public death, expiry, disconnection,
source consumption, urgent interruptions, task execution and OFF/impostor paths.
The retained ordinary task-execution action has stronger protection than merely
checking whether a task already made progress. Interruptions never extend the
original expiry, and clearing a plan does not permit the same stale source to
restart it. The direct planner and runtime cache reject changed same-tick packets.
No additional planner blocker was found in this bounded review; normal-policy
trajectories and complete API lifecycle checks remain separate integration work.

One concrete behavior limit remains for review: crewmates can see an adjacent
room's body, but the ordinary policy reports only a body in its own room. Finding
the missing subject's body in adjacent visibility cancels the search through
known-death evidence and may resume ordinary task travel without routing to
report. That is valid new information, but is not a claim of immediate reporting.
The candidate preserves the existing report routing; expanding that behavior
requires an explicit scope decision and its own route/priority controls.

## Replay checks and verification

Version-3 `eval/replay_walk.py` creates the same supported built-in policy objects
through the shared `PolicyReconstruction`, calls the same decision method before
applying recorded actions, delivers event observations afterward, and uses its
meeting lifecycle hooks. The reader applies the original actions and refuses a
policy mismatch; it never substitutes a recomputed action to heal a recording.
Its internal verification memory is separate from external consumers' existing
folds. Earlier replay versions retain their existing walk behavior.

A genuine partial version-3 recording reconstructs successfully. Replacing a
recorded action is refused even under a test profile with state-hash verification
disabled, demonstrating that this gate checks actual policy intent. Temporary
audit resources are removed on generator exhaustion, explicit early close and a
consumer-thrown exception.

Development verification:

```sh
.venv/bin/pytest -q --tb=short tests/agents/test_investigation_memory.py tests/agents/test_investigation_planner.py tests/eval/test_investigation_replay_walk.py tests/eval/test_replay_walk.py
.venv/bin/mypy agents/memory/investigation.py agents/memory/working.py eval/replay_walk.py tests/agents/test_investigation_memory.py tests/eval/test_investigation_replay_walk.py
```

These commands passed 98 tests and strict mypy for five files at this review
point. Ruff and formatting passed on owned implementation/tests. The coordinator
owns the full project gate, canonical recording verification, source-bound
normal-policy evidence, API/viewer integration and final synthesis. No live
provider, historical re-recording or default adoption occurred in this work.

## Dated coordinator disposition — 2026-09-06

After the independently frozen findings, the coordinator accepted currently
visible adjacent-body approach and the immediate response to a source-tick kill
as required search overrides. The tactical worker implemented the helpers and
authored the actual adapter control; the coordinator wired and verified them.
The report path still uses the ordinary engine meeting transition. Hidden corpses
do not become route targets, and no persistent new flight strategy was added.
The 51-test coordinator priority/integration/planner run passed, including a
spent-emergency control, reported-claim refusal, no-second-ingestion cache check,
discarded-action mismatch and reconstruction-constructor resource cleanup.

The memory/replay reviewer independently inspected the root adapter and ran 45
integration/contextual-reporting controls before these final refinements. The
final coordinator changes received the full gate documented in the checkpoint;
they are not represented as a second blind independent review. The owner's
external Claude review remains outstanding.

Source-bound measurement also separates differing submitted actions from
differing engine states, including post-meeting resolution hashes. An altered
discarded attempt cannot count as an effective changed trajectory. That semantic
control supplements, rather than replaces, recorded action verification.
