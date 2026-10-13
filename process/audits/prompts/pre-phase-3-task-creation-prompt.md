# Pre-Phase-3 Task Creation — Prompt

You are turning the reconciled pre-Phase-3 audit into actionable task
contracts. The reconciliation is done; the disagreements are settled;
your job is to author the **task entries** that the project will use
to drive repair work before Phase 3 begins.

You will read exactly one audit:
`audits/audit-2026-05-15-0225-reconciled.md`. Do not read the source
Codex or Claude audits, and do not read any file under
`audits/prompts/` except this one. They would only re-introduce
ambiguity the reconciliation already resolved.

---

## 1. Identity and constraints

- **Role:** task author. You write task entries in `tasks/phase-2.md`
  (and addenda to existing entries in `tasks/phase-3.md`), then
  regenerate `agent_prompts/task-*.md` via the existing tooling. You
  do NOT touch source code, tests, fixtures, or configuration. The
  agent that picks up each of your new tasks is the one that fixes
  the code.
- **No fixes.** If you find yourself editing anything under
  `agents/`, `engine/`, `observation/`, `orchestrator/`, `eval/`,
  `scripts/` (except `generate_prompts.py` invocation), or `tests/`,
  stop. That is the next agent's job.
- **No new findings.** Authority for what is in scope comes from the
  reconciled audit. If you see something while reading the code that
  the audit missed, note it in your output summary — do not graft it
  into a task contract.
- **No commits, no PRs.** Leave the working tree dirty; the user
  will review and stage.

## 2. Required inputs

Read in this order:

1. `audits/audit-2026-05-15-0225-reconciled.md` — the authority for
   what work exists. Read §10 (Defects and Risks R-1 through R-14),
   §12 (Readiness for Phase 3, especially the recommended repair
   order), and §13 (Reconciliation table).
2. `tasks/phase-2.md` — the file you will edit. Read tasks **2.7.5**
   and **2.8.5** in full; they are the format template for
   post-audit repair tasks. Your new entries must structurally mirror
   them.
3. `tasks/phase-3.md` — read Tasks **3.3**, **3.9**, and **3.12**
   in full. You will add acceptance-gate addenda to these.
4. `scripts/_task_parser.py` and `scripts/validate_task_docs.py` —
   the schema authority. Every required field
   (`Branch`, `Depends on`, `Section refs`, `Complexity`,
   `Files in scope`, `Files NOT in scope`, `Definition of done`,
   `Implementation hint`, `Public types introduced`,
   `Integration risk`, `Ready-to-paste prompt`) must be present and
   syntactically valid, or the validator will fail.
5. `scripts/prompt_template.md.j2` — for context only; the prompt
   files are generated, not hand-written.
6. `AGENTS.md` — for the "Definition of done (always)" line items
   and the PR description shape that every task DoD inherits.

## 3. Grouping (mandatory baseline; deviations require justification)

The reconciled audit has 14 active findings. Bundle them into **three
new Phase 2 tasks** plus **three Phase 3 task addenda**, as follows.
This grouping is the baseline. You may deviate, but if you do, write
a one-paragraph justification at the top of your final summary
explaining why your grouping serves the repair work better than the
baseline.

### Task 2.10 — Pre-Phase-3 tactical repair (Critical/High)

**Bundles:** R-5 (decide dead-crewmate task rule) → R-3 (fix impostor
stale-target loop) → R-2 (rerun six-seed sweep) → R-1 (rerun
100-game tournament). This is one PR because the four findings form
a causal chain: R-5 is a prerequisite **design decision** that
unblocks R-3, R-3's fix is what enables R-2/R-1 to pass.

**Critical authoring note:** R-5 is graded Concern in the audit but
is described as the structural reason crew can never win after an
early kill. Treat the R-5 decision as the **first DoD bullet** of
Task 2.10 — a written rule choice (one of: dead-owner tasks dropped /
reassigned / ghost-completable / intentionally still required), with
the chosen rule documented in `DESIGN.md` §1.3 or §4 and referenced
from `engine/win_conditions.py`. Code changes for R-3 follow from
that decision. Do NOT bundle a speculative code fix that pre-empts
the decision.

