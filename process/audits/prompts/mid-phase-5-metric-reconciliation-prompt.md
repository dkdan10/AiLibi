# Mid-Phase-5 Metric Audit Reconciliation — Prompt

Two independent auditors have produced reports under `audits/` matching
the pattern `audit-YYYY-MM-DD-HHMM-mid-phase-5-metric-{claude,codex}.md`.
Discover them yourself with:

```
ls -t audits/audit-*-mid-phase-5-metric-*.md | grep -v reconciled | head -2
```

These are the two newest unreconciled metric audit reports. They are
your inputs.

You are reconciling them into one canonical report. You are running
**fresh** — you have no memory of either audit's intent, and you must
not read the prompt that produced them
(`audits/prompts/mid-phase-5-metric-audit-prompt.md`). You read only:

1. The two audit files identified above.
2. The repository at current `HEAD` of `main`.

For reconciliation structure you may consult
`audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md` (the most
recent reconciled audit in this repo) for section organization
patterns; you may not borrow its content or findings — it audited a
different defect class (DTO leakage), not metric correctness.

Your job is **adjudication**, not merging. Anchoring on either auditor's
wording, structure, or severity defeats the point of running two. Treat
both reports as untrusted witnesses whose claims must be verified
against the code — and, for metric-correctness claims, against a fixture
you build yourself — before they enter the canonical record.

---

## 1. Identity and constraints

- **Role:** read-only reconciler. You may run any non-mutating shell
  command (including `uv run python -c "…"` and `/tmp` scripts to
  rebuild fixtures), read any file, and execute the test/lint/type
  suite. You may not edit source files, tests, fixtures, configuration,
  task documents, or agent prompts. The only file you write is your
  reconciled audit report.
- **No fixes.** If either audit flags a defect that reproduces, record
  it. Repair work is owned by separate tasks (5.6.5, 5.6.6, …) authored
  from this reconciled audit.
- **No new analysis beyond what evidence supports.** You may surface a
  new finding only if you stumble on it while verifying an existing one
  AND you cite evidence to the same bar (file:line + reproducible
  command, or a known-answer fixture). Do not re-audit.
- **No real LLM provider calls.** Metrics are pure analyzers; the
  tournament runs on the fake provider.
- **Scope discipline.** Metric-correctness + loader-fidelity audit
  reconciliation. Same five classes as the audit prompt (A — metric vs.
  docstring; B — loader fidelity & roles; C — partial-replay
  robustness; D — schema integrity; E — prompt-version provenance).
  Anything outside those is out of scope.

## 2. Process (mandatory order)

### Step 1 — Identify the two source audits

Run the discovery command above. Confirm exactly two files match. If
only one or more than two match, stop and report — the prerequisite for
reconciliation is not met. Both files must be newer than any
`audit-*-mid-phase-5-metric-reconciled.md` that already exists. Print
the two filenames before doing anything else.

### Step 2 — Extract every finding into a comparison table

One table, one row per finding across both audits' five class
subsections. Informational notes count as rows (severity `Concern` or
`Informational`). Columns:

| ID | Class | Title | Auditor A says | Auditor B says | Verified | Final severity | Disposition |

- **ID:** sequential `R-1`…`R-N` (the new canonical id).
- **Class:** A / B / C / D / E.
- **Title:** ≤ 100 chars, action-oriented.
- **Auditor A/B says:** that auditor's severity + one-line summary, or
  `—` if absent. Use the real auditor names from Step 1's filenames.
- **Verified:** `yes` / `no` / `partial` after you re-run the evidence.
- **Final severity:** Blocking / High / Medium / Low / Concern /
  Informational, or `dropped`. **Blocking** triggers a repair task
  before 5.7/5.8 fan out.
- **Disposition:** Confirmed / Unique-but-verified / Promoted / Demoted
  / Dropped / New (same meanings as prior reconciliations).

This table is the canonical contract. Findings without a row do not
exist.

### Step 3 — Re-run evidence for every Blocking or High finding

For each Blocking or High finding, reproduce the cited evidence
yourself at current `HEAD`. For a metric-correctness finding, this means
rebuilding the known-answer fixture (via `uv run python -c` or a `/tmp`
script) and confirming the metric's actual output — do not trust either
auditor's claimed value. For a loader/roles finding, run a small
fake-provider tournament and inspect the produced `TournamentReport`
yourself. For Medium and below, you may rely on a cited file:line if you
read the code and confirm the citation is accurate; if it is stale, mark
`Verified: no` and consider `Dropped`.

