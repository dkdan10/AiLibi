# Post-3.8 Checkpoint Audit — Prompt

You are auditing the AiLibi repository at its current `HEAD` of `main`,
at the end of Phase 3 sub-phase B (Meeting machinery: Tasks 3.4, 3.5,
3.6, 3.7, 3.8). The next sub-phase (3.9–3.12: strategic reasoner,
voting, contradiction detection, orchestrator integration) closes
Phase 3. Sub-phase C's tasks all consume what landed in sub-phase B:
the prompt templates, the canonical-ordered transcript, the meeting
state machine, and the `MeetingResult` shape. A defect in the
sub-phase B substrate compounds across four downstream tasks; that
is what this checkpoint exists to catch.

You will produce **one audit report** in `audits/` following the
format, rigor, and section structure of the most recent prior audit
(`audits/audit-2026-05-16-0611-claude.md`). That file is the
canonical template; do not invent a new shape.

You are running independently from another auditor (a different LLM
tool) who may be producing their own report from the same prompt.
**Do not read any other audit file under `audits/` newer than
`audit-2026-05-16-0611-claude.md`, and do not read any file under
`audits/prompts/` except this one.** If two reports get produced,
they will be reconciled in a later step using
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
  authored from this audit (or its reconciliation, if two reports
  are produced).
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

**Audit window:** commits `7050235` (HEAD when the post-3.3 audit
ran, after Task 3.3 merged) → current `HEAD` of `main`. Use
`git log 7050235..HEAD --oneline --name-status` to enumerate every
commit and changed file in the window.

**Tasks landed in the window** (verify each against
`tasks/phase-3.md`):