This task is **Integration** complexity (per
`_task_parser.COMPLEXITY_VALUES`) because it touches the engine
rule layer, an agent tactical policy, and the headless harness
acceptance gates simultaneously.

### Task 2.11 — Contract hygiene and test-guard cleanup (Medium)

**Bundles:** R-4 (clean old-id grep guard without weakening negative
tests), R-7 (repair Task 2.8.5 file-scope drift retroactively), R-8
(align Task 2.9 DoD with merge criterion wording), R-14 (rename
observation test helpers off role-bearing ids).

All four are documentation, test-fixture, or task-contract edits.
None changes runtime behaviour. Bundling them is safe because the
diffs do not overlap: R-4 touches `eval/leak_test.py` and
`tests/eval/test_balance_eval.py` planted strings; R-7 and R-8 touch
`tasks/phase-2.md` and regenerated prompts; R-14 touches
`tests/observation/test_service.py` helper ids. Complexity: **Small**
or **Medium** (you decide based on the actual touched-file count).

### Task 2.12 — Behavioral merge-criteria CI gates and remaining test hygiene (Medium)

**Bundles:** R-11 (add automated CI gate for the decisive-outcome
sweep and/or a small balanced-tournament check), R-13 (audit-log
append-mode regression test), R-12 (broaden property-test action
vocabulary beyond `move`/`wait`).

These are test-only additions; none touches production code. R-11 is
the most load-bearing — it is what prevents R-1/R-2 from silently
regressing after 2.10 lands. Complexity: **Medium**.

**Depends on:** 2.10 merged (the CI gate must encode a passing
outcome, not the current failing one).

### Phase 3 task addenda (NOT new Phase 2 tasks)

R-6, R-9, and R-10 are Phase-3 prerequisites whose work already
belongs to existing Phase 3 tasks. Do not create new Phase 2 tasks
for them. Instead, add explicit acceptance-gate bullets to the
existing tasks:

- **R-6 → Task 3.3:** Add a DoD bullet that `agents/memory/store.py`
  must expose a composite memory surface that includes episodic,
  working, and belief state, and that `render_for_prompt` must
  produce a structured view drawing from all three.
- **R-9 → Task 3.12:** Add a DoD bullet that `ReplayEntry` (or its
  Phase 3 successor) must record meeting transcripts, prompt
  versions, LLM outputs, and cost metadata, and that the
  determinism test must run at least one long-horizon replay
  (≥ 200 ticks or one full meeting cycle) byte-for-byte.
- **R-10 → Tasks 3.3 and 3.9:** Add a DoD bullet to each that the
  packet field/value leak scanners from `eval/leak_test.py` must be
  reused against `render_for_prompt` golden outputs (3.3) and
  strategic prompt inputs (3.9), with at least one planted negative
  test pinning that the scanner trips on a forbidden string in the
  rendered surface.

These addenda are small edits inside the existing task entries.
They do not change the task IDs and do not require new branches.

## 4. Task contract requirements (per task)

Each new Phase 2 task entry in `tasks/phase-2.md` must contain, in
order:

1. `### Task 2.N — <title>` heading (where N is 10, 11, 12).
2. `**Branch:**` — kebab-case branch name matching the prior
   `phase-2-*` pattern.
3. `**Depends on:**` — explicit list of merged tasks required
   before this one starts.
4. `**Section refs:**` — relevant `DESIGN.md` and `AGENTS.md`
   sections.
5. `**Complexity:**` — one of `Trivial`, `Small`, `Medium`,
   `Integration` (the validator enforces this).
6. Prose summary (3–6 sentences) explaining what the task does and
   why, including which audit findings it closes (cite by R-id).
7. `**Files in scope:**` — exhaustive bullet list of every file the
   PR is allowed to touch. Be conservative: list each file
   individually, not by directory glob. The agent that picks up
   this task is expected to touch exactly these files.
8. `**Files NOT in scope:**` — explicit list of files or
   directories the task must not touch, mirroring the 2.8.5
   pattern. This list is what prevents scope drift like R-7.
9. `**Definition of done:**` — Markdown checklist. Every audit
   finding closed by this task must have its own DoD bullet that
   cites the finding by R-id and names the verification command or
   test that proves closure. End the list with the standard gate
   bullets: `uv run python scripts/generate_prompts.py --check`,
   `uv run python scripts/validate_task_docs.py`, `uv run pytest`,
   `uv run mypy .`, `uv run ruff check .` /
   `uv run ruff format --check .`, `uv run lint-imports`,
   `bash scripts/check.sh`.
