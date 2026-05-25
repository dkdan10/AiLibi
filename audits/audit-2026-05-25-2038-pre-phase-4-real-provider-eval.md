# Pre-Phase-4 Real-Provider Eval — 2026-05-25 20:38 UTC

## 1. Verdict

**Phase 3 blocked.** Merge criterion #1 (50 games complete without
crashes) FAILED: the tournament crashed during game 24 (seed 23) with
a Pydantic `ValidationError` on `ReportDocument` — the model emitted
the meeting `ReportDocument` using **old field names**
(`player_id`, `location`, `tick_start`, `tick_end`, `description`,
`target_id`) while the schema requires **new field names**
(`subject`, `room`, `from_tick`, `to_tick`, `against`, `body_of`).
The first 23 games (seeds 0–22) completed cleanly but produced **zero
meetings** at the live ~7–10% trigger rate, so criteria #2–#5 (win
rate band, mean cost, transcript readability, replay-record
completeness) cannot be evaluated from the partial data. The
underlying defect is a prompt-template ↔ Pydantic-schema drift in
the meeting `ReportDocument` path: the prompt instructs the model to
use the legacy keys, but `model_validate_json` enforces the new keys
with `extra='forbid'`, so the **first** real meeting deterministically
crashes the eval.

## 2. Environment

- Provider: `AILIBI_LLM_PROVIDER=anthropic`
- Meeting model: `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- Trigger model: `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8-char prefix only)
- Env vars were not exported into the shell automatically — sourced
  from project `.env` before each invocation (project code itself
  does not call `load_dotenv`; relies on env being pre-set).
- `bash scripts/check.sh` → **pass** (676 passed, 3 skipped in 4.42s).
- Direct sanity call → **pass**:
  `model=claude-sonnet-4-6 cost_usd=0.000105 text='OK'` (non-zero
  cost proves live provider; model matches `MEETING_MODEL`).
- 3-game smoke (`/tmp/eval-smoke`) → **pass**: 3 games completed,
  no crashes, zero meetings fired (expected at ~7–10% rate); per-game
  cost via `compute_cost_usd` was `$0.00` for all three — consistent
  with no LLM meeting traffic. Wrapper integration validated.
- 50-game tournament command exactly as invoked:

  ```bash
  uv run python scripts/run_tournament.py \
    --num-games 50 \
    --start-seed 0 \
    --output-dir /tmp/eval-50 \
    --max-ticks 1000
  ```

## 3. Tournament outcome

**Tournament crashed.** Process exited non-zero before the
`_format_report` summary was printed. No `decisive_split` line was
ever emitted, so the canonical four-bucket counts are unavailable.

Reconstructed from the output directory:

- Replay+audit pairs written: **23 games** (seeds 0–22 inclusive).
- Replay files for the 23 completed games contain only `kind=tick`
  records (no game-result record is written into the JSONL; outcome
  is only reflected in the printed summary, which the crash suppressed).
- Crash trace head (full trace in `/tmp/eval-50/tournament-stdout.log`,
  174 lines):

  ```
  File ".../orchestrator/game.py", line 763, in _run_and_apply_meeting
  File ".../meetings/manager.py", line 520, in _collect_one_report
  File ".../llm/provider.py", line 128, in complete
      schema.model_validate_json(text)
  pydantic_core._pydantic_core.ValidationError:
      38 validation errors for ReportDocument
  observations.0.saw_player.player_id  Extra inputs are not permitted [...]
  observations.0.saw_player.subject     Field required [...]
  observations.0.saw_player.room        Field required [...]
  observations.5.found_body.player_id   Extra inputs are not permitted [...]
  observations.5.found_body.body_of     Field required [...]
  claims.0.alibi.tick_start             Extra inputs are not permitted [...]
  claims.0.alibi.from_tick              Field required [...]
  claims.0.alibi.to_tick                Field required [...]
  claims.0.alibi.subject                Field required [...]
  claims.0.alibi.room                   Field required [...]
  claims.1.accusation.target_id         Extra inputs are not permitted [...]
  claims.1.accusation.against           Field required [...]
  ```

  Pattern: every `saw_player`, `found_body`, `alibi`, and `accusation`
  field the model emitted used a legacy key; the schema required the
  new key and rejected the legacy key (extra='forbid' shape).

