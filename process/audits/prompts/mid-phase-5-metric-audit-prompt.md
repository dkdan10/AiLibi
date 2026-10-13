# Mid-Phase-5 Metric Correctness Audit — Prompt

You are auditing the AiLibi repository's Phase 5 eval-metric surface
after Task 5.6 (tournament metric integration) has landed. At this
point Phase 5 has produced:

- Task 5.1 — eval report schema (`eval/report_schema.py`:
  `TournamentReport`, `GameReport`, `MeetingReport`, `GameCostSummary`,
  `CURRENT_FORMAT_VERSION`)
- Task 5.2 — vote-correctness metric (`eval/vote_correctness.py`)
- Task 5.3 — accusation-calibration metric (`eval/accusation_calibration.py`)
- Task 5.4 — alibi-fabrication-rate metric (`eval/alibi_fabrication.py`)
- Task 5.5 — cost-dashboard metric (`eval/cost_dashboard.py`)
- Task 5.6 — tournament integration: the JSONL→`TournamentReport`
  loader and `run_tournament_eval` (`eval/balance_eval.py`), the
  `TournamentEvalReport` wrapper + `build_tournament_eval_report`
  (`eval/meeting_quality.py`), and JSON emit (`scripts/run_tournament.py`)

This is the **substrate that 5.7 (tournament dashboard) and 5.8
(prompt regression suite) will fan out against**, and 5.8 IS the Phase
5 close gate (a prompt-template change must produce a measurable metric
delta). A metric that computes the wrong number, or a loader that
silently drops ground truth, poisons every downstream consumer and the
close gate itself. That is what this audit exists to catch.

The defect class is **"does each metric compute what its docstring
claims?"** — NOT "does a DTO field leak?" (that was the Phase 4 audit).
A metric can be fully typed, pass its own unit tests, and still measure
the wrong thing. Your job is to verify the numbers against
ground truth you construct independently.

You will produce **one audit report** in `audits/` following the
format and rigor of the most recent reconciled mid-phase audit
(`audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md` is the
structural reference). This is one of two parallel audits — a separate
reconciliation session will adjudicate both reports against the code
before the project acts. Write your audit as if it stands alone; do
not soften a finding expecting the reconciler to catch it. The final
verdict comes from the reconciliation, not from your report.

---

## 1. Identity and constraints

- **Role:** read-only auditor. You may read any file, run any
  non-mutating shell command, and execute the full test/lint/type
  suite. You may construct throwaway fixtures via `uv run python -c
  "..."` or a script under `/tmp` (these do not mutate the repo). You
  may not edit source files, tests, fixtures, configuration, task
  documents, agent prompts, or any file outside `audits/`. The only
  file you write is your audit report.
- **No fixes.** If you see a defect, record it as a finding. Do not
  patch it, even one line. Repair work is owned by separate tasks
  (5.6.5, 5.6.6, …) that will be authored from this audit.
- **No speculation.** Every finding must cite a `file:line` AND/OR a
  reproducible command and its observed output. For a metric-
  correctness finding, the gold standard is: "I built fixture X where
  the metric value is Z by inspection; `compute_…` returned Y ≠ Z."
  A finding without reproducible evidence is not a finding.
- **No drive-by suggestions.** If a recommendation does not address a
  cited defect or unverified invariant, omit it. This is a defect
  register, not a wishlist. Metric design preferences (different bin
  counts, alternative join rules) are out of scope unless the shipped
  choice produces a value that contradicts the module's own docstring.
- **No real LLM provider calls.** The metrics are pure analyzers and
  the tournament runs on the FAKE provider. Run `bash scripts/check.sh`,
  any pytest invocation, and `scripts/run_tournament.py` against a
  small fake-provider run, but never invoke the real Anthropic client.
- **Scope discipline.** This is a metric-correctness + loader-fidelity
  audit. Findings about Phase 3/4 code, prompt-template wording, UI, or
  Phase 5 dashboard/regression design (5.7/5.8 are not built yet) are
  out of scope unless they directly cause a wrong metric value or a
  schema/loader defect. When in doubt, omit.

## 2. Scope

**In scope:**