- Task 3.4 — Crewmate report prompt (PR #40, merged `22c32f7`).
- Task 3.5 — Impostor report prompt (PR #42, merged `ef59611`).
- Task 3.6 — Accusation round prompt (PR #43, merged `9cb1de2`).
- Task 3.7 — Vote ballot prompt (PR #41, merged `fc0ac90`).
- Task 3.8 — Meeting state machine (PR #44, merged `45e664f`).

Plus small task-doc-only commits (e.g. `0ab6c5d setup task 3.8`) and
review-iteration commits within each task — the diff against `main`
is what matters; do not separately audit each iteration commit.

**Explicitly out of scope:** Phase 0, Phase 1, Phase 2 code that was
verified in previous audits and has not changed in the window. Use
`git diff 7050235..HEAD -- <path>` to confirm "no diff" before
marking anything as "Still Pass (no diff)" in your Regression
Baseline section. Sub-phase C work (Tasks 3.9–3.12) is not yet
started; `agents/strategic/reasoner.py`, voting wiring, contradiction
detection, and orchestrator/meeting integration do not exist yet.

## 3. Required evidence

Run all of the following from the repo root. Record exit codes and
the last line of output for each in §3 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run mypy --strict agents observation orchestrator engine llm meetings`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run pytest tests/meetings -v`
- `uv run pytest tests/llm -v`
- `uv run pytest tests/agents -v`
- `uv run pytest tests/observation -v`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/generate_prompts.py --check`
- `git grep -nE "_BODY_ID_VICTIM_PATTERN" agents/`
  (must return empty — R-4 retirement should still hold)
- `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/`
  (must return empty — pre-existing guard)
- `git grep -nE "anthropic|cache_control|extended_thinking" agents/ meetings/ orchestrator/`
  (occurrences here would mean Anthropic-specific concepts leaked
  outside `llm/`; verify each hit is documentation-only or in scope)
- `git grep -nE "round_index" meetings/ tests/meetings/`
  (every consumer of `Statement.round_index` should rely on the
  canonical-order contract from Task 3.8, not re-sort)

Then run the live harnesses to verify outcomes:

- Six-seed sweep:
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/audit-r-$seed.jsonl --max-ticks 1000; done`
  — record outcomes. Phase 2 substrate balance was 62.37%/37.63%
  post-3.3; re-verify it has not drifted.
- 100-game tournament:
  `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/audit-tournament-3-8 --max-ticks 1000`
  — both decisive sides must still > 20%.
- 100-game tournament leak scan (scanner should PASS over all
  packets across all 100 games).

Then run the meeting state machine end-to-end with the fake provider
to verify the C-3 canonical-order contract holds in practice:

- `uv run pytest tests/meetings/test_manager.py -v`
- `uv run pytest tests/meetings/test_transcript.py -v`

Run additional commands as needed to verify specific findings.
Every command you run appears in §3 with its output evidence.

## 4. Required report structure

Mirror the structure of `audit-2026-05-16-0611-claude.md`:

1. Executive Summary (≤ 8 sentences; lead with the verdict).
2. Verdict — one of: **Ready for sub-phase C**, **Ready with fixes**,
   **Not ready**. Quantify what "fixes" means if applicable.
3. Commands Run and Evidence Sources.
4. Regression Baseline — table comparing every prior-Pass row in
   `audit-2026-05-16-0611-claude.md` §4 to current state. "No
   diff" ⇒ Still Pass; "diff exists" ⇒ re-verified with citation.
5. Prior Audit Follow-Through — for each finding L-1, L-2, C-1,
   C-2, C-3 in `audit-2026-05-16-0611-claude.md` §10, state whether
   the in-window work closed it. C-3 was explicitly assigned to
   Task 3.8; verify the resolution. L-1 and L-2 may have been
   addressed during 3.4–3.7 review cycles or left open — cite the
   evidence either way. C-1 belongs to Task 3.9 (sub-phase C) and
   stays open at this checkpoint by design. C-2 belongs to the
   sub-phase B reviewer; if not addressed during 3.4–3.7 reviews,
   call it out as still open.
6. Task-by-Task DoD Audit — one subsection per in-window task (3.4,
   3.5, 3.6, 3.7, 3.8). For each: enumerate every DoD bullet from
   `tasks/phase-3.md`, mark Pass / Fail / Partial, cite evidence.
   Task 3.8's C-3 directive bullets are the most important — verify
   both the implementation choice and the regression test.
7. Architectural Invariant Audit — re-run every invariant from
   `audit-2026-05-16-0611-claude.md` §7 (I-1 through I-12 plus
   multi-agent). The new `meetings/manager.py` and the four prompt
   templates expand the LLM call surface; firewall and engine-purity
   invariants must be re-verified.
8. Specific Questions for the Sub-Phase C Layer — answer each
   question in §7 below.
9. Test Quality and Coverage Gaps — scrutinize the new tests in
   `tests/meetings/test_manager.py`, `test_transcript.py`, and the
   four prompt-template test files for false-positive risk. Each
   prompt template's tests must actually exercise role-appropriate
   behavior (a crewmate-report test that just checks "the prompt
   returns *any* string" is a false positive).
10. Defects and Risks (ordered by severity) — `[Severity] short title`
    then Status / Evidence / Why it matters / Recommended action.
    Severity buckets: **Critical**, **High**, **Medium**, **Low**,
    **Concern**.
11. Document Conflicts — `DESIGN.md`, `AGENTS.md`,
    `AGENT_IMPLEMENTATION.md`, `tasks/phase-*.md`, and code. Note
    new conflicts only.
12. Readiness for Sub-Phase C — direct answer with citations. See
    §7 below.

## 5. Severity grading rubric

- **Critical** — A documented invariant is violated by code currently
  on `main`, OR observation packets leak hidden information, OR
  determinism is broken across two runs of the same seed, OR a Phase
  2 Merge Criterion fails on a real harness invocation, OR an
  Anthropic-specific concept leaks through the `LLMClient` Protocol
  surface, OR Task 3.8's C-3 canonical-order contract is violated
  by code on `main` (statements not actually in canonical order, OR
  the regression test does not fail against a violating implementation).
- **High** — A DoD bullet for an in-window task is unmet, OR an
  architectural invariant is no longer pinned by a test (the code
  may still happen to satisfy it), OR a prompt template produces
  schema-invalid output under the fake provider, OR the meeting
  state machine has a deadline path that emits malformed
  `MeetingResult` shapes.
- **Medium** — Scope discipline violation (a PR touched files
  outside its contract's `Files in scope`, beyond what `## Decisions`
  documented), OR a documented behaviour is contradicted by another
  document, OR a regression test required by a DoD is missing but
  the underlying behaviour is correct.
- **Low** — Brittleness, latent failure modes that are currently
  unreachable, or coupling that is not enforced by a test.
- **Concern** — Worth flagging for sub-phase C but not a defect in
  current code.

If unsure between two buckets, choose the more conservative
(higher-severity) reading and say why in the finding body.

## 6. Deep-focus areas (do not skip)

These are the highest-blast-radius spots in the five in-window PRs.
Produce a verdict for each with citations, even if the verdict is
"Pass".

### 6.1 C-3 resolution completeness (Task 3.8)

Task 3.8 resolved C-3 (from the post-3.3 audit) by picking option
(a) — producer-guaranteed canonical order. Verify:

- `meetings/transcript.py` exposes `canonically_ordered()` and
  `is_canonically_ordered()` helpers documenting the
  `(round_index, insertion_order)` contract.
- `meetings/manager.py` produces transcripts where
  `statements` is already in canonical order — no consumer-side
  re-sort needed. Read the relevant section of `run()` and confirm
  the construction is `tuple(stmt for r in rounds for stmt in r.statements)`
  or equivalent ordered concatenation.
- `tests/meetings/test_manager.py` (or `test_transcript.py`) has at
  least one regression that drives the state machine through ≥ 2
  rounds with multiple participants and asserts the resulting
  transcript is canonically ordered. The test must fail against an
  implementation that shuffles statements within a round (e.g. by
  applying `random.shuffle(round_statements)` before concatenation).
- The C-3 directive's prose contract (the docstring on
  `MeetingManager.run` or equivalent) is present and matches the
  task contract's option-(a) wording: *"Consumers may read
  `transcript.statements` in tuple order and trust that statements
  are sorted by `(round_index, insertion_order)` without re-sorting."*

If the canonical-order contract is documented but not actually
produced by `MeetingManager`, that is **Critical** (the C-3 directive
is unmet). If the contract is produced but no regression pin exists
that would fail on a violation, that is **High**.

### 6.2 Prompt template determinism + schema-validity (Tasks 3.4–3.7)

Each of the four prompt templates must:
- Produce output that passes `meetings/schemas.py` Pydantic
  validation when called with the fake deterministic provider.
- Be deterministic given the fake provider (same prompt inputs → same
  prompt template output → same parsed schema response).
- Not bypass the `LLMClient` Protocol (e.g. by importing
  `AnthropicClient` directly or hardcoding model names).

Read each prompt template (`agents/strategic/prompts/` or wherever
they live) and the corresponding tests. For each:

- **Task 3.4 — Crewmate report prompt:** produces a
  `ReportDocument` with role-appropriate content (truthful claims
  about observations from the crewmate's actual memory; no
  fabricated kills witnessed).
- **Task 3.5 — Impostor report prompt:** produces a
  `ReportDocument` that may include fabricated claims (the impostor's
  job), but the *schema* shape is identical to the crewmate's. The
  fabrication discipline (e.g. no claim referencing a tick the
  impostor has no episodic record of, per DESIGN.md §10.4) must be
  enforced by the prompt or by schema validation.
- **Task 3.6 — Accusation round prompt:** produces a `Statement` that
  references round context (round_index, prior statements) and
  conforms to the schema.
- **Task 3.7 — Vote ballot prompt:** produces a `VoteBallot` with a
  valid vote target (alive player id, or `SKIP`) and a justification.

If any template returns schema-invalid output under the fake
provider, that is **High** (sub-phase C consumers will fail on
parse).

### 6.3 Meeting state machine lifecycle and deadlines (Task 3.8)

Read `meetings/manager.py` `MeetingManager.run` (or equivalent
entry point). Verify the state machine traverses the §5.1/§5.2
phases in order:

1. Report intake — each alive agent submits a `ReportDocument`
   within the deadline; missed deadlines yield a default report.
2. Accusation rounds — agents submit `Statement`s in canonical
   order across rounds; default no-statement on deadline.
3. Voting — each agent submits a `VoteBallot`; default no-vote on
   deadline.
4. Resolution — tally the votes, produce a `MeetingResult`.

Verify:

- The manager does NOT mutate engine state. It consumes
  `WorldState` (or a subset thereof) read-only and returns a
  `MeetingResult` for the orchestrator (3.12) to apply.
- Missed-deadline behavior is tested (at least one test per phase
  exercises a participant that fails to respond before the
  deadline).
- The state machine is deterministic given the fake provider — two
  runs of the same meeting setup produce byte-identical
  `MeetingResult` and identical transcripts.

If the manager mutates engine state, that is **Critical** (the
firewall is violated).

### 6.4 LLM call surface and budget under a full meeting

A full meeting makes ~N agents × (1 report + R rounds + 1 vote)
LLM calls. With N=5 and R=2, that's ~20 calls per meeting. The
$0.30/game budget assumes ~1 meeting/game; with the per-call cost
the budget might be tight. Verify:

- The budget tracks cumulative cost across all calls within a
  meeting. The state machine does not bypass the budget for any
  call.
- A budget-exceeded mid-meeting raises the typed
  `BudgetExceededError` from Task 3.1, NOT silent truncation.
- Tests cover at least one meeting that approaches the budget
  ceiling.
- The fake provider's cost-per-call is set realistically (matches
  the Anthropic Sonnet 4.6 / Haiku 4.5 pricing roughly enough that
  CI cost-tracking tests are not pinned to fantasy values).

If a meeting silently bypasses the budget on overrun, that is **High**.

### 6.5 Engine isolation and dependency direction

With `meetings/manager.py` added, reconfirm:

- `lint-imports` still kept the agent→engine firewall.
- No `engine.*` import has slipped into `agents/`, `llm/`, or
  `meetings/`. Run `grep -rn "from engine" agents/ llm/ meetings/`
  to confirm.
- No `agents.*` import has slipped into `engine/`.
- `meetings/` does not import from `engine/`. The state machine may
  read engine-shaped types only through `observation/` boundary
  schemas or shared `meetings/schemas.py` types.
- `agents/strategic/prompts/` (or wherever prompt templates live)
  does not import from `engine/` or use Anthropic-specific helpers.

### 6.6 Prior-audit follow-through

For each finding in `audit-2026-05-16-0611-claude.md` §10, state
whether the in-window work closed it:

- **L-1 (budget cap-slack pin):** Was the boundary test added during
  any 3.4–3.8 review iteration? If not, this is still open.
- **L-2 (`last_seen` confirmed-dead pin):** Same question. If not
  addressed, still open.
- **C-1 (R-10 scanner-reuse hedge for 3.9):** Still open by design
  (3.9 owns it). Note in the report; this is not a fresh finding.
- **C-2 (`render_for_prompt` budget overflow):** The sub-phase B
  reviewer (you, in your audit role) should now decide whether
  the prompt templates that landed in 3.4–3.7 hit the overflow path
  in practice. Read the actual prompt invocations in
  `tests/meetings/test_manager.py` and trace whether any test
  exercises beliefs + contradictions large enough to push
  `render_for_prompt` past its budget. If yes and the test passes,
  the budget contract is being violated silently — flag as **High**.
  If no, the concern remains forward-looking — note and defer to
  the pre-Phase-4 audit.
- **C-3 (statement ordering):** Resolved by Task 3.8 — verify per
  §6.1 above.

### 6.7 Phase 2 substrate still healthy

Sub-phase B added LLM call paths but should not have touched
Phase 2 engine code. Verify:

- 100-game tournament still meets the merge criterion (both
  decisive sides > 20%). The post-3.3 baseline was 62.37%/37.63%;
  this checkpoint should reproduce or be close.
- Six-seed sweep still all decisive, all under ~12 ticks.
- 200-tick same-seed byte identity still PASS.
- Leak scanner still PASS over a 100-game tournament audit log.

If any Phase 2 gate fails, that is **Critical** (something in sub-phase
B touched code it should not have).

### 6.8 Sub-phase C consumability of sub-phase B's outputs

Read `tasks/phase-3.md` Tasks 3.9, 3.10, 3.11, 3.12. For each,
identify what sub-phase B outputs that task will consume, and
verify the consumed shape exists and is implementable:

- **3.9 strategic reasoner** consumes `render_for_prompt` + the four
  prompt templates + the LLM client. Are these wired in a way that
  the reasoner can sequence them?
- **3.10 voting** consumes `VoteBallot` and `MeetingResult`. Are
  the tally semantics specified clearly enough?
- **3.11 contradiction detection** consumes `MeetingTranscript`
  (in canonical order) and the agent's belief state. Is the
  cross-round comparison surface implementable?
- **3.12 orchestrator integration** consumes `MeetingManager.run`
  and the new `MeetingResult` shape. Is the
  `MEETING_PHASE_REACHED` pause point in `orchestrator/game.py`
  positioned to call into the manager cleanly?

If any sub-phase C task's required input shape is missing or
mis-specified, that is a **Medium** finding (sub-phase C's
implementing agent would have to invent the missing piece, which
risks drift).

## 7. Specific questions for the sub-phase C layer

Answer each in §12 of your report with a one-paragraph verdict and
citations:

1. **Does `MeetingManager` expose enough surface for Task 3.12
   (orchestrator integration)?** The orchestrator currently pauses
   on `state.phase == "MEETING"` and emits `MEETING_PHASE_REACHED`.
   Task 3.12 replaces that branch with a `MeetingManager` dispatch.
   Read `orchestrator/game.py:162-167` (the meeting interpose
   branch) and `meetings/manager.py`. Is the substitution clean?
2. **Does `MeetingResult` carry enough metadata for Task 3.10
   (voting)?** Task 3.10's DoD requires per-agent vote tallies +
   resolution (who was ejected, or no-eject). Is the
   `MeetingResult` shape sufficient?
3. **Can Task 3.11 (contradiction detection) consume the
   transcript without inventing structure?** The canonical-order
   contract from C-3 makes cross-round comparison cleaner. Verify
   that `MeetingTranscript.statements` carries enough fields
   (round_index, claim references, agent ids) for contradiction
   detection to work over fixed-shape Pydantic types.
4. **Can Task 3.9 (strategic reasoner) wire `render_for_prompt` +
   prompts + LLM client without re-implementing any plumbing?**
   The reasoner is the integration point for sub-phase B's
   outputs; if it requires adapter code that should have been in
   3.4–3.8, flag the gap.
5. **Are there Anthropic-specific assumptions in
   `meetings/manager.py` or `agents/strategic/prompts/`?** Run the
   grep above; for each hit, decide whether it's a real coupling
   or documentation-only.
6. **Did the Phase 2 substrate hold?** Tournament balance, byte
   identity, leak scan — re-verify.
7. **New Critical/High findings introduced by this audit window?**
   List any. If yes, they must be addressed before sub-phase C
   begins; if no, sub-phase C may proceed.

## 8. Output

Write your report to:

`audits/audit-YYYY-MM-DD-HHMM-<tool>.md`

where `<tool>` is `codex` or `claude` (whichever you are). Use the
current local date and time. Include `<tool>` in the filename so
two independent reports (if run in parallel) do not collide.

If only one tool is running this audit, the filename suffix is
still required — reconciliation tooling auto-discovers the two
newest unreconciled audit files. A single-tool run still produces
a canonical audit when no reconciliation is needed; the reviewer
reads the single report directly.

Do not commit. Do not open a PR. Do not modify any other file. When
finished, print the absolute path of the report and a one-paragraph
summary naming: the verdict, the count of Critical / High / Medium
findings, and the single most important thing to fix before
sub-phase C begins.

---

## Anti-patterns (do not do these)

- Do not paraphrase the post-3.3 audit's findings as if you
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
- Do not write more than ~500 lines. The audit window is five
  tasks; that bounds the report length.
- Do not re-litigate Task 3.8's C-3 choice (producer-guaranteed
  canonical order). The decision is final and documented at
  `meetings/transcript.py` and `meetings/manager.py`. Audit the
  implementation of the choice, not the choice itself.
- Do not audit Task 3.9–3.12 work that does not exist yet. If a
  question depends on code that hasn't been written, frame it as a
  sub-phase C readiness question (§7), not a finding.
