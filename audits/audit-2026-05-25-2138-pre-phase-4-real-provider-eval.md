# Pre-Phase-4 Real-Provider Eval — 2026-05-25 21:38 UTC

## 1. Verdict

**Phase 3 blocked.** Merge criterion #1 (50 games complete without
crashes) FAILED: the tournament crashed during game 24 (seed 23) with
a Pydantic `ValidationError` on `ReportDocument` — the meeting-report
response from the live provider arrived as a **markdown-fenced JSON
block whose opening fence was emitted but whose closing fence was
not** (consistent with the response being truncated at the
`DEFAULT_REPORT_MAX_TOKENS=1024` cap mid-output). Because
`_strip_json_code_fences` is conservative and only strips when **both**
an opening and a closing fence are present at the string edges, it
returned the text unchanged, and `model_validate_json` then failed
on the leading backtick.

This is a **distinct defect from the prior 2038 eval crash**. That
crash was a prompt↔schema field-name drift (legacy `player_id`,
`location`, `tick_start`, etc.) which Task 3.16 has since resolved.
The current crash is at the same code line (`llm/provider.py:128`,
`model_validate_json(text)`) but is caused by the
fence-stripping logic added in Task 3.15 not handling the
"truncated-response → unclosed-fence" edge case. The static and
fake-provider audits cannot surface this because the fake provider
returns provider-shape responses by construction, never running into
real-model truncation behavior — exactly the class of defect the
live eval exists to catch.

The first 23 games (seeds 0–22) completed cleanly but produced
**zero meetings** at the live ~7–10% trigger rate, so criteria #2–#5
(win rate band, mean cost, transcript readability, replay-record
completeness) cannot be evaluated from the partial data.

## 2. Environment

- Provider: `AILIBI_LLM_PROVIDER=anthropic`
- Meeting model: `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- Trigger model: `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8-char prefix only)
- Env vars sourced from project `.env` before each invocation (project
  code does not call `load_dotenv`; relies on env being pre-set in
  the parent shell).
- `bash scripts/check.sh` → **pass** with `AILIBI_LLM_PROVIDER`
  unset (676 passed, 7 skipped in 4.71s). Note: when run with
  `AILIBI_LLM_PROVIDER=anthropic` already exported, 2 tests fail
  because tests named `test_default_cap_admits_fake_provider_meeting`
  and `test_meetings_fire_and_game_resumes_from_public_factory_path`
  consult the live provider via `build_default_client`. This matches
  `llm/README.md`'s instruction that CI must leave the var unset; see
  §9 Observations.
- Direct sanity call → **pass**:
  `model=claude-sonnet-4-6 cost_usd=0.000105 text='OK'` (non-zero
  cost proves the live provider was actually called; model matches
  `MEETING_MODEL`).
- 3-game smoke (`/tmp/eval-smoke`) → **pass**: 3 games completed,
  no crashes, zero meetings fired (expected at ~7–10% rate); per-game
  cost via `compute_cost_usd` was `$0.00` for all three — consistent
  with no LLM meeting traffic. Tournament-wrapper integration
  validated.
- 50-game tournament command exactly as invoked:

  ```bash
  uv run python scripts/run_tournament.py \
    --num-games 50 \
    --start-seed 0 \
    --output-dir /tmp/eval-50 \
    --max-ticks 1000
  ```

## 3. Tournament outcome

**Tournament crashed.** Process exited **1** (the background-task
notification reported exit 0; `$?` from the parent shell captured 1
and the stdout log ends in a Python traceback, no summary line —
treat exit 1 as the truth). `_format_report` was never reached so the
canonical four-bucket counts are unavailable.

Reconstructed from the output directory:

- Replay+audit pairs written: **23 games** (seeds 0–22 inclusive).
- Replay files for the 23 completed games contain only `kind=tick`
  records (no game-result row is persisted to JSONL).
