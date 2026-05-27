# Mid-Phase-4 DTO Audit Reconciliation — Prompt

Two independent auditors have produced reports under `audits/`
matching the pattern
`audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-{claude,codex}.md`. Discover
them yourself with:

```
ls -t audits/audit-*-mid-phase-4-dto-*.md | grep -v reconciled | head -2
```

These are the two newest unreconciled DTO audit reports. They are
your inputs.

You are reconciling them into one canonical report. You are running
**fresh** — you have no memory of either audit's intent, and you
must not read the prompt that produced them
(`audits/prompts/mid-phase-4-dto-audit-prompt.md`). You read only:

1. The two audit files identified above.
2. The repository at current `HEAD` of `main`.

There is no prior mid-phase DTO reconciled audit to use as a
baseline — this is the first run of this audit shape. For
reconciliation structure you may consult
`audits/audit-2026-05-25-0414-reconciled.md` (the most recent
reconciled audit in this repo, pre-phase-4 verification) for section
organization patterns; you may not borrow its content or findings.

Your job is **adjudication**, not merging. Anchoring on either
auditor's wording, structure, or severity will defeat the point of
running two. Treat both reports as untrusted witnesses whose claims
must be verified against the code before they enter the canonical
record.

---

## 1. Identity and constraints

- **Role:** read-only reconciler. You may run any non-mutating shell
  command, read any file, and execute the test / lint / type suite.
  You may not edit source files, tests, fixtures, configuration,
  task documents, or agent prompts. The only file you write is your
  reconciled audit report.
- **No fixes.** If either audit flags a defect that reproduces,
  record it. Repair work is owned by separate tasks (4.4.6, 4.4.7,
  ...) that will be authored from this reconciled audit.
- **No new analysis beyond what evidence supports.** You may surface
  a new finding only if you stumble on it while verifying an
  existing finding *and* you cite evidence to the same bar the
  audits were held to (file:line + reproducible command). Do not
  re-audit.
- **No real LLM provider calls.** Phase 4 added no new LLM-call
  paths.
- **Scope discipline.** This is a DTO / leak audit reconciliation,
  not a general code audit. Same scope guard as the audit prompt —
  DTO leakage, endpoint drift, TypeScript / Pydantic drift, frontend
  store / component leak, determinism + state-hash integrity.
  Anything outside those five classes is out of scope.

## 2. Process (mandatory order)

### Step 1 — Identify the two source audits

Run the discovery command above. Confirm exactly two files match. If
only one matches, or more than two, stop and report — the
prerequisite condition for reconciliation is not met. Both files
must be newer than any `audit-*-mid-phase-4-dto-reconciled.md` that
already exists (if any).

Print the two filenames you identified before doing anything else.

### Step 2 — Extract every finding into a comparison table

Build one table with one row per finding. A "finding" is anything
either audit reports in any of its five findings-class subsections
(Class A — DTO field leakage; Class B — Endpoint response drift;
Class C — TypeScript / Pydantic drift; Class D — Frontend store /
component leak; Class E — Determinism + state-hash integrity).
Informational notes (the audit prompt's §7 explicitly allows these)
count as rows; they just carry severity `Concern` or
`Informational`.

Use these columns:

| ID | Class | Title | Auditor A says | Auditor B says | Verified | Final severity | Disposition |

- **ID:** sequential, `R-1` through `R-N`. This is the new canonical
  id.
- **Class:** A / B / C / D / E from the audit prompt.
- **Title:** ≤ 100 chars, action-oriented.
- **Auditor A says / Auditor B says:** that auditor's severity + a
  one-line summary, or `—` if absent. Use the actual auditor names
  (e.g. "Claude" / "Codex") in the column headers based on the
  filenames you identified in Step 1.
- **Verified:** `yes`, `no`, or `partial` after you re-run the cited
  evidence.
- **Final severity:** Blocking / High / Medium / Low / Concern /
  Informational, or `dropped`. **Blocking** is the severity that
  triggers a repair task before 4.4.5–4.8 fan out.
- **Disposition:** one of:
  - **Confirmed** — both audits cited it, evidence reproduces.
  - **Unique-but-verified** — one audit cited it, evidence
    reproduces.
  - **Promoted** — severity raised from the audit's grading (with
    reason).
  - **Demoted** — severity lowered from the audit's grading (with
    reason).
  - **Dropped** — evidence does not reproduce, citation is stale, or
    finding is a duplicate of another row.
  - **New** — surfaced during your verification, not in either
    audit.

This table is the canonical contract. Every finding in the final
report must trace back to a row. Findings without a row do not
exist.

### Step 3 — Re-run evidence for every Blocking or High finding

Phase 3 reconciliations established that the two auditors share
blind spots. Same risk applies here. For each Blocking or High
finding, run the cited command(s) yourself at current `HEAD` and
record the actual output in the table's "Verified" column. For
findings that depend on the running API, boot it locally
(`uv run uvicorn api.main:app --port 8000`) and curl the endpoint
yourself — do not trust either auditor's response JSON.

For Medium and below, you may rely on the cited file:line if you
read the cited code and confirm the citation is accurate. If the
citation is wrong or stale, mark `Verified: no` and consider
`Dropped`.

### Step 4 — Apply the severity tie-breaker rule

When the two audits disagree on severity:

