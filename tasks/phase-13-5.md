# Phase 13.5 — Memory correctness: truth-up → substrate (before the Phase 14 model migration)

> **STATUS: AUTHORING (2026-06-25).** The complete memory-correctness work that precedes the
> Phase 14 model migration, in ONE phase. Grounded in the 2026-06-25 memory-pipeline diagnosis
> (workflow `wg54kfoxy`: 7 subsystem maps, 33 confirmed + 7 partial discrepancies, 3 prior claims
> refuted-as-already-fixed). Plan: `~/.claude/plans/i-want-to-create-twinkling-firefly.md`.

Goal: make the memory subsystem deliver CORRECT information to the model — fix the docs/dead-code
that mislead, then fix the substrate that collapses social/spoken information to a numeric scalar
(testimony never content, witnessed kill mints no flag, movement unperceived, rendered memory
frozen). Three waves, ordered by risk:

- **Wave A — doc reconciliation** (design-thread, not dispatched). Behavior-neutral.
- **Wave B — dead-code truth-up** (`13.5.1`). Behavior-neutral; `scripts/check.sh` only.
- **Wave C — correct-information substrate** (`13.5.2`–`13.5.5`). Behavior-CHANGING; each behind a
  config flag, validated by structural tests + a 9B SMOKE, **not** a 50-game R1 re-record.

Validation cadence is per-task, not per-phase: the neutral waves (A/B) change no recorded game
outcome and need **no eval** (`replays/samples/**` untouched; `verify_samples.sh` still byte-
identical); the substrate wave (C) is smoke-validated for correctness, with its gameplay value
measured for the first time on the new model in Phase 14's ONE combined re-record. The phase-end
gate is: substrate smoke green + byte-identical reconstruction + corrected-substrate 9B prompts
pinned as the Phase-14 reference.

---

## Wave A — Doc reconciliation (DESIGN-THREAD work, NOT a dispatched task)

The full `DESIGN.md` + `AGENT_IMPLEMENTATION.md` reconciliation is executed by the design thread,
**not** materialized as an `agent_prompts/` task — the prompt generator hard-codes
`Do not modify DESIGN.md` / `Do not modify AGENT_IMPLEMENTATION.md` into every prompt
(`scripts/generate_prompts.py::_constraints_for`), so a task whose job is to edit those files
cannot be expressed through it. `DESIGN.md` is the design thread's own artifact. Tracked here for
completeness; committed to main with the rest of 13.5.

Stale claims to reconcile against HEAD (anchor cases, not exhaustive — the owner chose the full
sweep):
- belief Rule 3 (corroboration) + Rule 5 (decay) marked **deferred** (`DESIGN.md:631, :633`;
  reading-note `:14–15`) but **live** (`agents/memory/beliefs.py` `CORROBORATION_SUSPICION_DELTA`,
  `MEETING_SUSPICION_DECAY_RATE`, applied in `apply_meeting_evidence_rules`) → flip to live.
- `"reported"` provenance documented on `EpisodicEvent` but never written; "working memory rebuilt
  each tick" (store unwired); per-tick coalescing, meeting memo, 4th strategic trigger
  (unimplemented); the hallucination-guard validator (correctly noted deferred — leave) → state
  each accurately.
- Agent-memory notes (non-repo) — **already truthed-up this session**: own-kill "discovered the
  body" bug is FIXED by Task 11.3; the impostor-info-ceiling "never emits vents/sabotage" claim is
  superseded by Phase 11. No further action.

---

## Wave B — Dead-code disposition (behavior-neutral, dispatched)

### Task 13.5.1 — Dead-code truth-up: relabel AgentRuntime + earmark WorkingMemory/alibi docstrings
**Branch:** `phase-13-5-dead-code-truthup`
**Depends on:** none
**Section refs:** the 2026-06-25 memory-pipeline diagnosis (workflow `wg54kfoxy`; the cited structures verified to have ZERO production writers — a NEUTRAL classification); agents/runtime.py; agents/memory/working.py; agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis`); agents/memory/store.py (the `last_seen` render hook); orchestrator/game.py (`TacticalAgent`, the real production agent)
**Complexity:** Small
**Files in scope:**
- agents/runtime.py
- agents/memory/working.py
- agents/memory/beliefs.py
- agents/memory/store.py
**Files NOT in scope:**
- tests/ — the relabel is docstring-only and keeps every public API byte-identical, so no test changes are needed; if a test breaks, STOP and report (the edit was not neutral)
- DESIGN.md and AGENT_IMPLEMENTATION.md — the doc reconciliation is the design thread's Wave A, not this task
- the substrate wiring — Wave C (13.5.2–13.5.5) wires these structures; this task only DOCUMENTS their current status and earmark, and must neither wire nor delete them

Three memory structures are wired into the composite memory surface but never written in
production (diagnosis-verified: zero non-test callers of `WorkingMemory.set_goal` /
`set_path` / `record_sighting` and `BeliefState.record_alibi`; `AgentRuntime` is a Phase-2 glue
stub whose `_choose_action` always returns `WaitIntent` and whose `_update_memory` is a no-op,
imported only by tests — the production agent is `orchestrator/game.py::TacticalAgent`). They are
NOT bugs and must NOT be deleted: they are the scaffolding Wave C wires (the alibi list ←
testimony-as-content; `working.last_seen` ← movement perception). This task makes the code
self-documenting about that status so a reader — and the Phase-14 migration author — is not
misled into thinking they are live or into deleting them. Strictly docstrings and `#` comments:
no logic, no signature, no public type, no render-output change.

