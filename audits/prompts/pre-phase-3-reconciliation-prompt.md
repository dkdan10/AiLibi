# Pre-Phase-3 Audit Reconciliation — Prompt

Two independent auditors have produced reports at:

- `audits/audit-2026-05-15-0115-claude.md`
- `audits/audit-2026-05-15-0124-codex.md`

You are reconciling them into one canonical report. You are running
**fresh** — you have no memory of either audit's intent, and you must
not read the prompt that produced them
(`audits/prompts/pre-phase-3-audit-prompt.md`). You read only:

1. The two audit files above.
2. The repository at current `HEAD` of `main`.
3. The prior audit `audits/audit-2026-05-10-0721.md` (as a regression
   baseline reference only).

Your job is **adjudication**, not merging. Anchoring on either
auditor's wording, structure, or severity will defeat the point of
running two. Treat both reports as untrusted witnesses whose claims
must be verified against the code before they enter the canonical
record.

---

## 1. Identity and constraints

- **Role:** read-only reconciler. You may run any non-mutating shell
  command, read any file, and execute the test/lint/type/harness
  suites. You may not edit source files, tests, fixtures,
  configuration, task documents, or agent prompts. The only files
  you write are your reconciled audit report and (optionally) a
  short working scratch file under `audits/prompts/scratch/` if you
  need one — do not commit it.
- **No fixes.** Repair work is owned by a separate task that will be
  authored from this reconciled audit.
- **No new analysis beyond what evidence supports.** You may surface
  a new finding only if you stumble on it while verifying an
  existing finding *and* you cite evidence to the same bar the
  audits were held to (file:line + reproducible command). Do not
  re-audit.

## 2. Process (mandatory order)

### Step 1 — Extract every finding into a comparison table

Build one table with one row per finding. A "finding" is anything
either audit lists in §10 (Defects and Risks) or anything either
audit calls a Fail, Concern, or Phase-3 blocker in §5, §6, §7, §8,
§9, §11, or §12. Use these columns:

| ID | Title | Claude says | Codex says | Verified | Final severity | Disposition |

- **ID:** sequential, `R-1` through `R-N`. This is the new canonical id.
- **Title:** ≤ 100 chars, action-oriented.
- **Claude says:** that auditor's severity + a one-line summary, or `—` if absent.
- **Codex says:** same, or `—` if absent.
- **Verified:** `yes`, `no`, or `partial` after you re-run the cited evidence.
- **Final severity:** Critical / High / Medium / Low / Concern, or `dropped`.
- **Disposition:** one of:
  - **Confirmed** — both audits cited it, evidence reproduces.
  - **Unique-but-verified** — one audit cited it, evidence reproduces.
  - **Promoted** — severity raised from the audit's grading (with reason).
  - **Demoted** — severity lowered from the audit's grading (with reason).
  - **Dropped** — evidence does not reproduce, citation is stale, or finding
    is a duplicate of another row.
  - **New** — surfaced during your verification, not in either audit.

This table is the canonical contract. Every finding in the final
report must trace back to a row. Findings without a row do not exist.

### Step 2 — Re-run evidence for every Critical or High finding

Both prior audits famously missed the original id leak even though
they both ran the leak test. Same blind spot is possible here. For
each Critical or High finding, run the cited command(s) yourself at
current `HEAD` and record the actual output in the table's "Verified"
column. For findings that depend on running the orchestrator,
re-run the actual seed sweep and tournament — do not trust either
auditor's numbers.

For Medium and below, you may rely on the cited file:line if you
read the cited code and confirm the citation is accurate. If the
citation is wrong or stale, mark `Verified: no` and consider
`Dropped`.

### Step 3 — Apply the severity tie-breaker rule

When the two audits disagree on severity:

1. Default to the **higher** severity.
2. Only demote if (a) your re-verification shows the evidence is
   weaker than the higher-severity auditor claimed, OR (b) the
   higher-severity grading depends on a rubric interpretation that
   the rubric does not actually require. State the reasoning
   explicitly in the table's Disposition column and again in §13
   below.

The exception is when one auditor writes a self-aware downgrade
clause (e.g. "a reconciler may downgrade to Concern if X"). Treat
that as a hint, not a binding instruction — you still apply rule (1)
unless your re-verification supports the downgrade on its own
merits.

### Step 4 — Write the canonical report

After the table is complete and every row's evidence has been
verified, write the canonical audit report in the same section
structure as `audits/audit-2026-05-10-0721.md` (§1 Executive Summary
through §12 Readiness for Phase 3), with one new section appended:

**§13 Reconciliation** containing:
- §13.1 The full comparison table from Step 1.
- §13.2 Disagreements and resolutions — one paragraph per row whose
  Disposition is not `Confirmed`. Each paragraph names the auditor
  whose grading was rejected and why, and cites the specific
  evidence that settled the call.
- §13.3 Verdict reconciliation — if the two verdicts in §2 of the
  source audits differed, state which won and why in one short
  paragraph. If they agreed, say so in one sentence.

## 3. Section-by-section reconciliation rules

For each section of the canonical report:

- **§1 Executive Summary** — synthesise, do not concatenate. Lead
  with the verdict. ≤ 10 sentences. Quote the Critical/High count
  from the reconciliation table.
- **§2 Verdict** — one of **Ready for Phase 3**, **Ready with fixes**,
  **Not ready**. If both source audits agree, adopt that verdict.
  If they disagree, choose the more conservative reading and
  justify in §13.3.