Crash location in the seed sweep: the next seed after the last
completed game (22) is **seed 23**, and the trigger rate observed
across the 23 prior games is 0 meetings — so the crash is consistent
with "first meeting ever triggered against the live provider fails."

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
| **Total real-provider spend this eval** | **~$0.0001** | — |

**Cannot evaluate** against the $0.30/game criterion: every
completed game emitted zero meeting LLM calls because no meeting was
triggered before the crash. The cost target is a per-game *budget*
intended to cover meeting traffic; observing $0 here is not evidence
of "under budget," only evidence that the eval never exercised the
path the budget governs. The crashed game (seed 23) would have been
the first data point on real meeting cost and was lost.

Mid-run abort conditions: none fired prior to the crash (first-10
mean $0.00 ≪ $0.60; per-game max $0.00 ≪ $1.00).

## 5. Win-rate analysis

**Cannot evaluate.** The tournament summary that emits
`decisive_split: CREWMATES=...% IMPOSTORS=...%` was never printed
(crash occurred inside `run_balance_eval` before `_format_report`).
The per-game replay JSONLs the script *did* write contain only
`kind=tick` records — no per-game `GameResult` row is persisted,
so I cannot reconstruct crew/impostor decisive counts from the 23
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
would be required *after the underlying crash is fixed*; recommending
a longer run on the current code would just hit the same crash on
the first meeting.

## 9. Observations

- The crash is a **prompt ↔ schema drift** on `ReportDocument`. The
  Pydantic schema enforces `subject`, `room`, `from_tick`, `to_tick`,
  `against`, `body_of`, with `extra='forbid'`; the live model emitted
  `player_id`, `location`, `tick_start`, `tick_end`, `description`,
  `target_id`. The model's output is internally consistent (it picked
  a coherent set of legacy keys) which suggests the meeting-report
  prompt template still describes the legacy field names. The fake
  provider never exercises this divergence because it constructs
  `ReportDocument` objects directly from internal fixtures rather
  than round-tripping JSON shaped by the prompt — so the static and
  fake-provider audits could not have caught it. This is exactly the
  class of defect the live eval exists to catch.
- The per-game replay files do not persist a `GameResult` row, so
  partial-tournament outcome reconstruction is impossible without
  re-parsing the audit log or re-running with a tee'd summary. If
  future eval crashes are anticipated, persisting per-game outcome
  to replay JSONL would meaningfully improve diagnostic value.
- The merge criterion "mean cost ≤ $0.30/game" is currently
  un-stress-tested in any setting that actually exercises meetings,
  because (a) fake provider has $0 cost and (b) live provider here
  crashed on first meeting. A follow-up fix MUST validate cost on a
  run that produces meetings, not just one that finishes.

## 10. Verdict justification

§3 documents a non-zero-exit crash during the 50-game eval, which
directly fails merge criterion #1 (50 games complete without
crashes). §4, §5, §7, §8 each carry "Cannot evaluate" because the
crash occurred on the first meeting attempted (seed 23), depriving
those criteria of any meaningful data — every completed game is a
"no-meeting" game. §6 (leak scan) is the only criterion with a clean
Pass, but a single passing criterion is not sufficient. Per the
prompt's verdict rules ("Crash → code defect, escalate to a hygiene
task"), the verdict is **Phase 3 blocked** and the remediation path
is a follow-up task to (a) align the meeting-report prompt template
with the current `ReportDocument` field names, (b) add a real-provider
schema-roundtrip test exercising `ReportDocument` directly (analogous
to Task 3.15's markdown-fence stripping test), and (c) re-run this
eval after the fix lands. Re-running this eval against the current
code would burn API spend to reproduce the same crash.
