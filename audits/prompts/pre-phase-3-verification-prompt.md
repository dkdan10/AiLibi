# Pre-Phase-3 Verification Audit — Prompt

You are running a lightweight, single-tool verification pass. The question
you answer is exactly:

> Are R-1 through R-14 in `audits/audit-2026-05-15-0225-reconciled.md`
> actually closed at current `HEAD`?

This is the unit test for the implementation work landed in PR #30
(Task 2.10), PR #31 (2.10.5), PR #33 (2.11), and PR #34 (2.12). It is
NOT a fresh audit. A separate full-pipeline audit
(`audits/prompts/pre-phase-3-audit-prompt.md`) handles fresh-discovery
work — keep that scope clean by staying narrow here.

---

## 1. Identity and constraints

- **Role:** read-only verifier. May run any non-mutating shell command
  and the full test/lint/type/harness suite. May not edit any source,
  test, configuration, task, or prompt file. The only file you write
  is your verification report.
- **Verification, not discovery.** Do not surface new findings. If you
  notice something while verifying R-N that is not covered by
  R-1...R-14, record it in §4 "Observations" — one paragraph, no
  detailed analysis. The full Phase 2 closing audit will sweep for
  new findings; do not pre-empt it.
- **No severity re-grading.** The reconciled audit's gradings stand.
  Your job is closure adjudication, not re-litigation.

## 2. Inputs and forbidden inputs

**Allowed reads:**

- `audits/audit-2026-05-15-0225-reconciled.md` (the spec — read §10
  and §13 in full; the rest is reference).
- The repository at current `HEAD` of `main`.
- Any PR's diff via `gh pr diff <N>` for PRs #30, #31, #33, #34.

**Forbidden reads** (would re-anchor your judgment):

- Other audit files under `audits/` (the two May-15 source audits, the
  prior May-10 audit).
- Other prompt files under `audits/prompts/` except this one.
- The `## Decisions` blocks of the implementation PRs — for closure
  evidence, look at the **code and tests** directly. PR descriptions
  are claims, not evidence.

## 3. Required evidence (commands to run)