- The four metric modules (`eval/vote_correctness.py`,
  `eval/accusation_calibration.py`, `eval/alibi_fabrication.py`,
  `eval/cost_dashboard.py`): does each public `compute_*` return the
  value its docstring and the DESIGN.md §11.3 definition claim, on
  fixtures whose answer is known by inspection?
- The loader and runner in `eval/balance_eval.py`
  (`run_tournament_eval`, the per-seed `GameReport` assembly,
  `_seeded_roles`, `_balance_report_from_tournament`, `run_balance_eval`).
- The wrapper + assembler in `eval/meeting_quality.py`
  (`TournamentEvalReport`, `build_tournament_eval_report`).
- The emit path in `scripts/run_tournament.py`.
- The integration tests in `tests/eval/test_tournament_report.py` —
  read them, but do NOT trust them as proof; construct your own
  independent fixtures. A test that asserts the metric's own (possibly
  wrong) output is not verification.
- `eval/report_schema.py` ONLY as the contract the emitted artifact
  must validate against (do not re-audit its 5.1 design; check that the
  integration honors it).

**Out of scope:**

- The internal design of `eval/report_schema.py` (Task 5.1, merged and
  separately reviewed). In scope only as a validation target.
- Engine / agents / llm / meetings / observation / orchestrator
  internals, except `orchestrator.replay.read_all_entries` /
  `compute_cost_usd` and `orchestrator.game.HeadlessGameResult`
  insofar as the loader consumes them.
- 5.7 dashboard and 5.8 regression-suite design — not built yet.
- Performance (Task 5.9).
- Test coverage as a metric; coverage gaps that hide a wrong-number
  defect are in scope, coverage gaps that don't are not.

## 3. Audit window

Enumerate every commit since the Phase 5 schema landed:

```bash
git log --oneline --name-status ddc34b3~1..HEAD
```

The commits should correspond to Tasks 5.1–5.6. Confirm 5.6 is merged
(the loader + `TournamentEvalReport` + JSON emit are present). If 5.6
is not yet merged, abort and note: "Audit run before 5.6 merged;
integration substrate incomplete."

Record the `bash scripts/check.sh` one-line result up front. If any
static gate is red, that is a Blocking finding before you go further.

## 4. The five findings classes you must check

For each class, the report has a dedicated subsection. Every subsection
either lists concrete findings (with citations) OR states "No findings
in this class" with one sentence of evidence.

### Class A — Metric vs. docstring correctness

For each of the four `compute_*` functions: read its docstring and the
DESIGN.md §11.3 definition, then construct at least one synthetic
`TournamentReport` (or `GameReport` sequence) fixture whose metric value
you know by inspection, and confirm the function returns it. Build
fixtures by instantiating the schema models directly via `uv run python
-c` or a `/tmp` script — do NOT reuse the shipped test fixtures as your
only evidence.

Specific high-risk predicates to probe (these are where a wrong number
hides):

- **vote_correctness:** Construct an `EJECTED` meeting that ejects an
  impostor with NO contradiction naming them and NO kill-witness chain
  — it must score as NOT evidence-backed (else the metric is just the
  impostor-ejection rate, the circularity DESIGN.md §11.3 warns
  against). Confirm `vote_correctness_rate` is `None` (not `0.0`) when
  there are zero impostor ejections, and that the bucket invariant
  (`impostor_ejections + crewmate_ejections == total_ejections`) holds.
  Verify the "real evidence" predicate matches the docstring: a
  `ContradictionRef` whose `subjects` include the ejected player, or a
  `FoundBodyObservation` + `SawPlayerObservation` co-location — and that
  a bare accusation against the ejected player does NOT count.
- **accusation_calibration:** Confirm `confidence == 1.0` lands in the
  top bin (closed `[lo, 1.0]`), not dropped or overflowing. Confirm
  `AccusationClaim` and `VoteBallot` confidences are reported as TWO
  separate curves, never pooled. Confirm a `"SKIP"` ballot is excluded.
  Confirm a target absent from `roles` is fail-loud (raises), not
  silently scored as a miss. Confirm the ECE uses each bin's empirical
  `mean_confidence` and is `None` for a curve with zero accusations.
