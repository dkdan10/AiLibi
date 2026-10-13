# Pre-Phase-4 Real-Provider Eval — 2026-05-25 18:23

## 1. Verdict

**Phase 3 blocked.** Merge criterion #1 (50 games complete without
crashes) FAILED. The 50-game tournament crashed at the start of game
24 (seed 23) with a Pydantic `ValidationError` raised by
`schema.model_validate_json(text)` at `llm/provider.py:128`. The
schema this time was **`Statement`** (a meeting participant's
turn-statement), not the `ReportDocument` schema that crashed the
prior 21:38 run. The live-provider response was truncated mid-string
inside a `"reason": "...erious problem with p-4"` field — classic
`max_tokens` truncation, this time on the statement-collection
pathway in [meetings/manager.py:576](meetings/manager.py#L576)
(`_collect_statement`) rather than the report pathway that Task 3.17
addressed.

Criteria #2 through #5 cannot be evaluated: the 23 games that
completed (seeds 0–22) all ended decisively in 7–13 ticks and
**fired zero meetings**, so there is no live-LLM cost data,
no transcript to read, and no `MeetingReplayEntry` in any replay
log. The leak scan is the only data merge-criterion that returned a
green light, on partial data.

## 2. Environment

- Provider: `AILIBI_LLM_PROVIDER=anthropic`
- Meeting model: `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- Trigger model: `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8-char prefix only)
- Env vars sourced from project [.env](.env) before each invocation
  (project code does not call `load_dotenv`; relies on env being
  pre-set in the parent shell).
- [scripts/check.sh](scripts/check.sh) → **pass** under documented CI
  configuration (`AILIBI_LLM_PROVIDER=fake`): 678 passed, 8 skipped
  in 4.63s. Note: when invoked with `AILIBI_LLM_PROVIDER=anthropic`
  already exported, 2 tests fail (`test_default_cap_admits_fake_provider_meeting`
  in [tests/llm/test_budgeted_client.py](tests/llm/test_budgeted_client.py)
  and `test_meetings_fire_and_game_resumes_from_public_factory_path`
  in [tests/orchestrator/test_meeting_integration.py](tests/orchestrator/test_meeting_integration.py))
  because they consult `build_default_client` and end up calling the
  live API — counter to [llm/README.md](llm/README.md)'s contract.
  See §9.
- Direct sanity call → **pass**:
  `model=claude-sonnet-4-6 cost_usd=0.000105 text='OK'`. Non-zero
  cost proves the live provider was actually called; model id matches
  `MEETING_MODEL`.
- 3-game smoke (`/tmp/eval-smoke`) → **pass**: 3 games completed,
  no crashes, zero meetings fired (expected at ~7–10% rate);
  `compute_cost_usd` returned `$0.00` for all three.
- 50-game tournament command exactly as invoked:

  ```bash
  uv run python scripts/run_tournament.py \
    --num-games 50 \
    --start-seed 0 \
    --output-dir /tmp/eval-50 \
    --max-ticks 1000
  ```

## 3. Tournament outcome

**Tournament crashed.** Process exited non-zero; `_format_report` was
never reached so the canonical four-bucket counts are unavailable.

Reconstructed from `/tmp/eval-50`:

- Replay + audit pairs written: **23 games** (seeds 0–22).
- Crashed seed: **23** (no replay file produced; the failure happened
  during meeting setup before any tick record was flushed).
- Crash signature (verbatim, abridged):

  ```
  File ".../orchestrator/game.py", line 763, in _run_and_apply_meeting
  File ".../meetings/manager.py", line 576, in _collect_statement
  File ".../llm/provider.py", line 128
      schema.model_validate_json(text)
  pydantic_core._pydantic_core.ValidationError: 1 validation error for Statement
    Invalid JSON: EOF while parsing a string at line 37 column 57
    [type=json_invalid, input_value='{\n  "statement_id": "s"...erious problem with p-4', input_type=str]
  ```

- The 23 completed games each ended at tick 7–13 (decisive outcome;
  none reached `tick_budget_reached` and none triggered a meeting).
- Outcome split for the 23 completed games is **not reconstructable**
  from the replay JSONL alone — the records contain only per-tick
  `{tick, game_id, state_hash, actions, kind="tick"}` rows; the
  decisive winner is computed by `HeadlessGame.run()` and only
  observable via its return value, which the tournament loop swallowed
  on crash before any aggregate was printed. (Not a code-level audit
  finding; just an evidentiary limitation of partial data.)

## 4. Cost analysis

| Metric                     | Value     | Merge criterion |
|----------------------------|-----------|------------------|
| Mean cost / game           | $0.0000   | ≤ $0.30         |
| Median cost / game         | $0.0000   | —                |
| Max cost (single game)     | $0.0000   | —                |
| Min cost (single game)     | $0.0000   | —                |
| Std dev                    | $0.0000   | —                |
| Total tournament spend     | $0.0000   | —                |
| Sanity-call spend          | $0.000105 | —                |
| **Total eval spend**       | **$0.000105** | —            |

Computed via
[orchestrator.replay.compute_cost_usd](orchestrator/replay.py) over
the 23 `/tmp/eval-50/replay-seed-*.jsonl` files (excluding
`*.audit.jsonl`). All 23 returned `0.0` because none contain a
`MeetingReplayEntry` (zero meetings fired pre-crash). The single
non-zero cost in this eval is the §2 direct sanity call.

