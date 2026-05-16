# Post-3.3 Checkpoint Audit — Prompt

You are auditing the AiLibi repository at its current `HEAD` of `main`,
at the end of Phase 3 sub-phase A (Foundation: Tasks 3.1, 3.2, 3.3).
The next sub-phase (3.4–3.8: prompt templates + meeting state machine)
will build on top of what landed in these three tasks. The cost of a
shaky foundation is high; that is what this checkpoint exists to
catch before more code is built on it.

You will produce **one audit report** in `audits/` following the
format, rigor, and section structure of the most recent prior audit
(`audits/audit-2026-05-16-0036-reconciled.md`). That file is the
canonical template; do not invent a new shape.

You are running independently from another auditor (a different LLM
tool) who may be producing their own report from the same prompt.
**Do not read any other audit file under `audits/` newer than
`audit-2026-05-16-0036-reconciled.md`, and do not read any file
under `audits/prompts/` except this one.** If two reports get
produced, they will be reconciled in a later step using
`audits/prompts/pre-phase-3-reconciliation-prompt.md`; their value
depends on being produced blind to each other.

---

## 1. Identity and constraints

- **Role:** read-only auditor. You may read any file, run any
  non-mutating shell command, and execute the full test/lint/type
  suite. You may not edit source files, tests, fixtures,
  configuration, task documents, agent prompts, or any file outside
  `audits/`. The only file you write is your audit report.
- **No fixes.** If you see a defect, record it as a finding. Do not
  patch it, even one line. Repair work is owned by a separate task
  that will be authored from this audit (or its reconciliation, if
  two reports are produced).
- **No speculation.** Every finding must cite a `file:line` (or a
  reproducible shell command and its observed output). A finding
  without a citation is not a finding.
- **No drive-by suggestions.** If a recommendation does not address a
  cited defect or unverified invariant, omit it. The audit is a
  defect register, not a wishlist.
- **No real LLM provider calls.** Tests in this repo use a fake
  deterministic provider. You may run `bash scripts/check.sh` and
  any pytest invocation, but do not invoke the real Anthropic
  client. If a CI test depends on a real provider, that is itself
  a finding (`pytest.mark.real_provider` should isolate those).

## 2. Scope