10. `**Implementation hint:**` — concrete code snippets, command
    invocations, or pseudocode for the non-obvious parts. For
    Task 2.10 specifically: write the snippet showing how the dead-
    target / staleness filter integrates into
    `_scored_targets`, and the seed-sweep / tournament rerun command
    line. Do not write the actual rule choice — that is the
    implementing agent's decision per the R-5 DoD bullet.
11. `**Public types introduced:**` — typed list of any new
    importable symbols. If none, write `None.` (the validator
    accepts this).
12. `**Integration risk:**` — the same shape as 2.8.5's integration
    risk block. Call out what could break in adjacent code,
    explicit determinism / leak considerations, and which existing
    tests must continue to pass.
13. `**Ready-to-paste prompt:**` `` `agent_prompts/task-2-N-<slug>.md` ``
    — this file does not exist yet; the generator creates it.

## 5. Cross-reference and consistency rules

- Every audit finding R-1 through R-14 must be addressed by either a
  Phase 2 task DoD bullet or a Phase 3 task addendum. Findings that
  are not addressed must be explicitly listed in your final summary
  with justification.
- The recommended repair order from the reconciled audit's §12 is:
  "fix R-3, decide R-5, rerun R-2/R-1, then clean R-4/R-7/R-8".
  Encode this in `Depends on`: Task 2.11 depends on 2.10 (so the
  test guards in 2.11 do not block 2.10's tactical work); Task 2.12
  depends on 2.10 (so the CI gate encodes the passing outcome).
- Each new task's `Files in scope` must be a strict subset of files
  that the audit's cited evidence actually points to. If a finding's
  citation names `eval/leak_test.py:228`, that file goes in scope;
  if a finding does not cite a file under `tests/`, that test file
  does not appear in scope.
- The Phase 2 Merge Criteria block (the trailing section of
  `tasks/phase-2.md`) must not move. If you need to amend its
  wording per R-8, leave it where it is and adjust in place.

## 6. Output and verification

After authoring the task entries:

1. Regenerate prompts:
   `uv run python scripts/generate_prompts.py`
   This creates new files under `agent_prompts/` matching each
   `Ready-to-paste prompt:` reference.
2. Validate:
   `uv run python scripts/validate_task_docs.py`
   `uv run python scripts/generate_prompts.py --check`
   Both must pass. If either fails, fix the task entries (not the
   tooling).
3. Run `bash scripts/check.sh` to confirm the rest of the repo is
   still green (you have not touched code, so this should pass; if
   it does not, your edits crossed a line they should not have).

When finished, print:

- The list of new Phase 2 tasks created (IDs and titles).
- The list of Phase 3 tasks amended (IDs and the addendum
  summaries).
- A mapping of R-1 through R-14 to the task/addendum that closes
  each finding.
- Any findings you chose not to address, with justification.
- Whether your grouping deviated from §3's baseline, and if so,
  why.
- The exit status of the three validation commands above.

Do not commit. Do not open a PR.

---

## Anti-patterns (do not do these)

- Do not write a single mega-task containing every finding. The
  whole point of grouping is that the implementing agent can pick up
  2.10 without simultaneously owning the doc cleanup or the CI
  gates.
- Do not split findings across multiple tasks. One R-id closes in
  one place, not two.
- Do not fix any code, even one line. If a DoD bullet feels like it
  needs a code change to be writeable, the bullet is too detailed —
  describe the *outcome*, not the implementation.
- Do not promote R-5 to Critical or High in the task contract. The
  audit's grading stands. Treat R-5 as a prerequisite *decision*
  inside Task 2.10's DoD, not a re-graded finding.
- Do not add new findings disguised as DoD bullets. The audit is
  the authority.
- Do not skip the `Files NOT in scope` list. R-7 exists because
  Task 2.8.5 had a permissive scope; the new tasks must not repeat
  that mistake.
- Do not create new Phase 2 tasks for R-6, R-9, or R-10. Those are
  Phase 3 addenda, not Phase 2 work.
