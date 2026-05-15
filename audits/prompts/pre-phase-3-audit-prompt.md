# Pre-Phase-3 Checkpoint Audit — Prompt

You are auditing the AiLibi repository at its current `HEAD` of `main`. You
will produce **one audit report** in `audits/` following the format,
rigor, and section structure of the most recent prior audit
(`audits/audit-2026-05-10-0721.md`). That file is the canonical template;
do not invent a new shape.

You are running independently from another auditor (a different LLM tool)
who is producing their own report from the same prompt. **Do not read
any other file under `audits/` newer than `audit-2026-05-10-0721.md`,
and do not read any file under `audits/prompts/` except this one.** The
two reports will be reconciled in a later step; their value depends on
being produced blind to each other.

---

## 1. Identity and constraints

- **Role:** read-only auditor. You may read any file, run any
  non-mutating shell command, and execute the full test/lint/type
  suite. You may not edit source files, tests, fixtures, configuration,
  task documents, agent prompts, or any file outside `audits/`. The
  only file you write is your audit report.
- **No fixes.** If you see a defect, record it as a finding. Do not
  patch it, even one line. The repair work is owned by a separate
  task that will be authored from the reconciled audit.
- **No speculation.** Every finding must cite a `file:line` (or a
  reproducible shell command and its observed output). A finding
  without a citation is not a finding.
- **No drive-by suggestions.** If a recommendation does not address a
  cited defect or unverified invariant, omit it. The audit is a
  defect register, not a wishlist.

## 2. Scope

**Audit window:** commits `014cca5` (HEAD at prior audit) → current
`HEAD` of `main`. Use
`git log 014cca5..HEAD --oneline --name-status` to enumerate every
commit and changed file in the window.

**Tasks landed in the window** (verify each against
`tasks/phase-2.md`):

- Task 2.7.5 — Post-2.7 audit repair (commit `d2db84d`)
- Task 2.8 — Headless game orchestrator (commit `aed06d0`)
- Task 2.8.5 — Critical leak repair and tactical termination
  (commit `e3b2a60`)
- Task 2.9 — Headless tournament harness (commit `ce44eaa`)

**Phase-3 readiness check (out-of-window but in-scope for this audit):**
Phase 3 has not begun coding. `llm/` and `meetings/` contain only
`__init__.py`. Audit the *preconditions* for Phase 3 starting safely
(see §7 below). Do not audit Phase 3 task contracts themselves for
content quality — those have not been exercised yet.

**Explicitly out of scope:** Phase 0 and Phase 1 code that was already
verified in the prior audit and has not changed in the window. Use
`git diff 014cca5..HEAD -- <path>` to confirm "no diff" before
marking anything as "Still Pass (no diff)" in your Regression
Baseline section.

## 3. Required evidence

