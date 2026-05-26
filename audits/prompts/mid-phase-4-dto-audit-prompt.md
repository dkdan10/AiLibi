# Mid-Phase-4 DTO Audit — Prompt

You are auditing the AiLibi repository's spectator API surface after
Task 4.4 (MapView vertical slice) has landed. At this point Phase 4
has produced:

- Task 4.1 — FastAPI app skeleton + DTO inventory (`api/schemas.py`,
  `api/routes/`, `tests/api/`)
- Task 4.2 — Replay loader + endpoint implementation
  (`api/replay_loader.py`, populated route handlers)
- Task 4.3 — React + Vite + Tailwind + PixiJS frontend skeleton
  (`frontend/src/api/`, `frontend/src/store/`, `frontend/src/types/`)
- Task 4.4 — MapView vertical slice (`frontend/src/components/`
  consuming the substrate end-to-end)

This is the **substrate that 4.4.5–4.8 will fan out against** —
MapView full, MeetingView, ThoughtStream, BeliefMatrix, ReplayControls.
Five components will build against the API + store contract. The cost
of a leaky or drifted substrate is high — five PRs will all encode the
same mistakes. That is what this audit exists to catch.

You will produce **one audit report** in `audits/` following the
format, rigor, and section structure of recent post-checkpoint
audits (`audits/audit-2026-05-25-1539-pre-phase-4-real-provider-eval.md`
is one structural reference; `audits/audit-2026-05-25-1823-pre-phase-4-real-provider-eval.md`
is another). Single-tool — there is no reconciliation step for this
audit. The verdict you write is the verdict the project acts on.

---

## 1. Identity and constraints

- **Role:** read-only auditor. You may read any file, run any
  non-mutating shell command, and execute the full test/lint/type
  suite. You may not edit source files, tests, fixtures, configuration,
  task documents, agent prompts, or any file outside `audits/`. The
  only file you write is your audit report.
- **No fixes.** If you see a defect, record it as a finding. Do not
  patch it, even one line. Repair work is owned by a separate task
  (4.4.6, 4.4.7, ...) that will be authored from this audit.
- **No speculation.** Every finding must cite a `file:line` (or a
  reproducible shell command and its observed output). A finding
  without a citation is not a finding.
- **No drive-by suggestions.** If a recommendation does not address a
  cited defect or unverified invariant, omit it. The audit is a
  defect register, not a wishlist.
- **No real LLM provider calls.** Phase 4 added no new LLM-call paths.
  Run `bash scripts/check.sh` and any pytest invocation, but do not
  invoke the real Anthropic client.
- **Scope discipline.** This is a DTO / leak audit, NOT a general code
  audit. Findings about Phase 3 code quality, prompt template style,
  Phase 5 readiness, or stylistic frontend choices are out of scope
  unless they directly cause a DTO leak or substrate defect. When in
  doubt, omit.

## 2. Scope

**In scope:**

- Every DTO in `api/schemas.py`. Each DTO's field list compared
  against the engine / meetings / orchestrator type it shadows. Each
  field categorized: intentional exposure, deliberate omission, or
  potential leak.
- Every endpoint in `api/routes/`. The response actually serialized
  vs. what the `response_model` annotation promises.
- `api/replay_loader.py`. Specifically: does it serialize anything
  that bypasses the DTO contract (e.g. raw `WorldState`, raw
  `ReplayEntry`)?
- Frontend `types/api.ts`. Drift from the Pydantic DTOs. Are there
  fields in the TypeScript types that don't exist in the Pydantic
  source? Or vice versa?
- Frontend store (`store/replayStore.ts`) — does it cache or expose
  any data that shouldn't be exposed?
- Frontend components in `frontend/src/components/` introduced by 4.4
  — do they consume any field that should have been excluded?
- The `tests/api/test_leak.py` test pattern — is it still catching
  what it should, given the new code?

**Out of scope:**

- Phase 3 code (engine, agents, llm, meetings, observation,
  orchestrator). These are read by the new code; their internal
  structure is not in scope unless they directly expose private
  state through an API field.
- Visual / UX quality of the MapView slice. The vertical slice's
  acceptance is one screenshot; that's not a DTO audit concern.
- TypeScript style, ESLint config, CSS organization.
- Pagination, authentication, rate-limiting — explicitly deferred at
  the Phase 4 plan level.
- Test coverage as a metric. Coverage gaps that cause leak risk are
  in scope; coverage gaps that don't are not.
