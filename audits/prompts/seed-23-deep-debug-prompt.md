# Seed 23 Deep Debug — Prompt

You are debugging seed 23 of the AiLibi headless tournament. Every
Pre-Phase-4 real-provider eval to date has crashed at the same point:
the first live meeting, which always fires in game 24 (seed 23) of
the 50-game sweep. Three sequential eval runs surfaced three distinct
defect classes (markdown fences, prompt↔schema drift, truncation),
each fixed in a separate Task (3.15, 3.16, 3.17). The pattern is
"one defect per eval, find at first meeting, fix in a focused PR,
repeat." This investigation breaks the pattern.

**Your goal:** capture EVERY layer of the live meeting flow for seed
23 in a single comprehensive pass, surface all remaining latent
defects (not just the next surface crash), and produce one detailed
report. Continue past any failure by exercising downstream layers
manually with direct live-provider calls.

You write **no source code edits** — only an ephemeral debugging
script under `/tmp/` and your final report under `audits/`. You may
spend up to **$5 of live API budget** for this investigation;
typically actual spend will be ~$0.50–$2.

---

## 1. Identity and constraints

- **Role:** read-only investigator with one ephemeral-script
  exception. You may read any file, run any non-mutating shell
  command, write a single ad-hoc debugging script to `/tmp/seed-23-debug/`
  (NOT committed; not under `agents/`, `engine/`, `tests/`, etc.),
  and call the live Anthropic provider as needed.
- **No source code edits.** Fixes live in follow-up tasks; this
  investigation surfaces what needs fixing, not how. If your script
  needs to import from the project, do so by reading public symbols
  — do not modify any project file.
- **No test edits.** Same reasoning.
- **No commits.** Working tree stays clean.
- **Budget discipline.** Hard cap: $5 in live API spend for this
  investigation. Soft target: $0.50–$2. If a single call costs >$0.50,
  stop and report. If cumulative spend exceeds $3, stop and finalize
  the report with what you have.
- **No git push, no PR.** Pure investigation deliverable.

## 2. Inputs and forbidden inputs

**Allowed reads:**

- The repository at current `HEAD`.
- The four prior Pre-Phase-4 real-provider eval reports under
  `audits/audit-2026-05-25-*-pre-phase-4-real-provider-eval.md`
  (the chain of crashes that led here).