- **alibi_fabrication:** Determine which join rule shipped
  (subject-membership vs event-id reconstruction) and test its stated
  failure mode. If subject-membership: build a cross-author case (an
  `alibi_conflict` whose `subjects` name the impostor's subject but
  authored by two OTHER players) and confirm the documented behavior
  (does the impostor's own alibi count as caught or survived?). Confirm
  "impostor alibi" is identified by AUTHOR role (`ReportDocument.agent_id`
  / `Statement.speaker`), not by `AlibiClaim.subject`. Confirm the same
  alibi tuple restated in a report and a statement is deduped (counted
  once).
- **cost_dashboard:** Confirm `total_cost_usd` is read straight from
  `GameCostSummary.total_cost_usd` and `failed_calls` cost is NOT added
  again (build a game with a `failed_calls` row and check the total is
  not inflated). Confirm per-`(template, version)` totals OVERLAP (a
  game counts its full cost under each template) and do NOT sum to the
  tournament total. Confirm `mean_cost_per_game == 0.0` for a zero-game
  report (no division-by-zero / NaN).

### Class B — Loader fidelity & roles ground truth

The loader in `eval/balance_eval.py` (`run_tournament_eval`) turns a
real run into a `TournamentReport`. Verify:

1. **Roles are real and complete.** Run a small fake-provider
   tournament, then for every `GameReport`: `roles` is non-empty, its
   key set equals the game's player set, and exactly `num_impostors`
   entries are `"IMPOSTOR"`. Roles must come from the in-memory seeded
   result (`HeadlessGameResult.final_state.players`), NOT the replay
   JSONL (which never persists them). Confirm `_seeded_roles` (the
   aborted-game fallback) yields the same role assignment as the live
   game for the same seed + config.
2. **Cost reconciles.** For each seed, `GameReport.cost.total_cost_usd`
   equals `orchestrator.replay.compute_cost_usd(replay-seed-{seed}.jsonl)`.
   `by_model` and token totals sum the same records (meeting `llm_calls`
   plus `failed_calls`). No double-count.
3. **Record→report mapping.** `MeetingReplayEntry` rows map to
   `MeetingReport` with the same `meeting_id`/`tick`/`outcome`/
   `ejected_player_id`/`transcript`/`ballots`/`contradictions`/
   `llm_calls`; `GameEndReplayEntry` populates `winner`/`reason`/
   `final_tick`; `FailedCallReplayEntry` rows populate `failed_calls`.
4. **`run_balance_eval` still returns a `BalanceReport`** equal to what
   it returned before (the migration kept it as a thin reducer); the
   buckets it derives match the `TournamentReport` winners.

### Class C — Partial-replay robustness

Construct or capture each degenerate input and confirm no metric and no
loader raises (or that it fails loud only where it should):

- A game with no meetings (metrics contribute zero; loader yields a
  `GameReport` with empty `meetings`).
- A partial/crashed run with no `game_over` record → `winner=None`,
  `final_tick=None`; the loader does not raise (but still fails loud on
  a doubled/corrupted file via `read_all_entries`'s `CorruptedFileError`).
- A meeting that aborted on a failed LLM call (the 5.6 follow-up
  "recover partial game on per-seed meeting abort") — confirm the
  partial game is recovered with correct roles and its `failed_calls`
  spend counted once.
- An `EJECTED` meeting with `ejected_player_id is None` (type-possible;
  `MeetingReport` does not enforce the coupling) — confirm
  vote_correctness skips it rather than crashing on a `roles[None]`
  lookup.
- Empty `prompt_versions` on a game — confirm cost_dashboard handles it.

### Class D — Schema integrity of the emitted artifact

1. Run `scripts/run_tournament.py` on a few fake-provider seeds and
   load the emitted JSON. It must `model_validate_json` cleanly against
   `TournamentEvalReport` / `TournamentReport` (round-trip:
   `model_validate_json(model_dump_json(x))` is identity).
2. `format_version == CURRENT_FORMAT_VERSION`; the validator rejects a
   bumped version.
3. No field the schema promises is left empty by the integration where
   data exists (e.g. `roles` populated, `cost` populated,
   `prompt_versions` populated for games with meetings), and no value
   appears that the schema's `extra="forbid"` would reject (round-trip
   would catch this — confirm).
4. The `TournamentEvalReport` wrapper carries the four metric blocks and
   the underlying `TournamentReport`; confirm `build_tournament_eval_report`
   calls each public `compute_*` and packs the result without recomputing.

### Class E — Prompt-version provenance

The Phase 5 close loop attributes metric and cost deltas to prompt
versions. Verify:

1. `GameReport.prompt_versions` is populated from the meeting records'
   `MeetingReplayEntry.prompt_versions` and reflects the templates
   actually in play.
2. `cost_dashboard`'s `per_prompt_version` keys by the real
   `(template_name, version)` pairs; a single-run report (one version
   set) collapses to keys whose `game_count` covers every game.
3. A game with no meetings has the documented `prompt_versions`
   behavior (empty) and does not corrupt the per-version roll-up.

## 5. Report format

Your report goes to
`audits/audit-YYYY-MM-DD-HHMM-mid-phase-5-metric-{tool}.md` where
`{tool}` is your own tool name in lowercase — `claude` or `codex`
(whichever you actually are). The pairing with the other auditor's
report (same convention) is what enables the downstream reconciliation
step.

Required sections:

1. **Verdict.** Exactly one of:
   - "Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8."
   - "Mid-phase metric audit blocks fan-out — repair tasks required: …"
     (list the repair task names).
2. **Environment.** Commit `HEAD` short-hash. `bash scripts/check.sh`
   one-line summary ("X passed, Y skipped"). `git log --oneline -6`.
3. **Class A — Metric vs. docstring correctness findings.** One
   subsection per metric (or "No findings" with the fixture evidence
   you ran).
4. **Class B — Loader fidelity & roles ground truth findings.**
5. **Class C — Partial-replay robustness findings.**
6. **Class D — Schema integrity findings.**
7. **Class E — Prompt-version provenance findings.**
8. **Repair task proposals.** For each blocking finding, a one-paragraph
   task sketch (branch name like `phase-5-metric-fix-…`, files in scope,
   one-line definition-of-done). The next session turns each into a full
   contract (5.6.5, 5.6.6, …).
9. **Required closing fields:**
   - Report path
   - Verdict (verbatim, one of the two above)
   - Findings count by class
   - Total findings

## 6. Cost discipline

Zero API spend (fake provider only). Local CPU only. If you exceed ~40
minutes wall clock or ~60 shell commands, write a partial report — the
auditor's value drops past that point. Keep tournament runs small
(e.g. 3–8 seeds) — you are verifying correctness, not balance.

## 7. What "passes" looks like

A passing audit has zero blocking findings in any class: every metric
returns the value its docstring claims on independently-constructed
fixtures, the loader populates `roles` completely and reconciles cost,
the emitted JSON validates against the 5.1 schema, and prompt-version
provenance is intact. Informational notes (e.g. "alibi_fabrication
shipped subject-membership; the cross-author false positive is real but
documented and low-frequency") are fine and useful as long as they do
not block fan-out.

A blocking finding has the shape: "metric `compute_X` returns Y on a
fixture whose correct value is Z," or "loader leaves `roles` empty so
vote-correctness silently scores zero," or "emitted JSON fails to
validate against `TournamentReport`," or "cost double-counts failed
calls." Each requires a repair task before 5.7/5.8 dispatch.

## 8. Anti-patterns to flag (high-signal example findings)

FORMAT references — only report if you actually observe and reproduce:

- **"`compute_vote_correctness` counts an impostor ejection with no
  contradiction and no kill-witness as evidence-backed: fixture with a
  single `EJECTED` meeting (ejected = impostor `p-2`, empty
  `contradictions`, empty `observations`) returns
  `evidence_backed_impostor_ejections=1`, but by inspection it is 0.
  The predicate at `eval/vote_correctness.py:NN` is reading the ballot
  target, not real evidence."**
- **"`run_tournament_eval` populates `GameReport.roles` from the replay
  file rather than `final_state`; every `roles` map is empty in a real
  run (`uv run python -c '…'` shows `roles == {}`), so all of 5.2–5.4
  silently report zero impostor signal."**
- **"Emitted `tournament-eval-report.json` carries `roles` as a list,
  not a mapping; `TournamentReport.model_validate_json` raises at
  `GameReport.roles`. The emit path at `scripts/run_tournament.py:NN`
  bypasses the schema."**

Cite real `file:line` and reproducible command output for every finding
in your actual report.

---

**Begin the audit. Write only to your report file in `audits/`. Do not
modify any other file. End with the "Required closing fields" block in
§5 #9.**