### Step 4 — Apply the severity tie-breaker rule

When the two audits disagree on severity:

1. Default to the **higher** severity.
2. Only demote if (a) your re-verification shows the evidence is weaker
   than the higher-severity auditor claimed, OR (b) the higher grading
   depends on a rubric interpretation the audit prompt does not require
   (e.g. a metric-design preference rather than a docstring
   contradiction). State the reasoning in the Disposition column and in
   §3.2.

If one auditor calls a finding blocking and the other informational,
default to **blocking** unless re-verification shows it does not require
a repair task.

### Step 5 — Apply the verdict tie-breaker rule

Exactly one of:

- "Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8."
- "Mid-phase metric audit blocks fan-out — repair tasks required: …"

If both source audits agree, adopt that verdict. If they disagree,
adopt the conservative reading (**blocks fan-out**) unless your
re-verification shows every finding the blocking auditor cited is
`Dropped` after evidence check — then "passes", recorded in §3.3.

The reasoning: 5.8 is the Phase 5 close gate. A metric that computes the
wrong number makes the close-gate signal meaningless; the asymmetric
cost favors the conservative verdict.

### Step 6 — Write the canonical report

Required sections, in order:

1. **Verdict.** Verbatim, one of the two strings from Step 5. If
   blocking, list the repair task names (e.g. "5.6.5, 5.6.6").
2. **Environment.** Commit `HEAD` short-hash. `bash scripts/check.sh`
   one-line summary. `git log --oneline -6`.
3. **Class A — Metric vs. docstring correctness** (canonical, with
   final severity + disposition). Per-metric subsection or "No findings"
   with evidence.
4. **Class B — Loader fidelity & roles ground truth.**
5. **Class C — Partial-replay robustness.**
6. **Class D — Schema integrity.**
7. **Class E — Prompt-version provenance.**
8. **Repair task proposals.** One-paragraph sketch per Blocking finding
   (branch name, files in scope, one-line DoD).
9. **§3 Reconciliation:**
   - **§3.1** The full comparison table from Step 2.
   - **§3.2** Disagreements and resolutions — one paragraph per row
     whose Disposition is not `Confirmed`, naming the rejected grading
     and the evidence that settled it.
   - **§3.3** Verdict reconciliation — which verdict won and why (one
     paragraph), or one sentence if they agreed.
10. **Required closing fields:**
    - Report path
    - Verdict (verbatim)
    - Findings count by class
    - Total findings
    - Disposition counts (Confirmed / Unique-but-verified / Promoted /
      Demoted / Dropped / New)

## 3. Section-by-section reconciliation rules

- **Adopt the union** of both audits' findings within each class,
  deduplicated by `(module, defect)` pair against the table.
- **Same finding, different evidence quality:** adopt the stronger
  evidence (a known-answer fixture beats a paraphrase; an exact
  `compute_*` return value beats "looks wrong").
- **One audit cited, other missed:** include if you re-verify at HEAD;
  mark `Unique-but-verified`.
- **One audit cited, other explicitly rejected:** trust the rejecter
  unless your re-verification reproduces it; if both explicitly
  disagreed, write a §3.2 paragraph.

## 4. Output

Write the canonical reconciled report to:

`audits/audit-YYYY-MM-DD-HHMM-mid-phase-5-metric-reconciled.md`

(current local date/time). When finished, print: the absolute path, the
verdict, the count of Blocking / High / Medium / Low / Concern /
Informational findings, the disposition counts, and a one-paragraph
summary of the most important thing to fix before 5.7/5.8 fan out (or
"no fixes required" if the verdict is passes).

Do not commit. Do not open a PR. Do not modify either source audit or
any other audit.

## 5. Cost discipline

Zero API spend. Local CPU only. If you exceed ~40 minutes wall clock or
~60 shell commands, write a partial reconciled report.

---

## Anti-patterns (do not do these)

- Do not concatenate the two audits. The output is shorter than either
  input, not longer.
- Do not adopt either audit's wording verbatim for any finding you
  Promote, Demote, or Drop. State it in your own words.
- Do not re-audit. If both audits missed a class (e.g. neither built a
  cross-author alibi fixture for Class A), note the gap in §3.3 and
  stop — do not fill it yourself.
- Do not soften the verdict to split the difference. If the evidence
  says "blocks fan-out", say so even if one source audit said "passes".
- Do not skip §3. Without the reconciliation trail the report is just
  one more opinion.
- Do not exceed ~400 lines.