Specifics: (1) `agents/runtime.py` — a loud module + class docstring stating `AgentRuntime` is a
TEST-ONLY harness (a Phase-2 scaffold), NOT the production agent, and naming
`orchestrator/game.py::TacticalAgent` as the real one; note `_choose_action` is a hardcoded
`WaitIntent` and `_update_memory` a no-op. (2) `agents/memory/working.py` — docstring states
`WorkingMemory` currently has no production writer (`_last_seen` is always empty at runtime) and
earmarks `last_seen` as wired by Wave C (movement perception). (3) `agents/memory/beliefs.py` —
docstrings on `record_alibi` and `PlayerBelief.alibis` state the list is written by no production
path and rendered nowhere today, earmarked for Wave C (testimony-as-content). (4)
`agents/memory/store.py` — a comment at the `last_seen` render hook noting the suffix never renders
today (no writer), populated by Wave C (movement perception).

**Definition of done:** `AgentRuntime` carries a module + class docstring identifying it as a
test-only harness and naming `orchestrator/game.py::TacticalAgent` as the production agent;
`WorkingMemory`, `record_alibi` / `PlayerBelief.alibis`, and the `store.py` `last_seen` hook each
carry a docstring or comment stating current dead status plus the Wave-C lever that will wire
them; NO logic, signature, public-type, or render-output change (a memory-render fixture is
byte-identical before and after); `git diff` shows only docstring/comment lines; the full
`scripts/check.sh` is green.
**Implementation hint:**
Before documenting anything as dead, CONFIRM zero production writers yourself —
`grep -rn "record_alibi\|set_goal\|set_path\|record_sighting" agents/ orchestrator/ meetings/ api/ | grep -v tests/`
and `grep -rn "AgentRuntime\|agents.runtime" --include=*.py . | grep -v tests/` — and if any
production writer exists, STOP and report (the diagnosis would be wrong). Edit only docstrings and
`#` comments; touch no executable line. Run a memory-render fixture test
(`tests/agents/test_memory_rendering.py`) before and after to confirm byte-identical output. The
relabel is in-place (a docstring); relocating `AgentRuntime` under `tests/` is OUT of scope (it
would change test imports and is not neutral).
**Ready-to-paste prompt:** `agent_prompts/task-13-5-1-dead-code-truthup.md`

---

## Wave C — Correct-information substrate (roadmap; behavior-CHANGING, smoke-validated)

The behavior-changing core. Each item is elaborated to a full `### Task` contract immediately
before dispatch (each depends on substrate interfaces the prior lever introduces, so the
contracts firm up as the spine lands). Each lever ships **behind a config flag** and must fit the
salience render budget (`DEFAULT_TOKEN_BUDGET=1500`, `agents/memory/store.py`) under the frozen
generation caps (turn 2048 / vote 1024); prompt templates (`agents/strategic/prompts/*.j2`) gain a
short directive per new content type. Validation is structural tests + a 9B SMOKE (parse-success,
leak suite, meeting-rate ≥ 0.60, byte-identical reconstruction) — NOT a 50-game R1 re-record;
gameplay value is measured for the first time on the new model in Phase 14's combined re-record.

- **13.5.2 — Testimony as episodic content** (`"reported"` provenance write path:
  `meetings/manager.py` evidence derivation → ingest into `agents/perception` /
  `agents/memory/store.py`; render; wires `record_alibi`). Today testimony persists only as a
  scalar suspicion Δ.
- **13.5.3 — Witnessed kill → STRONG contradiction flag** (`meetings/schemas.py` new observation
  type + `meetings/transcript.py` detector + `beliefs.apply_contradiction_rule`). Today the
  eyewitness is unstructured free-text and mints nothing (STRONG path fired 0/114).
- **13.5.4 — Movement perception** (`observation/service.py` reads `MovedEvent`/`last_action` → new
  `agents/perception` event + render; wires `working.last_seen`). Today only current-room snapshots.
- **13.5.5 — Unfreeze rendered memory mid-meeting** (`orchestrator/game.py`,
  `meetings/manager.py::MeetingParticipant`). HIGHEST RISK — replay-determinism hazard; flag and
  gate separately; land last, after 13.5.2–13.5.4.

The phase closes when Wave C's smoke is green and the corrected-substrate 9B prompts are pinned;
then **Phase 14** (model migration, PR #196) selects + re-baselines on this corrected substrate.
