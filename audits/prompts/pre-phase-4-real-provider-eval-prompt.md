# Pre-Phase-4 Real-Provider Eval — Prompt

You are running the Phase 3 closing merge-criteria eval. This is the
**only audit-pipeline stage that uses live Anthropic API calls**. It
runs a 50-game tournament against the real provider and evaluates
against Phase 3's merge criteria that cannot be validated with the
fake provider:

- 50-game eval completes end-to-end (no crashes).
- Impostor win rate in [25%, 65%] band.
- Cost per game ≤ $0.30.
- Meeting transcripts are human-readable.
- Replay/eval records include meeting artifacts, prompt versions, and
  LLM cost metadata.

This prompt is **operational**, not a code audit. The deliverable is
a tournament-outcome report with cost analysis, transcript samples,
and a Phase 3 merge-criteria verdict. Code-level findings belong to
the `pre-phase-4-audit-prompt.md` (run BEFORE this) — by the time
you read this prompt, the static / fake-provider audit has already
returned **Ready for Phase 4 (pending real-provider eval)** or
equivalent.

**Run order is mandatory:**

1. `pre-phase-4-verification-prompt.md` (verification — fake provider)
2. `pre-phase-4-audit-prompt.md` (full audit — fake provider; two-tool + reconciliation)
3. **This prompt** (real-provider eval — only after the prior two pass)

Running this prompt out of order wastes API spend on a substrate that
may be defective.

---

## 1. Identity and constraints

- **Role:** evaluator + auditor. You run a real Anthropic-backed
  tournament, capture its outputs, and evaluate against the Phase
  3 merge criteria. You may run any non-mutating shell command
  including the live tournament. You may not edit source files,
  tests, fixtures, configuration, task documents, agent prompts, or
  any file outside `audits/`.
- **No fixes.** If you find a defect (e.g. unreadable transcripts,
  cost overrun, win-rate outside the band), record it as a finding.
  Repair work — prompt tuning, model swaps, budget adjustments — is
  owned by a follow-up task authored from this report.
- **No speculation about Phase 3 code.** Code-level audit findings
  are out of scope here. If you spot a code defect while reviewing
  transcripts or replay records, note it in §6 "Observations" — one
  paragraph, no detailed analysis.
- **Cost discipline is your responsibility.** You are spending real
  money. Apply the abort conditions in §3 strictly. If a single game
  costs more than $1.00, stop the tournament and report before
  continuing.

## 2. Pre-flight setup

Before launching the tournament, verify the environment is configured
correctly. Run each command and confirm the expected output before
proceeding to §3.

- `echo $ANTHROPIC_API_KEY | head -c 8`
  Must print 8 characters (i.e., the env var is set). Do NOT print
  the full key to the report.
- `echo $AILIBI_LLM_PROVIDER`
  Must print `anthropic` (or whatever value Task 3.1's
  `## Decisions` documented — read `llm/README.md` if uncertain).
- `echo $AILIBI_LLM_MEETING_MODEL`
  Must print `claude-sonnet-4-6` (or the configured override).
- `echo $AILIBI_LLM_TRIGGER_MODEL`
  Must print `claude-haiku-4-5-20251001` (or the configured override).
- `bash scripts/check.sh`
  Must pass. If the static gates fail, the tournament will inherit
  the breakage; do not proceed.

If any pre-flight check fails, stop and report. The verdict in §1
of your report becomes **Pre-flight failed — eval not run.**

Then run a **3-game smoke** to verify the live provider is reachable
and produces sane output BEFORE committing to the 50-game spend:

```bash
uv run python scripts/run_tournament.py \
  --num-games 3 \
  --start-seed 0 \
  --output-dir /tmp/eval-smoke \
  --max-ticks 1000
```

Read the printed summary. Required smoke outcomes:

- All 3 games completed (no crashes, no `pytest`-style errors).
- At least one game produced at least one meeting (`meeting_phase_reached > 0`
  in the bucket counts OR meetings fired internally — check
  `/tmp/eval-smoke/*.replay.jsonl` for `MeetingReplayEntry` rows).