Run all of the following from the repo root. Record exit code and the
last line of output for each in §2 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run pytest`
- `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/`
  (must return empty)
- `git grep -nE "['\"](player|impostor|victim|observer|crew-[0-9]+)['\"]" tests/observation/test_service.py`
  (must return empty)
- Six-seed sweep:
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/verify-r-$seed.jsonl --max-ticks 1000; done`
- Small tournament for R-1 spot-check:
  `uv run python scripts/run_tournament.py --num-games 20 --start-seed 0 --output-dir /tmp/verify-tournament --max-ticks 1000`
  (20 games is the verification budget; the full 100-game gate already
  passed at PR #31 — this is a smoke check, not a re-run of the gate)
- Targeted regression-test runs for the closure pins:
  - `uv run pytest tests/agents/test_impostor_policy.py -v -k "Stale or Dead"`
  - `uv run pytest tests/engine/test_tick.py -v -k "dead_crewmate"`
  - `uv run pytest tests/eval/test_balance_eval.py -v -k "canonical_balance or default_agent_sweep"`
  - `uv run pytest tests/observation/test_service.py -v -k "audit_log_appends"`
  - `uv run pytest tests/engine/test_tick_properties.py -v`

Run additional commands as needed to verify specific R-ids. Every
command appears in §2.

## 4. Required report structure

Write to:

`audits/audit-YYYY-MM-DD-HHMM-pre-phase-3-verification.md`

Use the current local date and time. Required sections, in this order:

1. **Verdict.** One of:
   - **Verification passed — Phase 3 may begin.** Every R-id is Closed
     OR Closed-via-Phase-3-addendum (for R-6/R-9/R-10).
   - **Verification blocked.** One or more R-ids of Medium or higher
     severity are Not closed, or one or more are Partial with material
     residual risk.
2. **Commands run.** Every command + its last-line output.
3. **R-id closure table.** One row per R-1 through R-14:

   | R-id | Severity | Disposition | Evidence | Phase-3 blocker? |

   - **Disposition:** `Closed`, `Closed-via-Phase-3-addendum`,
     `Partial`, or `Not closed`.
   - **Evidence:** the specific `file:line`, commit, or passing test
     name that proves closure. Cite concretely; no hand-waves.
   - **Phase-3 blocker:** `yes` or `no`. A Partial may or may not
     block depending on severity; explain in the row.
4. **Observations.** One paragraph (≤ 150 words) noting anything you
   spotted while verifying that is outside R-1...R-14's scope. If
   nothing, write "None."
5. **Verdict justification.** One paragraph stating, in plain prose,
   why the verdict in §1 follows from the table in §3.

## 5. R-id-specific closure checks

Walk this list in order. For each R-id, the listed evidence is the
minimum for `Closed`. If the evidence is incomplete but partially
present, that's `Partial` — explain in the row. If the evidence is
absent, that's `Not closed`.

- **R-1 (Critical, tournament balance).** Run the 20-game tournament
  above. Both `CREWMATES%` and `IMPOSTORS%` of decisive games must
  exceed 20%. The PR #31 baseline was 73.12% / 26.88% at
  `kill_cooldown_ticks=4` over 100 games.
- **R-2 (Critical, six-seed decisive sweep).** Run the six-seed
  sweep. At least one seed must end at `CREWMATES` or `IMPOSTORS`.
  (The PR #31 baseline had all six decisive.)
- **R-3 (High, impostor staleness/dead-target).** Read
  `agents/tactical/impostor_policy.py` and confirm
  `_STALENESS_THRESHOLD`, `_BODY_ID_VICTIM_PATTERN`,
  `_confirmed_dead_from_bodies`, and the `confirmed_dead` /
  staleness filters in `_scored_targets` are present. The `Stale or
  Dead` test class in `tests/agents/test_impostor_policy.py` must
  pass.
- **R-4 (High, old-id grep guard).** Run the `eval/ tests/` grep
  above. Must return empty. Confirm the scanner self-tests at
  `eval/leak_test.py` and `tests/eval/test_balance_eval.py` still
  use sentinels that trip the value scanner (substring `crew`).
- **R-5 (Concern, dead-crewmate rule).** Confirm `DESIGN.md` §3.5
  documents the `dropped` rule and the kill-triggers-crew-win
  consequence. Confirm `engine/tick.py::_apply_kill` removes the
  killed player's incomplete tasks. The `dead_crewmate` test in
  `tests/engine/test_tick.py` must pass.
- **R-6 (Concern, Phase 3 addendum).** Read `tasks/phase-3.md` Task
  3.3 DoD. Confirm an R-6 acceptance-gate bullet exists referencing
  the reconciled audit and `agents/memory/store.py` as the
  composite memory surface. Disposition is
  `Closed-via-Phase-3-addendum` (implementation is Phase 3.3's job).
- **R-7 (Medium, Task 2.8.5 scope drift note).** Read
  `tasks/phase-2.md` Task 2.8.5 body. Confirm a "Historical note
  (added 2026-05-15 by Task 2.11)" block exists between the
  Implementation hint and the Integration risk block,
  enumerating the unlisted files in the original PR's diff.
- **R-8 (Medium, Task 2.9 DoD wording).** Read `tasks/phase-2.md`
  Task 2.9 DoD bullet about "Both decisive sides win > 20% of
  decisive games" and the Phase 2 Merge Criteria block. The two
  must be verbatim identical (the wording fix from PR #33).
- **R-9 (Concern, Phase 3 addendum).** Read `tasks/phase-3.md` Task
  3.12 DoD. Confirm an R-9 acceptance-gate bullet exists referencing
  the reconciled audit, `ReplayEntry` extensions, and the
  long-horizon byte-identical replay test.
- **R-10 (Concern, Phase 3 addenda).** Read `tasks/phase-3.md`
  Task 3.3 AND Task 3.9 DoDs. Both must contain R-10
  acceptance-gate bullets about reusing the leak scanners on
  `render_for_prompt` output (3.3) and strategic prompt inputs
  (3.9), with at least one planted negative test each.
- **R-11 (Concern, decisive-outcome CI guard).**
  `tests/eval/test_balance_eval.py` must contain a test like
  `test_default_agent_sweep_reaches_at_least_one_decisive_outcome`.
  Run it. It must encode a small seed list and assert at least one
  decisive outcome.
- **R-12 (Low, property-test vocabulary).**
  `tests/engine/test_tick_properties.py` must contain a `hypothesis`
  strategy covering kill/vent/report actions in addition to
  move/wait, plus a property that exercises the new vocabulary.
- **R-13 (Low, audit-log append-mode regression).**
  `tests/observation/test_service.py` must contain a test like
  `test_audit_log_appends_across_two_instances`. Run it.
- **R-14 (Concern, observation helper ids).** Run the
  `tests/observation/test_service.py` grep above. Must return
  empty. Helper ids in that file must be `p-N` form.

## 6. Verdict rules

- **All Closed (or Closed-via-Phase-3-addendum) ⇒ Verification passed.**
- **Any R-id Medium-or-higher = `Not closed` ⇒ Verification blocked.**
- **Any R-id Low/Concern = `Partial` ⇒ judgment call.** Block only if
  the residual risk is material; otherwise pass with a note.
- If any required command fails (e.g. `bash scripts/check.sh`
  non-zero), that is `Verification blocked` regardless of the table.

When finished, print:

- The absolute path of the report.
- The verdict.
- The count of Closed / Closed-via-Phase-3-addendum / Partial / Not
  closed dispositions.
- Any commands that failed.

---

## Anti-patterns

- Do not surface new findings as R-ids. Record observations only.
- Do not run the full 100-game tournament. 20 games is the verification
  budget; the full gate already passed at PR #31.
- Do not edit any audit, prompt, or task file.
- Do not exceed 200 lines in the output report. A passing verification
  fits in well under 200 lines; a blocking verification adds the
  evidence for the blocker but stays focused.
- Do not adjudicate severity. If the reconciled audit said Medium, it's
  Medium here too.