- npm dependency version pin choices, unless a chosen dependency
  itself causes a leak (extremely unlikely).

## 3. Audit window

Use `git log` to enumerate every commit on `main` since the start of
Phase 4:

```bash
git log --oneline --name-status $(git merge-base main HEAD)..HEAD
```

(Adjust the base ref if Phase 4 work was done on a different branch
structure.) The commits should correspond to Tasks 4.1, 4.2, 4.3, 4.4
landings. If any task is not yet merged at the time you run, abort
the audit and note in your report: "Audit run before all four
foundation tasks merged; substrate incomplete."

## 4. The five findings classes you must check

For each class, the report has a dedicated subsection. Every subsection
either lists concrete findings (with `file:line` citations) OR states
"No findings in this class" with one sentence of evidence (e.g. "Ran
X command; output Y matches expected").

### Class A — DTO field leakage

For each DTO in `api/schemas.py.__all__`:

1. Identify the engine / meetings / orchestrator type it shadows
   (from its docstring or by structural inspection).
2. List every field in the source type.
3. Match each source field to either (a) an intentional DTO field,
   (b) a deliberate omission documented in the DTO docstring, or
   (c) **a potential leak** — a source field that's exposed without
   intentionality.

Specific high-risk fields to verify:

- `PlayerState.role` — exposed via `PlayerView.role`. INTENTIONAL
  (privileged spectator).
- `PlayerState.kill_cooldown_ticks` / `vent_cooldown_ticks` — should
  be OMITTED. Verify they're not in `AgentTickStateView`.
- `WorldState.bodies` — exposed via `KillEventView` / `ReportBodyEventView`,
  NOT via raw `BodyState`. Verify the body markers visible to the
  spectator don't include any `BodyState`-only fields.
- `ReplayEntry.state_hash` — should be OMITTED from every DTO.
  Verify it's not in `TickView`.
- `LLMCallRecord.prompt` — exposed via `LLMCallView.prompt_text`.
  INTENTIONAL but high-risk: the prompt text contains
  `rendered_memory` for the agent that made the call. Is the
  rendered_memory accidentally leaking through to another agent's
  view in `AgentMemoryView`?
- `Statement.statement_id` / `Statement.speaker` — these are engine-
  authoritative override fields. Verify they're exposed as the
  CANONICAL (post-override) values, not the raw LLM-emitted
  placeholder.

### Class B — Endpoint response vs. response_model drift

For each endpoint in `api/routes/`:

1. Inspect the route's `response_model=...` declaration.
2. Inspect the actual return path. Does it always return the declared
   type, or are there paths that return raw dicts, raw Pydantic
   models from other modules, or strings?

The risk: FastAPI's response_model serialization re-validates outgoing
data — but if the handler returns a `MeetingReplayEntry` directly (raw
orchestrator type) instead of a `MeetingView`, FastAPI may serialize
extra fields that the DTO didn't promise.

For each endpoint, run a `TestClient` request and inspect the response
JSON. Verify that the response JSON keys match exactly the DTO's
declared fields. Any extra key is a leak.

### Class C — TypeScript / Pydantic drift

`frontend/src/types/api.ts` mirrors the Python DTOs. Drift sources:

1. A field added to Python after the TypeScript was generated /
   authored. The TypeScript silently misses it; the frontend works
   anyway because TypeScript's structural typing tolerates missing
   keys.
2. A field renamed in Python; TypeScript still references the old
   name. The frontend silently reads `undefined`.
3. A field deleted in Python; TypeScript still references it. The
   frontend treats it as `undefined`; downstream display logic may
   crash on `null.property`.

Check by:

- If types were generated from OpenAPI: re-run `npm run gen:api`
  (with the API running) and `git diff` to see if the generated
  output matches what's committed. Any diff is drift.
- If types were hand-authored: walk every Pydantic DTO and grep the
  TypeScript module for each field name. Any missing or extra field
  is drift.

### Class D — Frontend store / component leak

`frontend/src/store/replayStore.ts` holds the loaded replay in memory.
Components (`frontend/src/components/`) consume it. Risks:

1. The store caches `ReplayView` data including fields the spectator
   shouldn't render at this UI surface. (Replay viewer IS privileged,
   so most fields are fine; the audit catches accidentally-rendered
   fields, not cached fields.)
2. A component renders a field that wasn't supposed to be visible at
   that surface (e.g. MapView displaying `role` directly on the
   token — that's a UX choice, not a leak; but rendering raw replay
   internals IS a leak).