1. Default to the **higher** severity.
2. Only demote if (a) your re-verification shows the evidence is
   weaker than the higher-severity auditor claimed, OR (b) the
   higher-severity grading depends on a rubric interpretation that
   the audit prompt does not actually require. State the reasoning
   explicitly in the table's Disposition column and again in §3.2
   of the final report.

In particular, the audit prompt's §7 distinguishes "blocking" from
"informational" findings. If one auditor calls a finding blocking
and the other calls it informational, default to **blocking** unless
re-verification of the cited evidence shows the finding does not
actually require a repair task.

### Step 5 — Apply the verdict tie-breaker rule

The audit prompt mandates exactly one of two verdicts:

- "Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8."
- "Mid-phase DTO audit blocks fan-out — repair tasks required: …"

If both source audits agree, adopt that verdict. If they disagree,
adopt the more conservative reading (**blocks fan-out**) unless your
re-verification shows that every finding the blocking auditor cited
is `Dropped` after evidence check — in which case the verdict is
"passes" and you record this resolution in §3.3 below.

The reasoning: a substrate that five PRs will build against is more
expensive to fix later than to fix now. The asymmetric cost favors
the conservative verdict.

### Step 6 — Write the canonical report

After the table is complete and every row's evidence has been
verified, write the canonical reconciled report. Required sections,
in this order:

1. **Verdict.** Verbatim, one of the two strings from Step 5. If
   blocking, list the repair task names (e.g. "4.4.6, 4.4.7").

2. **Environment.** Commit `HEAD` short-hash. `bash scripts/check.sh`
   one-line summary. Output of `git log --oneline -5`.

3. **Class A — DTO field leakage findings** (canonical, with the
   final severity and disposition per the table). Per-DTO
   subsection, or "No findings in this class" with evidence.

4. **Class B — Endpoint response drift findings.**

5. **Class C — TypeScript / Pydantic drift findings.**

6. **Class D — Frontend store / component leak findings.**

7. **Class E — Determinism + state-hash findings.**

8. **Repair task proposals.** For each finding whose final severity
   is Blocking, propose a one-paragraph task sketch (branch name,
   files in scope, one-line definition-of-done). The next session
   will turn each proposal into a full task contract.

9. **§3 Reconciliation** containing:
   - **§3.1** The full comparison table from Step 2.
   - **§3.2** Disagreements and resolutions — one paragraph per row
     whose Disposition is not `Confirmed`. Each paragraph names the
     auditor whose grading was rejected and why, and cites the
     specific evidence that settled the call.
   - **§3.3** Verdict reconciliation — if the two verdicts in the
     source audits differed, state which won and why in one short
     paragraph. If they agreed, say so in one sentence.

10. **Required closing fields** (extending §5 #9 of the audit prompt):
    - Report path
    - Verdict (verbatim, one of the two)
    - Findings count by class
    - Total findings
    - Disposition counts (`Confirmed` / `Unique-but-verified` /
      `Promoted` / `Demoted` / `Dropped` / `New`)

## 3. Section-by-section reconciliation rules

For each class subsection of the canonical report:

- **Adopt the union** of both audits' findings within that class,
  deduplicated against the comparison table by `(file, defect)`
  pair.
- **Where both audits cited the same finding** with different
  evidence quality, adopt the stronger evidence (more specific
  citation, more reproducible command, exact response JSON over
  paraphrase).
- **Where one audit cited a finding the other missed**, include it
  if you can re-verify the cited evidence at HEAD. Mark the row
  `Unique-but-verified` in the table.
- **Where one audit cited a finding the other dropped** (i.e. the
  other audit actively considered and rejected it), trust the
  rejecter unless your re-verification reproduces the finding. If
  both audits explicitly considered and disagreed, this is a §3.2
  disagreement requiring an explicit paragraph.

## 4. Output

Write the canonical reconciled report to:

`audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-reconciled.md`

(use current local date / time). When finished, print:

- The absolute path of the file.
- The verdict.
- The count of Blocking / High / Medium / Low / Concern /
  Informational findings.
- The count of `Confirmed` / `Unique-but-verified` / `Promoted` /
  `Demoted` / `Dropped` / `New` dispositions from §3.1.
- A one-paragraph summary of the most important thing to fix
  before 4.4.5–4.8 fan out (or "no fixes required" if the verdict
  is passes).

Do not commit. Do not open a PR. Do not modify either source audit
or any other audit.

## 5. Cost discipline

This reconciliation costs zero API spend (no real-provider calls).
Local CPU only. If you spend more than 30 minutes wall clock or
your local shell command count exceeds ~50, stop and write a
partial reconciled report — the reconciler's value drops past that
point.

---

## Anti-patterns (do not do these)

- Do not concatenate the two audits. The output is shorter than
  either input, not longer.
- Do not adopt either audit's wording verbatim for any finding you
  Promote, Demote, or Drop. State the finding in your own words so
  the change in severity is unambiguous.
- Do not re-audit. If both audits missed a class of findings (e.g.
  neither checked Class E), note the gap in §3.3 and stop. Do not
  attempt to fill the gap yourself — that's a re-audit, not a
  reconciliation.
- Do not soften the verdict to split the difference. If the
  evidence says "blocks fan-out", say "blocks fan-out" even if one
  source audit said "passes".
- Do not skip §3. The reconciliation section is the audit trail
  that justifies the canonical record; without it the reconciled
  audit is just one more opinion.
- Do not exceed ~400 lines. A reconciled DTO audit at this scope
  should be ~200–400 lines. If you are over, you are re-auditing.