- **§3 Commands Run and Evidence Sources** — list every command
  you ran during reconciliation (not the union of both audits'
  command lists). Both audits' command lists are an input to your
  work, not your output.
- **§4 Regression Baseline** — adopt the table from
  `audit-2026-05-10-0721.md` and reconcile any cells where the two
  audits disagree. Re-verify any "Still Pass (no diff)" claim by
  running `git diff 014cca5..HEAD -- <path>` for that row.
- **§5 Prior Audit Follow-Through** — both source audits already
  re-checked M-1 and L-1 through L-5. Where they agree, adopt. Where
  they disagree, re-verify and decide.
- **§6 Task-by-Task DoD Audit** — for each of 2.7.5, 2.8, 2.8.5,
  2.9: take the union of DoD bullets both audits evaluated, and for
  each bullet record Pass / Fail / Partial with the strongest
  cited evidence from either audit (plus your re-verification if
  the bullet is Fail).
- **§7 Architectural Invariant Audit** — for each invariant (I-1
  through I-12 plus multi-agent): if both audits Pass it, Pass it.
  If either Fails it, re-run the invariant check yourself.
- **§8 Specific Questions** — synthesise both answers into one. If
  the answers contradict, re-read the cited code and write a single
  reconciled answer that cites the evidence that settled it.
- **§9 Test Quality and Coverage Gaps** — adopt the union of both
  lists, deduplicated. A gap mentioned by only one auditor still
  counts if you can re-verify the gap exists.
- **§10 Defects and Risks** — populate exclusively from the
  reconciliation table. Number findings R-1 through R-N matching
  the table. Use the same format as `audit-2026-05-10-0721.md` §11
  (Status / Evidence / Why it matters / Recommended action). If
  you Promoted or Demoted a finding, note the original auditor's
  severity in the Status line.
- **§11 Document Conflicts** — adopt the union, deduplicated.
- **§12 Readiness for Phase 3** — your reconciled answer. If the
  source audits' answers differ in any substantive way, note the
  divergence in §13.3.
- **§13 Reconciliation** — as described above.

## 4. Known disagreement hotspots to adjudicate

You will need a verdict on these specifically. Both are real
disagreements between the two source audits and the reconciliation
exists in part to resolve them:

1. **The id-grep guard finding.** Codex grades it **Critical**
   (their finding #2); Claude grades it **High** (their §10.4) and
   teed up a downgrade. The literal regex match exists in
   `tests/eval/test_balance_eval.py:258` and `eval/leak_test.py:228`.
   Both lines are deliberate negative-test fixtures inside the value
   scanner's self-test. Decide whether the audit prompt's "any hit
   in `tests/` is Critical" rule applies to negative-test fixtures.
   Cite both the literal grep output and the surrounding test
   function (read it, do not trust either summary).

2. **The impostor-stalemate root cause.** Claude graded as **High**
   (their §10.3) with a specific code trace through
   `agents/tactical/impostor_policy.py:219-265` and a tick-970–999
   action trace from seed 0. Codex does not name this finding. If
   you confirm the trace by re-running seed 0 and reading the
   policy code, this is `Unique-but-verified` at the original
   severity; if the trace does not reproduce, this is `Dropped`. Do
   not split the difference.

3. **The Phase 3.3 memory-store gap.** Codex graded as **High**
   (their finding #4); Claude addressed memory shape in §8 / §12 but
   did not flag it as a discrete defect. Decide whether the gap is a
   Phase-3 blocker (High) or an unresolved-contract-to-write
   (Concern). The evidence is whether `agents/memory/store.py` is
   absent and whether Task 3.3's DoD names it.

4. **Verdict.** Codex says "Not ready to start Phase 3 safely".
   Claude's §2 verdict — read it. If they agree, the question is
   trivial; if they disagree, §13.3 must adjudicate.

## 5. Output

Write the canonical reconciled report to:

`audits/audit-YYYY-MM-DD-HHMM-reconciled.md`

(use current local date/time). When finished, print:

- The absolute path of the file.
- The verdict.
- The count of Critical / High / Medium / Low / Concern findings.
- The count of `Confirmed` / `Unique-but-verified` / `Promoted` /
  `Demoted` / `Dropped` / `New` dispositions from §13.1.
- A one-paragraph summary of the most important thing to fix
  before Phase 3 begins.

Do not commit. Do not open a PR. Do not modify either source audit
or the prior audit.

---

## Anti-patterns (do not do these)

- Do not concatenate the two audits. The output is shorter than
  either input, not longer.
- Do not adopt either audit's wording verbatim for any finding you
  Promote, Demote, or Drop. State the finding in your own words so
  the change in severity is unambiguous.
- Do not re-audit. If both audits missed something obvious you stumble
  on while verifying, you may add it as a `New` row — but resist the
  pull to keep looking. The reconciliation has a fixed scope.
- Do not soften the verdict to split the difference. If the evidence
  says "Not ready", say "Not ready" even if one source audit said
  "Ready with fixes".
- Do not skip §13. The reconciliation section is the audit trail
  that justifies the canonical record; without it the reconciled
  audit is just one more opinion.
- Do not exceed the prior audit's length. A reconciled audit at this
  scope should be ~600–800 lines. If you are over, you are
  re-auditing.
