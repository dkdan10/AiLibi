# Pre-Phase-3 Checkpoint Audit — Prompt

You are auditing the AiLibi repository at its current `HEAD` of `main`. You
will produce **one audit report** in `audits/` following the format,
rigor, and section structure of the most recent prior audit
(`audits/audit-2026-05-15-0225-reconciled.md`). That file is the
canonical template; do not invent a new shape.

You are running independently from another auditor (a different LLM tool)
who is producing their own report from the same prompt. **Do not read
any other audit file under `audits/` newer than
`audit-2026-05-15-0225-reconciled.md`, and do not read any file under
`audits/prompts/` except this one.** The two reports will be reconciled
in a later step; their value depends on being produced blind to each
other.

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

**Audit window:** commits `0610b72` (HEAD at the prior reconciled
audit) → current `HEAD` of `main`. Use
`git log 0610b72..HEAD --oneline --name-status` to enumerate every
commit and changed file in the window.

**Tasks landed in the window** (verify each against `tasks/phase-2.md`):

- Task 2.10 — Pre-Phase-3 tactical repair (PR #30, commit `30725b0`,
  merged at `36177ea`)
- Task 2.10.5 — Phase 2 tournament balance (PR #31, commit `1ae5fe8`,
  merged at `d278829`)
- Task 2.11 — Contract hygiene and test-guard cleanup (PR #33,
  commit `9c27a30`, merged at `ed56e6f`)
