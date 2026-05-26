# Pre-Phase-4 Real-Provider Eval — 2026-05-25 20:18

## 1. Verdict

**Phase 3 blocked.** Merge criterion #1 (50 games complete without
crashes) **FAILED**. The 50-game tournament crashed at the start of
game 28 (seed 27) with a Pydantic `ValidationError` raised at
[llm/provider.py:128](llm/provider.py#L128) inside
`schema.model_validate_json(text)`. The failing schema was
`ReportDocument` — same family as the earlier 21:38 run (also
`ReportDocument`) and a different family from the 18:23 run
(`Statement`). The live-LLM payload that broke parsing began with a
**prose preamble** ("`I need to analyze my mem…ous candidate."\n}\n````"`)
wrapping JSON inside a markdown code fence — a shape the existing
fence-stripper added by task 3.17 does not match, because its open
regex `^\s*```(?:json)?\s*` requires the fence to start the response.

Criterion #2 (impostor win rate band) is **Cannot evaluate** — the
replay JSONL does not persist `GameOverEvent.winner`, the tournament
crashed before printing its aggregate summary, and the prompt
forbids re-running. Criterion #3 (cost ≤ $0.30 mean) **passes on the
partial 27-game data set** (mean $0.0157, two meeting-bearing games
$0.21 each, rest $0.00). Criterion #4 (transcript readability) is
**Cannot evaluate** — only 2 games fired meetings before the crash,
below the 3-game minimum specified in §4 of the prompt; the 2 we did
read look strong. Criterion #5 (replay record completeness) **passes
on the 2 sampled games** (meeting transcripts, prompt versions at
meeting level, 12 LLMCallRecord rows per meeting, cost reconstruct-
able via `compute_cost_usd`).

## 2. Environment

- Provider: `AILIBI_LLM_PROVIDER=anthropic`
- Meeting model: `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- Trigger model: `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8-char prefix only — full
  key never echoed).
- Env vars sourced from project [.env](.env) before each invocation
  (`set -a; source .env; set +a`); project code does not call
  `load_dotenv`.
- [scripts/check.sh](scripts/check.sh) → **pass** (678 passed, 10
  skipped in 4.50s) under default CI config (provider env unset →
  fake provider).
- Direct sanity call (small `client.complete` with `prompt="Respond
  with the single token: OK"`, no schema): `model=claude-sonnet-4-6
  cost_usd=0.000105 text='OK'` → live provider confirmed reachable
  and non-zero-cost (so we know `build_default_client` did not
  silently fall back to fake).
- Pre-flight smoke (3 games, seeds 0–2,
  `/tmp/eval-smoke/`): all 3 games completed, no meetings fired (0%
  trigger rate at n=3 is normal at the documented ~7–10% baseline),
  per-game cost $0.0000. The smoke verified the wrapper survives,
  not the meeting pathway — the direct sanity call already validated
  the live provider.
- 50-game tournament command (exact invocation):
  ```bash
  uv run python scripts/run_tournament.py \
    --num-games 50 \
    --start-seed 0 \
    --output-dir /tmp/eval-50 \
    --max-ticks 1000
  ```

## 3. Tournament outcome

- **Tournament did not print a summary.** The script raised an
  uncaught `pydantic_core._pydantic_core.ValidationError` and exited
  non-zero before
  [eval/balance_eval.py:163-167](eval/balance_eval.py#L163-L167)
  could assemble the `BalanceReport`.
- **27 of 50 games completed** (seeds 0 through 26). Game 28 (seed
  27) is the crashing game — it produced no replay or audit file,
  consistent with the crash firing during `_collect_reports` before
  any `record_meeting` or end-of-game `record_tick` could persist
  anything for that game.
- The crashing traceback (verbatim, last 18 lines):
  ```
  File "orchestrator/game.py", line 763, in _run_and_apply_meeting
      artifacts = _drive_async(...)
  File "orchestrator/game.py", line 914, in _drive_async
      return asyncio.run(coro)
  File "orchestrator/game.py", line 292, in run_meeting
      result = await self._manager.run(...)
  File "meetings/manager.py", line 443, in run
      reports = await self._collect_reports(...)
  File "meetings/manager.py", line 506, in _collect_reports
      return await _gather_all_or_cancel(coroutines)
  File "meetings/manager.py", line 173, in _gather_all_or_cancel
      raise eg.exceptions[0] from None
  File "meetings/manager.py", line 527, in _collect_one_report
      response = await asyncio.wait_for(...)
  File "meetings/manager.py", line 141, in _isolate_provider_timeout
      return await coro
  File "orchestrator/game.py", line 214, in complete
      response = await self._inner.complete(...)
  File "llm/budgeted_client.py", line 266, in complete
      response = await self._inner.complete(...)
  File "llm/provider.py", line 128, in complete
      schema.model_validate_json(text)
  pydantic_core._pydantic_core.ValidationError: 1 validation error
    for ReportDocument
    Invalid JSON: expected ident at line 1 column 2
    input_value='I need to analyze my mem...ous candidate."\n}\n```'
  ```
- The visible portion of `input_value` shows: prose preamble
  ("`I need to analyze my mem…`") then a closing JSON `"\n}` then a
  closing fence ` ``` `. So the model returned **prose + fenced
  JSON**, which the existing
  [`_strip_json_code_fences`](llm/provider.py#L211) regex
  (`^\s*```(?:json)?\s*` anchored at start) does not match.