**Audit window:** commits `b8fbb21` (HEAD after Task 2.14 merged, the
prior audit's effective endpoint) → current `HEAD` of `main`. Use
`git log b8fbb21..HEAD --oneline --name-status` to enumerate every
commit and changed file in the window.

**Tasks landed in the window** (verify each against
`tasks/phase-3.md`):

- Task 3.1 — LLM client (PR #37, merged at `dffe2ef`). New
  package `llm/`: client, provider, fake provider, cache, budget,
  plus `llm/README.md` documenting the cross-provider portability
  shape.
- Task 3.2 — Shared meeting/output schemas and `BodyView.victim_id`
  boundary (PR #38, merged at `f4c44e0`). Two bundled deliverables:
  (a) `meetings/schemas.py` canonical meeting DTOs, (b) the R-4
  retirement walking engine → observation → perception → impostor
  policy to replace `_BODY_ID_VICTIM_PATTERN` with a typed
  `victim_id` field on `BodyView`.
- Task 3.3 — Memory rendering (PR #39, merged at `7050235`). New
  module `agents/memory/store.py` exposing the composite memory
  surface and `render_for_prompt` per DESIGN.md §6.6. Closes R-6.

Note: each task had review-iteration commits (e.g. "task 3.1:
address codex review"). The diff against `main` is what matters; do
not separately audit each iteration commit.

**Explicitly out of scope:** Phase 0, Phase 1, and Phase 2 code that
was verified in the May-16 reconciled audit and has not changed in
the window. Use `git diff b8fbb21..HEAD -- <path>` to confirm "no
diff" before marking anything as "Still Pass (no diff)" in your
Regression Baseline section. Sub-phase B work (Tasks 3.4–3.8) is
not yet started; `llm/` and `meetings/` are populated but the four
prompt templates and the meeting state machine do not exist yet.

## 3. Required evidence

Run all of the following from the repo root. Record exit codes and
the last line of output for each in §3 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run mypy --strict agents observation orchestrator engine llm meetings`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run pytest tests/llm -v`
- `uv run pytest tests/meetings -v`
- `uv run pytest tests/agents -v`
- `uv run pytest tests/observation -v`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/generate_prompts.py --check`
- `git grep -nE "_BODY_ID_VICTIM_PATTERN" agents/`
  (must return empty — the regex must be deleted, not just stopped-being-used)
- `git grep -nE "re\.compile\(.*body-" agents/ observation/`
  (must return empty — no surviving regex pattern matching engine body-id formats)
- `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/`
  (must return empty — pre-existing guard from Task 2.11)
- `git grep -nE "anthropic|cache_control|extended_thinking" agents/ meetings/ orchestrator/`
  (occurrences here would mean Anthropic-specific concepts leaked outside `llm/`; verify each hit is documentation-only or in scope)

Then run the live harnesses to verify outcomes:

- Six-seed sweep:
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/audit-r-$seed.jsonl --max-ticks 1000; done`
  — record outcomes; balance check confirmed by 2.14, this is a
  smoke check.
- 100-game tournament:
  `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/audit-tournament-3-3 --max-ticks 1000`
  — verify both decisive sides still > 20% post-2.14. The pre-3.x
  baseline from PR #31 was 73.12% / 26.88%; the new value may have
  shifted after Task 2.14's win-order change. Both should stay > 20%.
- 100-game tournament leak scan (scanner should PASS over all
  packets across all 100 games — `BodyView.victim_id` addition
  must not break it).

Run additional commands as needed to verify specific findings.
Every command you run appears in §3 with its output evidence.

## 4. Required report structure

Mirror the structure of `audit-2026-05-16-0036-reconciled.md`:

1. Executive Summary (≤ 8 sentences; lead with the verdict).
2. Verdict — one of: **Ready for sub-phase B**, **Ready with fixes**,
   **Not ready**. Quantify what "fixes" means if applicable.
3. Commands Run and Evidence Sources.
4. Regression Baseline — table comparing every prior-Pass row in
   `audit-2026-05-16-0036-reconciled.md` §4 to current state. "No
   diff" ⇒ Still Pass; "diff exists" ⇒ re-verified with citation.
5. Prior Audit Follow-Through — for each finding R-1 through R-7 in
   `audit-2026-05-16-0036-reconciled.md` §10, state whether the
   in-window work closed it. R-1 (DESIGN.md `tasks_per_crewmate`
   drift), R-2 (same-tick crew-win pin), R-3 (body-id missing-payload
   pin), R-4 (body-id regex retirement, owned by 3.2), R-5 (Phase 2
   long-horizon byte identity, still owned by 3.12), R-6 (composite
   memory surface, owned by 3.3), R-7 (`"victim-body"` test string).
   Cite resolving commits, diffs, and pinning tests.
6. Task-by-Task DoD Audit — one subsection per in-window task (3.1,
   3.2, 3.3). For each: enumerate every DoD bullet from
   `tasks/phase-3.md`, mark Pass / Fail / Partial, cite evidence.
7. Architectural Invariant Audit — re-run every invariant from
   `audit-2026-05-16-0036-reconciled.md` §7 (I-1 through I-12 plus
   multi-agent). The boundary refactor in 3.2 and the new `llm/`
   surface in 3.1 mean the firewall and engine-purity invariants
   must be re-verified, not assumed.
8. Specific Questions for the Sub-Phase B Layer — answer each
   question in §7 below.
9. Test Quality and Coverage Gaps — scrutinize the new tests in
   `tests/llm/`, `tests/meetings/`, `tests/agents/test_memory_rendering.py`
   for false-positive risk and whether they actually catch the
   regression they claim to.
10. Defects and Risks (ordered by severity) — `[Severity] short title`
    then Status / Evidence / Why it matters / Recommended action.
    Severity buckets: **Critical**, **High**, **Medium**, **Low**,
    **Concern**.
11. Document Conflicts — `DESIGN.md`, `AGENTS.md`,
    `AGENT_IMPLEMENTATION.md`, `tasks/phase-*.md`, and code. Note
    new conflicts only.
12. Readiness for Sub-Phase B — direct answer with citations. See
    §7 below.

## 5. Severity grading rubric

- **Critical** — A documented invariant is violated by code currently
  on `main`, OR observation packets leak hidden information, OR
  determinism is broken across two runs of the same seed, OR a Phase
  2 Merge Criterion fails on a real harness invocation, OR an
  Anthropic-specific concept leaks through the `LLMClient` Protocol
  surface in a way that prevents swapping providers without
  refactoring call sites.
- **High** — A DoD bullet for an in-window task is unmet, OR an
  architectural invariant is no longer pinned by a test (the code
  may still happen to satisfy it), OR the fake provider is not
  actually deterministic across two same-prompt calls, OR the budget
  enforcement silently truncates instead of raising.
- **Medium** — Scope discipline violation (a PR touched files
  outside its contract's `Files in scope`, beyond what `## Decisions`
  documented), OR a documented behaviour is contradicted by another
  document, OR a regression test required by a DoD is missing but
  the underlying behaviour is correct.
- **Low** — Brittleness, latent failure modes that are currently
  unreachable, or coupling that is not enforced by a test.
- **Concern** — Worth flagging for sub-phase B but not a defect in
  current code.

If unsure between two buckets, choose the more conservative
(higher-severity) reading and say why in the finding body.

## 6. Deep-focus areas (do not skip)

These are the highest-blast-radius spots in the three in-window PRs.
Produce a verdict for each with citations, even if the verdict is
"Pass".

### 6.1 R-4 retirement completeness (Task 3.2)

Task 3.2 was supposed to delete `_BODY_ID_VICTIM_PATTERN` and walk
the new `BodyView.victim_id` field through observation → perception →
impostor policy. Verify the full chain:

- `observation/packet.py::BodyView` has a `victim_id: PlayerId`
  field with Pydantic validation.
- `observation/service.py` populates `BodyView.victim_id` from
  `BodyState.player_id` on every body in every packet.
- `agents/perception.py` adds `victim_id` to `saw_body` event
  payloads (the existing `body_id` field stays for body identity).
- `agents/tactical/impostor_policy.py::_confirmed_dead_from_bodies`
  reads `victim_id` directly and no longer references any regex.
- `_BODY_ID_VICTIM_PATTERN` is deleted from `agents/tactical/impostor_policy.py`
  entirely. The `re` import is removed if it became unused.
- Task 2.13's R-3 test (formerly
  `test_confirmed_dead_from_bodies_raises_on_missing_body_id`)
  is renamed and retargeted for `victim_id`. The test must NOT
  pin a removed code path.
- The leak scanner still passes on 10+ tournament audit logs with
  `BodyView.victim_id` present in every packet's body list.

Any incomplete step is a **High** finding; if the regex still exists
in code, that is **Critical** (the audit's R-4 finding is not
closed).

### 6.2 R-6 closure: composite memory surface (Task 3.3)

Task 3.3's R-6 acceptance gate required `agents/memory/store.py` to
expose a composite memory surface aggregating episodic, working,
and belief state, with `render_for_prompt` reading from all three.
Verify:

- `agents/memory/store.py` exists and is importable.
- The composite surface reads from `agents/memory/episodic.py`,
  `agents/memory/working.py`, AND `agents/memory/beliefs.py` — not
  one of the three in isolation.
- `render_for_prompt` produces a structured view per DESIGN.md §6.6
  (role, tasks completed, recent observations salience-sorted,
  beliefs, open contradictions).
- The token-budget mechanism documented in DESIGN.md §6.6 (drop
  events past budget by lowest salience first) is implemented and
  tested.
- Golden fixtures or tests pin the rendered output structure.

If the composite surface only reads from one or two components, R-6
is **Partial** (a fresh High finding). If `render_for_prompt`
doesn't exist, R-6 is **Not closed** (Critical).

### 6.3 LLM client provider-neutrality (Task 3.1)

The Protocol must not expose Anthropic-specific concepts. Verify:

- `llm/client.py` defines an `LLMClient` Protocol. Its public method
  signatures take provider-neutral arguments: prompt text, schema,
  max_tokens, temperature, etc. No `cache_control`, no
  `extended_thinking`, no `beta` parameters in the Protocol itself.
- `llm/provider.py` (or wherever `AnthropicClient` lives) implements
  the Protocol. Anthropic-specific behaviors are private to that
  module.
- `llm/README.md` (or top-of-file docstring) shows the minimum
  surface a second-provider adapter must implement, with a 10–20
  line sketch demonstrating an OpenAI or DeepSeek shape.
- Call sites in `agents/`, `meetings/`, and `orchestrator/` (if any
  exist yet — likely just imports of types) reference only the
  Protocol, never `AnthropicClient` directly.
- `git grep -nE "anthropic|cache_control|extended_thinking" agents/ meetings/ orchestrator/`
  returns either nothing or documentation-only hits.

A Protocol that leaks Anthropic concepts to call sites is **Critical**
(it defeats the cross-provider portability requirement that was
explicitly contracted).

### 6.4 Fake provider determinism (Task 3.1)

The fake provider must produce the same response shape for the same
prompt across two calls. Verify:

- Read `llm/fake_provider.py`. The implementation must NOT use
  randomness, wall-clock time, or any non-deterministic input. If
  it uses hashing for response selection, the hash input is purely
  the prompt content + schema.
- Tests in `tests/llm/test_client.py` (or equivalent) call the fake
  provider with the same prompt twice and assert identical response
  shape.
- The fake provider produces schema-valid responses (i.e. responses
  that pass Pydantic validation against the requested schema).

A fake provider that is not actually deterministic is **High** — CI
would flake.

### 6.5 Budget enforcement is fail-loud (Task 3.1)

The per-game budget must raise a typed exception on overrun, not
silently truncate. Verify:

- `llm/budget.py` defines a budget object that tracks cumulative
  cost across a game.
- On overrun, the budget raises a typed exception (not just
  `Exception`; not just a print/log).
- Tests cover the overrun path explicitly.
- The budget is wired through `LLMClient` so every call goes through
  it; there is no path that bypasses the budget.

A silently-truncating budget is **High** — Phase 3.x agents could
hit the limit mid-meeting and produce invalid output.

### 6.6 Meeting schema completeness vs DESIGN.md §5.3/§5.5 (Task 3.2)

`meetings/schemas.py` should match the canonical types in DESIGN.md.
Verify:

- `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and
  contradiction/result DTOs exist with shapes matching DESIGN.md
  §5.3 and §5.5.
- The schemas are Pydantic v2 (suitable for structured LLM output).
- `agents/strategic/output_schemas.py` re-exports or wraps these
  without duplicating them.
- No type drift between `meetings/schemas.py` and any usage site.

If a type is missing or shape-mismatched against DESIGN.md, that is
a **Medium** finding (sub-phase B prompts will need to invent it,
which drifts further).

### 6.7 Composite memory's token-budget behavior (Task 3.3)

DESIGN.md §6.6 requires the renderer to drop events past the token
budget by lowest salience first. Verify:

- The renderer measures token count (or a proxy thereof — character
  count is acceptable as long as the choice is documented).
- Events are dropped salience-sorted, lowest first, not in arrival
  order or alphabetical order.
- The token budget is configurable per call (not hardcoded), so
  Phase 3.9's strategic reasoner can tune it.
- Tests cover at least one over-budget case (forcing event drop)
  and one under-budget case (all events fit).

A renderer that doesn't drop events under budget, or drops by the
wrong rule, is **High**.

### 6.8 Engine isolation under the new modules

With `llm/` and `meetings/` added, reconfirm:

- `lint-imports` still kept the agent→engine firewall.
- No `engine.*` import has slipped into `agents/`, `llm/`, or
  `meetings/`. Run `grep -rn "from engine" agents/ llm/ meetings/`
  to confirm.
- No `agents.*` import has slipped into `engine/`.
- `llm/` does not import from `agents/` or `meetings/` (the
  dependency should flow `agents/`, `meetings/` → `llm/`, not back).

## 7. Specific questions for the sub-phase B layer

Answer each in §12 of your report with a one-paragraph verdict and
citations:

1. **Can the four prompt templates (Tasks 3.4–3.7) consume
   `meetings/schemas.py` without re-defining types?** Read the
   schemas and consider what `task-3-4-crewmate-report-prompt.md`,
   `task-3-5-impostor-report-prompt.md`,
   `task-3-6-accusation-round-prompt.md`, and
   `task-3-7-vote-ballot-prompt.md` will need. If any of these will
   require a type that does not exist in `meetings/schemas.py`,
   that is a sub-phase B blocker (Medium at minimum).
2. **Does `render_for_prompt`'s output shape match what the prompt
   templates need to feed to the LLM?** The four prompt tasks will
   wrap rendered memory + meeting context into LLM calls. If
   `render_for_prompt` returns a Markdown string only, that may
   force prompt templates to do their own context assembly; if it
   exposes structured fields, prompt templates can compose more
   cleanly. Either is fine — but flag which it is and whether
   sub-phase B's task contracts assume the right shape.
3. **Does the meeting state machine (Task 3.8) have a clean
   integration point in the LLM client?** Sub-phase B's 3.8 will
   call the LLM client for each agent's report / accusation / vote.
   The `LLMClient.complete` (or equivalent) signature must support
   per-call schema constraints. If the Protocol can only return
   unstructured text, 3.8 will have to do its own JSON-parsing,
   which is a sub-phase B-readiness gap.
4. **Are there any Anthropic-specific assumptions in `agents/` or
   `meetings/` that would break a future OpenAI/DeepSeek swap?** Run
   the grep above; for each hit, decide whether it's a real coupling
   or documentation-only.
5. **Did Task 2.14's win-order change interact with anything
   3.1/3.2/3.3 introduced?** It shouldn't (the win order is an
   engine concern; LLM/schemas/memory don't read win conditions),
   but verify. A tournament rerun in §3 will surface unexpected
   interaction if any.
6. **New Critical/High findings introduced by this audit window?**
   List any. If yes, they must be addressed before sub-phase B
   begins; if no, sub-phase B may proceed.

## 8. Output

Write your report to:

`audits/audit-YYYY-MM-DD-HHMM-<tool>.md`

where `<tool>` is `codex` or `claude` (whichever you are). Use the
current local date and time. Include `<tool>` in the filename so
two independent reports (if run in parallel) do not collide.

If only one tool is running this audit, the filename suffix is still
required — reconciliation tooling auto-discovers the two newest
unreconciled audit files. A single-tool run still produces a
canonical audit when no reconciliation is needed; the reviewer reads
the single report directly.

Do not commit. Do not open a PR. Do not modify any other file. When
finished, print the absolute path of the report and a one-paragraph
summary naming: the verdict, the count of Critical / High / Medium
findings, and the single most important thing to fix before
sub-phase B begins.

---

## Anti-patterns (do not do these)

- Do not paraphrase the May-16 reconciled audit's findings as if you
  re-verified them. Either re-run the check and cite the new
  evidence, or omit the finding.
- Do not produce a "looks good" section. Either a thing is verified
  with evidence, or it is a Concern.
- Do not include code suggestions, refactor proposals, or
  architectural improvements that are not tied to a cited defect.
- Do not soften severities to be polite. A Critical finding stays
  Critical even if the responsible PR is recent.
- Do not invoke the real Anthropic provider. Every test in this
  audit runs against the fake.
- Do not write more than ~500 lines. The audit window is three
  tasks; that bounds the report length.
- Do not re-litigate Task 2.14's win-order change. That decision is
  final and documented in DESIGN.md §3.5. Audit the implementation
  of subsequent tasks, not the win-order choice.
- Do not audit Task 3.4–3.8 work that does not exist yet. If a
  question depends on code that hasn't been written, frame it as a
  sub-phase B readiness question (§7), not a finding.