- Task 2.12 — Behavioral merge-criteria CI gates and remaining test
  hygiene (PR #34, commit `d92da83`, merged at `5f15af9`)

Plus the small AGENTS.md edits adding the `## GitHub operations`
section (`f41de17`, `9b87e7f`) and any other in-window commits.

**Phase-3 readiness check (out-of-window but in-scope for this audit):**
Phase 3 has not begun coding. `llm/` and `meetings/` still contain
only `__init__.py`. The Phase-3 task addenda for R-6/R-9/R-10 should
be in `tasks/phase-3.md` Tasks 3.3, 3.9, 3.12 — verify they are
correctly wired (see §6.6 and §7 below).

**Explicitly out of scope:** Phase 0, Phase 1, and Phase 2 code that
was already verified in the May-15 reconciled audit and has not changed
in the window. Use `git diff 0610b72..HEAD -- <path>` to confirm "no
diff" before marking anything as "Still Pass (no diff)" in your
Regression Baseline section.

## 3. Required evidence

Run all of the following from the repo root. Record exit codes and the
last line of output for each in §3 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run mypy --strict agents observation orchestrator engine`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `uv run pytest tests/orchestrator -v`
- `uv run pytest tests/eval -v`
- `uv run pytest tests/agents -v`
- `uv run pytest tests/engine -v`
- `uv run pytest tests/observation -v`
- `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/generate_prompts.py --check`
- `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/`
  (must return empty post-2.11)
- `git grep -nE "['\"](player|impostor|victim|observer|crew-[0-9]+)['\"]" tests/observation/test_service.py`
  (must return empty post-2.11)

Then exercise the live harnesses to verify outcomes, not just clean
exits:

- Six-seed sweep:
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/audit-r-$seed.jsonl --max-ticks 1000; done`
  — record the outcome of each seed.
- 100-game tournament re-run:
  `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/audit-tournament --max-ticks 1000`
  — record the four-bucket counts and decisive split. Both
  `CREWMATES%` and `IMPOSTORS%` of decisive must exceed 20% per the
  Phase 2 Merge Criterion. PR #31 baseline: 73.12% / 26.88%.
- 100-game tournament leak scan (the scanner should still PASS over
  all packets across all 100 games).

Run additional commands as needed to verify specific findings. Every
command you run appears in §3 with its output evidence.

## 4. Required report structure

Your report MUST contain these sections, in this order, with these
exact headings (mirroring `audit-2026-05-15-0225-reconciled.md`):

1. Executive Summary (≤ 8 sentences; lead with the verdict).
2. Verdict — one of: **Ready for Phase 3**, **Ready with fixes**,
   **Not ready**. Quantify what "fixes" means if applicable.
3. Commands Run and Evidence Sources (the §3 list above, plus any
   you added).
4. Regression Baseline — table comparing every prior-audit Pass
   finding (from `audit-2026-05-15-0225-reconciled.md` §4) to current
   state. For each row: "no diff" ⇒ Still Pass, "diff exists" ⇒
   re-verified with citation.
5. Prior Audit Follow-Through — for each finding R-1 through R-14 in
   `audit-2026-05-15-0225-reconciled.md` §10, state whether the
   in-window work actually closed it. Cite the resolving commit, the
   resolving diff, and the test (if any) that pins the fix. A finding
   marked resolved without a pinning test is a fresh Concern.
6. Task-by-Task DoD Audit — one subsection per in-window task
   (2.10, 2.10.5, 2.11, 2.12). For each: enumerate every DoD bullet
   from `tasks/phase-2.md`, mark Pass / Fail / Partial, cite evidence.
   Pay special attention to file-scope discipline (the diff must not
   touch files outside the contract's `Files in scope`, except for
   the deviations explicitly documented in each PR's `## Decisions`).
7. Architectural Invariant Audit — re-run every invariant from
   `audit-2026-05-15-0225-reconciled.md` §7 (I-1 through I-12 plus
   the multi-agent block). The four implementation PRs added engine
   and agent surface area; the firewall and purity invariants must
   be re-verified, not assumed.
8. Specific Questions for the Post-2.12 Layer — answer each question
   in §7 below.
9. Test Quality and Coverage Gaps — call out missing regression
   pins, fixtures that test happy paths only, and any new code added
   in the window whose only test is its own author's round-trip.
   Specifically scrutinize the three CI tests added in PR #34
   (R-11, R-12, R-13) for false-positive risk and for whether they
   actually catch the regression they claim to.
10. Defects and Risks (ordered by severity) — one numbered finding
    per defect. Use the format `[Severity] short title`, then
    Status / Evidence / Why it matters / Recommended action. Use
    these severity buckets: **Critical**, **High**, **Medium**,
    **Low**, **Concern**. A Critical or High finding must block the
    Verdict from being "Ready for Phase 3".
11. Document Conflicts — disagreements between `DESIGN.md`,
    `AGENTS.md`, `AGENT_IMPLEMENTATION.md`, `tasks/phase-*.md`, and
    code. Note new conflicts only; the prior audit's resolved
    conflicts should not be re-listed unless they regressed.
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
  outside its contract's `Files in scope`, beyond what `## Decisions`
  documented), OR a documented behaviour is contradicted by another
  document, OR a regression test required by a DoD is missing but
  the underlying behaviour is correct.
- **Low** — Brittleness, latent failure modes that are currently
  unreachable, or coupling that is not enforced by a test.
- **Concern** — Worth flagging for the next phase but not a defect
  in current code.

If you are unsure between two buckets, choose the more conservative
(higher-severity) reading and say why in the finding body.

## 6. Deep-focus areas (do not skip)

These are the highest-blast-radius spots in the four in-window PRs.
Produce a verdict for each with citations, even if the verdict is "Pass".

### 6.1 The new agent→engine string coupling in `_BODY_ID_VICTIM_PATTERN`

PR #30 introduced `agents/tactical/impostor_policy.py::_BODY_ID_VICTIM_PATTERN`,
a regex that parses engine-generated body ids matching `^body-(.+)-\d+$`
to derive the impostor's `confirmed_dead` set. This is a **new
string-based coupling between engine code (`engine/rules.py` body-id
emission) and agent code**. Verify:

- The pattern's documentation references it as a Phase-2 inference
  to be retired in Phase 3 (a `BodyView.victim_id` field on the
  boundary type).
- The pattern is robust: tests cover malformed body ids, missing
  payload, and at least one engine-format change scenario.
- The coupling does not create a hidden read path from engine state
  to agent state (the body id is part of the public `BodyView`, but
  parsing it inside agent code is brittle — flag any non-test code
  that *relies* on the pattern matching).
- The pattern is consistent with `engine/rules.py`'s actual body-id
  format. Read the engine code to confirm.

### 6.2 The R-5 `_apply_kill` rewrite in `engine/tick.py`

PR #30 added two new behaviors to `_apply_kill`:

- Clears the victim's `last_action` to prevent `_advance_tasks`
  from raising on the next tick.
- Removes the killed player's incomplete tasks from `state.tasks`.

Verify:

- Engine purity preserved: the function is still a pure function
  of state + action + map. No agent imports, no randomness, no
  hidden state.
- Determinism preserved: replay byte content may change vs. pre-PR
  but two runs of the same seed at current `HEAD` are byte-identical.
- The "kill triggers crew win on the same tick" edge case
  (documented in `DESIGN.md` §3.5 as expected behavior) is
  reachable in code. Either pin it with a unit test or confirm
  the documentation is honest about the lack of pinning.
- The completed-but-dead-owner task accounting is correct:
  already-completed tasks owned by the dead crewmate must remain in
  `state.tasks` so they keep counting toward `crew_tasks_done`.

### 6.3 Canonical map retune (`kill_cooldown_ticks: 10 → 4`)

PR #31 changed the canonical map's kill cooldown. Verify:

- No surviving test asserts the literal `10` against the canonical
  map. Use `git grep -nE "kill_cooldown_ticks|cooldowns\[.*\] == 10"`
  across `tests/` to catch holdouts.
- `tests/engine/test_tick.py:110, 117` updates are correct (per the
  Task 2.11 retroactive historical note).
- The new balance regression test
  (`test_canonical_balance_keeps_both_sides_alive` in
  `tests/eval/test_balance_eval.py`) actually catches the regression
  it claims to: invert the canonical cooldown to 10, confirm the
  test fails; revert. Or read the test and reason about whether the
  10-game sample is large enough to reliably catch a 0/0 imbalance.

### 6.4 Phase 2 tuning lever documentation (DESIGN.md §3.5)

PR #31 added two paragraphs to DESIGN.md §3.5: the tuning-lever
subsection and the `dropped`-rule consequence note. Verify:

- The documented levers map to real code anchors (cooldown in
  `engine/maps/canonical_1.yaml`, sabotage `duration_ticks` in same
  YAML, `tasks_per_crewmate` in `orchestrator/seeder.py` — but
  `tasks_per_crewmate` is not actually parameterized in
  `orchestrator/seeder.py` because the cooldown-only fix made it
  unnecessary. If the docs claim a parameter that doesn't exist,
  that's a **Medium** doc-vs-code conflict).
- The search order documented in DESIGN is consistent with the
  contracted search order in Task 2.10.5.
- The dropped-rule consequence paragraph is accurate against the
  `_apply_kill` implementation.

### 6.5 The three new CI tests in PR #34 (R-11, R-12, R-13)

Read each new test and ask: would it actually catch the regression
it claims to catch?

- **R-11 (decisive-outcome guard)** — invert the canonical cooldown
  back to 10 mentally; would the test fail? Is the seed list small
  enough for CI but representative? The PR description claimed yes;
  re-verify by reading the test.
- **R-12 (property-test vocabulary)** — does the new strategy
  actually generate kill/vent/report tuples that the engine then
  processes? Or does it generate combinations that get filtered to
  move/wait anyway? Read the strategy implementation.
- **R-13 (audit-log append regression)** — would the test fail if
  `observation/audit.py:20-23` were mutated from `"a"` to `"w"`?
  Mentally trace the test logic; if the test only checks that "two
  packets are recorded" without verifying order or that the file
  was reopened (not re-created), it may not catch the regression
  it claims to.

If any of these three tests fails the "would it actually catch?"
check, flag as **High** — a false-positive CI gate is worse than no
gate at all.

### 6.6 Phase 3 task addenda are still wired and implementable

`tasks/phase-3.md` Tasks 3.3, 3.9, and 3.12 should contain R-6, R-10,
R-9, and another R-10 acceptance-gate bullets per the May-15 task
creation. Verify:

- Each addendum cites `audits/audit-2026-05-15-0225-reconciled.md`
  explicitly.
- Each addendum is implementable — concrete enough that the Phase 3
  implementing agent can act on it without further design work. If
  any addendum is vague ("memory store should be composite" without
  specifying the shape), flag as **Medium**.
- The addenda do not conflict with each other or with the rest of
  the Phase 3 task contracts.

### 6.7 Contract hygiene completeness (PR #33)

PR #33 closed R-4, R-7, R-8, R-14 plus the optional 2.10.5 historical
note. Verify each is complete:

- R-4: the old-id grep returns empty across `eval/` and `tests/`.
  The scanner self-tests still trip on the new sentinel
  (`crew_role_leak_fixture`).
- R-7: the historical note in Task 2.8.5 lists the six files
  enumerated in the contract.
- R-8: Task 2.9 DoD line matches the Phase 2 Merge Criterion text
  verbatim.
- R-14: helper ids in `tests/observation/test_service.py` are
  `p-N` form. PR #33 `## Decisions` flagged `"victim-body"` at
  `tests/observation/test_service.py:357` as a leftover; verify
  whether this is still acceptable or has now become a finding.

### 6.8 Engine isolation under the post-2.12 layer

With four PRs touching engine, agent, and test code, reconfirm:

- `lint-imports` still kept the contract (`bash scripts/check.sh`
  prints the KEPT line).
- No new `engine.*` import has slipped into `agents/`. Run an AST
  scan or `grep -rn "from engine" agents/` to confirm.
- No new `agents.*` import has slipped into `engine/`.

## 7. Specific questions for the post-2.12 layer

Answer each in §12 of your report with a one-paragraph verdict and
citations:

1. **Determinism for Phase 3 LLM debugging.** With R-5's
   `_apply_kill` rewrite landed and the cooldown retune in place, is
   the Phase 2 replay determinism still tight enough that introducing
   LLM nondeterminism in Phase 3 will be debuggable? Specifically:
   when a Phase 3 meeting produces a divergent state hash, will the
   orchestrator's replay format (`orchestrator/replay.py`) record
   enough state to isolate the nondeterminism to the LLM call?
2. **`agents/memory/` shape for Phase 3.3.** `agents/memory/store.py`
   is still absent. Read Task 3.3's R-6 acceptance gate. Is the
   composite-memory contract specified concretely enough that 3.3's
   implementing agent will not have to invent the boundary?
3. **Orchestrator meeting interpose point.** Read
   `orchestrator/game.py`. Is the meeting pause point still a single
   clean call site that Phase 3.12 can replace without surgery?
4. **Leak test extension.** The packet-level leak scanner is strong.
   The R-10 addenda say it should extend to rendered memory and
   strategic prompt inputs in Phase 3. Are those addenda specified
   tightly enough that Phase 3.3 and 3.9 implementations will inherit
   correct scanning behavior?
5. **Tuning levers in DESIGN.md vs reality.** PR #31's DESIGN.md
   §3.5 tuning-lever subsection names `tasks_per_crewmate` as a
   lever; the cooldown-only fix means that parameter was never
   added to `orchestrator/seeder.py`. Is this a doc-vs-code drift
   that needs a follow-up cleanup?
6. **New findings introduced by the audit window.** List any
   Critical/High findings this audit surfaces that did not exist in
   the May-15 reconciled audit. If yes, they must be addressed before
   Phase 3 begins; if no, Phase 3 may proceed.

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

- Do not paraphrase the May-15 reconciled audit's findings as if you
  re-verified them. Either re-run the check and cite the new evidence,
  or omit the finding.
- Do not produce a "looks good" section. Either a thing is verified
  with evidence, or it is a Concern.
- Do not include code suggestions, refactor proposals, or
  architectural improvements that are not tied to a cited defect.
- Do not soften severities to be polite. A Critical finding stays
  Critical even if the responsible PR is recent.
- Do not skip the regression baseline. The point of a baseline is
  that you only re-audit what changed; skipping it forces the
  reconciler to redo your work.
- Do not write more than ~700 lines. If you are over, you are
  repeating yourself or auditing out-of-scope code.
- Do not re-litigate the `dropped`-rule choice. That decision is
  final and documented in DESIGN.md §3.5. Audit the implementation
  of the choice, not the choice itself.