- This is the **third consecutive 50-game eval** to fail on
  schema-validation of a live-provider meeting response (prior
  attempts at 15:39, 18:23, 21:38 — see other reports under the
  same name). Each iteration has hit a different schema or a
  different malformed shape; whack-a-mole patching (3.17, 3.18,
  3.20) has reduced but not eliminated the failure mode.

## 4. Cost analysis

Computed via `orchestrator.replay.compute_cost_usd` across the 27
replay JSONL files in `/tmp/eval-50/` (excluding `*.audit.jsonl`).

| Metric                 | Value     | Merge criterion |
|------------------------|-----------|-----------------|
| Mean cost / game       | $0.0157   | ≤ $0.30 ✅      |
| Median cost / game     | $0.0000   | —               |
| Max cost (single game) | $0.2159   | (< $1.00 abort)  |
| Min cost (single game) | $0.0000   | —               |
| Std dev                | $0.0566   | —               |
| Total spend (replay)   | $0.4240   | —               |
| Games with cost > 0    | 2 of 27   | —               |

Plus out-of-tournament spend tracked separately:

- Direct sanity call: $0.000105
- Estimated lost spend from the crashed seed-27 meeting (no replay
  written; visible from traceback that ≥1 `client.complete` call
  returned): ~$0.01–0.05 (unmeasurable; this is an additional reason
  to fix the crash path so cost gets persisted before it's discarded).

The cost criterion **passes on the partial data**, but the partial
data is heavily zero-weighted: 25 of 27 games never fired a meeting
and so spent $0. The two games that did fire meetings landed at
$0.2082 (seed 22) and $0.2159 (seed 24) — both below the $0.30
target but only by about ~30%. With more meeting-bearing games in
the sample, the mean would rise substantially; a full 50-game run
that fired ~5 meetings would land around $0.020–0.025 mean. That is
still inside the target, but the headroom is thinner than the
current 0.0157 number suggests. Cost discipline appears fine in
principle; the bottleneck is the crash, not budget.

## 5. Win-rate analysis

**Cannot evaluate.** The tournament crashed before
[eval/balance_eval.py:163-167](eval/balance_eval.py#L163-L167) emit-
ted the `BalanceReport`, and the per-seed replay JSONL files do not
persist `GameOverEvent.winner` (the replay only records `actions` +
`state_hash` per tick — outcomes live in engine events that aren't
written to disk; see [orchestrator/replay.py:74-83](orchestrator/replay.py#L74-L83)
for the `ReplayEntry` schema and [orchestrator/game.py:832-838](orchestrator/game.py#L832-L838)
for `_game_over_outcome`'s in-memory dependence on `last_events`).

The audit log per agent terminates at the LLM-decision tick (not the
game-end tick), so it cannot be used to infer winners either: max
audit tick per game is 5–13 against `--max-ticks 1000`, confirming
games ended decisively, but not which side won.

Re-running to recover this data is forbidden by §1 of the eval
prompt ("Do not re-run the tournament if it crashes; report the
crash"). A follow-up task should either (a) persist `GameOverEvent`
into the replay so post-hoc analysis works on crashed runs, or
(b) emit a side-file with the in-progress tally so a partial run
yields a partial win-rate.

## 6. Leak scan

All 27 audit logs scanned via
[`eval/leak_test.py::_assert_no_recursive_hidden_fields`](eval/leak_test.py#L158)
+ [`_assert_no_role_bearing_values`](eval/leak_test.py#L175).

| Metric         | Value |
|----------------|-------|
| Games scanned  | 27    |
| Packets scanned| 900   |
| Violations     | 0 ✅  |

## 7. Replay record completeness

Sampled the **2 games with `MeetingReplayEntry` rows** (seeds 22 &
24 — the only meeting-bearing games in the partial run). Note: this
is **below the 5-game target** in §3 of the prompt, but is the full
available coverage given the partial run.

| seed | `MeetingReplayEntry` | `LLMCallRecord` rows | sample row shape                                          | `compute_cost_usd` reconstructs? |
|------|---------------------|---------------------|----------------------------------------------------------|----------------------------------|
| 22   | Yes (1, tick 7)     | 12                  | `model='claude-sonnet-4-6' cost_usd=0.013041 kind=meeting` | Yes — $0.2082, matches §4 sum    |
| 24   | Yes (1, tick 10)    | 12                  | `model='claude-sonnet-4-6' cost_usd=0.015912 kind=meeting` | Yes — $0.2159, matches §4 sum    |

`prompt_versions` are present at the **meeting-entry level** (not
nested per-LLM-call), consistent with concern R-3 in
[audits/audit-2026-05-25-0414-reconciled.md](audits/audit-2026-05-25-0414-reconciled.md).
The observed map for both meetings:
```
{
  'accusation_round': 'accusation_round.v1',
  'crewmate_report':  'crewmate_report.v1',
  'impostor_report':  'impostor_report_v1',
  'vote_ballot':      'vote_ballot/v1',
}
```
Each `LLMCallRecord` carries `call_kind`, `cost_usd`,
`input_tokens`, `output_tokens`, `model`, `prompt`, `response_text`
— the merge-criterion-required fields are all there. **Pass** on
the games sampled.

## 8. Transcript readability

**Cannot evaluate** by the §4 rubric (≥3 games sampled is the
threshold; only 2 meeting-bearing games exist in the partial run).

Even though we cannot reach a Pass/Fail verdict, the transcripts we
do have are largely strong; the per-game judgment table is included
below for completeness, not as a verdict.

| seed | Coherent English | Role-appropriate | Grounded in game state | Vote justifications | Game verdict (if evaluable) |
|------|------------------|------------------|------------------------|---------------------|-----------------------------|
| 22   | Pass             | Pass             | Pass                   | Pass                | (4/4 dims pass)             |
| 24   | Pass             | Pass             | **Partial**            | Pass                | (3/4 — see notes)           |

Reasoning per dimension (kept short — full transcripts in
`/tmp/eval-50/replay-seed-{22,24}.jsonl`):

**Seed 22** — meeting at tick 7, triggered by p-3 finding p-1's
body in CAFETERIA at tick 6. All three living players (p-2, p-3,
p-4) submit reports grounded in their observation streams. Two
statement rounds, structured `alibi` / `corroboration` /
`accusation` claims, evidence cites specific ticks and rooms that
appear in the audit log. Vote rationales are full prose, each
voter explains why they ruled out alternatives, and p-4's
rationale even self-admits the impostor role ("As the impostor, I
killed p-1 in CAFETERIA and my best survival play is to keep the
vote on p-2") — that's in-character reasoning, not a hidden-state
leak, because it's in the **voter's own** ballot which the voter
already knows. The meeting ejects p-2 (a crewmate); the impostor
deception succeeded. All 4 dimensions Pass.

**Seed 24** — meeting at tick 10, triggered by p-3 finding p-1's
body. Reports and statements are grammatical, the meeting plays
out coherently with two statement rounds and decisive voting.
However, p-4's statement (round 0) contains
`"alibi": {"subject": "p-5", ...}` — referencing a player ID
**p-5 that does not exist** in this 4-player game (players are
p-1..p-4). The claim is schema-valid (the schema accepts any
string), but ungrounded. This is the kind of fabrication that the
grounding dimension is meant to catch. Marked Partial, not Fail,
because every other claim in p-4's statement, and every claim in
the other 5 statements, ties to real players/rooms/ticks. Other
dimensions Pass: votes and rationales are coherent ("a body can
only be discovered once, so one report is fabricated"); the
contradicting body-discovery timestamps between p-2 and p-3 are
the central plot of the meeting and the votes correctly resolve
it. The meeting ejects p-2.

These two transcripts are encouraging — when the model **does**
produce schema-valid JSON, the in-game content is rich. The
problem this eval surfaces is the upstream parse failure, not
quality.

## 9. Observations

Three code-level items worth flagging for the follow-up task that
will fix the crash (not full audit findings — those are for the
static audit stage):

(1) **Fence-stripper is open-anchored only.**
[`_strip_json_code_fences`](llm/provider.py#L211) in
[llm/provider.py](llm/provider.py) uses
`_FENCE_OPEN_PATTERN = re.compile(r"^\s*` ``` `(?:json)?\s*", IGNORECASE)`.
It requires the fence to be the very first thing in the response
(after whitespace). The crashing payload here started with a prose
preamble ("I need to analyze my memory…") *before* the fenced JSON
— the open regex didn't match and the fence stayed, the prose
stayed, and `model_validate_json` died on the leading `I`. The fix
is either (a) extract the first balanced `{…}` block, (b)
search-not-anchor the open fence and crop everything before it, or
(c) re-prompt with a stricter "JSON only, no prose" instruction
combined with a parser-side fallback. (a) is the most robust and
provider-neutral.

(2) **Crashing meetings drop their cost.** The exception fires inside
`provider.complete` *before* `LLMResponse` is constructed, so the
budget layer never sees the tokens that the model already burned to
generate the rejected response, and `ReplayLog.record_meeting` is
never called for the meeting. Result: §4 undercounts spend, and we
can't audit how much we paid for the responses that broke us.
Consider recording a partial `LLMCallRecord` (or a
`FailedLLMCallRecord`) before re-raising, so post-mortem analysis
can see what the cost discipline cost us.

(3) **Replay does not persist game outcome.**
`ReplayEntry`'s `kind="tick"` records actions + state_hash but not
the engine events. `GameOverEvent.winner` is consumed by
`_game_over_outcome` in memory and discarded. A 27-of-50 partial
run with no recovered win-rate is the directly observable cost of
this — see §5. A one-line `record_game_end(winner)` would unblock
post-hoc analysis on every crashed run.

## 10. Verdict justification

The verdict in §1 follows directly from criterion #1: a single
uncaught `ValidationError` aborted the tournament at game 28, so
"50 games complete without crashes" is unambiguously not met. The
remaining criteria are non-verdicts on a deeper read: cost passes
on partial data (§4), leak scan passes on partial data (§6),
replay completeness passes on the 2 games available (§7); win-rate
and readability are not evaluable from a partial run with only 2
meeting-bearing games (§5, §8). When the crash root cause is fixed,
a fresh 50-game eval should reach all five criteria. The single
remediation that would unblock Phase 3 is hardening the JSON
extraction layer in [llm/provider.py](llm/provider.py) so prose
preambles and unanchored fences both get stripped before
`model_validate_json` — same family of fix as task 3.17, broader
in shape coverage.