**Pass / Fail on merge criterion (mean ≤ $0.30):** **Cannot evaluate.**
Zero meetings on the live wire means no representative live-meeting
cost was sampled. The numeric "$0.00 ≤ $0.30" comparison is vacuously
true but does not validate the criterion.

## 5. Win-rate analysis

**Cannot evaluate.** Decisive split (CREWMATES% / IMPOSTORS%) for the
23 completed games is not reconstructable from the replay JSONL
without re-running the seeds or simulating the engine end-condition
externally — and re-running burns spend without changing the
diagnosis (prompt §"Anti-patterns"). The tournament's printed summary
would have given the four-bucket counts, but the crash short-circuited
it.

What can be said: all 23 completed games reached a decisive outcome
(not `tick_budget_reached`) in 7–13 ticks. That is a substrate
observation, not a balance verdict.

**Pass / Fail on merge criterion (impostor in [25%, 65%]):** **Cannot
evaluate.**

## 6. Leak scan result

| Bucket            | Count |
|-------------------|-------|
| Games scanned     | 23    |
| Packets scanned   | 748   |
| Violations        | **0** |

Ran
[`_assert_no_recursive_hidden_fields`](eval/leak_test.py#L158) +
[`_assert_no_role_bearing_values`](eval/leak_test.py#L175) over every
record in every `*.audit.jsonl` in `/tmp/eval-50`. Each audit record
is itself a flat observation packet (`agent_id`, `tick`, `self_state`,
`visible_players`, `visible_bodies`, `audible_events`, `cooldown`,
`global_state`) — the scanners' native input shape.

**Pass / Fail:** **Pass** (on partial data — 23/50 games).

## 7. Replay record completeness

**Cannot evaluate.** Sampling protocol called for "the first 5 games
(lowest game_id first) that contain at least one `MeetingReplayEntry`."
**Zero** of the 23 completed games contain any `MeetingReplayEntry`
(verified: the only `kind` value found across all replay records is
`"tick"`). The criterion is therefore unevaluable on this partial
data.

| game_id / seed | MeetingReplayEntry present? | LLMCallRecord rows | Cost reconstructable? |
|----------------|------------------------------|--------------------|------------------------|
| —              | n/a — no sample available    | n/a                | n/a                    |

**Pass / Fail:** **Cannot evaluate.**

## 8. Transcript readability

**Cannot evaluate.** Same root cause as §7: zero `MeetingReplayEntry`
rows across the 23 completed games means there are no transcripts to
rate. Per the prompt's protocol, "if the 50-game eval produces fewer
than 3 games with meetings, verdict the criterion as **Cannot
evaluate** and recommend a longer eval run." That recommendation
applies *if and only if* the crash is fixed first — extending the
seed range past 22 is what produced the crash in the first place.

| game_id / seed | Coherent English | Role-appropriate | Grounded | Vote justifications | Game verdict |
|----------------|------------------|------------------|----------|---------------------|--------------|
| —              | n/a              | n/a              | n/a      | n/a                 | n/a          |

**Pass / Fail:** **Cannot evaluate.**

## 9. Observations

1. **`Statement` schema is a sibling of the `ReportDocument` defect
   Task 3.17 fixed.** The 21:38 prior eval crashed on `ReportDocument`
   truncation; Task 3.17 raised its `max_tokens` and improved
   unclosed-fence stripping. The current crash is the same shape
   (truncated-JSON → `model_validate_json` failure) on a *different*
   schema and code path
   ([meetings/manager.py:576](meetings/manager.py#L576),
   `_collect_statement`). The truncated input ends with
   `..."reason": "...erious problem with p-4` — a `Statement` (or
   nested `VoteBallot`) field cut off mid-string, consistent with the
   `Statement`-side `max_tokens` cap not having been raised alongside
   the report-side cap. Recommendation: a hygiene task that
   (a) audits every meeting-LLM call site for an analogous
   `max_tokens` headroom check and (b) considers hoisting the
   fence-strip + retry-on-truncation logic into a shared layer above
   `provider.complete()` so any future schema picks it up by default.
2. **CI contract drift.** `check.sh` is sensitive to whether
   `AILIBI_LLM_PROVIDER` is exported at invocation. Two tests build
   `build_default_client()` and inherit the env; both fail when the
   var is `anthropic`. The README's "CI must leave it unset" rule
   should be enforced in code (e.g., the two tests should construct
   `FakeProvider()` directly, or monkeypatch the env, rather than
   rely on the caller). Not blocking this eval — but it is a quiet
   sharp edge.

## 10. Verdict justification

The eval did not produce a complete data set: the tournament crashed
at seed 23 (game 24 of 50), and none of the 23 games that completed
exercised any meeting LLM traffic. Merge criterion #1 ("50 games
complete without crashes") is therefore a definitive **Fail**.
Criteria #2 (win-rate band), #3 (mean cost ≤ $0.30), #4 (transcript
readability), and #5 (replay record completeness) are **Cannot
evaluate** because each requires data the partial run did not
generate. Only criterion-adjacent diligence — the leak scan over the
23 completed audits — passed on partial data. Per §6 of the prompt,
**Phase 3 blocked** with the remediation path "Crash → code defect,
escalate to a hygiene task" is the correct verdict; the hygiene task
is the `Statement` `max_tokens` headroom (Observation 1).