- Tasks 3.14 through 3.17 in `tasks/phase-3.md` (the chain of fixes).
- `audits/audit-2026-05-25-0414-reconciled.md` (the Pre-Phase-4
  reconciled audit, for context on the substrate's intent).
- Live calls to the Anthropic provider via the existing
  `llm.provider.AnthropicClient`.

**Forbidden reads:**

- No other audit prompt files under `audits/prompts/` (they would
  anchor your investigation to their framings).
- No other audits under `audits/` newer than the Pre-Phase-4
  reconciled audit, except the four real-provider eval reports above.

## 3. Required investigation steps

Walk these in order. Each step's findings feed the next.

### 3.1 Pre-flight

- Confirm `.env` is sourced and the live provider is configured:
  - `echo "$AILIBI_LLM_PROVIDER"` → `anthropic`
  - `echo "$AILIBI_LLM_MEETING_MODEL"` → `claude-sonnet-4-6`
  - `echo "$ANTHROPIC_API_KEY" | head -c 8` → 8 chars (do NOT log the rest)
- Run `bash scripts/check.sh` — must pass (676+ tests, some skipped).
  Confirms the substrate hasn't regressed between Task 3.17 merge and
  this investigation.
- Run the direct sanity call from
  `audits/prompts/pre-phase-4-real-provider-eval-prompt.md` §2 — must
  return non-zero `cost_usd`, sensible text. Cost: ~$0.0001.

If any check fails, stop and report. Verdict: **Pre-flight failed.**

### 3.2 Fake-provider baseline for seed 23

Run seed 23 against the fake provider and capture the meeting trigger
details:

```bash
uv run python scripts/run_game.py \
  --seed 23 \
  --replay-path /tmp/seed-23-debug/fake-replay.jsonl \
  --max-ticks 1000
```

(Make `/tmp/seed-23-debug/` first.)

Examine the replay log. Required findings:

- **Outcome:** what did the game end with? (CREWMATES, IMPOSTORS,
  TICK_BUDGET_REACHED, or did it actually fire a meeting under the
  fake provider?)
- **Meeting trigger:** if a meeting did fire (the prior reports
  suggest one does at the first live attempt), at which tick? Which
  agent reported the body or pressed emergency? Who was alive at
  trigger time?
- **Pre-trigger state:** which agents are alive, where, with which
  observations? Read the `tick` entries before the meeting (or before
  the crash) to reconstruct.

Record findings in §3 of your report.

### 3.3 Identify the exact meeting trigger for seed 23

Whether or not the fake-provider baseline fires a meeting (the FakeProvider
may or may not fire one depending on its trigger-condition handling),
trace the engine + orchestrator code path to identify what triggers a
meeting for seed 23 specifically. Read:

- `engine/tick.py` — what conditions trigger a `MEETING` phase?
- `orchestrator/game.py` — the meeting interpose branch.
- The seed-23 replay log to identify the tick and triggering action.

Required findings:

- The exact tick at which the meeting fires.
- The triggering action (body discovery, emergency button, etc.).
- The triggering agent (who pressed the button or reported the body).
- The list of alive agents at trigger time (the meeting participants).

### 3.4 Capture rendered_memory for each participant (instrumented run)

Write an ad-hoc Python script at `/tmp/seed-23-debug/capture_prompts.py`
that:

1. Loads the canonical map.
2. Replays seed 23 deterministically up to the meeting trigger tick
   (use `engine.tick.advance_tick` directly or `HeadlessGame` with a
   patched runner).
3. At the trigger tick, for each alive agent, constructs the
   `rendered_memory` view they would see at meeting time. Use
   `agents.memory.store.render_for_prompt` against the agent's
   memory state at that tick.
4. For each agent, constructs the production crewmate or impostor
   report prompt by loading the actual `.j2` template via
   `agents.strategic.prompts.loader` and rendering it with the
   agent's `rendered_memory` + meeting context.
5. Writes each prompt verbatim to `/tmp/seed-23-debug/prompts/<agent_id>-report.txt`.

The script is ad-hoc and ephemeral; do not commit it. The agent code
paths are stable enough that you can read them and construct the
inputs without modifying any source file.

Required findings for §3 of your report:

- The four (or five — depends on alive count at trigger) full
  rendered prompts. Quote each prompt's first ~500 chars and last
  ~200 chars verbatim.
- Note: prompt length per agent (token estimate via simple
  whitespace split is fine; the actual tokenization happens
  inside `AnthropicClient`).

### 3.5 Live-provider full meeting walk

For each captured prompt from §3.4, send it to the live Anthropic
provider via `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"]).complete(...)`
with `schema=ReportDocument`, `max_tokens=2048` (the current
`DEFAULT_REPORT_MAX_TOKENS` post-Task 3.17), `temperature=0.0`.

**This is the critical step.** Capture EVERY response:

1. The raw response text (pre-strip, pre-validate).
2. The post-fence-strip text (after `_strip_json_code_fences`).
3. Whether `model_validate_json` succeeded.
4. If it failed, the full Pydantic error message + the offending
   input value (first 500 chars).
5. Token usage: `input_tokens`, `output_tokens`.
6. Cost: `cost_usd`.
7. Model id returned.

Save each response to `/tmp/seed-23-debug/responses/<agent_id>-report-<phase>.json`.

**Continue past any crash.** If agent p-1's report call fails with a
ValidationError, do NOT stop — proceed to agent p-2's report call,
then p-3, etc. The goal is to characterize ALL the failure modes in
one pass, not just the first one.

**After the report phase, simulate the accusation phase.** Even if
some reports failed, construct a synthetic `MeetingTranscript`
containing whatever valid reports were captured (or hand-write a
minimal valid transcript if all reports failed) and exercise the
accusation_round prompt template for each agent. Same capture
protocol. Schema: `Statement`. `max_tokens=512`.

**After the accusation phase, simulate the voting phase.** Same:
synthetic transcript, exercise the vote_ballot template, capture
every response. Schema: `VoteBallot`. `max_tokens=384`.

Required findings:

- Per-agent, per-phase outcome: succeeded / failed with [error type].
- Per-call cost.
- Cumulative cost for the full meeting simulation.
- Any failure mode NOT seen in the prior four eval crashes.

Budget check: each call costs ~$0.015–$0.05. Five agents × three
phases = 15 calls ≈ $0.20–$0.75 worst case. Stop if any single call
exceeds $0.50 or cumulative exceeds $3.

### 3.6 Pipeline analysis

For every failed call from §3.5, trace exactly where the failure
occurred in the pipeline:

- Did the raw response have markdown fences? Were they closed?
- Did `_strip_json_code_fences` correctly handle the response?
- Did the JSON parse? If not, was it truncated, malformed, or
  schema-noncompliant?
- If parsed, did Pydantic accept it? Which fields failed validation?
- Were the field names in the response consistent with the current
  schema (`subject`, `room`, `from_tick`, `to_tick`, etc.)?

Required findings:

- A trace table mapping each failed call to its precise failure
  layer.
- Identification of any defect class NOT already covered by Tasks
  3.15, 3.16, 3.17.

### 3.7 Latent issue audit

Beyond surface crashes, look for:

- **Token usage near caps.** If any successful call's `output_tokens`
  is ≥ 95% of its `max_tokens` cap, the next eval run could see
  truncation. Flag.
- **Discriminated union edge cases.** The `Claim` and
  `ObservationClaim` types are likely discriminated unions. Did the
  model ever emit a discriminator value that the schema doesn't
  accept? An empty discriminator?
- **Cost per call vs estimated.** Are real-provider per-call costs
  meaningfully higher than the eval prompt's estimates? If so, the
  $0.30/game merge criterion may be unmeetable.
- **Latency / rate-limit signals.** Did any call take unusually
  long? Did you see HTTP 429 responses?
- **JSON quirks beyond fences.** Trailing commas? Comments?
  Pre/post-JSON prose? XML tags? Empty responses?
- **Schema field naming gaps.** Even if Task 3.16 fixed the known
  drift, are there fields the templates ask for that don't exist on
  the schema (or vice versa)?
- **Meeting state machine assumptions.** Does the manager assume
  every agent submits a valid response? What happens to an agent
  whose report parsed but contained an empty list of observations?

Each latent issue gets a row in the report's §10.

## 4. Required report structure

Write to `audits/audit-YYYY-MM-DD-HHMM-seed-23-deep-debug.md` (use
current local date/time). Required sections:

1. **Executive summary.** ≤ 8 sentences. Lead with: did seed 23
   complete a meeting end-to-end? Total live spend? Count of distinct
   defect classes surfaced (NEW vs already-known).
2. **Pre-flight outcome.** Env vars, sanity call result.
3. **Fake-provider baseline.** Outcome of seed 23 under fake
   provider; meeting trigger details if available.
4. **Meeting trigger characterization.** Exact tick, action, agent,
   alive participants for seed 23.
5. **Captured prompts.** Per-agent prompt summaries (length, first
   and last chunks). Note any prompt-level anomalies.
6. **Per-call response capture.** Table:

   | Phase | Agent | Schema | Raw text len | Stripped len | Parse ok? | Validation ok? | tokens (in/out) | Cost |
   |---|---|---|---|---|---|---|---|---|

   One row per call attempted.
7. **Pipeline failures.** For each parse/validation failure, the
   precise layer and exact error.
8. **Cost summary.** Total spend; mean per call; max single call;
   estimated per-full-meeting cost.
9. **Latent issues surfaced.** Per §3.7, every potential future
   failure mode you identified. Each gets a `[Severity] short title`
   header (Critical / High / Medium / Low / Concern), plus
   Status / Evidence / Why it matters / Recommended remediation
   (one or two sentences each).
10. **Defect-class taxonomy.** A list of all defect classes seen
    across the four prior eval crashes + this investigation. Mark
    each as Fixed (which task) or Open. Include any NEW classes you
    found in §3.5–§3.7.
11. **Recommended next task scope.** If a fix is clearly needed,
    sketch the task scope (~5–8 bullets): what files, what change,
    what test. If multiple fixes are needed, group them logically
    (one task per defect class, or one bundled task if they share
    a code path).
12. **Confidence assessment.** After this debug pass, how confident
    are you the next eval will complete? List remaining unverified
    risks.

## 5. Output deliverables

- The report at `audits/audit-YYYY-MM-DD-HHMM-seed-23-deep-debug.md`.
- The ephemeral artifacts under `/tmp/seed-23-debug/` (prompts,
  responses, instrumentation script). Reference them in the report;
  do NOT commit them.
- The total live API spend, printed at the end of the report.

When finished, print:

- The absolute path of the report.
- Total live spend in USD.
- Count of NEW defect classes (not previously seen in 3.15/3.16/3.17).
- Recommended next-step verdict: **Run eval again** /
  **Fix [N] issues first** / **Investigation incomplete**.

---

## 6. Anti-patterns (do not do these)

- Do not stop at the first failure. The whole point is to surface
  ALL failures in one pass. Continue manually past any crash.
- Do not modify any source file. The investigation produces
  findings; fixes go in follow-up tasks.
- Do not run the full 50-game tournament. Seed 23 in isolation is
  the target.
- Do not commit the `/tmp/seed-23-debug/` artifacts. Ephemeral
  only.
- Do not print the API key. Eight-character prefix in the report;
  nothing more.
- Do not assume the live model will fail the same way as prior
  evals. The point is to characterize NEW failure modes, not
  re-litigate old ones.
- Do not exceed $5 in cumulative live API spend. Stop and
  finalize the report if approaching the budget.
- Do not produce a "looks good" section. Either something is
  verified with captured evidence, or it is a Concern.
- Do not write more than ~700 lines in the report. The investigation
  is detailed but bounded; if you are over, you are speculating
  rather than capturing evidence.