- Crash trace (full trace 62 lines in
  `/tmp/eval-50/tournament-stdout.log`; final 12 lines):

  ```
  File ".../orchestrator/game.py", line 292, in run_meeting
  File ".../meetings/manager.py", line 436, in run
  File ".../meetings/manager.py", line 499, in _collect_reports
  File ".../meetings/manager.py", line 166, in _gather_all_or_cancel
  File ".../meetings/manager.py", line 520, in _collect_one_report
  File ".../meetings/manager.py", line 134, in _isolate_provider_timeout
  File ".../orchestrator/game.py", line 214, in complete
  File ".../llm/budgeted_client.py", line 266, in complete
  File ".../llm/provider.py", line 128, in complete
      schema.model_validate_json(text)
  pydantic_core._pydantic_core.ValidationError: 1 validation error
      for ReportDocument
        Invalid JSON: expected value at line 1 column 1
        input_value='```json\n{\n  "agent_id"...servations of p-2 after'
  ```

  The visible input value ends mid-sentence ("…of p-2 after") and
  starts with ` ```json\n ` — strong evidence the response was
  truncated at `report_max_tokens=1024` (see
  `meetings/manager.py:73`) before the model could emit the closing
  ``` ``` ``` fence. `_FENCE_CLOSE_PATTERN` is anchored at `\s*$`
  so an unclosed fence falls through unchanged.

Crash location: the next seed after the last completed game (22) is
**seed 23**, and the trigger rate observed across the 23 prior games
was 0 meetings fired — consistent with "first real-provider meeting
ever attempted fails."

## 4. Cost analysis

| Metric | Value | Merge criterion |
|---|---|---|
| Mean cost / game (23 completed) | $0.000000 | ≤ $0.30 |
| Median cost / game | $0.000000 | — |
| Max cost (single game) | $0.000000 | — |
| Min cost (single game) | $0.000000 | — |
| Std dev | $0.000000 | — |
| Total spend (tournament games) | $0.000000 | — |
| Direct sanity call | $0.000105 | — |
| 3-game smoke | $0.000000 | — |
| **Total real-provider spend this eval** | **~$0.0001** + 1 crashed meeting call | — |

**Cannot evaluate** against the $0.30/game criterion: every completed
game emitted zero meeting LLM calls because no meeting was triggered
before the crash. The cost target is a per-game *budget* intended to
cover meeting traffic; observing $0 here is not evidence of "under
budget," only evidence that the eval never exercised the path the
budget governs. The crashed game (seed 23) made one meeting-report
call to the live provider whose tokens were consumed but whose
`LLMResponse` was never assembled (validation failed before
`cost_usd` was computed and returned), so that spend is invisible to
`compute_cost_usd` but real on the Anthropic side. Order of magnitude
is the meeting-report call (1024-token output cap) against a few-kB
prompt — well under $0.05.

Mid-run abort conditions: none fired prior to the crash (first-10
mean $0.00 ≪ $0.60; per-game max $0.00 ≪ $1.00).

## 5. Win-rate analysis

**Cannot evaluate.** The tournament summary that emits
`decisive_split: CREWMATES=...% IMPOSTORS=...%` was never printed
(crash occurred inside `run_balance_eval` before `_format_report`).
The per-game replay JSONLs the script did write contain only
`kind=tick` records — no per-game `GameResult` row is persisted, so
crew/impostor decisive counts cannot be reconstructed from the 23
completed games. The impostor-band check ([25%, 65%]) is therefore
undetermined.

## 6. Leak scan result

- Audit files scanned: **23** (`*.audit.jsonl` for seeds 0–22).
- Packets scanned: **748**.
- Violations from `_assert_no_recursive_hidden_fields`: **0**.
- Violations from `_assert_no_role_bearing_values`: **0**.

**PASS** on what was scanned. This is the only merge criterion that
survives the partial data because the leak-scan invariants are about
the observation-packet stream, which the 23 pre-meeting games fully
exercised.

## 7. Replay record completeness

| Sampled game | MeetingReplayEntry? | LLMCallRecord count | Cost reconstructable? |
|---|---|---|---|
| (none available) | — | — | — |

**Cannot evaluate.** Zero `MeetingReplayEntry` rows were written
across all 23 completed game files (the meeting-firing rate observed
was 0/23, and the crash terminated the run before any meeting
artifact reached disk). The sample-size requirement (first 5 games
with meetings) is unmeetable from this run. The metadata contract
(prompt_version at meeting-entry level per R-3, populated `cost_usd`
on `LLMCallRecord`, etc.) is unverified for the live provider.

## 8. Transcript readability

| game_id / seed | Coherent English | Role-appropriate | Grounded | Vote justifications | Game verdict |
|---|---|---|---|---|---|
| (no transcripts) | — | — | — | — | — |

**Cannot evaluate** — fewer than 3 games with meetings sampled (zero
available). Per the §6 verdict rules, this means the overall verdict
on criterion #4 is "insufficient meeting data" and a longer eval run
would be required *after the underlying crash is fixed*; re-running
on the current code would just hit the same crash on the first
meeting.

## 9. Observations

- **The crash is a new real-provider edge case in fence-stripping.**
  Task 3.15 added `_strip_json_code_fences` to handle Claude's
  default markdown-fenced structured-output. The implementation
  (`llm/provider.py:211-234`) is intentionally conservative: it
  strips only when **both** an opening fence and a closing fence sit
  at the string edges (`^\s*```(?:json)?\s*` and `\s*```\s*$`). The
  live provider produced a meeting `ReportDocument` whose response
  was apparently truncated at `report_max_tokens=1024` (the visible
  pydantic input value ends mid-prose with "after"), so the model
  emitted the opening ``` ```json\n ``` fence and the JSON body but
  ran out of tokens before producing the closing fence. The
  fence-stripper saw the unclosed fence, returned the text unchanged,
  and `model_validate_json` failed on the leading backtick. The
  remediation surface is small but the choice matters: raising
  `report_max_tokens`, retrying on truncation, asking the API to
  return raw JSON via response-format constraints, or making the
  stripper handle the unmatched-open case are all candidates. This
  belongs to a follow-up task, not to this audit.
- **Same crash location, different root cause from the 2038 eval.**
  Both crashes occurred at `llm/provider.py:128`, the first meeting
  attempted (seed 23). The 2038 crash was prompt↔schema field-name
  drift on `ReportDocument`, fixed by Task 3.16. This crash is a
  fence-stripping edge case, surfacing only because 3.16 unblocked
  the path far enough to reveal the next defect. Pattern: every live
  eval to date has been blocked by *one* defect that the static
  audit cannot see, fixed in a single hygiene PR, then unblocks the
  next. Worth flagging that "ship Phase 4 only after a green
  real-provider eval" is necessarily an iterative gate.
- **`check.sh` behavior with `AILIBI_LLM_PROVIDER=anthropic` already
  exported is surprising.** Two tests (`test_default_cap_admits_
  fake_provider_meeting`, `test_meetings_fire_and_game_resumes_from_
  public_factory_path`) attempt live calls when the env var is set
  to `anthropic`, which contradicts the spirit of "CI must leave
  `AILIBI_LLM_PROVIDER` unset" in `llm/README.md`. Operators running
  the eval will typically have the var exported in their shell — a
  conftest fixture that forces fake provider for the non-real-
  provider-marked tests would prevent this footgun. (Out of scope
  for this audit; flagged for a future hygiene task.)
- **No per-game `GameResult` row in replay JSONL** continues to
  block partial-tournament diagnostic value (also noted in the
  2038 report). Tournament outcome is only printed to stdout by
  `_format_report` and is lost on any pre-summary crash.

## 10. Verdict justification

§3 documents a non-zero-exit crash during the 50-game eval (23/50
games completed before failure), which directly fails merge
criterion #1 (50 games complete without crashes). §4, §5, §7, §8
each carry "Cannot evaluate" because the crash occurred on the first
meeting attempted (seed 23), depriving those criteria of any
meaningful data — every completed game is a "no-meeting" game. §6
(leak scan) is the only criterion with a clean Pass, but a single
passing criterion is not sufficient. Per the prompt's verdict rules
("Crash → code defect, escalate to a hygiene task"), the verdict is
**Phase 3 blocked** and the remediation path is a follow-up task to
(a) make `_strip_json_code_fences` (or the meeting-report call site)
robust to the unclosed-fence / truncation case, (b) add a real-
provider schema-roundtrip regression test exercising
`ReportDocument` with a deliberately-truncated fenced response, and
(c) re-run this eval after the fix lands. Re-running this eval
against the current code would burn API spend to reproduce the same
crash.