For each component in `frontend/src/components/`, scan for direct
field accesses via `currentReplay.foo` or `tick.bar`. Verify each
accessed field is in `frontend/src/types/api.ts`. Any access to a
field not in the DTO inventory is either drift (Class C) or
unauthorized field invention.

### Class E — Determinism + state-hash integrity

This is a `api/replay_loader.py` correctness check, not strictly a
DTO leak, but it's load-bearing for the audit:

1. Run `uv run pytest tests/api/ -v`. The state-hash-mismatch test
   from 4.2's DoD must pass.
2. Pick one real replay file (e.g. `/tmp/eval-50/replay-seed-22.jsonl`
   if it still exists, or any in the configured `replay_dir`). Load
   it via the API:

   ```bash
   curl http://localhost:8000/replays/headless-seed-22 | jq '.metadata'
   curl http://localhost:8000/replays/headless-seed-22/ticks/0 | jq '.agent_states | length'
   ```

   The number of `agent_states` returned should match the player
   count of the original game (typically 5–7). If the response is
   500 or empty, that's a critical finding.

## 5. Report format

Your report goes to `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto.md`.
Required sections:

1. **Verdict.** Exactly one of:
   - "Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8."
   - "Mid-phase DTO audit blocks fan-out — repair tasks required: …"
     (list the repair task names).

2. **Environment.** Commit `HEAD` short-hash. Output of `bash scripts/check.sh`
   one-line summary ("X passed, Y skipped"). Output of
   `git log --oneline -5`.

3. **Class A — DTO field leakage findings.** Per-DTO subsection (or
   "No findings in this class" with evidence).

4. **Class B — Endpoint response drift findings.**

5. **Class C — TypeScript / Pydantic drift findings.**

6. **Class D — Frontend store / component leak findings.**

7. **Class E — Determinism + state-hash findings.**

8. **Repair task proposals.** For each finding that blocks fan-out,
   propose a one-paragraph task sketch (branch name, files in scope,
   one-line definition-of-done). The next session will turn each
   proposal into a full task contract.

9. **Required closing fields:**
   - Report path
   - Verdict (verbatim, one of the two above)
   - Findings count by class
   - Total findings

## 6. Cost discipline

This audit costs zero API spend (no real-provider calls). Local CPU
only. If you spend more than 30 minutes wall clock or your local
shell command count exceeds ~50, stop and write a partial report —
the auditor's value drops past that point.

## 7. What "passes" looks like

A passing audit has zero blocking findings in any class. A few
informational findings (e.g. "Class A: `LLMCallView.prompt_text`
exposes rendered_memory — INTENTIONAL but worth noting that
ThoughtStream should be careful to scope this per-agent") are fine
and useful, as long as they don't block fan-out.

A blocking finding has the shape: "DTO X exposes field Y which leaks
information that should be excluded, OR endpoint Z returns data that
bypasses the DTO contract, OR TypeScript drift means the frontend
silently uses a non-existent field." Each of these requires a repair
task before 4.4.5–4.8 can dispatch safely.

## 8. Anti-patterns to flag (high-signal example findings)

Examples of what a STRONG finding looks like (do not make these up —
only report if you actually observe them):

- **"`AgentMemoryView` for agent A includes `rendered_memory_text`
  containing the substring "Your role: IMPOSTOR" — the spectator
  endpoint exposes this. INTENTIONAL per the 4.1 privilege model.
  However, the same `rendered_memory_text` for a different agent B
  would contain "Your role: CREWMATE" — verify by curl that the API
  serves the correct per-agent view, not a single shared one."**

- **"`api/routes/replays.py:84` returns `meeting_entry.model_dump()`
  instead of constructing a `MeetingView` — this serializes every
  field on the raw `MeetingReplayEntry`, including `state_hash_before`
  and `state_hash_after` which the DTO excludes. Test: `curl
  /replays/.../meetings/...` shows `state_hash_before` in the
  response JSON."**

- **"TypeScript types include `replay_format_version: string` which
  does not exist on the Pydantic `ReplayMetadataView`. Generated
  types are stale — `npm run gen:api` shows a diff against
  HEAD-committed `types/api.ts`."**

These examples are FORMAT references, not findings to copy. Cite real
`file:line` evidence for every finding in your actual report.

---

**Begin the audit. Write only to your report file in `audits/`. Do
not modify any other file. End with the "Required closing fields"
block in §5 #9.**