- Per-game cost from the 3-game replay is computable. If
  `LLMCallRecord` rows exist in the replay JSONL, sum their
  `cost_usd` per `game_id`.

If the smoke shows any single game cost > $1.00 or any game crash,
**stop and report**. Do not run the 50-game eval. Verdict: **Smoke
failed — eval not run.**

## 3. Required evidence (50-game eval)

After the smoke passes, run the 50-game tournament. Use a fresh
output directory.

```bash
uv run python scripts/run_tournament.py \
  --num-games 50 \
  --start-seed 0 \
  --output-dir /tmp/eval-50 \
  --max-ticks 1000
```

**Hard abort conditions** — monitor the tournament's progress (the
script should print per-game completion). If any of these fire,
kill the tournament with Ctrl+C, record what completed, and verdict
the eval as **Aborted by cost discipline**:

- After game 10 completes: sum the per-game costs. If the mean of
  the first 10 games > $0.60, abort. (2× the merge criterion target;
  continuing would not produce a passing verdict.)
- Any single game costs > $1.00. Abort regardless of which game.
- Any game crashes (the tournament script exits non-zero). Abort.

If the tournament completes normally, record the printed summary
(four-bucket counts + decisive split) in your report.

Then collect the per-game data:

- **Cost analysis.** Parse `/tmp/eval-50/*.replay.jsonl` for
  `LLMCallRecord` rows; sum `cost_usd` per `game_id`. Compute mean,
  median, max, min, std dev. Compare each to the $0.30 target.
- **Win-rate analysis.** From the tournament summary, compute
  decisive split (CREWMATES% / IMPOSTORS%). Compare to the [25%, 65%]
  band for impostor win rate.
- **Leak scan.** Walk all 50 audit logs through
  `eval/leak_test.py::_assert_no_recursive_hidden_fields` +
  `_assert_no_role_bearing_values`. Zero violations required.
- **Replay record completeness.** Sample 5 games (deterministic
  selection: games at seeds 0, 12, 25, 37, 49 — assuming seed
  ordering matches game numbering). For each, verify the replay
  JSONL contains:
  - At least one `MeetingReplayEntry` with a populated
    `MeetingTranscript` (reports, statements, votes, result).
  - Multiple `LLMCallRecord` rows, each with `model`,
    `prompt_version`, parsed output, and `cost_usd`.
  - Per-game cost is reconstructable by summing `LLMCallRecord.cost_usd`.

## 4. Transcript readability protocol

Sample the same 5 games (seeds 0, 12, 25, 37, 49). For each game,
extract every `MeetingReplayEntry` from its replay JSONL and read
the meeting transcripts (reports + statements + votes). Rate each
sampled game on the following dimensions, scoring **Pass** /
**Partial** / **Fail**:

| Dimension | Pass criterion |
|---|---|
| Coherent English | Statements are grammatical and structurally complete; no model-output artifacts (truncated, repeated tokens, JSON leakage into prose). |
| Role-appropriate | Crewmate reports describe observations truthfully; impostor reports may fabricate but stay schema-valid; accusations cite witnesses or behavior; votes have justifications. |
| Grounded in game state | Claims reference ticks, rooms, or players that exist in the game (or are plausibly fabricated by the impostor — the impostor lying is in-game-correct, but lying outside the world-state grammar is not). |
| Vote justifications | Each `VoteBallot` includes a non-empty `justification` field that semantically connects to the vote target. |

The pass criterion for each game: **at least 3 of 4 dimensions Pass**
(no Fails; Partials are tolerated).

The pass criterion for transcript readability overall: **at least 4
of 5 sampled games pass**. (Allowing one sub-par game accounts for
LLM variance and small seed-specific behaviors.)

Readability is necessarily a judgment call. Document your reasoning
per sampled game in §5 of the report. Do not pretend the assessment
is fully objective; transparent judgment is the bar.

## 5. Required report structure

Write to `audits/audit-YYYY-MM-DD-HHMM-pre-phase-4-real-provider-eval.md`.

Required sections:

1. **Verdict.** One of:
   - **Phase 3 complete — Phase 4 may begin.** All five merge
     criteria passed.
   - **Phase 3 blocked.** One or more merge criteria failed.
     Specify which.
   - **Pre-flight failed / Smoke failed / Aborted by cost discipline.**
     Eval did not run to completion.