Run all of the following from the repo root. Record exit codes and the
last line of output for each in §3 of your report ("Commands Run and
Evidence Sources"):

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run mypy --strict agents observation orchestrator engine`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `uv run pytest tests/orchestrator -v`
- `uv run pytest tests/eval -v`
- `uv run pytest tests/agents -v`
- `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/generate_prompts.py --check`

Then run the orchestrator and tournament harnesses to verify they
produce non-trivial outcomes, not just clean exits:

- `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/audit-r-$seed.jsonl --max-ticks 1000; done`
  — record the outcome of each seed. At least one must be
  `CREWMATES` or `IMPOSTORS`. If all six are `TICK_BUDGET_REACHED`,
  that is a **Critical** finding against Task 2.8.5's DoD.
- `uv run python scripts/run_tournament.py` (or the smallest invocation
  that exercises `eval.balance_eval.run_balance_eval` across a
  multi-seed range — read `scripts/run_tournament.py` to find the
  right flags). Record the `BalanceReport` and check Phase 2 Merge
  Criteria: both decisive sides > 20% of decisive games,
  `TICK_BUDGET_REACHED` reported as its own bucket, leak test passes
  across all games.

Run additional commands as needed to verify specific findings. Every
shell command you run should appear in §3 with its output evidence.

## 4. Required report structure

Your report MUST contain these sections, in this order, with these
exact headings (mirroring `audit-2026-05-10-0721.md`):

1. Executive Summary (≤ 8 sentences; lead with the verdict)
2. Verdict — one of: **Ready for Phase 3**, **Ready with fixes**,
   **Not ready**. Quantify what "fixes" means if applicable.
3. Commands Run and Evidence Sources (the §3 list above, plus any
   you added)
4. Regression Baseline — table comparing every prior-audit Pass
   finding to current state. For each row: "no diff" ⇒ Still Pass,
   "diff exists" ⇒ re-verified with citation. Use the table format
   from `audit-2026-05-10-0721.md` §4.
5. Prior Audit Follow-Through — for each finding in
   `audit-2026-05-10-0721.md` §11 (M-1, L-1 through L-5), state
   whether 2.7.5 (or any subsequent task) actually resolved it.
   Cite the resolving commit, the resolving diff, and the test (if
   any) that pins the fix. A finding marked resolved without a
   pinning test is a fresh Concern.
6. Task-by-Task DoD Audit — one subsection per in-window task
   (2.7.5, 2.8, 2.8.5, 2.9). For each: enumerate every DoD bullet
   from `tasks/phase-2.md`, mark Pass / Fail / Partial, cite
   evidence. Pay special attention to file-scope discipline (the
   diff must not touch files outside the contract's `Files in
   scope`).
7. Architectural Invariant Audit — re-run every invariant from
   `audit-2026-05-10-0721.md` §8 (I-1 through I-12 plus the
   multi-agent block). The orchestrator now exists, so the
   "multi-agent / agent-driven scenarios" item that was Concern
   (deferred) last time must be re-evaluated as Pass or Fail with
   evidence from the running orchestrator. The replay-determinism
   invariant (I-3) must be exercised through `HeadlessGame`, not
   just hand-authored fixtures.
8. Specific Questions for the Orchestrator + Tournament Layer —
   answer each question in §7 below.
9. Test Quality and Coverage Gaps — call out missing regression
   pins, fixtures that test happy paths only, and any new code
   added in the window whose only test is its own author's
   round-trip.
10. Defects and Risks (ordered by severity) — one numbered finding
    per defect. Use the format `[Severity] short title`, then
    Status / Evidence / Why it matters / Recommended action. Use
    these severity buckets: **Critical**, **High**, **Medium**,
    **Low**, **Concern**. A Critical or High finding must block the
    Verdict from being "Ready for Phase 3".
11. Document Conflicts — disagreements between `DESIGN.md`,
    `AGENTS.md`, `AGENT_IMPLEMENTATION.md`, `tasks/phase-*.md`, and
    code. The prompt validator already pins task-doc / prompt
    agreement; you are looking for design-doc / code drift.
12. Readiness for Phase 3 — direct answer, in plain English, with
    citations. See §7 below.

## 5. Severity grading rubric

Apply consistently:

- **Critical** — A documented invariant is violated by code currently
  on `main`, OR observation packets leak hidden information, OR
  determinism is broken across two runs of the same seed, OR a Phase
  2 Merge Criterion fails on a real harness invocation.
- **High** — A DoD bullet for an in-window task is unmet, OR an
  architectural invariant is no longer pinned by a test (the code
  may still happen to satisfy it).
- **Medium** — Scope discipline violation (a PR touched files
  outside its contract's `Files in scope`), OR a documented
  behaviour is contradicted by another document, OR a regression
  test required by a DoD is missing but the underlying behaviour is
  correct.
- **Low** — Brittleness, latent failure modes that are currently
  unreachable, or coupling that is not enforced by a test.
- **Concern** — Worth flagging for the next phase but not a defect
  in current code.

If you are unsure between two buckets, choose the more conservative
(higher-severity) reading and say why in the finding body.

## 6. Deep-focus areas (do not skip)

These are areas where the prior audits found issues, where the recent
work has the largest blast radius, or where Phase-3 risk is highest.
You must produce a verdict for each, with citations, even if the
verdict is "Pass".

### 6.1 Information leakage — observation firewall

Task 2.8.5 added a value-scanning pass to `eval/leak_test.py` after
both prior audits missed that `visible_players[].id` literally named
the impostor on tick 0. Verify the value scanner exists, runs against
all scripted fixtures, and *actually fails on a planted role-bearing
value* (run the scanner self-test). Then independently confirm
across all three scripted fixtures and a fresh orchestrator-driven
run (seed 42, 200 ticks) that no observation packet contains the
substrings `impostor`, `crewmate`, or `crew` outside the
`self_state.role` allow-list. Use `jq` or a short Python one-liner to
walk the replay JSONL.

### 6.2 Role-neutral id rename — completeness

`git grep -nE "['\"](player|impostor)-[0-9]+['\"]"` over the entire
working tree must return zero hits in non-audit, non-prompt files.
Audit reports under `audits/` may legitimately reference the old
ids when describing history. Audit prompts (this file included) may
also reference them. If the grep returns hits anywhere in `agents/`,
`engine/`, `observation/`, `orchestrator/`, `eval/`, `scripts/`,
`tests/`, or `tests/fixtures/`, that is a **Critical** regression.

### 6.3 Crewmate task-completion fix

Task 2.8.5's DoD requires that across seeds {0, 1, 2, 7, 42, 100},
at least one game reaches a decisive outcome (`CREWMATES` or
`IMPOSTORS`) rather than `TICK_BUDGET_REACHED`. Re-run the seed
sweep yourself; do not trust the PR description. Also locate and
read the regression test in `tests/agents/test_crewmate_policy.py`
that pins a full task-completion cycle through `CrewmatePolicy.decide`.
Confirm the test exists, asserts on `DoTaskIntent` issuance, and
would fail against the pre-2.8.5 code (you cannot run the pre-2.8.5
code here, but you can verify the test's structure makes it a real
regression pin, not a tautology).

### 6.4 Determinism through the orchestrator

The prior audit flagged L-1: "No agent-driven replay-determinism
test". That deferred work belonged to Task 2.8. Verify a test exists
that runs `HeadlessGame` twice with the same seed and compares
per-tick state hashes (or full state snapshots) byte-for-byte.
Locate the test, read it, run it. If no such test exists, that is a
**High** finding against Task 2.8's DoD. If the test exists but
operates only on hand-authored fixtures (not through `HeadlessGame`),
that is also **High**.

### 6.5 Tournament harness — outcome accounting

Task 2.9's DoD requires `TICK_BUDGET_REACHED` to be a first-class
outcome bucket alongside `CREWMATES` and `IMPOSTORS`. Read
`eval/balance_eval.py::BalanceReport` and confirm the bucket exists
as a named field, is incremented in the aggregation loop, and is
surfaced in any human-readable report rendering. Then verify Phase 2
Merge Criteria: "Both decisive sides win > 20% of decisive games".
Run a real tournament (10+ seeds is enough for this audit; full
100 is preferable if the run completes in under five minutes) and
record the actual percentages.

### 6.6 Engine isolation under the orchestrator

The orchestrator (`orchestrator/game.py`) is now the single owner of
engine imports. Verify with `lint-imports` plus an AST scan that
**no** module under `agents/` imports from `engine/`, directly or
transitively. The previous audit confirmed this for the static
agent layer; you must reconfirm it now that `orchestrator/` mediates
the live loop. Also verify that `agents/` does not import from
`orchestrator/`.

### 6.7 Scope discipline across the four in-window PRs

For each merged PR in the window, run
`git show <merge-commit> --stat` and compare the touched files to
the corresponding task's `Files in scope` and `Files NOT in scope`
lists in `tasks/phase-2.md`. Task 2.8.5 has an unusually large file
list (the id rename cascade); that is contracted, not drift. Any
diff to a file in `Files NOT in scope` is **Medium** at minimum.

## 7. Specific questions for the Phase-3 readiness section

Answer each in §12 of your report with a one-paragraph verdict and
citations:

1. Is the determinism boundary clean enough that introducing LLM
   nondeterminism in Phase 3 will be debuggable? Specifically: when
   a Phase 3 meeting produces a divergent outcome between two runs
   of the same seed, will the orchestrator's existing replay format
   (`orchestrator/replay.py`) record enough state to isolate the
   nondeterminism to the LLM call rather than masking it as a
   pathing or perception bug?
2. Does `agents/memory/` expose the shape that Phase 3.3 (memory
   rendering) needs? Read `tasks/phase-3.md` Task 3.3's DoD and
   compare it to what `agents/memory/episodic.py`,
   `agents/memory/working.py`, and `agents/memory/beliefs.py`
   currently expose. Flag any shape gap as a **High** Phase-3
   blocker.
3. Does the orchestrator expose a clean seam for Phase 3.8 (meeting
   state machine) to interpose? `tasks/phase-2.md` Task 2.8 says
   the loop pauses on `phase == "MEETING"` and emits
   `MEETING_PHASE_REACHED`. Verify by reading `orchestrator/game.py`
   that the pause point is a single, well-named call site that
   Phase 3.12 can replace without surgery on the surrounding loop.
4. Is the leak test now strong enough to catch a Phase-3-introduced
   leak (e.g. an LLM prompt that accidentally embeds a hidden field
   from working memory in the rendered context)? §6.1 covers
   value-scanning of packets; this question is about whether the
   same scanning extends to anything the LLM layer will consume.
5. Are there any uncommitted hardening tasks (from §10 of this
   audit) that Phase 3 work would compound rather than expose? If
   yes, list them as Phase-3 prerequisites in §12.

## 8. Output

Write your report to:

`audits/audit-YYYY-MM-DD-HHMM-<tool>.md`

where `<tool>` is `codex` or `claude` (whichever you are). Use the
current local date and time. Include `<tool>` in the filename so the
two independent reports do not collide.

Do not commit. Do not open a PR. Do not modify any other file. When
finished, print the absolute path of the report and a one-paragraph
summary that names: the verdict, the count of Critical / High /
Medium findings, and the single most important thing to fix before
Phase 3 begins.

---

## Anti-patterns (do not do these)

- Do not paraphrase the prior audit's findings as if you re-verified
  them. Either re-run the check and cite the new evidence, or omit
  the finding.
- Do not produce a "looks good" section. Either a thing is verified
  with evidence, or it is a Concern.
- Do not include code suggestions, refactor proposals, or
  architectural improvements that are not tied to a cited defect.
- Do not soften severities to be polite. A Critical finding stays
  Critical even if the responsible PR is recent.
- Do not skip the regression baseline. The point of a baseline is
  that you only re-audit what changed; skipping it forces the
  reconciler to redo your work.
- Do not write more than the prior audit. ~700 lines is the upper
  bound for a checkpoint audit at this scope; if you are over, you
  are repeating yourself or auditing out-of-scope code.