2. **Environment.**
   - Provider, models, API key presence (8-character prefix only).
   - Pre-flight smoke result (3-game summary).
   - Tournament command exactly as invoked.
3. **Tournament outcome.**
   - Raw printed summary (four-bucket counts, decisive split).
   - Any crashed games or abort.
4. **Cost analysis.** Table: per-game cost stats.

   | Metric | Value | Merge criterion |
   |---|---|---|
   | Mean cost / game | $X.XX | ≤ $0.30 |
   | Median cost / game | $X.XX | — |
   | Max cost (single game) | $X.XX | — |
   | Min cost (single game) | $X.XX | — |
   | Std dev | $X.XX | — |
   | Total spend | $X.XX | — |

   Pass / Fail on the merge criterion (mean ≤ $0.30).
5. **Win-rate analysis.** Decisive split + impostor band check
   ([25%, 65%]). Pass / Fail.
6. **Leak scan result.** Counts: games scanned, packets scanned,
   violations. Zero violations required.
7. **Replay record completeness.** For each of the 5 sampled games
   (seeds 0, 12, 25, 37, 49):
   - `MeetingReplayEntry` present? Yes/No.
   - `LLMCallRecord` rows: count + sample shape (one row's
     `model` + `prompt_version` + presence of `cost_usd`).
   - Per-game cost reconstructable from records? Yes/No (matches
     §4 mean computation?).
8. **Transcript readability.** Per-sampled-game table:

   | Seed | Coherent English | Role-appropriate | Grounded | Vote justifications | Game verdict |
   |---|---|---|---|---|---|

   Pass / Fail on the readability criterion (≥ 4 of 5 games pass).
9. **Observations.** One paragraph (≤ 200 words) noting anything
   worth flagging that is outside the merge criteria. Code-level
   defects spotted during transcript review go here, NOT in a
   findings table.
10. **Verdict justification.** One short paragraph stating why the
    verdict in §1 follows from §3–§8.

## 6. Verdict rules

- **Phase 3 complete** requires all five merge criteria to Pass:
  1. 50 games complete without crashes.
  2. Impostor win rate in [25%, 65%].
  3. Mean cost / game ≤ $0.30.
  4. ≥ 4 of 5 sampled games pass the readability rubric.
  5. All 5 sampled replay records contain the required metadata
     (meeting transcripts, prompt versions, LLM outputs, cost
     metadata).
- **Phase 3 blocked** if any of the five fails. The remediation
  path differs by which:
  - Cost overrun → prompt brevity / cache-key review / consider
    Haiku fallback for triggered checks.
  - Win-rate out of band → prompt-quality issue; impostor or
    crewmate prompt may need sharpening.
  - Unreadable transcripts → prompt-template rework.
  - Crash → code defect, escalate to a hygiene task.
  - Missing replay metadata → R-9 incomplete, escalate.
- **Pre-flight / Smoke / Abort** verdicts indicate the eval did
  not produce a complete data set. Re-run after the underlying
  issue is fixed.

When finished, print:

- The absolute path of the report.
- The verdict.
- The per-game mean cost.
- The decisive split.
- The total API spend for this eval (sum of all `LLMCallRecord.cost_usd`).

---

## Anti-patterns (do not do these)

- Do not run the 50-game tournament without completing the
  pre-flight checks. The smoke is required.
- Do not continue the tournament past an abort condition. Cost
  discipline is non-negotiable.
- Do not print the full API key in the report. The 8-character
  prefix is the audit trail; the rest stays out.
- Do not re-run the tournament if it crashes; report the crash.
  Re-running burns spend without changing the diagnosis.
- Do not perform code-level audit work. Code findings belong to
  the static audit (Stage 2). Observations are fine; full findings
  are not.
- Do not soften the readability rubric to make a marginal eval
  pass. The 4-of-5 + 3-of-4-dimensions threshold is the spec; a
  3-of-5 result is a Fail.
- Do not exceed ~400 lines in the output report. The eval is
  data-heavy; keep prose tight.
